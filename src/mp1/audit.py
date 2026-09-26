"""Lossless source inspection and aggregate provenance reporting."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import os
import re
import tempfile
import unicodedata
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd

from mp1.config import load_config
from mp1.paths import get_drive_root

SCHEMA_VERSION = "1.0"
TABLE_COLUMNS = {
    "dataset_summary.csv": [
        "dataset",
        "source_file",
        "source_sha256",
        "source_bytes",
        "raw_rows",
        "column_count",
        "full_sample_rows_before_sensitivity",
        "rows_removed",
        "missing_cells",
        "identifier_status",
    ],
    "column_schema.csv": [
        "dataset",
        "position",
        "column",
        "role",
        "storage_type",
        "inferred_value_type",
        "distinct_nonmissing_values",
    ],
    "missingness_summary.csv": [
        "dataset",
        "column",
        "null_count",
        "empty_count",
        "whitespace_only_count",
        "configured_token_count",
        "missing_count",
        "missing_proportion",
    ],
    "duplicate_summary.csv": [
        "dataset",
        "basis",
        "status",
        "eligible_rows",
        "incomplete_identifier_rows",
        "duplicate_groups",
        "duplicate_member_rows",
        "duplicate_excess_rows",
        "unique_records",
        "largest_group_size",
        "rows_removed",
    ],
    "categorical_values.csv": ["dataset", "column", "value", "count"],
    "d3_institution_review.csv": [
        "raw_institution",
        "count",
        "comparison_key",
        "labels_sharing_key",
        "label_contains_college",
        "review_status",
        "approved_institution",
        "evidence",
    ],
    "metadata_comparisons.csv": [
        "dataset",
        "metric",
        "reference_value",
        "observed_value",
        "matches",
        "reference_source",
        "interpretation",
    ],
    "discrepancies.csv": ["dataset", "issue", "evidence", "status", "required_review"],
}


@dataclass(frozen=True)
class RawDataset:
    """A source fingerprint and its unmodified CSV field values."""

    name: str
    path: Path
    sha256: str
    byte_count: int
    frame: pd.DataFrame


def sha256_file(path: str | Path) -> str:
    """Fingerprint the original bytes."""
    with Path(path).open("rb") as handle:
        return hashlib.file_digest(handle, "sha256").hexdigest()


def read_raw_csv(path: str | Path, name: str, encoding: str = "utf-8-sig") -> RawDataset:
    """Read every record without NA inference, header repair, or value normalization."""
    source = Path(path).resolve()
    if not source.is_file():
        raise FileNotFoundError(f"Required source file does not exist: {source}")
    content = source.read_bytes()
    text = content.decode(encoding, errors="strict")
    if "\x00" in text:
        raise ValueError(f"NUL character found in CSV: {source.name}")
    try:
        reader = csv.reader(io.StringIO(text, newline=""), strict=True)
        header = next(reader, None)
        if not header or any(not column.strip() for column in header):
            raise ValueError(f"CSV requires a nonblank header: {source.name}")
        if len(set(header)) != len(header):
            raise ValueError(f"Duplicate column names in {source.name}")
        rows = []
        for number, row in enumerate(reader, start=1):
            if len(row) != len(header):
                raise ValueError(
                    f"{source.name}: data record {number} has {len(row)} fields; "
                    f"expected {len(header)}. No records were skipped."
                )
            rows.append(row)
    except csv.Error as exc:
        raise ValueError(f"Malformed CSV in {source.name}: {exc}") from exc
    frame = pd.DataFrame(rows, columns=header, dtype="string")
    return RawDataset(name, source, hashlib.sha256(content).hexdigest(), len(content), frame)


def missing_mask(frame: pd.DataFrame, tokens: list[str]) -> pd.DataFrame:
    """Recognize nulls, blank fields, and explicitly configured exact tokens."""
    return frame.apply(
        lambda column: (
            column.isna()
            | column.astype("string").str.fullmatch(r"\s*", na=False)
            | column.isin(tokens)
        )
    ).astype(bool)


def duplicate_counts(frame: pd.DataFrame) -> dict[str, int]:
    """Separate all group members from repetitions beyond the first record."""
    group_sizes = frame.value_counts(dropna=False, sort=False)
    repeated = group_sizes[group_sizes > 1]
    return {
        "duplicate_groups": int(len(repeated)),
        "duplicate_member_rows": int(repeated.sum()),
        "duplicate_excess_rows": int((repeated - 1).sum()),
        "unique_records": int(len(group_sizes)),
        "largest_group_size": int(group_sizes.max()) if len(group_sizes) else 0,
    }


def inferred_value_type(values: pd.Series) -> str:
    """Describe lexical numeric content without converting the source values."""
    if values.empty:
        return "empty"
    text = values.astype("string")
    if text.str.fullmatch(r"[+-]?\d+").all():
        return "integer"
    numeric = r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?"
    return "number" if text.str.fullmatch(numeric).all() else "text"


def institution_review(values: pd.Series) -> pd.DataFrame:
    """Propose comparison keys without treating them as approved aliases."""
    counts = values.value_counts(sort=False)
    keys = {
        str(value): " ".join(unicodedata.normalize("NFKC", str(value)).casefold().split())
        for value in counts.index
    }
    collisions = Counter(keys.values())
    rows = [
        {
            "raw_institution": str(value),
            "count": int(count),
            "comparison_key": keys[str(value)],
            "labels_sharing_key": collisions[keys[str(value)]],
            "label_contains_college": "college" in keys[str(value)].split(),
            "review_status": "unresolved_no_alias_applied",
            "approved_institution": "",
            "evidence": "",
        }
        for value, count in sorted(counts.items(), key=lambda item: str(item[0]))
    ]
    return pd.DataFrame(rows, columns=TABLE_COLUMNS["d3_institution_review.csv"])


def _string_list(value: Any, label: str, *, nonempty: bool = False) -> list[str]:
    if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
        raise ValueError(f"{label} must be a list of strings.")
    if len(value) != len(set(value)) or (nonempty and not value):
        raise ValueError(f"{label} must contain distinct values and satisfy its required length.")
    return value


def _source_path(root: Path, relative: str) -> Path:
    if not isinstance(relative, str) or not relative:
        raise ValueError("Source locations must be nonempty relative paths.")
    candidate = Path(relative)
    if candidate.is_absolute() or ".." in candidate.parts:
        raise ValueError(
            f"Source location must be relative to the configured Drive root: {relative}"
        )
    return root / candidate


def repository_path(config_path: str | Path, value: str) -> Path:
    """Resolve output locations relative to the directory containing config/."""
    if not isinstance(value, str) or not value:
        raise ValueError("Output locations must be nonempty paths.")
    path = Path(value).expanduser()
    base = Path(config_path).resolve().parent.parent
    return (base / path).resolve() if not path.is_absolute() else path.resolve()


def load_inputs(config_path: str | Path) -> tuple[dict, dict[str, RawDataset], dict]:
    """Load configured inputs and validate the explicit item and metadata columns."""
    config = load_config(config_path)
    try:
        settings = config["integrity"]
        root = get_drive_root(config["project"]["drive_root_env"])
        tokens = _string_list(settings["missing_tokens"], "integrity.missing_tokens")
        if any(not token.strip() for token in tokens):
            raise ValueError("Blank fields are already missing; do not list blank missing tokens.")
        specs = settings["datasets"]
        if not isinstance(specs, dict) or set(specs) != {"D5", "D3"}:
            raise ValueError("integrity.datasets must contain D5 and D3.")
        raw = {}
        for name, spec in specs.items():
            items = _string_list(spec["survey_items"], f"{name}.survey_items", nonempty=True)
            metadata = _string_list(spec["metadata_columns"], f"{name}.metadata_columns")
            identifiers = _string_list(spec["identifier_columns"], f"{name}.identifier_columns")
            categories = _string_list(spec["categorical_columns"], f"{name}.categorical_columns")
            responses = _string_list(
                spec["allowed_responses"], f"{name}.allowed_responses", nonempty=True
            )
            if len(items) < 2 or set(items) & set(metadata + identifiers):
                raise ValueError(
                    f"{name}: survey items must be distinct from metadata and identifiers."
                )
            if any(not value or value in tokens for value in responses):
                raise ValueError(f"{name}: allowed responses overlap missing values.")
            dataset = read_raw_csv(
                _source_path(root, config["data"][spec["source_key"]]),
                name,
                settings["csv_encoding"],
            )
            required = set(items + metadata + identifiers + categories)
            if spec.get("institution_column"):
                required.add(spec["institution_column"])
            absent = sorted(required - set(dataset.frame.columns))
            if absent:
                raise ValueError(f"{name}: required columns are missing: {absent}")
            raw[name] = dataset
        dictionary_path = _source_path(root, config["data"]["data_dictionary"])
        if not dictionary_path.is_file():
            raise FileNotFoundError(f"Required data dictionary does not exist: {dictionary_path}")
        dictionary_bytes = dictionary_path.read_bytes()
        dictionary_text = dictionary_bytes.decode("utf-8-sig")
    except KeyError as exc:
        raise ValueError(
            f"Required analysis configuration entry is missing: {exc.args[0]}"
        ) from exc
    headings = re.findall(r"^#{1,6}\s+(.+)$", dictionary_text, flags=re.MULTILINE)
    dictionary = {
        "path": str(dictionary_path.resolve()),
        "sha256": hashlib.sha256(dictionary_bytes).hexdigest(),
        "dataset_headings_found": {
            name: any(re.search(rf"\b{re.escape(name)}(?:\b|_)", heading) for heading in headings)
            for name in raw
        },
    }
    return config, raw, dictionary


def source_fingerprints(raw: dict[str, RawDataset], dictionary: dict) -> dict[Path, str]:
    return {
        **{item.path: item.sha256 for item in raw.values()},
        Path(dictionary["path"]): dictionary["sha256"],
    }


def verify_unchanged(fingerprints: dict[Path, str]) -> None:
    for path, expected in fingerprints.items():
        if sha256_file(path) != expected:
            raise RuntimeError(f"Source changed during the audit: {path.name}")


def guard_output(path: Path, fingerprints: dict[Path, str]) -> None:
    """Reject writes in source directories, including resolved symbolic links."""
    destination = path.resolve()
    for source in fingerprints:
        if destination == source or destination.is_relative_to(source.parent):
            raise ValueError(f"Output location overlaps a source directory: {path}")


def write_reports(
    directory: Path,
    tables: dict[str, pd.DataFrame],
    summary: dict,
    summary_name: str,
    fingerprints: dict[Path, str],
    narrative: str | None = None,
) -> None:
    """Stage complete reports and publish the fingerprint manifest last."""
    targets = [*tables, summary_name] + (["summary.md"] if narrative is not None else [])
    for name in targets:
        guard_output(directory / name, fingerprints)
    verify_unchanged(fingerprints)
    directory.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".mp1-", dir=directory) as temporary:
        staging = Path(temporary)
        for name, table in tables.items():
            table.to_csv(staging / name, index=False, lineterminator="\n")
        if narrative is not None:
            (staging / "summary.md").write_text(narrative, encoding="utf-8")
        manifest = dict(summary)
        manifest["artifact_sha256"] = {
            name: sha256_file(staging / name) for name in targets if name != summary_name
        }
        (staging / summary_name).write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False, allow_nan=False) + "\n",
            encoding="utf-8",
        )
        verify_unchanged(fingerprints)
        for name in [item for item in targets if item != summary_name] + [summary_name]:
            os.replace(staging / name, directory / name)
    verify_unchanged(fingerprints)


def audit_dataset(dataset: RawDataset, spec: dict, tokens: list[str]) -> dict[str, list[dict]]:
    """Summarize one complete file without changing its records."""
    frame = dataset.frame
    name = dataset.name
    n_rows = len(frame)
    missing = missing_mask(frame, tokens)
    tables: dict[str, list[dict]] = {key: [] for key in TABLE_COLUMNS}
    tables["dataset_summary.csv"].append(
        {
            "dataset": name,
            "source_file": dataset.path.name,
            "source_sha256": dataset.sha256,
            "source_bytes": dataset.byte_count,
            "raw_rows": n_rows,
            "column_count": len(frame.columns),
            "full_sample_rows_before_sensitivity": n_rows,
            "rows_removed": 0,
            "missing_cells": int(missing.sum().sum()),
            "identifier_status": "configured" if spec["identifier_columns"] else "not_available",
        }
    )
    for position, column in enumerate(frame.columns, start=1):
        values = frame[column]
        available = values[~missing[column]]
        role = "unclassified"
        for label, names in [
            ("metadata", spec["metadata_columns"]),
            ("survey_item", spec["survey_items"]),
            ("identifier", spec["identifier_columns"]),
        ]:
            if column in names:
                role = label
        tables["column_schema.csv"].append(
            {
                "dataset": name,
                "position": position,
                "column": column,
                "role": role,
                "storage_type": "string",
                "inferred_value_type": inferred_value_type(available),
                "distinct_nonmissing_values": int(available.nunique()),
            }
        )
        empty = values.eq("").fillna(False)
        whitespace = values.str.fullmatch(r"\s+", na=False)
        explicit = values.isin(tokens) & ~empty & ~whitespace
        count = int(missing[column].sum())
        tables["missingness_summary.csv"].append(
            {
                "dataset": name,
                "column": column,
                "null_count": int(values.isna().sum()),
                "empty_count": int(empty.sum()),
                "whitespace_only_count": int(whitespace.sum()),
                "configured_token_count": int(explicit.sum()),
                "missing_count": count,
                "missing_proportion": count / n_rows if n_rows else None,
            }
        )
        if column in spec["categorical_columns"]:
            for value, count in available.value_counts(sort=False).sort_index().items():
                tables["categorical_values.csv"].append(
                    {
                        "dataset": name,
                        "column": column,
                        "value": value,
                        "count": int(count),
                    }
                )
    duplicates = duplicate_counts(frame)
    tables["duplicate_summary.csv"].append(
        {
            "dataset": name,
            "basis": "all_raw_columns",
            "status": "assessed",
            "eligible_rows": n_rows,
            "incomplete_identifier_rows": None,
            **duplicates,
            "rows_removed": 0,
        }
    )
    identifiers = spec["identifier_columns"]
    complete = ~missing[identifiers].any(axis=1) if identifiers else None
    identifier_result = (
        duplicate_counts(frame.loc[complete, identifiers])
        if identifiers
        else {key: None for key in duplicates}
    )
    tables["duplicate_summary.csv"].append(
        {
            "dataset": name,
            "basis": "respondent_identifier",
            "status": "assessed" if identifiers else "not_available",
            "eligible_rows": int(complete.sum()) if identifiers else None,
            "incomplete_identifier_rows": int((~complete).sum()) if identifiers else None,
            **identifier_result,
            "rows_removed": 0,
        }
    )
    metrics = {"raw_rows": n_rows, "survey_item_count": len(spec["survey_items"])}
    institution_column = spec.get("institution_column")
    if institution_column:
        labels = frame.loc[~missing[institution_column], institution_column]
        review = institution_review(labels)
        tables["d3_institution_review.csv"] = review.to_dict(orient="records")
        metrics["raw_institution_strings"] = int(labels.nunique())
        metrics["institution_comparison_keys"] = int(review["comparison_key"].nunique())
    for claim in spec["reference_claims"]:
        metric = claim["metric"]
        if metric not in metrics:
            raise ValueError(f"{name}: unsupported reference metric: {metric}")
        observed = metrics[metric]
        matches = observed == claim["value"]
        tables["metadata_comparisons.csv"].append(
            {
                "dataset": name,
                "metric": metric,
                "reference_value": claim["value"],
                "observed_value": observed,
                "matches": matches,
                "reference_source": claim["source"],
                "interpretation": claim["interpretation"],
            }
        )
        if not matches:
            tables["discrepancies.csv"].append(
                {
                    "dataset": name,
                    "issue": f"reference_mismatch_{metric}",
                    "evidence": f"Reference={claim['value']}; observed={observed}; "
                    f"{claim['source']}",
                    "status": "unresolved",
                    "required_review": claim["interpretation"],
                }
            )
    if duplicates["duplicate_excess_rows"]:
        tables["discrepancies.csv"].append(
            {
                "dataset": name,
                "issue": "identical_records_require_review",
                "evidence": f"{duplicates['duplicate_excess_rows']} excess identical records; "
                f"largest identical group={duplicates['largest_group_size']}",
                "status": "unresolved_all_retained",
                "required_review": "Identical anonymous records do not establish duplicate people. "
                "Obtain source clarification before deciding any exclusion.",
            }
        )
    unclassified = sorted(
        set(frame.columns) - set(spec["metadata_columns"] + spec["survey_items"] + identifiers)
    )
    if unclassified:
        tables["discrepancies.csv"].append(
            {
                "dataset": name,
                "issue": "unclassified_columns",
                "evidence": json.dumps(unclassified),
                "status": "unresolved",
                "required_review": "Review new columns; they were excluded from survey flags.",
            }
        )
    return tables


def run_provenance(config_path: str | Path = "config/analysis.yaml") -> Path:
    """Write the reproducible provenance report for the configured D5 and D3 files."""
    config, raw, dictionary = load_inputs(config_path)
    settings = config["integrity"]
    rows: dict[str, list[dict]] = {name: [] for name in TABLE_COLUMNS}
    for name, dataset in raw.items():
        result = audit_dataset(dataset, settings["datasets"][name], settings["missing_tokens"])
        for table, records in result.items():
            rows[table].extend(records)
        if not dictionary["dataset_headings_found"][name]:
            rows["discrepancies.csv"].append(
                {
                    "dataset": name,
                    "issue": "dictionary_dataset_section_absent",
                    "evidence": f"No {name} section heading in the supplied data dictionary.",
                    "status": "unresolved",
                    "required_review": "Obtain the codebook. Eligibility uses explicit "
                    "raw question headers and response labels, without construct scoring.",
                }
            )
        metadata = settings["datasets"][name]["source_metadata"]
        published_sha256 = metadata.get("published_file_sha256")
        if published_sha256 != dataset.sha256:
            rows["discrepancies.csv"].append(
                {
                    "dataset": name,
                    "issue": "public_download_identity_unverified"
                    if published_sha256 is None
                    else "public_file_fingerprint_mismatch",
                    "evidence": "No independent published-file fingerprint is configured."
                    if published_sha256 is None
                    else f"Published SHA-256={published_sha256}; local SHA-256={dataset.sha256}",
                    "status": "unresolved",
                    "required_review": "Compare the published version and obtain "
                    "source clarification. Do not infer the reason for any count difference.",
                }
            )
        if (
            metadata.get("reported_duplicate_removal")
            and result["duplicate_summary.csv"][0]["duplicate_excess_rows"]
        ):
            rows["discrepancies.csv"].append(
                {
                    "dataset": name,
                    "issue": "source_cleaning_statement_requires_clarification",
                    "evidence": "Public metadata describes duplicate removal. Identical complete "
                    "records remain in the attached file.",
                    "status": "unresolved",
                    "required_review": "Clarify the source's duplicate definition "
                    "and compare the original release before interpreting these repetitions.",
                }
            )
    tables = {
        name: pd.DataFrame(records, columns=TABLE_COLUMNS[name]) for name, records in rows.items()
    }
    destination = repository_path(config_path, config["outputs"]["root"]) / "provenance"
    summary = {
        "schema_version": SCHEMA_VERSION,
        "config_sha256": sha256_file(config_path),
        "datasets": rows["dataset_summary.csv"],
        "source_metadata": {
            name: spec["source_metadata"] for name, spec in settings["datasets"].items()
        },
        "dictionary": {key: value for key, value in dictionary.items() if key != "path"},
        "policies": {
            "row_exclusions": "none",
            "normalizations_applied": "none",
            "aliases_applied": "none",
            "recoding": "none",
            "imputation": "none",
            "missing_tokens": settings["missing_tokens"],
            "blank_fields": "Empty or whitespace-only fields count as missing; strings remain.",
            "csv_values": "Original values remain strings; inferred types are descriptive.",
            "institution_comparison": "NFKC, casefold, and space collapse form review keys only. "
            "Raw string counts are not verified counts of distinct institutions.",
        },
        "metadata_comparisons": rows["metadata_comparisons.csv"],
        "discrepancies": rows["discrepancies.csv"],
        "acceptance_status": "requires_researcher_review",
    }
    narrative = (
        "# Provenance audit\n\n"
        + "\n".join(
            f"- {item['dataset']}: {item['raw_rows']} records, {item['column_count']} columns, "
            f"{item['missing_cells']} missing cells, 0 exclusions."
            for item in rows["dataset_summary.csv"]
        )
        + "\n\nFull-sample counts describe retained records, not verified unique respondents. "
    )
    narrative += "Review discrepancies.csv, duplicate_summary.csv, and d3_institution_review.csv. "
    narrative += "Reference counts remain claims until reconciled. "
    narrative += "This report does not authorize later analyses.\n"
    fingerprints = source_fingerprints(raw, dictionary)
    fingerprints[Path(config_path).resolve()] = sha256_file(config_path)
    write_reports(destination, tables, summary, "provenance_summary.json", fingerprints, narrative)
    return destination
