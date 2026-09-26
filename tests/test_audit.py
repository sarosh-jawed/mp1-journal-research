from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pytest
import yaml

from mp1.audit import (
    TABLE_COLUMNS,
    RawDataset,
    audit_dataset,
    duplicate_counts,
    guard_output,
    institution_review,
    load_inputs,
    missing_mask,
    read_raw_csv,
    run_provenance,
    sha256_file,
    verify_unchanged,
)
from mp1.paths import get_drive_root


def test_reader_preserves_values_and_multiline_records(tmp_path: Path) -> None:
    path = tmp_path / "source.csv"
    path.write_bytes(b'\xef\xbb\xbfid,item,note\r\n001,NA,"a\nb"\r\n002,," quoted "\r\n')
    before = path.read_bytes()
    data = read_raw_csv(path, "synthetic")
    assert data.frame.to_dict(orient="records") == [
        {"id": "001", "item": "NA", "note": "a\nb"},
        {"id": "002", "item": "", "note": " quoted "},
    ]
    assert path.read_bytes() == before
    assert data.sha256 == sha256_file(path)
    assert all(str(dtype) == "string" for dtype in data.frame.dtypes)


@pytest.mark.parametrize(
    "content,message",
    [
        ("", "nonblank header"),
        ("a,a\n1,2\n", "Duplicate column names"),
        ("a, \n1,2\n", "nonblank header"),
        ("a,b\n1\n", "data record 1 has 1 fields"),
        ("a,b\n1,2,3\n", "data record 1 has 3 fields"),
        ("a,b\n1,2\n\n", "data record 2 has 0 fields"),
        ('a,b\n1,"unfinished\n', "Malformed CSV"),
        ("a,b\n1,\x00\n", "NUL character"),
    ],
)
def test_reader_rejects_ambiguous_csv(tmp_path: Path, content: str, message: str) -> None:
    path = tmp_path / "source.csv"
    path.write_text(content, encoding="utf-8")
    with pytest.raises(ValueError, match=message):
        read_raw_csv(path, "synthetic")


def test_missing_file_fails(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match="Required source file"):
        read_raw_csv(tmp_path / "absent.csv", "synthetic")


def test_duplicate_counts_distinguish_groups_members_and_excess() -> None:
    frame = pd.DataFrame({"a": [1, 1, 1, 2, 2, 3], "b": ["x", "x", "x", "y", "y", "z"]})
    before = frame.copy(deep=True)
    assert duplicate_counts(frame) == {
        "duplicate_groups": 2,
        "duplicate_member_rows": 5,
        "duplicate_excess_rows": 3,
        "unique_records": 3,
        "largest_group_size": 3,
    }
    pd.testing.assert_frame_equal(frame, before)


def test_missingness_policy_preserves_literal_na_and_disjoint_counts() -> None:
    frame = pd.DataFrame({"item": [None, "", " \t", "NA", "missing", "0", "Yes"]}, dtype="string")
    assert missing_mask(frame, ["missing"])["item"].tolist() == [
        True,
        True,
        True,
        False,
        True,
        False,
        False,
    ]
    assert frame.loc[3, "item"] == "NA"


def test_institution_keys_are_not_aliases() -> None:
    values = pd.Series([" Alpha U ", "alpha u", "Alpha U", "Beta U"], dtype="string")
    report = institution_review(values)
    assert len(report) == 4
    assert report["comparison_key"].nunique() == 2
    assert report.loc[report["comparison_key"].eq("alpha u"), "labels_sharing_key"].eq(3).all()
    assert report["approved_institution"].eq("").all()
    assert values.iloc[0] == " Alpha U "


def test_composite_identifiers_exclude_incomplete_keys() -> None:
    frame = pd.DataFrame(
        {
            "site": ["A", "A", "B", "", ""],
            "id": ["01", "01", "01", "01", "01"],
            "q1": ["No", "Yes", "No", "No", "No"],
            "q2": ["Yes"] * 5,
        },
        dtype="string",
    )
    data = RawDataset("synthetic", Path("unused.csv"), "a" * 64, 0, frame)
    spec = {
        "identifier_columns": ["site", "id"],
        "metadata_columns": ["site", "id"],
        "survey_items": ["q1", "q2"],
        "categorical_columns": [],
        "reference_claims": [],
    }
    result = audit_dataset(data, spec, [])
    identifiers = result["duplicate_summary.csv"][1]
    assert identifiers["eligible_rows"] == 3
    assert identifiers["incomplete_identifier_rows"] == 2
    assert identifiers["duplicate_excess_rows"] == 1
    assert identifiers["duplicate_member_rows"] == 2
    assert identifiers["duplicate_groups"] == 1


