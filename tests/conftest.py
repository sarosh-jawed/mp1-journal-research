from __future__ import annotations

import csv
from pathlib import Path

import pytest
import yaml


@pytest.fixture
def synthetic_project(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    root = tmp_path / "research"
    source = tmp_path / "sources"
    (root / "config").mkdir(parents=True)
    source.mkdir()
    items = ["question_1", "question_2", "question_3"]
    records = {
        "D5": [
            ["m1", "001", "No", "No", "No"],
            ["m2", "002", "No", "Yes", "No"],
            ["m2", "002", "No", "Yes", "No"],
            ["m3", "", "Yes", "", "Yes"],
            ["m4", "004", "Maybe", "Maybe", "Maybe"],
            ["m5", "005", "Unexpected", "Unexpected", "Unexpected"],
        ],
        "D3": [
            [" Alpha U ", "01", "Yes", "Yes", "Yes"],
            ["alpha u", "02", "No", "No", "Yes"],
            ["Beta U", "03", "No", "No", "No"],
        ],
    }
    specs = {}
    for name, rows in records.items():
        metadata = ["metadata" if name == "D5" else "institution", "respondent_id"]
        with (source / f"{name}.csv").open("w", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle)
            writer.writerow(metadata + items)
            writer.writerows(rows)
        specs[name] = {
            "source_key": name.lower() + "_raw",
            "metadata_columns": metadata,
            "identifier_columns": ["respondent_id"],
            "categorical_columns": metadata[:1],
            "survey_items": items.copy(),
            "allowed_responses": ["No", "Maybe", "Yes"],
            "source_metadata": {
                "url": "https://example.org/synthetic",
                "published_file_sha256": None,
            },
            "reference_claims": [
                {
                    "metric": "raw_rows",
                    "value": len(rows) + 1,
                    "source": "synthetic source claim",
                    "interpretation": "Review the count difference.",
                }
            ],
        }
    specs["D3"]["institution_column"] = "institution"
    specs["D5"]["prior_straight_line_count"] = 99
    specs["D5"]["prior_straight_line_source"] = "synthetic historical claim"
    (source / "dictionary.md").write_text("# D1 synthetic dictionary\n", encoding="utf-8")
    config = {
        "project": {"drive_root_env": "MP1_SYNTHETIC_ROOT"},
        "data": {"d5_raw": "D5.csv", "d3_raw": "D3.csv", "data_dictionary": "dictionary.md"},
        "outputs": {"root": "outputs"},
        "integrity": {"csv_encoding": "utf-8-sig", "missing_tokens": [], "datasets": specs},
        "response_quality": {"private_flags": "data/processed/response_quality_flags.csv"},
    }
    config_path = root / "config/analysis.yaml"
    config_path.write_text(yaml.safe_dump(config, sort_keys=False), encoding="utf-8")
    monkeypatch.setenv("MP1_SYNTHETIC_ROOT", str(source))
    return config_path
