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
The active work is Work Package D: outcome and cross-cultural validation.
Research Control accepted A and B on 2026-09-26. C is frozen under the current pre-specified design as a predictive-feasibility result. The accepted D5 target was reconstructed exactly, all 25 target-defining survey items were excluded as direct leakage, and predictive fitting was withheld because the released repeated-record structure makes the planned held-out comparison non-defensible. No classifier, SHAP, LIME, calibration, or predictive-performance claim was produced. Do not bypass that gate, remove repeated records, redefine the target, or search for a favorable split. C may be reopened only with explicit approval for a justified revised design or additional data.
Before editing or accepting the D implementation, read:
- the canonical Research Control document in full
- docs/data_integrity.md
- docs/measurement_cluster_structure.md
- docs/predictive_feasibility.md
- the accepted aggregate outputs for A, B, and C
- the D3 raw source and its accepted quality flags
- the U.S.-Indonesia source workbook and codebook in Google Drive
D has two bounded analytical questions.
1. D3 academic outcome validation: evaluate profile-level Current CGPA differences without assuming an ordinal trend. Use Kruskal-Wallis, an appropriate effect size, justified multiplicity-corrected pairwise post hoc comparisons, and profile-level distributions. The accepted two-profile solution has only one contrast, so no separate post hoc family is required. Preserve accepted D3 clustering logic and do not invent institution mappings or respondent independence.
2. Cross-cultural compatibility: audit whether the U.S.-Indonesia measures are meaningfully comparable to the accepted constructs before writing pooled or harmonized analysis. Do not force raw-score equivalence. If construct compatibility is insufficient, use separate country-specific analyses or an explicitly justified standardized comparison. The Vietnam dataset remains fallback only unless Research Control is amended.
Do not begin publication-lock work from E. Any D method that changes accepted A/B/C preprocessing, profile definitions, or source interpretation requires a recorded methodological decision first.

## D implementation awaiting review

The bounded D analysis is implemented from baseline
`dad222a9a0143887e7e25a72e656ec21d0ebc253`; scientific acceptance is pending.
Read `docs/outcome_cross_cultural_validation.md`, `docs/work_package_d_colab.md`,
`docs/work_package_d_outputs.md`, `docs/work_package_d_validation.md` and
`docs/work_package_d_review.md` before changing this work.

D reproduces the accepted D3 partitions and finds a very small, inconclusive CGPA rank
association. Quality sensitivity and conditional repeated-record uncertainty retain that
conclusion. The external audit finds no identical Bangladesh anchors. GAID configural fit and
CT/TP category-support limits prevent a defensible latent country comparison. Country-specific
observed-item analyses remain exploratory. These limitations do not authorize revised A/B/C
methods, category merging, item removal, Vietnam use, predictive fitting or E work.

R/lavaan/semTools provide only the ordinal measurement engine under Python orchestration;
all other D analysis and source safeguards are Python. CI runs the same synthetic checks.
The proposed Research Control append is a local review document, not a remote edit. No commit
or push has been performed as part of this delivery.
