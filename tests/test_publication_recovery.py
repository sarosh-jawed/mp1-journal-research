"""Fail-closed checks for the documented candidate-only replay boundary."""

from __future__ import annotations

import pandas as pd
import pytest

from mp1.recovery import BASELINE, STAGE_FOLDERS, check_cell, check_report_boundary


def evidence():
    frame = pd.DataFrame([{"dataset": "D3", "sample": "full", "k": 6, "cluster": 1, "count": 247}])
    cell = {
        "csv_data_row": 1,
        "dataset": "D3",
        "sample": "full",
        "k": "6",
        "cluster": "1",
        "field": "count",
        "accepted_value": "247",
        "replayed_value": "246",
        "difference": -1.0,
        "selected_k2": False,
    }
    return frame, cell


def test_nonselected_discrete_difference_is_disclosed_without_replacement():
    frame, cell = evidence()
    check_cell(frame, cell)
    assert frame.loc[0, "count"] == 247


def test_selected_difference_cannot_receive_candidate_exception():
    frame, cell = evidence()
    frame.loc[0, "k"] = 2
    cell.update(k="2", selected_k2=True)
    with pytest.raises(ValueError, match="selected or unbounded"):
        check_cell(frame, cell)


def test_mismatch_cannot_be_attached_to_another_accepted_row():
    frame, cell = evidence()
    cell["cluster"] = "6"
    with pytest.raises(ValueError, match="row identity"):
        check_cell(frame, cell)


def test_altered_accepted_value_cannot_be_hidden_in_register():
    frame, cell = evidence()
    cell["accepted_value"] = "246"
    with pytest.raises(ValueError, match="accepted value"):
        check_cell(frame, cell)


def test_signed_difference_must_match_preserved_values():
    frame, cell = evidence()
    cell["difference"] = 1.0
    with pytest.raises(ValueError, match="signed difference"):
        check_cell(frame, cell)


def test_changed_retained_decision_blocks_qualified_recovery():
    hashes = {"raw.csv": "example"}
    stages = [
        {
            "stage": n,
            "exit_code": 0,
            "status": "FAIL" if n == "B_clustering" else "PASS",
            "decision_keys_equal": {"decision": n != "C_feasibility"},
        }
        for n in ["A_response_quality", *STAGE_FOLDERS]
    ]
    report = {
        "baseline_commit": BASELINE,
        "input_sha256": hashes,
        "input_sha256_after": hashes,
        "raw_source_immutable": True,
        "caller_accepted_files_unchanged": True,
        "stages": stages,
    }
    with pytest.raises(ValueError, match="retained scientific decision"):
        check_report_boundary(report, {"private_input_sha256": hashes})
