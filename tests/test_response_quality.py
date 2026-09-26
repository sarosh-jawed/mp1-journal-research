from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pytest
import yaml

from mp1.audit import RawDataset, load_inputs, sha256_file
from mp1.response_quality import (
    FLAG_COLUMNS,
    INVALID_COLUMNS,
    ITEM_COLUMNS,
    PATTERN_COLUMNS,
    SUMMARY_COLUMNS,
    assess_responses,
    read_quality_flags,
    run_response_quality,
)


def test_items_only_complete_valid_invariance(synthetic_project: Path) -> None:
    config, raw, _ = load_inputs(synthetic_project)
    spec = config["integrity"]["datasets"]["D5"]
    before = raw["D5"].frame.copy(deep=True)
    flags, summary, patterns, invalid = assess_responses(
        raw["D5"], spec["survey_items"], spec["allowed_responses"], []
    )
    assert flags["quality_straight_line"].tolist() == [True, False, False, False, True, False]
    assert flags["quality_assessable"].tolist() == [True, True, True, False, True, False]
    assert flags["include_sensitivity"].tolist() == [False, True, True, True, False, True]
    assert flags["include_full_sample"].all()
    assert flags.loc[0, "invariant_response"] == "No"
    assert flags.loc[4, "invariant_response"] == "Maybe"
    assert summary["straight_line_proportion_full_sample"] == pytest.approx(2 / 6)
    assert summary["straight_line_proportion_assessable"] == pytest.approx(2 / 4)
    assert summary["metadata_inclusive_invariant_rows"] == 0
    assert summary["flag_membership_changes_when_metadata_included"] == 2
    assert summary["unassessable_rows_retained_in_sensitivity"] == 2
    assert patterns.flagged_rows.sum() == 2
    assert invalid["count"].sum() == 3
    assert list(flags.columns) == FLAG_COLUMNS
    pd.testing.assert_frame_equal(raw["D5"].frame, before)


def test_missing_unknown_and_case_variants_are_not_silently_normalized() -> None:
    frame = pd.DataFrame(
        {
            "q1": ["Yes", "Yes", "yes", "", None, "?"],
            "q2": ["No", "Yes ", "yes", "", "Yes", "?"],
        },
        dtype="string",
    )
    data = RawDataset("synthetic", Path("unused.csv"), "a" * 64, 0, frame)
    flags, summary, _, invalid = assess_responses(data, ["q1", "q2"], ["No", "Yes"], [])
    assert not flags.quality_straight_line.any()
    assert flags.include_sensitivity.all()
    assert summary["assessable_rows"] == 1
    assert summary["rows_with_missing_items"] == 2
    assert summary["rows_with_invalid_items"] == 3
    assert set(invalid.unexpected_response) == {"Yes ", "yes", "?"}


def test_empty_dataset_has_explicit_undefined_proportions() -> None:
    frame = pd.DataFrame(columns=["meta", "q1", "q2"], dtype="string")
    data = RawDataset("synthetic", Path("unused.csv"), "a" * 64, 0, frame)
    flags, summary, patterns, invalid = assess_responses(data, ["q1", "q2"], ["No", "Yes"], [])
    assert flags.empty and list(flags.columns) == FLAG_COLUMNS
    assert summary["straight_line_proportion_full_sample"] is None
    assert summary["straight_line_proportion_assessable"] is None
    assert patterns.empty and list(patterns.columns) == PATTERN_COLUMNS
    assert invalid.empty and list(invalid.columns) == INVALID_COLUMNS
    json.dumps(summary, allow_nan=False)


@pytest.mark.parametrize("items", [["q1"], ["q1", "q1"], ["q1", "absent"]])
def test_invalid_item_lists_fail(items: list[str]) -> None:
    data = RawDataset(
        "synthetic", Path("unused.csv"), "a" * 64, 0, pd.DataFrame({"q1": ["Yes"], "q2": ["Yes"]})
    )
    with pytest.raises(ValueError):
        assess_responses(data, items, ["Yes"], [])


