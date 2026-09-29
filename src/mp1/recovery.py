"""Bound surviving replay evidence without fitting or replacing accepted A-D results."""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd

from mp1.clustering import select_k
from mp1.publication import BASELINE, dump, freeze, read_json, sha

STAGE_FOLDERS = {
    "B_measurement": "outputs/psychometrics",
    "B_clustering": "outputs/clustering",
    "C_feasibility": "outputs/modeling/work_package_c",
    "D_CGPA": "outputs/outcome_validation/work_package_d",
    "D_external": "outputs/external_validation/work_package_d",
}
KEYS = ["dataset", "sample", "variant", "country", "k", "cluster", "item"]


def check_cell(frame: pd.DataFrame, cell: dict) -> None:
    """Require an exact row identity and a finite numeric nonselected-candidate discrepancy."""
    position = int(cell["csv_data_row"]) - 1
    if position < 0 or position >= len(frame):
        raise ValueError("Replay row is outside accepted evidence.")
    row = frame.iloc[position]
    for key in KEYS:
        if key in frame and str(row[key]) != str(cell.get(key)):
            raise ValueError(f"Replay row identity disagrees: {key}")
    if "k" not in frame or int(row["k"]) not in {3, 4, 5, 6} or cell["selected_k2"]:
        raise ValueError("Mismatch affects selected or unbounded evidence.")
    field = cell["field"]
    if field not in frame or field in KEYS or field in {"selected", "passes_screen", "n"}:
        raise ValueError("Mismatch changes an identifier, decision or sample denominator.")
    if isinstance(row[field], (bool, np.bool_)):
        raise ValueError("Categorical evidence cannot use numeric discrepancy tolerance.")
    accepted, replayed, delta = map(
        float, [cell["accepted_value"], cell["replayed_value"], cell["difference"]]
    )
    if not np.isfinite([accepted, replayed, delta]).all():
        raise ValueError("Replay discrepancy is not finite.")
    if not np.isclose(float(row[field]), accepted, atol=1e-14, rtol=0):
        raise ValueError("Replay accepted value disagrees with frozen evidence.")
    if not np.isclose(replayed - accepted, delta, atol=1e-14, rtol=0):
        raise ValueError("Replay signed difference is inconsistent.")
    if field == "count" and (not accepted.is_integer() or not replayed.is_integer()):
        raise ValueError("A count discrepancy must use integer counts.")


def check_report_boundary(report: dict, locked: dict) -> None:
    """Validate the surviving report's scope; no historical FAIL is rewritten to PASS."""
    if report["baseline_commit"] != BASELINE:
        raise ValueError("Recovered replay baseline changed.")
    if report["input_sha256"] != locked["private_input_sha256"]:
        raise ValueError("Recovered input fingerprints disagree.")
    if report["input_sha256_after"] != report["input_sha256"]:
        raise ValueError("Recovered source immutability failed.")
    if not report["raw_source_immutable"] or not report["caller_accepted_files_unchanged"]:
        raise ValueError("Recovered preservation gate failed.")
    expected = ["A_response_quality", *STAGE_FOLDERS]
    if [s["stage"] for s in report["stages"]] != expected:
        raise ValueError("Recovered stage coverage is incomplete or reordered.")
    for stage in report["stages"]:
        if stage["exit_code"] != 0:
            raise ValueError("A source analysis did not complete in the recovered run.")
        expected_status = "FAIL" if stage["stage"] == "B_clustering" else "PASS"
        if stage["status"] != expected_status:
            raise ValueError("Recovered result status exceeds the bounded exception.")
        if not all(stage.get("decision_keys_equal", {}).values()):
            raise ValueError("A retained scientific decision changed in replay.")
    if not report["stages"][0]["quality_flags_sha256_equal"] or report["status"] != "FAIL":
        raise ValueError("Recovered flags or historical complete-grid status changed.")


