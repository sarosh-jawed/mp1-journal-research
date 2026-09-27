"""Synthetic ordinal outcomes, retained multiplicities and frozen-source safeguards."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import yaml
from scipy.stats import kruskal, mannwhitneyu
from sklearn.metrics import adjusted_rand_score
from threadpoolctl import threadpool_limits

from mp1.audit import read_raw_csv, sha256_file
from mp1.clustering import fit_partition, ordinal_features
from mp1.d_validation import reconcile_rank_table
from mp1.outcome_validation import (
    audit_cgpa,
    category_counts,
    ordinal_comparison,
    rank_effect,
    resampling_interval,
    run_outcome_validation,
)
from mp1.response_quality import assess_responses


@pytest.fixture
def outcome_project(tmp_path: Path) -> dict:
    repo, sources = tmp_path / "repo", tmp_path / "sources"
    (repo / "config").mkdir(parents=True)
    sources.mkdir()
    items, response = [f"q{i}" for i in range(4)], ["one", "two", "three", "four", "five"]
    rng = np.random.default_rng(513)
    x = np.vstack([rng.integers(1, 4, (160, 4)), np.tile([5, 4, 5, 4], (80, 1))])
    x[:3] = 2
    frame = pd.DataFrame(np.array(response)[x - 1], columns=items)
    frame["institution"] = [f"synthetic_{i % 8}" for i in range(len(frame))]
    frame["CGPA"] = [f"band{i % 4}" for i in range(len(frame))]
    source, flags_path = sources / "synthetic.csv", sources / "flags.csv"
    frame.to_csv(source, index=False)
    raw = read_raw_csv(source, "D3")
    flags, _, _, _ = assess_responses(raw, items, response, [])
    flags.to_csv(flags_path, index=False)
    config = {
        "project": {"random_seed": 7, "drive_root_env": "MP1_SYNTHETIC_D_ROOT"},
        "data": {"d3_raw": source.name},
        "clustering": {"n_init": 3},
        "response_quality": {"private_flags": "data/processed/flags.csv"},
        "integrity": {
            "csv_encoding": "utf-8-sig",
            "missing_tokens": [],
            "datasets": {
                "D3": {
                    "survey_items": items,
                    "allowed_responses": response,
                    "institution_column": "institution",
                    "source_metadata": {"published_file_sha256": raw.sha256},
                }
            },
        },
    }
    config_path = repo / "config/analysis.yaml"
    config_path.write_text(yaml.safe_dump(config))
    cluster_dir, measurement_dir = repo / "outputs/clustering", repo / "outputs/psychometrics"
    cluster_dir.mkdir(parents=True)
    measurement_dir.mkdir(parents=True)
    centroids, sizes, members, labels, expected = [], [], [], {}, {}
    mask = flags.include_sensitivity.to_numpy()
    with threadpool_limits(limits=1):
        for sample, keep in [("full", np.ones(len(x), dtype=bool)), ("sensitivity", mask)]:
            y, centers = fit_partition(ordinal_features(x[keep]), 2, 9, 3)
            labels[sample], expected[sample] = y, np.bincount(y).tolist()
            for j in [0, 1]:
                sizes.append(
                    {
                        "dataset": "D3",
                        "sample": sample,
                        "k": 2,
                        "cluster": j + 1,
                        "count": int(sum(y == j)),
                    }
                )
                for i, item in enumerate(items):
                    centroids.append(
                        {
                            "dataset": "D3",
                            "sample": sample,
                            "k": 2,
                            "cluster": j + 1,
                            "item": item,
                            **{
                                f"probability_above_{t + 1}": 2 * centers[j, i * 4 + t]
                                for t in range(4)
                            },
                        }
                    )
            members.extend(
                {
                    "dataset": "D3",
                    "source_sha256": raw.sha256,
                    "source_record_number": int(position),
                    "sample": sample,
                    "k": 2,
                    "cluster": int(label + 1),
                }
                for position, label in zip(np.flatnonzero(keep) + 1, y, strict=True)
            )
    pd.DataFrame(centroids).to_csv(cluster_dir / "cluster_centroids.csv", index=False)
    pd.DataFrame(sizes).to_csv(cluster_dir / "cluster_sizes.csv", index=False)
    pd.DataFrame(
        [
            {
                "dataset": "D3",
                "k": 2,
                "full_sensitivity_ari": adjusted_rand_score(
                    labels["full"][mask], labels["sensitivity"]
                ),
            }
        ]
    ).to_csv(cluster_dir / "quality_sensitivity.csv", index=False)
    (cluster_dir / "clustering_summary.json").write_text(
        json.dumps(
            {
                "choices": {"D3": {"k": 2}},
                "quality_flags_sha256": sha256_file(flags_path),
                "private_memberships": "data/interim/work_package_b/memberships.csv",
            }
        )
    )
    pd.DataFrame(
        {"dataset": "D3", "position": range(1, 5), "item": items, "raw_column": items}
    ).to_csv(measurement_dir / "item_inventory.csv", index=False)
    membership_path = sources / "memberships.csv"
    pd.DataFrame(members).to_csv(membership_path, index=False)
    settings = {
        "baseline_commit": "synthetic",
        "frozen_files": {
            str(p.relative_to(repo)): sha256_file(p) for p in repo.rglob("*") if p.is_file()
        },
        "d3": {
            "outcome": "CGPA",
            "categories": [f"band{i}" for i in range(4)],
            "expected_sizes": expected,
            "centroid_tolerance": 1e-12,
            "minimum_assignment_margin": 1e-12,
            "bootstrap_repetitions": 200,
            "bootstrap_seed": 12,
            "confidence_level": 0.95,
            "output_directory": "outputs/outcome_validation/work_package_d",
            "private_directory": "data/interim/work_package_d",
        },
    }
    settings_path = repo / "config/work_package_d.yaml"
    settings_path.write_text(yaml.safe_dump(settings))
    return {
        "config_path": config_path,
        "settings_path": settings_path,
        "d3_path": source,
        "flags_path": flags_path,
        "memberships_path": membership_path,
    }


def test_order_only_audit_preserves_missing_unknown_and_source_values() -> None:
    source = pd.Series(["low", "high", "low", "", None, "2.50"])
    original = source.copy()
    values, audit = audit_cgpa(source, ["low", "high"])
    assert values[:3].tolist() == [0, 1, 0]
    assert np.isnan(values[3:]).all()
    assert audit.records.sum() == 6
    assert set(audit.status) == {
        "eligible_ordered_band",
        "missing_ineligible",
        "unrecognized_ineligible",
    }
    assert not audit.midpoint_imputed.any()
    pd.testing.assert_series_equal(source, original)


def test_rank_effect_matches_all_pairs_and_mann_whitney_with_ties() -> None:
    a, b = np.array([0, 0, 1, 2, 3]), np.array([1, 1, 2, 2, 3, 3])
    outcome, labels = np.r_[a, b], np.r_[np.zeros(len(a)), np.ones(len(b))].astype(int)
    result = ordinal_comparison(outcome, labels, 4)
    expected = np.sign(b[:, None] - a).mean()
    assert result["cliff_delta_P2_minus_P1"] == pytest.approx(expected)
    assert expected == pytest.approx(2 * mannwhitneyu(b, a).statistic / (len(a) * len(b)) - 1)
    transformed = np.array([1, 5, 21, 900])[outcome]
    assert result["kruskal_h_tie_corrected"] == pytest.approx(
        kruskal(transformed[labels == 0], transformed[labels == 1]).statistic
    )
    assert result["posthoc_status"] == "not_needed_two_profiles_one_comparison"
    assert result["rank_epsilon_squared_H_over_N_minus_1"] == pytest.approx(
        result["kruskal_h_tie_corrected"] / 10
    )
    counts = category_counts(outcome, labels, 4)
    assert rank_effect(counts[::-1]) == pytest.approx(-expected)
    independent = reconcile_rank_table(counts)
    assert independent["h"] == pytest.approx(result["kruskal_h_tie_corrected"])
    assert independent["p"] == pytest.approx(result["nominal_p_value"])
    assert independent["delta"] == pytest.approx(expected)


def test_all_tied_outcomes_have_no_rank_information() -> None:
    result = ordinal_comparison(np.ones(20, dtype=int), np.repeat([0, 1], 10), 4)
    assert result["nominal_p_value"] == 1
    assert result["cliff_delta_P2_minus_P1"] == 0
    assert result["kruskal_h_tie_corrected"] == 0


@pytest.mark.parametrize(
    "outcome,labels", [([0, 5], [0, 1]), ([0, 1], [0, 2]), ([0, np.nan], [0, 1]), ([0, 1], [0, 0])]
)
def test_ineligible_outcomes_or_profiles_are_not_silently_dropped(outcome, labels) -> None:
    with pytest.raises(ValueError):
        category_counts(np.array(outcome), np.array(labels), 4)


def test_pattern_resampling_retains_multiplicity_and_is_deterministic() -> None:
    outcomes = np.r_[np.zeros(19), 3, np.zeros(10), np.repeat(3, 10)].astype(int)
    labels = np.repeat([0, 1], 20)
    units = np.array(["large_a"] * 19 + ["small_a"] + ["b0"] * 10 + ["b3"] * 10)
    args = (outcomes, labels, units, 4, 1000, 7, 0.95, True)
    result = resampling_interval(*args)
    assert result == resampling_interval(*args)
    assert result["resampling_units"] == 4
    assert result["cliff_delta"] == pytest.approx(0.45)
    assert result["cliff_delta"] != rank_effect(np.array([[1, 0, 0, 1], [1, 0, 0, 1]]))
    assert result["invalid_replicates"] == 0
    with pytest.raises(ValueError, match="cross profiles"):
        resampling_interval(outcomes, labels, np.arange(40) % 4, 4, 100, 7, 0.95, True)


def test_complete_outcome_pipeline_is_deterministic_and_preserves_sources(outcome_project) -> None:
    original = {path: path.read_bytes() for path in outcome_project.values()}
    destination = run_outcome_validation(**outcome_project)
    snapshot = {p.name: p.read_bytes() for p in destination.iterdir()}
    run_outcome_validation(**outcome_project)
    assert snapshot == {p.name: p.read_bytes() for p in destination.iterdir()}
    assert all(path.read_bytes() == content for path, content in original.items())
    audit = pd.read_csv(destination / "profile_reconstruction.csv")
    assert audit.ari_against_original_memberships.eq(1).all()
    assert set(pd.read_csv(destination / "cgpa_comparisons.csv").variant) == {
        "full",
        "quality_fixed_profiles",
        "quality_refit_profiles",
    }
    for path in destination.glob("*.csv"):
        assert "source_record_number" not in pd.read_csv(path).columns
    manifest = json.loads((destination / "outcome_summary.json").read_text())
    assert all(
        sha256_file(destination / name) == digest
        for name, digest in manifest["artifact_sha256"].items()
    )


@pytest.mark.parametrize("kind", ["raw", "flags", "frozen_centroids"])
def test_corrupted_evidence_stops_outcome_analysis(outcome_project, kind) -> None:
    paths = {
        "raw": outcome_project["d3_path"],
        "flags": outcome_project["flags_path"],
        "frozen_centroids": outcome_project["config_path"].parent.parent
        / "outputs/clustering/cluster_centroids.csv",
    }
    if kind == "raw":
        paths[kind].write_text(paths[kind].read_text().replace("synthetic_0", "changed", 1))
    else:
        with paths[kind].open("a") as handle:
            handle.write(" ")
    with pytest.raises(ValueError, match="fingerprint|Frozen"):
        run_outcome_validation(**outcome_project)


def test_private_output_cannot_be_redirected_to_public_files(outcome_project) -> None:
    path = outcome_project["settings_path"]
    settings = yaml.safe_load(path.read_text())
    settings["d3"]["private_directory"] = "outputs/exposed"
    path.write_text(yaml.safe_dump(settings))
    with pytest.raises(ValueError, match="ignored data/interim"):
        run_outcome_validation(**outcome_project)
    assert not (path.parent.parent / "outputs/exposed").exists()
