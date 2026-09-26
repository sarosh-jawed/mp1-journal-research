# Astra Handoff

Before writing code, read the canonical Research Control document in full:

https://docs.google.com/document/d/19i3A-Vy6GnIYNsgZB8exYQJRn2JdCUhFCliUaJmze_o/edit

Fresh Google Drive workspace:

https://drive.google.com/drive/folders/1Q9g0dQAupgGQO7kd3KuXkqz89z3OSeYy

## Operating rule

Work only on the active work package recorded in the Research Control document.

Do not use the legacy V3 scripts as a coding template. Implement independently from the raw data, codebook, advisor materials, and approved methodology. Legacy outputs may be compared only after the independent result exists.

## Required response format for analytical work

For every code delivery:

1. State the exact scientific question being addressed.
2. State the input files and required columns.
3. Explain the method in plain language before showing code.
4. Provide complete production-quality code for the intended files.
5. Provide exact Colab instructions for running it.
6. State the expected output files.
7. Provide numerical and structural checks that confirm the run is valid.
8. State what should be inspected manually before commit.
9. Provide a professional commit message that describes the actual change.
10. Provide the exact Research Control progress update to append after successful verification.

## Coding constraints

- No hard-coded absolute paths.
- No silent filtering, row deletion, recoding, or imputation.
- Never modify raw source files.
- Use explicit random seeds.
- Reusable analytical logic belongs in `src/mp1`.
- Files in `scripts` remain thin entry points.
- Save meaningful results as CSV or JSON rather than console-only output.
- Write figures to the appropriate output directory.
- Use concise comments only where reasoning is not obvious.
- Do not use em dash characters in code, comments, docstrings, commit messages, or project documentation.
- Avoid words such as batch, step, and task in commit messages and code comments.
- Do not add models, datasets, or analyses outside the approved scope without first documenting a methodological reason in Research Control.

## Current starting point

The active work is data integrity and response quality.

The first analytical files are:

- `scripts/provenance_audit.py`
- `scripts/response_quality.py`

Do not proceed to psychometrics or clustering until the provenance and response-quality outputs are verified and the Research Control document is updated.
