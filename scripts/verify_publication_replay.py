"""Replay accepted analyses solely for reproduction in an isolated, disposable checkout.

Never overwrite the accepted results in the caller's checkout. Private outputs and logs stay
inside the caller-specified private work directory. A-D methods and settings remain unchanged.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd

BASELINE = "56b335c705ef15d5a261865382dd79991d2a93a2"


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def compare_csv(reference, replay, tolerance=1e-10):
    a, b = pd.read_csv(reference), pd.read_csv(replay)
    if list(a) != list(b) or a.shape != b.shape:
        raise ValueError(f"Output schema/shape changed: {reference.name}")
    differences = []
    cells = []
    keys = [
        k for k in ["dataset", "sample", "variant", "country", "k", "cluster", "item"] if k in a
    ]
    for i in range(len(a)):
        for column in a:
            av, bv = a.iloc[i][column], b.iloc[i][column]
            if pd.isna(av) and pd.isna(bv):
                continue
            numeric = isinstance(av, (int, float, np.number)) and not isinstance(
                av, (bool, np.bool_)
            )
            same = (
                np.isclose(av, bv, atol=tolerance, rtol=0, equal_nan=True) if numeric else av == bv
            )
            if not same:
                cells.append(
                    {
                        "csv_data_row": i + 1,
                        **{k: str(a.iloc[i][k]) for k in keys},
                        "field": column,
                        "accepted_value": str(av),
                        "replayed_value": str(bv),
                        "difference": float(bv - av)
                        if numeric and np.isfinite(av) and np.isfinite(bv)
                        else None,
                        "selected_k2": bool(a.iloc[i]["k"] == 2) if "k" in a else None,
                    }
                )
    for column in a:
        if pd.api.types.is_numeric_dtype(a[column]) and not pd.api.types.is_bool_dtype(a[column]):
            av, bv = a[column].to_numpy(float), b[column].to_numpy(float)
            if not np.allclose(av, bv, atol=tolerance, rtol=0, equal_nan=True):
                finite = np.isfinite(av) & np.isfinite(bv)
                differences.append(
                    {
                        "column": column,
                        "maximum_absolute_difference": float(
                            np.max(np.abs(av[finite] - bv[finite]))
                        )
                        if finite.any()
                        else None,
                    }
                )
        elif not a[column].fillna("<NA>").equals(b[column].fillna("<NA>")):
            differences.append({"column": column, "categorical_or_order_difference": True})
    return {
        "file": reference.name,
        "rows": len(a),
        "absolute_tolerance": tolerance,
        "byte_identical": digest(reference) == digest(replay),
        "differences": differences,
        "mismatch_cells": cells,
        "status": "PASS" if not differences else "FAIL",
    }


def write_discrepancies(report, path):
    rows = []
    folders = {
        "B_measurement": "outputs/psychometrics",
        "B_clustering": "outputs/clustering",
        "C_feasibility": "outputs/modeling/work_package_c",
        "D_CGPA": "outputs/outcome_validation/work_package_d",
        "D_external": "outputs/external_validation/work_package_d",
    }
    for stage in report["stages"]:
        for comparison in stage["csv_comparisons"]:
            for cell in comparison.get("mismatch_cells", []):
                rows.append(
                    {"accepted_file": folders[stage["stage"]] + "/" + comparison["file"], **cell}
                )
    columns = [
        "accepted_file",
        "csv_data_row",
        "dataset",
        "sample",
        "variant",
        "country",
        "k",
        "cluster",
        "item",
        "field",
        "accepted_value",
        "replayed_value",
        "difference",
        "selected_k2",
    ]
    pd.DataFrame(rows).reindex(columns=columns).to_csv(path, index=False)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--inputs",
        type=Path,
        required=True,
        help="Private directory with the five exactly named input files in the freeze.",
    )
    p.add_argument("--work", type=Path, required=True, help="New private disposable directory.")
    p.add_argument("--runtime", type=Path, default=Path(".venv/ordinal/runtime.json"))
    p.add_argument("--report", type=Path, required=True, help="Aggregate-only verification JSON.")
    args = p.parse_args()
    root = Path(__file__).resolve().parents[1]
    locked = json.loads((root / "config/publication_freeze.json").read_text())
    before = {name: digest(args.inputs / name) for name in locked["private_input_sha256"]}
    if before != locked["private_input_sha256"]:
        raise ValueError(
            "Source hashes do not match accepted inputs. Do not edit or coerce sources."
        )
    if args.work.resolve().is_relative_to(args.inputs.resolve()):
        raise ValueError("Replay work must be outside the private input directory.")
    if args.work.exists():
        raise ValueError("Replay work directory already exists; use a new private directory.")
    args.work.mkdir(parents=True)
    checkout = args.work.resolve() / "checkout"
    subprocess.run(
        ["git", "clone", "--no-hardlinks", str(root), str(checkout)],
        check=True,
        stdout=subprocess.DEVNULL,
    )
    subprocess.run(
        ["git", "checkout", "--detach", BASELINE],
        cwd=checkout,
        check=True,
        stdout=subprocess.DEVNULL,
    )
    drive = args.work.resolve() / "private_source_mount"
    mapping = {
        "D5_cognitive_dependence_raw.csv": (
            "Source Data/D5 Bangladesh/D5_cognitive_dependence_raw.csv"
        ),
        "D3_dependency_vulnerability_raw.csv": (
            "Source Data/D3 Bangladesh/D3_dependency_vulnerability_raw.csv"
        ),
        "DATA_DICTIONARY.md": "Reference Materials/Data Dictionaries/DATA_DICTIONARY.md",
    }
    for name, relative in mapping.items():
        target = drive / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile((args.inputs / name).resolve(), target)
    runtime = json.loads(args.runtime.read_text())
    env = {
        **os.environ,
        "MP1_DRIVE_ROOT": str(drive),
        "PYTHONPATH": str(checkout / "src"),
        "PYTHONHASHSEED": "0",
        "OPENBLAS_NUM_THREADS": "1",
        "OMP_NUM_THREADS": "1",
        "MKL_NUM_THREADS": "1",
        "MP1_R_EXECUTABLE": runtime["R"],
        "R_LIBS_USER": runtime["R_LIBS_USER"],
        "R_LIBS_SITE": runtime["R_LIBS_USER"],
    }
    stages = [
        ("A_response_quality", "response_quality.py", [], None),
        ("B_measurement", "psychometrics_analysis.py", [], "outputs/psychometrics"),
        ("B_clustering", "clustering_analysis.py", [], "outputs/clustering"),
        ("C_feasibility", "predictive_audit.py", [], "outputs/modeling/work_package_c"),
        ("D_CGPA", "outcome_validation.py", [], "outputs/outcome_validation/work_package_d"),
        (
            "D_external",
            "external_validation.py",
            [
                "--external-workbook",
                str((args.inputs / "When Culture Meets AI - Survey Dataset.xlsx").resolve()),
            ],
            "outputs/external_validation/work_package_d",
        ),
    ]
    report = {
        "baseline_commit": BASELINE,
        "purpose": "reproduction only; no result replacement",
        "input_sha256": before,
        "stages": [],
        "status": "RUNNING",
        "private_logs_distributed": False,
        "original_private_B_memberships_available": False,
        "reconstructed_B_memberships": (
            "Preserved privately; withheld from C/D to match accepted invocation"
        ),
        "tolerance_policy": "Counts, labels and decisions exact; ordinary floats 1e-10; "
        "iterative B factor/ULS and external ULS/WLSMV outputs 1e-5 absolute. "
        "Iterative tolerance covers polychoric optimization and derived eigenvalues as well. "
        "An initial verifier wrongly treated those as exact arithmetic; see the E validation note.",
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    try:
        for label, script, extra, folder in stages:
            if label == "C_feasibility":
                members = checkout / "data/interim/work_package_b/cluster_memberships.csv"
                if members.exists():
                    members.rename(args.work / "reconstructed_B_memberships_private.csv")
            log = args.work / (label + ".log")
            with log.open("w") as stream:
                result = subprocess.run(
                    [sys.executable, str(checkout / "scripts" / script), *extra],
                    cwd=checkout,
                    env=env,
                    stdout=stream,
                    stderr=subprocess.STDOUT,
                    check=False,
                )
            stage = {"stage": label, "exit_code": result.returncode, "csv_comparisons": []}
            report["stages"].append(stage)
            if result.returncode:
                stage["status"] = "FAIL"
                report["status"] = "FAIL"
                raise RuntimeError(f"Replay failed: {label}. Inspect private log {log}")
            if folder:
                reproduced = args.work / "reproduced_aggregates" / label
                shutil.copytree(checkout / folder, reproduced)
                for ref in sorted((root / folder).glob("*.csv")):
                    iterative = ref.name in {
                        "item_correlations.csv",
                        "measurement_assumptions.csv",
                        "parallel_analysis.csv",
                        "factor_models.csv",
                        "factor_loadings.csv",
                        "factor_correlations.csv",
                        "reliability.csv",
                        "item_diagnostics.csv",
                        "country_factor_diagnostics.csv",
                        "country_factor_loadings.csv",
                        "country_factor_correlations.csv",
                        "ordinal_model_fit.csv",
                        "ordinal_model_parameters.csv",
                    }
                    stage["csv_comparisons"].append(
                        compare_csv(ref, checkout / folder / ref.name, 1e-5 if iterative else 1e-10)
                    )
                # Explicit decisions are compared independently of parameter tolerance.
                for filename, keys in {
                    "measurement_summary.json": ["samples", "decisions", "representation", "htmt"],
                    "clustering_summary.json": ["choices", "representation"],
                    "predictive_audit_summary.json": ["gate", "sensitivity", "performance_metrics"],
                    "outcome_summary.json": ["outcome", "posthoc", "raw_records_removed"],
                    "external_summary.json": [
                        "bangladesh_compatibility",
                        "invariance_interpretation",
                        "raw_rows_deleted",
                        "vietnam_used",
                    ],
                }.items():
                    if (root / folder / filename).exists():
                        a = json.loads((root / folder / filename).read_text())
                        b = json.loads((checkout / folder / filename).read_text())
                        stage["decision_keys_equal"] = {key: a[key] == b[key] for key in keys}
                # Revert only the disposable clone's accepted outputs so downstream frozen-input
                # checks receive the accepted bytes, never a numerically equivalent substitute.
                subprocess.run(
                    ["git", "restore", "--source", BASELINE, "--", folder], cwd=checkout, check=True
                )
            else:
                flags = checkout / "data/processed/response_quality_flags.csv"
                expected = json.loads(
                    (root / "outputs/psychometrics/measurement_summary.json").read_text()
                )
                stage["quality_flags_sha256_equal"] = (
                    digest(flags) == expected["quality_flags_sha256"]
                )
            stage["status"] = (
                "PASS"
                if (
                    all(c["status"] == "PASS" for c in stage["csv_comparisons"])
                    and all(stage.get("decision_keys_equal", {}).values())
                    and stage.get("quality_flags_sha256_equal", True)
                )
                else "FAIL"
            )
            args.report.write_text(json.dumps(report, indent=2) + "\n")
        report["status"] = (
            "PASS" if all(s["status"] == "PASS" for s in report["stages"]) else "FAIL"
        )
    except BaseException as exc:
        report["status"] = "FAIL"
        report["verification_error_type"] = type(exc).__name__
        raise
    finally:
        report["input_sha256_after"] = {name: digest(args.inputs / name) for name in before}
        report["raw_source_immutable"] = report["input_sha256_after"] == before
        report["caller_accepted_files_unchanged"] = all(
            digest(root / name) == value for name, value in locked["frozen_files"].items()
        )
        if not report["raw_source_immutable"] or not report["caller_accepted_files_unchanged"]:
            report["status"] = "FAIL"
        args.report.write_text(json.dumps(report, indent=2) + "\n")
        write_discrepancies(report, args.report.with_name("replay_discrepancies.csv"))
    if report["status"] != "PASS":
        raise SystemExit(
            "Reproduction mismatch: preserve evidence and review; no automatic acceptance."
        )
    print("Accepted A-D source replay and source immutability: PASS")


if __name__ == "__main__":
    main()
