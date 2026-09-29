# Work Package E: advisor review package

**Scope:** publication lock and reproducibility of accepted A-D evidence only. No new empirical
research question, model, construct or dataset is introduced. Nothing is committed or pushed
by Astra. Journal selection remains closed until E acceptance.

The canonical Research Control was read completely before repository work. Baseline and remote
main were verified as `56b335c705ef15d5a261865382dd79991d2a93a2`. README and ASTRA_HANDOFF were
reconciled to D accepted / E active before building publication artifacts.

## Read in this order

1. `docs/work_package_e_validation.md`: actual acceptance status, demonstrated discrepancies,
   completed verification and limits. A synthetic-test pass alone cannot close E.
2. `outputs/publication/work_package_e/retained_results_master.csv`: 31 retained findings,
   display statistics, interpretation limits and manuscript placement.
3. `outputs/publication/work_package_e/manuscript_evidence_map.md` and `.json`: readable claim
   decisions and exact machine-readable source selectors, values and file hashes.
4. `outputs/publication/work_package_e/complete_evidence_register.csv`: all 4,515 accepted
   CSV rows, without selection of only favorable diagnostics. The inventory freezes 60 outputs.
5. `outputs/publication/work_package_e/tables/statistical_tables.pdf` or `.html`: T01-T08,
   with T06 split into effect and uncertainty panels. Each table also has full-precision CSV
   and editable LaTeX. No old V3 performance/explanation table is retained.
6. `outputs/publication/work_package_e/figures/`: F01 measurement, F02 all candidate partitions,
   F03 descriptive item profiles, F04 CGPA distributions/conditional uncertainty and F05 bounded
   observed-item associations. All five have vector PDF/SVG, 600-DPI PNG and exact plot-data CSV.
   Captions and claim IDs are in `figure_manifest.json` and `figure_captions.md`.
7. `outputs/publication/manuscript_audit/`: complete V3 paragraph/table/figure dispositions,
   anchored to the original DOCX hash. `docs/manuscript_replacement_text.md` supplies the exact
   title, abstract, contribution, outcome paragraph, limitations and conclusion for review.
8. `docs/publication_terminology.md`, `docs/publication_reproducibility.md`, `environment/`
   and `docs/work_package_e_colab.md`: terminology, provenance and the reproducible delivery.

All underlying accepted files remain unchanged. E files are presentations and verification
records, not additional accepted scientific findings. Historical status fields inside A-D
manifests are superseded by the canonical acceptance record, without rewriting those artifacts.

## Manual review before any acceptance or commit

- Confirm that canonical control still designates E and the expected accepted baseline.
- Review every retained claim against its accepted output and prohibited-overclaim field.
- Inspect the full all-k candidate diagnostics and repeated-record concentration, including
  200/207 D5_P2 primary records and 200/205 in quality sensitivity.
- Check that no figure or paragraph implies five validated subscales, four natural types,
  respondent independence, causal effects or generalizable predictive performance.
- Check that the V3 classifier, precision-recall, SHAP, LIME, local-person explanation and
  counterfactual material is removed, rather than cosmetically relabeled.
- Confirm D3 uses nominal profiles and literal CGPA bands; the exact 2.50 boundary is unknown.
  Review all three outcome variants and all nine conditional intervals, with assumptions.
- Confirm external findings remain within-country observed-item/compatibility evidence;
  no Bangladesh anchors, latent equivalence, country-difference test or profile replication.
- Read the complete limitations and exact contribution. Cite the D5 companion paper and
  position beyond its regression study; do not copy its coefficients as MP1 results.
- Inspect all nine table pages and all five figure PDF/SVG files at intended reproduction size.
  Exact data are in the CSV/JSON companions; no individual-case images are distributed.
- Verify dependency installation, Ruff lint/format, all 125 synthetic tests, aggregate checks,
  clean-checkout render comparison and source immutability from the supplied reports.
- Review all 247 recorded nonselected B differences and their exact bounds. The historical
  complete-grid replay remains FAIL. Verify the fresh boundary report and unchanged retained
  rows, ranks, screens and decisions; accept the explicit publication limitation only if agreed.
- Inspect `git diff --stat`, `git diff --check`, every proposed file and the bundle inventory.
  Do not stage raw/interim/processed data, private logs, V3, source workbooks or runtime folders.
- Keep E open if any required gate is unresolved. A later acceptance requires the advisor's
  explicit review of the reproducibility record. Do not begin journal shortlisting now.

## Acceptance decision rule

Under the user's 2026-09-28 instruction, a bounded, fully disclosed mismatch in nonselected B
candidates alone does not reopen accepted B or prevent retained-result publication lock.
This delivery meets that qualified policy if the supplied fresh public and package checks pass
and the reviewer accepts the disclosed limitation. It does not claim full candidate-grid replay
success. Original runtime diagnosis remains unresolved, and the preserved report retains FAIL.

E can close after explicit manual acceptance. Until then canonical status remains D accepted /
E active. No code marks E accepted, edits Research Control, commits or pushes. Correcting V3
with the supplied disposition and replacement material remains a pre-submission task.
