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

Active work package: E. Publication lock and reproducibility only.
Canonical Research Control was reread completely on 2026-09-28 during controlled E recovery.
Accepted baseline: `56b335c705ef15d5a261865382dd79991d2a93a2` on main.
A, B and D are accepted. C is frozen as the accepted predictive-feasibility blocker
under the pre-specified design. Historical pending-review instructions in A-D
records are superseded by the canonical acceptance record, not new analyses.

Before E work, read all relevant accepted documentation, code, aggregate outputs,
provenance manifests, tests and CI. Audit Manuscript V3 against that evidence.
Freeze the retained results; map each finding to exact accepted evidence; prepare
publication tables, figures, limitations, contribution and reproducibility text.
Verify a clean checkout with synthetic tests and no private research data.

Preserve these boundaries:

- A source-documentation discrepancies remain external limitations.
- B does not validate five subscales or natural psychological types. k=2 partitions
  are descriptive and D5 repeated-record concentration must remain explicit.
- C produced no classifier comparison, SHAP, LIME, calibration or defensible
  generalizable predictive-performance claim. Do not fit those models.
- D3 CGPA is a coarse self-reported ordinal outcome with a very small, inconclusive
  association. Conditional uncertainty does not establish respondent independence.
- U.S.-Indonesia diagnostics do not establish Bangladesh latent equivalence,
  replicated profiles, cultural effects or objective performance effects.
- Do not add Vietnam, models, constructs, research questions or exploratory analyses.

E may regenerate presentations of accepted aggregates and verify provenance.
Do not change accepted scientific files unless an actual reproducibility defect
is demonstrated and explicitly documented. Produce one complete safely applicable
Colab delivery. Astra must not commit or push. The user reviews, applies, accepts,
updates Research Control and commits manually. Journal shortlisting remains
closed until the E evidence package is accepted.

## Recovery assessment

The retained-result lock is ready for manual acceptance with the documented nonselected B
replay limitation. Read docs/publication_recovery_inventory.md and
docs/publication_discrepancy_register.md. Preserve recovered source_replay.json as FAIL for
the complete grid; the separate recovery check verifies its 247-cell boundary and unchanged
selection ranks/screens/choices. Do not rerun A-D merely to repeat surviving verification.
No accepted k=2 defect is demonstrated. Canonical E remains active until manual acceptance.
