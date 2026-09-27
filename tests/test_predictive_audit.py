"""Synthetic tests for target identity, leakage policy and pre-fit evaluation safeguards."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import yaml
from sklearn.metrics import adjusted_rand_score
from threadpoolctl import threadpool_limits

from mp1.audit import read_raw_csv, sha256_file
from mp1.clustering import fit_partition, ordinal_features
from mp1.predictive_audit import (
    derived_information_policy,
    exact_record_groups,
    feature_eligibility,
    freeze_diagnostic_design,
    grouped_allocation_obstruction,
    metadata_profiles,
    methodological_gate,
    partition_overlap,
    run_predictive_audit,
)
from mp1.response_quality import assess_responses
from mp1.target_audit import align_partition, reconstruct_target


@pytest.fixture
def audit_project(tmp_path: Path) -> dict:
    """Create independent synthetic sources and matching aggregate B evidence."""
    repo, sources = tmp_path / "repo", tmp_path / "sources"
    (repo / "config").mkdir(parents=True)
    sources.mkdir()
    items = [f"synthetic_q{i}" for i in range(4)]
    response_labels = ["one", "two", "three", "four", "five"]
    rng = np.random.default_rng(519)
    x = np.vstack([rng.integers(1, 4, (180, 4)), np.tile([5, 4, 5, 4], (50, 1))])
    x[:3] = 2
    frame = pd.DataFrame(np.array(response_labels)[x - 1], columns=items)
    frame.insert(0, "context", [f"level{i % 7}" for i in range(180)] + ["repeated"] * 50)
    raw_path = sources / "synthetic.csv"
    frame.to_csv(raw_path, index=False)
    raw = read_raw_csv(raw_path, "D5")
    flags, _, _, _ = assess_responses(raw, items, response_labels, [])
    flags_path = sources / "flags.csv"
    flags.to_csv(flags_path, index=False)
    config = {
        "project": {"random_seed": 7, "drive_root_env": "MP1_SYNTHETIC_C_ROOT"},
        "data": {"d5_raw": "synthetic.csv"},
        "clustering": {"k_values": [2, 3, 4, 5, 6], "n_init": 3},
        "modeling": {"test_size": 0.2, "cv_folds": 5, "primary_metric": "macro_f1"},
        "response_quality": {"private_flags": "data/processed/response_quality_flags.csv"},
        "integrity": {
            "csv_encoding": "utf-8-sig",
            "missing_tokens": [],
            "datasets": {
                "D5": {
                    "survey_items": items,
                    "metadata_columns": ["context"],
                    "source_key": "d5_raw",
                    "allowed_responses": response_labels,
                    "source_metadata": {"published_file_sha256": raw.sha256},
                }
            },
        },
    }
    config_path = repo / "config/analysis.yaml"
    config_path.write_text(yaml.safe_dump(config, sort_keys=False))
    code_root = Path(__file__).resolve().parents[1] / "src/mp1"
    shared = {
        "config_sha256": sha256_file(config_path),
        "sources": {"D5": raw.sha256},
        "quality_flags_sha256": sha256_file(flags_path),
        "measurement_code_sha256": {
            name: sha256_file(code_root / name)
            for name in [
                "audit.py",
                "response_quality.py",
                "config.py",
                "paths.py",
                "ordinal.py",
                "psychometrics.py",
                "measurement.py",
            ]
        },
    }
    centroids, sizes, members, fitted_labels = [], [], [], {}
    expected_rows, expected_sizes = {}, {}
    with threadpool_limits(limits=1):
        for sample, keep in [
            ("full", np.ones(len(x), dtype=bool)),
            ("sensitivity", flags.include_sensitivity.to_numpy()),
        ]:
            y, centers = fit_partition(ordinal_features(x[keep]), 2, 9, 3)
            fitted_labels[sample] = y
            expected_rows[sample], expected_sizes[sample] = len(y), np.bincount(y).tolist()
            for cluster in [0, 1]:
                sizes.append(
                    {
                        "dataset": "D5",
                        "sample": sample,
                        "k": 2,
                        "cluster": cluster + 1,
                        "count": int(np.sum(y == cluster)),
                    }
                )
                for i, item in enumerate(items):
                    centroids.append(
                        {
                            "dataset": "D5",
                            "sample": sample,
                            "k": 2,
                            "cluster": cluster + 1,
                            "item": item,
                            **{
                                f"probability_above_{j + 1}": float(2 * centers[cluster, i * 4 + j])
                                for j in range(4)
                            },
                        }
                    )
            members.extend(
                {
                    "dataset": "D5",
                    "source_sha256": raw.sha256,
                    "source_record_number": int(position),
                    "sample": sample,
                    "k": 2,
                    "cluster": int(label + 1),
                }
                for position, label in zip(np.flatnonzero(keep) + 1, y, strict=True)
            )
    measurement_dir, cluster_dir = repo / "outputs/psychometrics", repo / "outputs/clustering"
    measurement_dir.mkdir(parents=True)
    cluster_dir.mkdir(parents=True)
    pd.DataFrame(
        {"dataset": "D5", "position": range(1, 5), "item": items, "raw_column": items}
    ).to_csv(measurement_dir / "item_inventory.csv", index=False)
    pd.DataFrame(centroids).to_csv(cluster_dir / "cluster_centroids.csv", index=False)
    pd.DataFrame(sizes).to_csv(cluster_dir / "cluster_sizes.csv", index=False)
    ari = adjusted_rand_score(
        fitted_labels["full"][flags.include_sensitivity], fitted_labels["sensitivity"]
    )
    pd.DataFrame([{"dataset": "D5", "k": 2, "full_sensitivity_ari": ari}]).to_csv(
        cluster_dir / "quality_sensitivity.csv", index=False
    )
    membership_path = sources / "accepted_memberships.csv"
    pd.DataFrame(members).to_csv(membership_path, index=False)
    measurement = {
        **shared,
        "samples": {"D5": expected_rows},
        "representation": "ordinal_item_thresholds",
    }
    clustering = {
        **shared,
        "choices": {"D5": {"k": 2}},
        "settings": config["clustering"],
        "clustering_code_sha256": sha256_file(code_root / "clustering.py"),
        "private_memberships": "data/interim/work_package_b/cluster_memberships.csv",
    }
    names = {}
    for directory, manifest, name in [
        (measurement_dir, measurement, "measurement_summary.json"),
        (cluster_dir, clustering, "clustering_summary.json"),
    ]:
        manifest["artifact_sha256"] = {p.name: sha256_file(p) for p in directory.glob("*.csv")}
        path = directory / name
        path.write_text(json.dumps(manifest))
        names[str(path.relative_to(repo))] = sha256_file(path)
    audit = {
        "baseline_commit": "synthetic",
        "research_control": {"scope": "synthetic"},
        "accepted_evidence": {
            "analysis_config_sha256": sha256_file(config_path),
            "manifests": names,
            "measurement_manifest": "outputs/psychometrics/measurement_summary.json",
            "clustering_manifest": "outputs/clustering/clustering_summary.json",
            "expected_rows": expected_rows,
            "expected_sizes": expected_sizes,
            "centroid_absolute_tolerance": 1e-12,
            "minimum_assignment_margin": 1e-12,
        },
        "diagnostic_design": {"split_seed": 19, "cv_seed": 20},
        "metadata_review": {
            "context": {
                "research_role": "synthetic_context",
                "interpretation": "Synthetic background category.",
                "limitation": "Unverified record independence.",
            }
        },
        "outputs": {
            "aggregate_directory": "outputs/modeling/work_package_c",
            "private_directory": "data/interim/work_package_c",
        },
    }
    audit_path = repo / "config/work_package_c.yaml"
    audit_path.write_text(yaml.safe_dump(audit))
    return {
        "config_path": config_path,
        "audit_config_path": audit_path,
        "d5_path": raw_path,
        "flags_path": flags_path,
        "memberships_path": membership_path,
    }


def test_reconstruction_matches_b_and_optional_memberships(audit_project: dict) -> None:
    result = reconstruct_target(**audit_project)
    assert result.checks.ari_against_accepted_centroid_assignments.eq(1).all()
    assert result.checks.ari_against_original_memberships.eq(1).all()
    assert result.checks.original_memberships_available.all()
    assert result.sensitivity["permanent_exclusions"] == 0
    assert result.sensitivity["straight_line_records"] > 0
    assert len(result.labels["full"]) == 230
    assert result.checks.source_values_and_order_unchanged.all()
    assert result.checks.all_quality_flag_fields_recomputed_equal.all()


def test_reconstruction_without_original_memberships_is_explicit(audit_project: dict) -> None:
    args = {k: v for k, v in audit_project.items() if k != "memberships_path"}
    result = reconstruct_target(**args)
    assert not result.checks.original_memberships_available.any()
    assert result.checks.ari_against_original_memberships.isna().all()
    assert result.checks.ari_against_accepted_centroid_assignments.eq(1).all()


def test_existing_default_b_memberships_are_automatically_compared(audit_project: dict) -> None:
    repo = audit_project["config_path"].parent.parent
    path = repo / "data/interim/work_package_b/cluster_memberships.csv"
    path.parent.mkdir(parents=True)
    path.write_bytes(audit_project["memberships_path"].read_bytes())
    args = {key: value for key, value in audit_project.items() if key != "memberships_path"}
    result = reconstruct_target(**args)
    assert result.checks.original_memberships_available.all()
    assert result.checks.ari_against_original_memberships.eq(1).all()


def test_private_records_cannot_be_written_to_public_output(audit_project: dict) -> None:
    path = audit_project["audit_config_path"]
    config = yaml.safe_load(path.read_text())
    config["outputs"]["private_directory"] = "outputs/modeling/exposed"
    path.write_text(yaml.safe_dump(config))
    with pytest.raises(ValueError, match="ignored data/interim"):
        run_predictive_audit(**audit_project)
    assert not (path.parent.parent / "outputs/modeling/exposed").exists()


@pytest.mark.parametrize("kind", ["raw", "flags", "config", "manifest", "artifact"])
def test_fingerprint_changes_fail_closed(audit_project: dict, kind: str) -> None:
    repo = audit_project["config_path"].parent.parent
    paths = {
        "raw": audit_project["d5_path"],
        "flags": audit_project["flags_path"],
        "config": audit_project["config_path"],
        "manifest": repo / "outputs/clustering/clustering_summary.json",
        "artifact": repo / "outputs/clustering/cluster_centroids.csv",
    }
    if kind == "raw":
        paths[kind].write_text(paths[kind].read_text().replace("level0", "levelx", 1))
    else:
        with paths[kind].open("a") as handle:
            handle.write(" ")
    with pytest.raises(ValueError, match="fingerprint|configuration"):
        reconstruct_target(**audit_project)


def test_flags_are_recomputed_not_just_trusted(
    audit_project: dict, monkeypatch: pytest.MonkeyPatch
) -> None:
    from mp1 import target_audit

    original = target_audit.assess_responses

    def inconsistent(*args: object, **kwargs: object) -> tuple:
        flags, summary, pattern, invalid = original(*args, **kwargs)
        flags.loc[0, "invariant_response"] = "different"
        return flags, summary, pattern, invalid

    monkeypatch.setattr(target_audit, "assess_responses", inconsistent)
    with pytest.raises(ValueError, match="complete recomputed"):
        reconstruct_target(**audit_project)


@pytest.mark.parametrize("corruption", ["source", "order", "label", "sample", "missing"])
def test_private_membership_corruption_fails(audit_project: dict, corruption: str) -> None:
    path = audit_project["memberships_path"]
    if corruption == "missing":
        path.unlink()
        with pytest.raises(FileNotFoundError, match="memberships are missing"):
            reconstruct_target(**audit_project)
        return
    frame = pd.read_csv(path)
    if corruption == "source":
        frame.loc[0, "source_sha256"] = "wrong"
    elif corruption == "order":
        frame.loc[0, "source_record_number"] = 2
    elif corruption == "sample":
        frame.loc[0, "sample"] = "unknown"
    else:
        frame.loc[0, "cluster"] = 3 - frame.loc[0, "cluster"]
    frame.to_csv(path, index=False)
    with pytest.raises(ValueError, match="membership"):
        reconstruct_target(**audit_project)


def test_private_membership_label_permutation_is_allowed(audit_project: dict) -> None:
    path = audit_project["memberships_path"]
    frame = pd.read_csv(path)
    frame["cluster"] = 3 - frame.cluster
    frame.to_csv(path, index=False)
    result = reconstruct_target(**audit_project)
    assert result.checks.ari_against_original_memberships.eq(1).all()


def test_centroid_comparison_allows_label_permutation_but_rejects_mismatch_and_ties() -> None:
    centers = np.array([[0.0, 0.0], [1.0, 1.0]])
    x = np.repeat(centers, 4, axis=0)
    y = np.repeat([0, 1], 4)
    aligned, report = align_partition(x, 1 - y, centers[::-1], centers, 1e-12, 1e-12)
    assert np.array_equal(aligned, y)
    assert report["ari_against_accepted_centroid_assignments"] == 1
    with pytest.raises(ValueError, match="exactly match"):
        align_partition(x, y, centers + 0.01, centers, 1e-12, 1e-12)
    x[0] = 0.5
    with pytest.raises(ValueError, match="exactly match"):
        align_partition(x, y, centers, centers, 1e-12, 1e-12)


def test_feature_audit_accounts_for_all_columns_and_unknowns_fail() -> None:
    frame = pd.DataFrame({"background": ["a", "b"], "q1": [1, 2], "q2": [3, 4]})
    review = {
        "background": {
            "research_role": "context",
            "interpretation": "Independent content.",
            "limitation": "Synthetic.",
        }
    }
    table = feature_eligibility(frame, ["q1", "q2"], review)
    assert table.column.tolist() == frame.columns.tolist()
    assert table.candidate_predictor.tolist() == ["yes", "no", "no"]
    assert table.target_defining_information.tolist() == ["no", "yes", "yes"]
    with pytest.raises(ValueError, match="Every raw column"):
        feature_eligibility(frame.assign(unreviewed=1), ["q1", "q2"], review)
    with pytest.raises(ValueError, match="distinct"):
        feature_eligibility(frame, ["q1", "background"], review)
    assert derived_information_policy().candidate_predictor.eq("no").all()
    assert "quality_straight_line" in derived_information_policy().information.tolist()


def test_diagnostic_design_is_frozen_stratified_and_fold_safe() -> None:
    labels = np.repeat([0, 1], [160, 40])
    design = freeze_diagnostic_design(labels, 0.2, 5, 3, 4)
    pd.testing.assert_frame_equal(design, freeze_diagnostic_design(labels, 0.2, 5, 3, 4))
    test = design.diagnostic_split.eq("test").to_numpy()
    assert np.bincount(labels[test]).tolist() == [32, 8]
    assert design.loc[test, "training_validation_fold"].eq(-1).all()
    assert set(design.loc[~test, "training_validation_fold"]) == set(range(1, 6))
    assert design.source_record_number.is_unique
    with pytest.raises(ValueError, match="binary"):
        freeze_diagnostic_design(np.ones(30), 0.2, 5, 3, 4)
    with pytest.raises(ValueError, match="cannot support"):
        freeze_diagnostic_design(np.repeat([0, 1], [25, 3]), 0.2, 5, 3, 4)


def test_overlap_counts_and_intact_group_impossibility_have_known_values() -> None:
    frame = pd.DataFrame({"a": ["a", "b", "c", "c", "c", "c"], "b": [0, 0, 1, 1, 1, 1]})
    y = np.array([0, 0, 1, 1, 1, 1])
    groups = exact_record_groups(frame, y)
    test = np.array([False, True, False, False, False, True])
    table = partition_overlap(groups, y, ~test, test)
    assert table.validation_records_with_pattern_in_training.tolist() == [0, 1]
    bound = grouped_allocation_obstruction(groups, y, test)
    assert bound.proven_incompatible_with_intact_groups.tolist() == [False, True]
    assert bound.largest_exact_record_group.tolist() == [1, 4]
    with pytest.raises(ValueError, match="disjoint"):
        partition_overlap(groups, y, test, test)
    with pytest.raises(ValueError, match="different deterministic"):
        exact_record_groups(frame, np.array([0, 0, 0, 1, 1, 1]))


def test_metadata_descriptions_are_exact_marginals_without_recoding() -> None:
    frame = pd.DataFrame({"discipline": ["C", "C", "full C", "C"], "age": ["20", "20", "21", "21"]})
    original = frame.copy(deep=True)
    labels = np.array([0, 1, 0, 1])
    table = metadata_profiles(frame, labels, list(frame))
    assert table.groupby("column").records.sum().eq(len(frame)).all()
    assert table.groupby(["column", "class_id"]).category_fraction_within_class.sum().eq(1).all()
    assert set(table.loc[table.column.eq("discipline"), "value"]) == {"C", "full C"}
    pd.testing.assert_frame_equal(frame, original)
    assert not any("p_value" in column for column in table)


def test_gate_distinguishes_metadata_from_psychological_predictors() -> None:
    eligibility = pd.DataFrame(
        {"column": ["context", "item"], "candidate_predictor": ["yes", "no"]}
    )
    result = methodological_gate(
        eligibility, pd.DataFrame({"proven_incompatible_with_intact_groups": [True]})
    )
    assert result["metadata_descriptive_comparison_defensible"]
    assert result["metadata_question_meaningful_in_principle"]
    assert not result["psychological_correlate_question_supported"]
    assert result["status"] == "blocked"
    assert not result["modeling_performed"]
    result = methodological_gate(
        eligibility, pd.DataFrame({"proven_incompatible_with_intact_groups": [False]})
    )
    assert result["status"] == "requires_methodological_review"
    assert not result["modeling_performed"]


def test_pipeline_is_deterministic_preserves_inputs_and_writes_only_aggregate_public_outputs(
    audit_project: dict,
) -> None:
    original = {path: path.read_bytes() for path in audit_project.values()}
    destination = run_predictive_audit(**audit_project)
    manifest = json.loads((destination / "predictive_audit_summary.json").read_text())
    assert manifest["gate"]["status"] == "blocked"
    assert manifest["performance_metrics"]["best_model"] is None
    assert manifest["explanations"]["status"] == "not_applicable_gate_blocked"
    assert manifest["policies"]["raw_rows_modified"] == 0
    snapshot = {p.name: p.read_bytes() for p in destination.iterdir()}
    run_predictive_audit(**audit_project)
    assert snapshot == {p.name: p.read_bytes() for p in destination.iterdir()}
    assert all(path.read_bytes() == content for path, content in original.items())
    assert all(
        sha256_file(destination / name) == digest
        for name, digest in manifest["artifact_sha256"].items()
    )
    for p in destination.glob("*.csv"):
        columns = pd.read_csv(p).columns
        assert "source_record_number" not in columns
        assert "prediction" not in columns
    profiles = pd.read_csv(destination / "metadata_profile_descriptions.csv")
    for variant, group in profiles.groupby("variant"):
        assert group.records.sum() == (
            230 if variant == "full" else manifest["sensitivity"]["retained_records"]
        )
    private = audit_project["config_path"].parent.parent / "data/interim/work_package_c"
    assert (private / "target_memberships.csv").is_file()
    assert (private / "diagnostic_design.csv").is_file()


def test_cli_produces_blocker_evidence_successfully(audit_project: dict) -> None:
    repo = Path(__file__).resolve().parents[1]
    result = subprocess.run(
        [
            sys.executable,
            str(repo / "scripts/predictive_audit.py"),
            "--config",
            str(audit_project["config_path"]),
            "--audit-config",
            str(audit_project["audit_config_path"]),
            "--d5-raw",
            str(audit_project["d5_path"]),
            "--quality-flags",
            str(audit_project["flags_path"]),
        ],
        env={**os.environ, "PYTHONPATH": str(repo / "src")},
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert len(result.stdout.splitlines()) == 1
    assert "repeated" not in result.stdout


def test_private_output_directory_remains_ignored() -> None:
    repo = Path(__file__).resolve().parents[1]
    result = subprocess.run(
        [
            "git",
            "check-ignore",
            "data/interim/work_package_c/target_memberships.csv",
            "data/interim/work_package_c/diagnostic_design.csv",
        ],
        cwd=repo,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0
    assert len(result.stdout.splitlines()) == 2
