"""Independent numerical reconciliation of aggregate D evidence and immutable inputs."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import chi2

from mp1.audit import repository_path, sha256_file
from mp1.outcome_validation import verify_frozen


def reconcile_rank_table(counts: np.ndarray) -> dict:
    """Derive rank sums, tie correction and all ordered pairs directly from a count table."""
    counts = np.asarray(counts, dtype=float)
    if counts.ndim != 2 or counts.shape[0] != 2 or not np.isfinite(counts).all():
        raise ValueError("A finite two-profile contingency table is required.")
    if (counts < 0).any() or (counts.sum(axis=1) <= 0).any():
        raise ValueError("Counts and profile denominators must be valid.")
    totals, n = counts.sum(axis=0), counts.sum()
    midranks = totals.cumsum() - (totals - 1) / 2
    correction = 1 - ((totals**3 - totals).sum() / (n**3 - n))
    if correction == 0:
        h = 0.0
    else:
        rank_sums = counts @ midranks
        h = (
            12 / (n * (n + 1)) * (rank_sums**2 / counts.sum(axis=1)).sum() - 3 * (n + 1)
        ) / correction
    signed_pairs = sum(
        counts[1, j] * counts[0, k] * np.sign(j - k)
        for j in range(counts.shape[1])
        for k in range(counts.shape[1])
    )
    return {
        "h": float(h),
        "p": float(chi2.sf(h, 1)),
        "epsilon_squared": float(h / (n - 1)),
        "delta": float(signed_pairs / counts.sum(axis=1).prod()),
    }


def require_close(left, right, label: str, tolerance: float = 1e-10) -> None:
    if not np.allclose(left, right, atol=tolerance, rtol=0):
        raise ValueError(f"Numerical reconciliation failed: {label}")


def verify_d_evidence(
    config_path: str | Path = "config/analysis.yaml",
    settings_path: str | Path = "config/work_package_d.yaml",
    d3_path: str | Path | None = None,
    flags_path: str | Path | None = None,
    workbook_path: str | Path | None = None,
) -> dict:
    """Verify hashes, denominators, rank calculations and country-preserving inference."""
    _, settings, _ = verify_frozen(config_path, settings_path)
    d3_dir = repository_path(config_path, settings["d3"]["output_directory"])
    external_dir = repository_path(config_path, settings["external"]["output_directory"])
    d3 = json.loads((d3_dir / "outcome_summary.json").read_text())
    external = json.loads((external_dir / "external_summary.json").read_text())
    artifacts = 0
    for folder, manifest in [(d3_dir, d3), (external_dir, external)]:
        if manifest["settings_sha256"] != sha256_file(settings_path):
            raise ValueError("Outputs belong to different D settings.")
        for name, digest in manifest["artifact_sha256"].items():
            if sha256_file(folder / name) != digest:
                raise ValueError(f"Aggregate artifact changed: {name}")
            frame = pd.read_csv(folder / name)
            if {"RespondentID", "source_record_number", "prediction"}.intersection(frame):
                raise ValueError("A private record field is present in public outputs.")
            if np.isinf(frame.select_dtypes(include="number").to_numpy()).any():
                raise ValueError(f"Infinite numerical result: {name}")
            artifacts += 1
    sources = [
        (d3_path, d3["source_sha256"]),
        (flags_path, d3["quality_flags_sha256"]),
        (workbook_path, external["source_sha256"]),
    ]
    for path, digest in sources:
        if path is not None and sha256_file(path) != digest:
            raise ValueError("A private input changed after analysis.")
    if sha256_file(Path(__file__).with_name("outcome_validation.py")) != d3["code_sha256"]:
        raise ValueError("Outcome code differs from executed evidence.")
    for name, digest in external["code_sha256"].items():
        path = (
            Path(__file__).with_name(name)
            if name.endswith(".py")
            else repository_path(config_path, f"scripts/{name}")
        )
        if sha256_file(path) != digest:
            raise ValueError("External code differs from executed evidence.")
    if (
        sha256_file(Path(settings_path).with_name("work_package_d_crosswalk.csv"))
        != external["crosswalk_sha256"]
    ):
        raise ValueError("Compatibility crosswalk differs from executed evidence.")
    distribution = pd.read_csv(d3_dir / "cgpa_distributions.csv")
    comparisons = pd.read_csv(d3_dir / "cgpa_comparisons.csv")
    for result in comparisons.itertuples():
        counts = (
            distribution[distribution.variant.eq(result.variant)]
            .pivot(index="profile", columns="order_code", values="records")
            .sort_index()
            .to_numpy()
        )
        checked = reconcile_rank_table(counts)
        require_close(counts.sum(), result.n, "D3 outcome accounting")
        require_close(checked["h"], result.kruskal_h_tie_corrected, "tie-corrected rank sum H")
        require_close(checked["p"], result.nominal_p_value, "nominal chi-square reference")
        require_close(checked["delta"], result.cliff_delta_P2_minus_P1, "all-pairs Cliff delta")
        require_close(
            checked["epsilon_squared"],
            result.rank_epsilon_squared_H_over_N_minus_1,
            "rank epsilon squared",
        )
    intervals = pd.read_csv(d3_dir / "conditional_uncertainty.csv")
    if (
        len(intervals) != 9
        or not intervals.invalid_replicates.eq(0).all()
        or intervals.conditional_percentile_lower.isna().any()
        or intervals.conditional_percentile_upper.isna().any()
        or not (
            intervals.conditional_percentile_lower <= intervals.conditional_percentile_upper
        ).all()
    ):
        raise ValueError("Conditional uncertainty evidence is incomplete or invalid.")
    accounting = pd.read_csv(external_dir / "sample_accounting.csv").set_index("country")
    frequencies = pd.read_csv(external_dir / "item_distributions.csv")
    for (country, _), frame in frequencies.groupby(["country", "item"]):
        require_close(
            frame.records.sum(),
            accounting.loc[country, "analytic_records"],
            "external item denominator",
        )
        require_close(frame.fraction.sum(), 1, "external item proportions")
    compatibility = pd.read_csv(external_dir / "item_compatibility.csv")
    if len(compatibility) != 29 or compatibility.exact_common_anchor.any():
        raise ValueError("Crosswalk coverage or non-equivalence decision changed.")
    associations = pd.read_csv(external_dir / "observed_item_associations.csv")
    if len(associations) != 4 or set(associations.country) != set(
        settings["external"]["country_order"]
    ):
        raise ValueError("The bounded country-specific comparison family changed.")
    order = np.argsort(associations.permutation_p_value)
    ordered = associations.permutation_p_value.to_numpy()[order]
    adjusted = np.minimum(1, np.maximum.accumulate(ordered * np.arange(4, 0, -1)))
    require_close(associations.holm_p_four_test_family.to_numpy()[order], adjusted, "Holm family")
    if external["warnings"] or external["ordinal_engine"]["warnings"]:
        raise ValueError("Model warnings require manual review before accepting this evidence.")
    return {
        "frozen_abc_files_verified": len(settings["frozen_files"]),
        "aggregate_artifacts_verified": artifacts,
        "supplied_private_inputs_verified": sum(path is not None for path, _ in sources),
        "rank_calculations_reconciled": len(comparisons),
        "holm_family_reconciled": 4,
        "warnings_requiring_review": 0,
        "private_records_in_public_tables": False,
    }
