# MP1 Journal Research

This repository contains the independently implemented analysis pipeline for the MP1 journal project.

## Canonical project control

Read the Research Control document before changing analysis code:

https://docs.google.com/document/d/19i3A-Vy6GnIYNsgZB8exYQJRn2JdCUhFCliUaJmze_o/edit

Fresh Google Drive workspace:

https://drive.google.com/drive/folders/1Q9g0dQAupgGQO7kd3KuXkqz89z3OSeYy

The Research Control document defines scope, datasets, methodological commitments, current status, decision rules, and progress recording. Do not duplicate that content in this README.

## Repository role

GitHub is the source of truth for code, configuration, tests, and reviewed small outputs.

Google Drive is the source of truth for raw datasets, advisor materials, and publication handoff files.

Colab is the execution environment. Code is reviewed locally before the user commits and pushes it manually.

## Setup in Colab

1. Mount Google Drive.
2. Clone this repository.
3. Set `MP1_DRIVE_ROOT` to the mounted `MP1 Journal Research` folder.
4. Install dependencies with `pip install -r requirements.txt`.
5. Run `pytest -q`.
6. Run `ruff check .`.
7. Run `ruff format --check .`.

Do not begin real-data analysis until the repository checks pass.

## Data policy

Raw, interim, and processed datasets are never committed to GitHub.

Expected raw file locations are defined in `config/analysis.yaml`.

All transformations must be reproducible from immutable raw inputs.

## Active analysis

The active work is data provenance and response quality:

- `scripts/provenance_audit.py`
- `scripts/response_quality.py`

See `docs/data_integrity.md` for the input contract, output definitions, and review requirements.

Run from the repository root after setting the configured Drive environment variable:

```bash
PYTHONPATH=src python scripts/provenance_audit.py --config config/analysis.yaml
PYTHONPATH=src python scripts/response_quality.py --config config/analysis.yaml
```

Both entry points retain every source record. The response-quality sensitivity indicator is written
to `data/processed/response_quality_flags.csv`, which is excluded from Git. Aggregate outputs still
require review before they are committed. An audit report does not resolve a source discrepancy
merely by recording it.

## Quality standard

- No hard-coded local or Colab paths.
- No silent row deletion or recoding.
- Explicit random seeds.
- Machine-readable outputs for important results.
- Focused tests for reusable analytical logic.
- Professional comments that explain reasoning rather than obvious syntax.
- No em dash characters in source or project documentation.
- Keep the model set and analyses within the approved research scope.
