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

Work Packages A and B are accepted. Their source documentation and measurement limitations remain
recorded without invented corrections. The accepted B entry points are:

- `scripts/psychometrics_analysis.py`
- `scripts/clustering_analysis.py`

Read `docs/measurement_cluster_structure.md` for the method, evidence, limitations, and review
requirements. The accepted input and quality-flag contract remains in `docs/data_integrity.md`.

Run from the repository root after setting the configured Drive environment variable:

```bash
PYTHONPATH=src python scripts/psychometrics_analysis.py --config config/analysis.yaml
PYTHONPATH=src python scripts/clustering_analysis.py --config config/analysis.yaml
```

Measurement must run first. Both full and quality-sensitivity analyses are explicit. Accepted
quality flags are read from `data/processed/response_quality_flags.csv`; if missing in a fresh clone,
regenerate them with `scripts/response_quality.py`. No raw records are changed. Cluster memberships
remain private under `data/interim/work_package_b/`. Review aggregates before committing them.
The active work is C. Its target and leakage audit reproduces B exactly, but withholds predictive
modeling and explainability because the repeated-record structure prevents a defensible comparison
under the planned held-out design. Read `docs/predictive_feasibility.md`. The retained C alternative
describes metadata marginals and the evaluation blocker. No D or E analysis has begun.

For C, read the accepted B outputs without rerunning or modifying B. Run:

```bash
PYTHONPATH=src python scripts/predictive_audit.py --config config/analysis.yaml --audit-config config/work_package_c.yaml
```

Optional `--d5-raw`, `--quality-flags`, and `--accepted-memberships` arguments accept existing input
paths. Only D5 and its accepted flags are required. Original B memberships are additionally checked
when available. C aggregates are under `outputs/modeling/work_package_c/`; record-level target and
diagnostic split files are ignored under `data/interim/work_package_c/`. A successful audit command
can report a scientific blocker. It does not authorize or train classifiers.

## Quality standard

- No hard-coded local or Colab paths.
- No silent row deletion or recoding.
- Explicit random seeds.
- Machine-readable outputs for important results.
- Focused tests for reusable analytical logic.
- Professional comments that explain reasoning rather than obvious syntax.
- No em dash characters in source or project documentation.
- Keep the model set and analyses within the approved research scope.
