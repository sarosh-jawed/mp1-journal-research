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
The accepted C work is complete under the pre-specified design. Its target and leakage audit reproduces B exactly and documents why predictive modeling and explainability were withheld: the D5 smaller class has 207 records, including one identical released full-record pattern of 200 records, and 40 of 41 diagnostic minority test records share an exact full-record pattern with training data. Read `docs/predictive_feasibility.md`. No classifier performance, SHAP, LIME, calibration, or generalizable prediction claims are authorized. C may be reopened only with explicit approval for a justified revised design or additional data.

For reproducibility, the accepted C entry point remains:

```bash
PYTHONPATH=src python scripts/predictive_audit.py --config config/analysis.yaml --audit-config config/work_package_c.yaml
C aggregates are under outputs/modeling/work_package_c/; record-level target and diagnostic split files remain ignored under data/interim/work_package_c/. A successful audit can report a scientific blocker. It does not authorize classifier fitting.
The active work is D: outcome and cross-cultural validation. D should analyze D3 CGPA profile differences with an appropriate nonparametric omnibus test, effect size, corrected pairwise comparisons, and profile-level distributions. It must also audit the U.S.-Indonesia codebook and construct compatibility before any cross-country analysis. Do not force raw-score harmonization, pooling, or profile equivalence. If direct comparability is not defensible, retain country-specific or appropriately standardized analyses. D implementation has not yet been added; read the canonical Research Control before writing it.
## Quality standard

- No hard-coded local or Colab paths.
- No silent row deletion or recoding.
- Explicit random seeds.
- Machine-readable outputs for important results.
- Focused tests for reusable analytical logic.
- Professional comments that explain reasoning rather than obvious syntax.
- No em dash characters in source or project documentation.
- Keep the model set and analyses within the approved research scope.