def verify_recovered_replay(root: Path) -> dict:
    """Cross-check every preserved mismatch and recompute only aggregate selection arithmetic."""
    locked = freeze(root)
    provenance = read_json(root / "config/publication_recovery.json")
    for name, expected in provenance["recovered_evidence_sha256"].items():
        if sha(root / name) != expected:
            raise ValueError(f"Recovered evidence changed: {name}")
    report = read_json(root / "outputs/publication/validation/source_replay.json")
    check_report_boundary(report, locked)
    expected_cells, csv_checks, selected_rows = [], 0, 0
    replay_metrics = pd.read_csv(root / "outputs/clustering/cluster_metrics.csv")
    for stage in report["stages"][1:]:
        folder = STAGE_FOLDERS[stage["stage"]]
        expected_files = {
            Path(n).name
            for n in locked["accepted_outputs"]
            if str(Path(n).parent) == folder and n.endswith(".csv")
        }
        comparisons = stage["csv_comparisons"]
        if {c["file"] for c in comparisons} != expected_files or len(comparisons) != len(
            expected_files
        ):
            raise ValueError("Recovered CSV comparison coverage is incomplete.")
        for comparison in comparisons:
            csv_checks += 1
            name = folder + "/" + comparison["file"]
            frame = pd.read_csv(root / name)
            if len(frame) != comparison["rows"]:
                raise ValueError("Recovered comparison row count changed.")
            cells = comparison["mismatch_cells"]
            if bool(cells) != (comparison["status"] == "FAIL"):
                raise ValueError("Recovered comparison hides or invents a failure.")
            if not cells and comparison["differences"]:
                raise ValueError("Recovered column differences lack cell evidence.")
            if "k" in frame and stage["stage"] == "B_clustering":
                selected_rows += int(frame.k.eq(2).sum())
            observed_columns = Counter(c["field"] for c in cells)
            if set(observed_columns) != {d["column"] for d in comparison["differences"]}:
                raise ValueError("Cell and column discrepancy coverage disagree.")
            for cell in cells:
                if stage["stage"] != "B_clustering":
                    raise ValueError("Unbounded discrepancy outside B candidates.")
                check_cell(frame, cell)
                expected_cells.append({"accepted_file": name, **cell})
                if comparison["file"] == "cluster_metrics.csv":
                    replay_metrics.loc[int(cell["csv_data_row"]) - 1, cell["field"]] = float(
                        cell["replayed_value"]
                    )
            for column in comparison["differences"]:
                maximum = max(abs(c["difference"]) for c in cells if c["field"] == column["column"])
                if not np.isclose(
                    maximum, column["maximum_absolute_difference"], atol=1e-14, rtol=0
                ):
                    raise ValueError("Reported discrepancy bound is inconsistent.")
    register = list(
        csv.DictReader((root / "outputs/publication/validation/replay_discrepancies.csv").open())
    )
    if len(register) != len(expected_cells):
        raise ValueError("Discrepancy register omits or adds cells.")
    for written, expected in zip(register, expected_cells, strict=True):
        for field in written:
            value = expected.get(field, "")
            if field in {"accepted_value", "replayed_value", "difference"}:
                if not np.isclose(float(written[field]), float(value), atol=1e-14, rtol=0):
                    raise ValueError("Register numeric evidence differs from the replay report.")
            elif written[field] != str(value):
                raise ValueError("Register row identity differs from the replay report.")
    if len(register) != 247 or any(c["selected_k2"] for c in expected_cells):
        raise ValueError("Recovered discrepancy fingerprint is outside the documented boundary.")
    summary = read_json(root / "outputs/clustering/clustering_summary.json")
    selection_checks = []
    accepted_metrics = pd.read_csv(root / "outputs/clustering/cluster_metrics.csv")
    for dataset in ["D5", "D3"]:
        for sample in ["both", "full", "sensitivity"]:
            frames = []
            for data in [accepted_metrics, replay_metrics]:
                part = data[data.dataset.eq(dataset)]
                frames.append(part if sample == "both" else part[part["sample"].eq(sample)])
            a, b = [select_k(frame, summary["settings"]) for frame in frames]
            discrete = [
                c
                for c in a[2]
                if c.startswith("rank_") or c in {"mean_metric_rank", "passes_screen", "selected"}
            ]
            if a[:2] != b[:2] or not a[2][discrete].equals(b[2][discrete]) or a[0] != 2:
                raise ValueError("Recorded discrepancies change aggregate candidate selection.")
            selection_checks.append(
                {
                    "dataset": dataset,
                    "sample": sample,
                    "accepted_k": a[0],
                    "recorded_replay_k": b[0],
                    "ranks_and_screens_equal": True,
                }
            )
    by_file = dict(Counter(c["accepted_file"] for c in expected_cells))
    maxima = {}
    for cell in expected_cells:
        key = cell["accepted_file"] + "::" + cell["field"]
        maxima[key] = max(maxima.get(key, 0), abs(cell["difference"]))
    return {
        "status": "PASS_WITH_DOCUMENTED_LIMITATION",
        "baseline_commit": BASELINE,
        "evidence_origin": "Recovered E archive; source analyses were not rerun in this recovery",
        "historical_complete_grid_source_replay_status": report["status"],
        "source_analyses_rerun": 0,
        "accepted_output_bytes_verified": len(locked["accepted_outputs"]),
        "frozen_files_verified": len(locked["frozen_files"]),
        "recovered_csv_comparisons_checked": csv_checks,
        "selected_k2_rows_in_compared_B_tables": selected_rows,
        "selected_k2_mismatch_cells": 0,
        "mismatch_cells": len(expected_cells),
        "by_file": by_file,
        "by_k": dict(Counter(c["k"] for c in expected_cells)),
        "maximum_absolute_difference_by_field": maxima,
        "aggregate_selection_recheck": selection_checks,
        "limitations": [
            "Complete nonselected candidate-grid source reproduction remains failed.",
            "Original numerical-runtime cause remains unproven.",
            "Raw replay aggregates and private execution logs were not in the recovered ZIP.",
            "Evidence supports the recorded replay comparison, not universal identity "
            "across platforms.",
            "Within-tolerance numerical differences are not enumerated cell by cell "
            "in the recovered report.",
        ],
        "publication_assessment": "Retained-result lock can close with this disclosed limitation "
        "after manual acceptance; no A-D reopening is justified by these differences.",
        "canonical_control_changed": False,
    }


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("outputs/publication/validation/recovery_discrepancy_check.json"),
    )
    args = parser.parse_args()
    result = verify_recovered_replay(args.root)
    dump(args.output, result)
    print(
        json.dumps(
            {
                k: result[k]
                for k in [
                    "status",
                    "mismatch_cells",
                    "selected_k2_mismatch_cells",
                    "source_analyses_rerun",
                ]
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
