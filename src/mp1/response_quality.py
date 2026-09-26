"""Raw-response invariance flags without respondent exclusions or item scoring."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

import pandas as pd

from mp1.audit import (
    SCHEMA_VERSION,
    RawDataset,
    guard_output,
    load_inputs,
    missing_mask,
    repository_path,
    sha256_file,
    source_fingerprints,
    verify_unchanged,
    write_reports,
)

BOOLEAN_COLUMNS = [
    "quality_assessable",
    "quality_straight_line",
    "has_missing_survey_response",
    "has_invalid_survey_response",
    "include_full_sample",
    "include_sensitivity",
]
FLAG_COLUMNS = [
    "dataset",
    "source_sha256",
    "source_record_number",
    *BOOLEAN_COLUMNS,
    "invariant_response",
]
SUMMARY_COLUMNS = [
    "dataset",
    "source_sha256",
    "sample_rows",
    "eligible_item_count",
    "assessable_rows",
    "rows_with_missing_items",
    "rows_with_invalid_items",
    "straight_line_rows",
    "straight_line_proportion_full_sample",
    "straight_line_proportion_assessable",
    "sensitivity_rows",
    "unassessable_rows_retained_in_sensitivity",
    "metadata_inclusive_invariant_rows",
    "flag_membership_changes_when_metadata_included",
]
PATTERN_COLUMNS = [
    "dataset",
    "response_value",
    "eligible_item_count",
    "flagged_rows",
    "proportion_full_sample",
]
INVALID_COLUMNS = ["dataset", "column", "unexpected_response", "count"]
ITEM_COLUMNS = ["dataset", "item_position", "column", "eligibility_basis"]


def assess_responses(
    dataset: RawDataset, items: list[str], allowed_responses: list[str], missing_tokens: list[str]
) -> tuple[pd.DataFrame, dict, pd.DataFrame, pd.DataFrame]:
    """Flag complete, in-domain invariant vectors using only the listed survey items."""
    if len(items) < 2 or len(set(items)) != len(items):
        raise ValueError("Straight-line detection requires at least two distinct survey items.")
    absent = sorted(set(items) - set(dataset.frame.columns))
    if absent:
        raise ValueError(f"{dataset.name}: required survey columns are missing: {absent}")
    if not allowed_responses or len(allowed_responses) != len(set(allowed_responses)):
        raise ValueError("Allowed responses must be a nonempty list of distinct values.")
    if set(allowed_responses) & set(missing_tokens) or any(
        not value.strip() for value in allowed_responses
    ):
        raise ValueError("Allowed responses cannot include missing tokens or blank values.")
    frame = dataset.frame.reset_index(drop=True)
    survey = frame[items]
    missing = missing_mask(survey, missing_tokens)
    invalid = ~survey.isin(allowed_responses) & ~missing
    has_missing = missing.any(axis=1)
    has_invalid = invalid.any(axis=1)
    assessable = ~(has_missing | has_invalid)
    invariant = assessable & survey.eq(survey.iloc[:, 0], axis=0).all(axis=1)
    flags = pd.DataFrame(
        {
            "dataset": dataset.name,
            "source_sha256": dataset.sha256,
            "source_record_number": range(1, len(frame) + 1),
            "quality_assessable": assessable,
            "quality_straight_line": invariant,
            "has_missing_survey_response": has_missing,
            "has_invalid_survey_response": has_invalid,
            "include_full_sample": True,
            "include_sensitivity": ~invariant,
            "invariant_response": survey.iloc[:, 0].where(invariant, ""),
        },
        columns=FLAG_COLUMNS,
    )
    all_missing = missing_mask(frame, missing_tokens).any(axis=1)
    metadata_inclusive = assessable & ~all_missing & frame.eq(frame.iloc[:, 0], axis=0).all(axis=1)
    n_rows = len(frame)
    count = int(invariant.sum())
    assessed = int(assessable.sum())
    summary = {
        "dataset": dataset.name,
        "source_sha256": dataset.sha256,
        "sample_rows": n_rows,
        "eligible_item_count": len(items),
        "assessable_rows": assessed,
        "rows_with_missing_items": int(has_missing.sum()),
        "rows_with_invalid_items": int(has_invalid.sum()),
        "straight_line_rows": count,
        "straight_line_proportion_full_sample": count / n_rows if n_rows else None,
        "straight_line_proportion_assessable": count / assessed if assessed else None,
        "sensitivity_rows": n_rows - count,
        "unassessable_rows_retained_in_sensitivity": n_rows - assessed,
        "metadata_inclusive_invariant_rows": int(metadata_inclusive.sum()),
        "flag_membership_changes_when_metadata_included": int(
            (invariant != metadata_inclusive).sum()
        ),
    }
    patterns = pd.DataFrame(
        [
            {
                "dataset": dataset.name,
                "response_value": response,
                "eligible_item_count": len(items),
                "flagged_rows": int(value),
                "proportion_full_sample": int(value) / n_rows,
            }
            for response, value in survey.loc[invariant, items[0]]
            .value_counts()
            .sort_index()
            .items()
        ],
        columns=PATTERN_COLUMNS,
    )
    invalid_rows = []
    for column in items:
        for response, value in (
            survey.loc[invalid[column], column].value_counts().sort_index().items()
        ):
            invalid_rows.append(
                {
                    "dataset": dataset.name,
                    "column": column,
                    "unexpected_response": response,
                    "count": int(value),
                }
            )
    return flags, summary, patterns, pd.DataFrame(invalid_rows, columns=INVALID_COLUMNS)


def read_quality_flags(
    path: str | Path, dataset: str, source_sha256: str, row_count: int
) -> pd.DataFrame:
    """Validate the source fingerprint and record order before later flag consumption."""
    flags = pd.read_csv(path, dtype="string", keep_default_na=False)
    if list(flags.columns) != FLAG_COLUMNS:
        raise ValueError("Quality flag schema does not match the supported schema.")
    selected = flags.loc[flags["dataset"].eq(dataset)].copy()
    if len(selected) != row_count or (row_count and selected.empty):
        raise ValueError("Quality flag row count does not match the source dataset.")
    if not selected["source_sha256"].eq(source_sha256).all():
        raise ValueError("Quality flag fingerprint does not match the source file.")
    expected = [str(number) for number in range(1, row_count + 1)]
    if selected["source_record_number"].tolist() != expected:
        raise ValueError("Quality flags must contain each source record once, in original order.")
    for column in BOOLEAN_COLUMNS:
        if not selected[column].isin(["True", "False"]).all():
            raise ValueError(f"Invalid boolean serialization in quality flags: {column}")
        selected[column] = selected[column].map({"True": True, "False": False}).astype(bool)
    if not selected["include_full_sample"].all():
        raise ValueError("Full-sample flags must retain every source record.")
    if not selected["include_sensitivity"].eq(~selected["quality_straight_line"]).all():
        raise ValueError("Sensitivity indicator is inconsistent with the straight-line flag.")
    expected_assessable = ~(
        selected["has_missing_survey_response"] | selected["has_invalid_survey_response"]
    )
    if not selected["quality_assessable"].eq(expected_assessable).all():
        raise ValueError("Assessment status is inconsistent with missing or invalid responses.")
    if (selected["quality_straight_line"] & ~selected["quality_assessable"]).any():
        raise ValueError("Unassessable records cannot be flagged as straight-liners.")
    if not selected["invariant_response"].ne("").eq(selected["quality_straight_line"]).all():
        raise ValueError("Invariant response labels are inconsistent with the quality flag.")
    selected["source_record_number"] = selected["source_record_number"].astype(int)
    return selected.reset_index(drop=True)


def run_response_quality(config_path: str | Path = "config/analysis.yaml") -> Path:
    """Save aggregate evidence and a separate, private record-level indicator file."""
    config, raw, dictionary = load_inputs(config_path)
    settings = config["integrity"]
    fingerprints = source_fingerprints(raw, dictionary)
    fingerprints[Path(config_path).resolve()] = sha256_file(config_path)
    all_flags, summaries, patterns, invalid, item_rows, comparisons = [], [], [], [], [], []
    for name, dataset in raw.items():
        spec = settings["datasets"][name]
        flags, summary, pattern, errors = assess_responses(
            dataset, spec["survey_items"], spec["allowed_responses"], settings["missing_tokens"]
        )
        all_flags.append(flags)
        summaries.append(summary)
        patterns.append(pattern)
        invalid.append(errors)
        item_rows.extend(
            {
                "dataset": name,
                "item_position": position,
                "column": column,
                "eligibility_basis": "Explicit question header and labels; no reverse coding.",
            }
            for position, column in enumerate(spec["survey_items"], start=1)
        )
        if "prior_straight_line_count" in spec:
            prior = spec["prior_straight_line_count"]
            comparisons.append(
                {
                    "dataset": name,
                    "prior_claim": prior,
                    "observed": summary["straight_line_rows"],
                    "matches": prior == summary["straight_line_rows"],
                    "reference_source": spec["prior_straight_line_source"],
                    "interpretation": "Prior counts are comparisons, never detection criteria.",
                }
            )
    destination = repository_path(config_path, config["outputs"]["root"]) / "response_quality"
    flag_path = repository_path(config_path, config["response_quality"]["private_flags"])
    guard_output(flag_path, fingerprints)
    flag_path.parent.mkdir(parents=True, exist_ok=True)
    flags = pd.concat(all_flags, ignore_index=True)
    verify_unchanged(fingerprints)
    with tempfile.TemporaryDirectory(prefix=".mp1-", dir=flag_path.parent) as temporary:
        staged = Path(temporary) / "flags.csv"
        flags.to_csv(staged, index=False, lineterminator="\n")
        for name, dataset in raw.items():
            read_quality_flags(staged, name, dataset.sha256, len(dataset.frame))
        verify_unchanged(fingerprints)
        os.replace(staged, flag_path)
    tables = {
        "response_quality_summary.csv": pd.DataFrame(summaries, columns=SUMMARY_COLUMNS),
        "flagged_response_patterns.csv": pd.concat(patterns, ignore_index=True),
        "invalid_response_values.csv": pd.concat(invalid, ignore_index=True),
        "eligible_survey_items.csv": pd.DataFrame(item_rows, columns=ITEM_COLUMNS),
    }
    summary = {
        "schema_version": SCHEMA_VERSION,
        "config_sha256": sha256_file(config_path),
        "datasets": summaries,
        "prior_claim_comparisons": comparisons,
        "eligible_survey_items": {
            name: spec["survey_items"] for name, spec in settings["datasets"].items()
        },
        "policies": {
            "definition": "All listed items must be present, in-domain, and exactly equal.",
            "missing_tokens": settings["missing_tokens"],
            "normalization": "none",
            "reverse_coding": "none",
            "imputation": "none",
            "primary_exclusions": "none",
            "sensitivity_indicator": "Exclude only quality_straight_line=True.",
            "unassessable_records": "Retained with quality_assessable=False; validity unconfirmed.",
            "interpretation": "Invariance is a diagnostic, not proof of carelessness.",
            "record_linkage": "Source-file SHA-256 plus 1-based data-record position. "
            "Positions are not respondent identifiers or physical line numbers.",
        },
        "private_flags": {
            "configured_path": config["response_quality"]["private_flags"],
            "sha256": sha256_file(flag_path),
        },
        "acceptance_status": "requires_researcher_review",
    }
    narrative = (
        "# Response quality\n\n"
        + "\n".join(
            f"- {item['dataset']}: {item['straight_line_rows']} invariant records among "
            f"{item['sample_rows']} records, using {item['eligible_item_count']} survey items. "
            f"Sensitivity indicator retains {item['sensitivity_rows']} records."
            for item in summaries
        )
        + "\n\nNo records were removed. Unassessable records remain explicitly "
    )
    narrative += (
        "identified and retained. No downstream analysis or construct scoring was performed.\n"
    )
    write_reports(
        destination, tables, summary, "response_quality_summary.json", fingerprints, narrative
    )
    return destination
