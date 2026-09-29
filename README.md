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

## Work Package E: publication lock

D is accepted at `56b335c705ef15d5a261865382dd79991d2a93a2`; E is active.
Use `docs/work_package_e_colab.md` for the complete Colab delivery and exact inputs.
The E environment is `environment/requirements.lock` plus `environment/R-lock.json`.
Use the hash-checked installation instructions, not a fresh resolution of broad requirements.

Start with `docs/work_package_e_review.md` and the retained-results master table in
`outputs/publication/work_package_e/`. The evidence map references only frozen accepted A-D
outputs. `docs/manuscript_replacement_text.md` and the complete V3 disposition register define
what the manuscript may retain. Publication rendering uses aggregate outputs and no private data.
Recovered source replay is preserved with its complete-grid FAIL and a 247-cell nonselected-B
discrepancy register. Fresh aggregate checks confirm unchanged retained k=2 evidence and
selection decisions. E can close with that disclosed limitation after manual acceptance.
See `docs/publication_discrepancy_register.md` and `docs/work_package_e_validation.md`.
The standard recovery commands do not rerun A-D or replace accepted results.

## Data policy

Raw, interim, and processed datasets are never committed to GitHub.

Expected raw file locations are defined in `config/analysis.yaml`.

All transformations must be reproducible from immutable raw inputs.

## Accepted entry points (historical methods; frozen)

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
```

C aggregates are under outputs/modeling/work_package_c/; record-level target and diagnostic split files remain ignored under data/interim/work_package_c/. A successful audit can report a scientific blocker. It does not authorize classifier fitting.

Work Package D is completed and accepted at
`56b335c705ef15d5a261865382dd79991d2a93a2`. Work Package E is active:
publication lock and reproducibility only. Read
`docs/outcome_cross_cultural_validation.md` for the CGPA eligibility audit, ordinal outcome
comparisons, quality and repeated-record sensitivity, complete compatibility audit and external
measurement-testing boundary. The methods preserve A/B/C and do not resume predictive modeling.

D entry points are:

- `scripts/outcome_validation.py`
- `scripts/external_validation.py`
- `scripts/verify_work_package_d.py`

Use `docs/work_package_d_colab.md` for exact execution instructions,
`docs/work_package_d_outputs.md` for the output inventory and
`docs/work_package_d_review.md` for scientific review and proposed project updates.
Only D aggregate outputs are added under the existing outcome and external validation folders.
Private D artifacts stay under ignored `data/interim/work_package_d/`. No commit, push or
Research Control edit was part of the historical D delivery. Its pending-review wording is
superseded by canonical Research Control acceptance on 2026-09-27. E preserves accepted A-D
results and does not authorize new empirical questions or journal shortlisting.

## Quality standard

- No hard-coded local or Colab paths.
- No silent row deletion or recoding.
- Explicit random seeds.
- Machine-readable outputs for important results.
- Focused tests for reusable analytical logic.
- Professional comments that explain reasoning rather than obvious syntax.
- No em dash characters in source or project documentation.
- Keep the model set and analyses within the approved research scope.