def test_provenance_outputs_and_immutability(synthetic_project: Path) -> None:
    config, raw, dictionary = load_inputs(synthetic_project)
    sources = [*(data.path for data in raw.values()), Path(dictionary["path"])]
    original = {path: path.read_bytes() for path in sources}
    destination = run_provenance(synthetic_project)
    for name, columns in TABLE_COLUMNS.items():
        assert pd.read_csv(destination / name).columns.tolist() == columns
    summaries = pd.read_csv(destination / "dataset_summary.csv").set_index("dataset")
    assert summaries.loc["D5", "raw_rows"] == 6
    assert summaries.loc["D5", "missing_cells"] == 2
    assert summaries["raw_rows"].equals(summaries["full_sample_rows_before_sensitivity"])
    assert summaries["rows_removed"].eq(0).all()
    missing = pd.read_csv(destination / "missingness_summary.csv")
    item = missing.loc[(missing.dataset == "D5") & (missing.column == "question_2")].iloc[0]
    assert item.missing_count == 1
    assert item.empty_count == 1
    assert item.missing_proportion == pytest.approx(1 / 6)
    summary = json.loads((destination / "provenance_summary.json").read_text())
    assert summary["dictionary"]["dataset_headings_found"] == {"D5": False, "D3": False}
    assert summary["policies"]["row_exclusions"] == "none"
    for name, checksum in summary["artifact_sha256"].items():
        assert sha256_file(destination / name) == checksum
    for path, content in original.items():
        assert path.read_bytes() == content
    snapshot = {path.name: path.read_bytes() for path in destination.iterdir() if path.is_file()}
    run_provenance(synthetic_project)
    assert snapshot == {
        path.name: path.read_bytes() for path in destination.iterdir() if path.is_file()
    }
    assert config["integrity"]["missing_tokens"] == []


def test_absent_identifier_is_not_reported_as_zero_duplicates(synthetic_project: Path) -> None:
    config = yaml.safe_load(synthetic_project.read_text())
    config["integrity"]["datasets"]["D5"]["identifier_columns"] = []
    synthetic_project.write_text(yaml.safe_dump(config))
    destination = run_provenance(synthetic_project)
    report = pd.read_csv(destination / "duplicate_summary.csv")
    row = report.loc[(report.dataset == "D5") & (report.basis == "respondent_identifier")].iloc[0]
    assert row.status == "not_available"
    assert pd.isna(row.duplicate_excess_rows)


def test_required_columns_fail_without_repair(synthetic_project: Path) -> None:
    config = yaml.safe_load(synthetic_project.read_text())
    config["integrity"]["datasets"]["D5"]["survey_items"].append("absent_question")
    synthetic_project.write_text(yaml.safe_dump(config))
    with pytest.raises(ValueError, match="required columns are missing.*absent_question"):
        run_provenance(synthetic_project)


def test_source_overlap_and_source_changes_are_detected(tmp_path: Path) -> None:
    source = tmp_path / "source" / "data.csv"
    source.parent.mkdir()
    source.write_text("a,b\n1,2\n")
    fingerprints = {source: sha256_file(source)}
    with pytest.raises(ValueError, match="overlaps a source directory"):
        guard_output(source.parent / "derived.csv", fingerprints)
    alias = tmp_path / "alias"
    alias.symlink_to(source.parent, target_is_directory=True)
    with pytest.raises(ValueError, match="overlaps a source directory"):
        guard_output(alias / "derived.csv", fingerprints)
    source.write_text("a,b\n1,3\n")
    with pytest.raises(RuntimeError, match="Source changed"):
        verify_unchanged(fingerprints)


def test_path_helper_respects_configured_environment(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("MP1_CUSTOM_LOCATION", str(tmp_path))
    assert get_drive_root("MP1_CUSTOM_LOCATION") == tmp_path
    monkeypatch.delenv("MP1_CUSTOM_LOCATION")
    with pytest.raises(RuntimeError, match="MP1_CUSTOM_LOCATION is not set"):
        get_drive_root("MP1_CUSTOM_LOCATION")
    file = tmp_path / "file"
    file.touch()
    monkeypatch.setenv("MP1_CUSTOM_LOCATION", str(file))
    with pytest.raises(NotADirectoryError):
        get_drive_root("MP1_CUSTOM_LOCATION")
