from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import yaml

from mp1.audit import sha256_file
from mp1.clustering import load_measurement_evidence, run_clustering
from mp1.measurement import load_measurement_inputs, run_measurement
from mp1.response_quality import run_response_quality


@pytest.fixture
def measurement_project(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    repository = Path(__file__).resolve().parents[1]
    config = yaml.safe_load((repository / "config/analysis.yaml").read_text())
    root, sources = tmp_path / "repo", tmp_path / "sources"
    (root / "config").mkdir(parents=True)
    sources.mkdir()
    rng = np.random.default_rng(551)
    labels = config["integrity"]["datasets"]["D5"]["allowed_responses"]
    for dataset, p in [("D5", 8), ("D3", 5)]:
        items = [f"q{i}" for i in range(p)]
        x = rng.integers(1, 6, (250, p))
        x[:3] = 5
        frame = pd.DataFrame(np.array(labels)[x - 1], columns=items)
        frame["metadata"] = [f"non_survey_{i}" for i in range(len(frame))]
        frame.to_csv(sources / f"{dataset}.csv", index=False)
        config["data"][f"{dataset.lower()}_raw"] = f"{dataset}.csv"
        config["integrity"]["datasets"][dataset] = {
            "source_key": f"{dataset.lower()}_raw",
            "survey_items": items,
            "metadata_columns": ["metadata"],
            "identifier_columns": [],
            "categorical_columns": [],
            "allowed_responses": labels,
            "source_metadata": {"published_file_sha256": sha256_file(sources / f"{dataset}.csv")},
        }
    (sources / "dictionary.md").write_text("# Synthetic ordinal items\n")
    config["data"]["data_dictionary"] = "dictionary.md"
    config["project"]["drive_root_env"] = "MP1_MEASUREMENT_TEST_ROOT"
    config["measurement"]["parallel_repetitions"] = 20
    config["clustering"].update(
        {"n_init": 3, "resampling_repetitions": 20, "resampling_fraction": 0.5}
    )
    config["measurement"]["d5_sections"] = {
        "A": {"label": "Synthetic A", "item_positions": [1, 2, 3, 4]},
        "B": {"label": "Synthetic B", "item_positions": [5, 6, 7, 8]},
    }
    path = root / "config/analysis.yaml"
    path.write_text(yaml.safe_dump(config))
    monkeypatch.setenv("MP1_MEASUREMENT_TEST_ROOT", str(sources))
    run_response_quality(path)
    return path


def test_measurement_reuses_flags_excludes_metadata_and_preserves_sources(
    measurement_project: Path,
) -> None:
    config, raw, samples, inventory, _ = load_measurement_inputs(measurement_project)
    original = {name: source.path.read_bytes() for name, source in raw.items()}
    assert samples["D5"]["full"].shape == (250, 8)
    assert len(samples["D5"]["sensitivity"]) == 247
    assert not inventory.raw_column.str.contains("metadata").any()
    destination = run_measurement(measurement_project)
    summary = load_measurement_evidence(measurement_project, config, raw)
    assert summary["samples"]["D5"] == {"full": 250, "sensitivity": 247}
    assert summary["representation"] == "ordinal_item_thresholds"
    assert pd.read_csv(destination / "reliability.csv").shape[0] == 4
    assert pd.read_csv(destination / "item_diagnostics.csv").shape[0] == 16
    assert pd.read_csv(destination / "item_distributions.csv").columns.tolist() == [
        "dataset",
        "sample",
        "n",
        "item",
        "count_1",
        "count_2",
        "count_3",
        "count_4",
        "count_5",
    ]
    assert all(source.path.read_bytes() == original[name] for name, source in raw.items())
    assert not any(
        "record_number" in column for column in pd.read_csv(destination / "item_diagnostics.csv")
    )
    evidence = json.loads((destination / "measurement_summary.json").read_text())
    assert all(
        sha256_file(destination / name) == value
        for name, value in evidence["artifact_sha256"].items()
    )
    clusters = run_clustering(measurement_project)
    metrics = pd.read_csv(clusters / "cluster_metrics.csv")
    assert len(metrics) == 20
    assert np.isfinite(metrics.select_dtypes(include="number").to_numpy()).all()
    sizes = pd.read_csv(clusters / "cluster_sizes.csv")
    totals = sizes.groupby(["dataset", "sample", "k"])["count"].sum()
    for (dataset, sample, _), count in totals.items():
        assert count == summary["samples"][dataset][sample]
    memberships = measurement_project.parent.parent / "data/interim/work_package_b"
    private = pd.read_csv(memberships / "cluster_memberships.csv")
    assert private.columns.tolist() == [
        "dataset",
        "source_sha256",
        "source_record_number",
        "sample",
        "k",
        "cluster",
    ]
    assert not private.duplicated(["dataset", "sample", "source_record_number"]).any()
    assert all(source.path.read_bytes() == original[name] for name, source in raw.items())
    (destination / "reliability.csv").write_text("changed")
    with pytest.raises(ValueError, match="artifact changed"):
        load_measurement_evidence(measurement_project, config, raw)


def test_measurement_rejects_missing_quality_flags(measurement_project: Path) -> None:
    flags = measurement_project.parent.parent / "data/processed/response_quality_flags.csv"
    flags.unlink()
    with pytest.raises(FileNotFoundError, match="quality flags"):
        load_measurement_inputs(measurement_project)


def test_measurement_rejects_new_source_version(measurement_project: Path) -> None:
    _, raw, _, _, _ = load_measurement_inputs(measurement_project)
    with raw["D5"].path.open("a") as handle:
        handle.write("\n")
    with pytest.raises(ValueError):
        load_measurement_inputs(measurement_project)