def test_response_outputs_private_flags_and_immutability(synthetic_project: Path) -> None:
    _, raw, dictionary = load_inputs(synthetic_project)
    original = {
        path: path.read_bytes()
        for path in [*(data.path for data in raw.values()), Path(dictionary["path"])]
    }
    destination = run_response_quality(synthetic_project)
    expected = {
        "response_quality_summary.csv": SUMMARY_COLUMNS,
        "flagged_response_patterns.csv": PATTERN_COLUMNS,
        "invalid_response_values.csv": INVALID_COLUMNS,
        "eligible_survey_items.csv": ITEM_COLUMNS,
    }
    for name, columns in expected.items():
        assert pd.read_csv(destination / name).columns.tolist() == columns
    assert not (destination / "response_quality_flags.csv").exists()
    private_path = synthetic_project.parent.parent / "data/processed/response_quality_flags.csv"
    flags = read_quality_flags(private_path, "D5", raw["D5"].sha256, 6)
    assert flags.quality_straight_line.sum() == 2
    assert flags.source_record_number.tolist() == [1, 2, 3, 4, 5, 6]
    summary = json.loads((destination / "response_quality_summary.json").read_text())
    assert summary["prior_claim_comparisons"][0]["matches"] is False
    assert summary["prior_claim_comparisons"][0]["observed"] == 2
    assert summary["private_flags"]["sha256"] == sha256_file(private_path)
    for name, checksum in summary["artifact_sha256"].items():
        assert sha256_file(destination / name) == checksum
    for path, content in original.items():
        assert path.read_bytes() == content
    snapshot = {path.name: path.read_bytes() for path in destination.iterdir() if path.is_file()}
    previous_flags = private_path.read_bytes()
    run_response_quality(synthetic_project)
    assert snapshot == {
        path.name: path.read_bytes() for path in destination.iterdir() if path.is_file()
    }
    assert private_path.read_bytes() == previous_flags


@pytest.mark.parametrize(
    "corruption",
    [
        "checksum",
        "order",
        "duplicate_record",
        "boolean",
        "sensitivity",
        "assessment",
        "label",
        "full_sample",
    ],
)
def test_flag_reader_rejects_incompatible_or_corrupt_flags(
    synthetic_project: Path, corruption: str
) -> None:
    _, raw, _ = load_inputs(synthetic_project)
    run_response_quality(synthetic_project)
    path = synthetic_project.parent.parent / "data/processed/response_quality_flags.csv"
    flags = pd.read_csv(path, dtype="string", keep_default_na=False)
    if corruption == "checksum":
        flags.loc[0, "source_sha256"] = "0" * 64
    elif corruption == "order":
        flags.iloc[[0, 1]] = flags.iloc[[1, 0]].to_numpy()
    elif corruption == "duplicate_record":
        flags.loc[1, "source_record_number"] = "1"
    elif corruption == "boolean":
        flags.loc[0, "quality_straight_line"] = "false"
    elif corruption == "sensitivity":
        flags.loc[0, "include_sensitivity"] = "True"
    elif corruption == "assessment":
        flags.loc[0, "quality_assessable"] = "False"
    elif corruption == "full_sample":
        flags.loc[0, "include_full_sample"] = "False"
    else:
        flags.loc[0, "invariant_response"] = ""
    flags.to_csv(path, index=False)
    with pytest.raises(ValueError):
        read_quality_flags(path, "D5", raw["D5"].sha256, 6)


def test_output_cannot_overwrite_a_raw_source(synthetic_project: Path) -> None:
    _, raw, _ = load_inputs(synthetic_project)
    original = raw["D5"].path.read_bytes()
    config = yaml.safe_load(synthetic_project.read_text())
    config["response_quality"]["private_flags"] = str(raw["D5"].path)
    synthetic_project.write_text(yaml.safe_dump(config))
    with pytest.raises(ValueError, match="overlaps a source directory"):
        run_response_quality(synthetic_project)
    assert raw["D5"].path.read_bytes() == original
