# Exact Work Package E outputs

The complete path-and-hash inventory is `bundle_manifest.json` at the ZIP root. Scientific
source inputs are never included. Existing accepted aggregate outputs remain in the baseline
checkout, identified by `config/publication_freeze.json`.

| Path | Purpose |
|---|---|
| `config/publication_freeze.json` | Baseline, canonical authority, 123 immutable accepted files, 60 accepted outputs, five private input hashes |
| `config/publication_claims.json` | 31 retained findings, exact accepted selectors and interpretation boundaries |
| `config/manuscript_v3_audit.json` | Complete 171-location review specification and source hashes |
| `outputs/publication/work_package_e/retained_results_master.csv` | Master finding register with display evidence and manuscript placement |
| `outputs/publication/work_package_e/manuscript_evidence_map.md` | Readable evidence map |
| `outputs/publication/work_package_e/manuscript_evidence_map.json` | Exact source paths, SHA-256, selectors and resolved evidence |
| `outputs/publication/work_package_e/complete_evidence_register.csv` | All 4,515 accepted CSV data rows, exact strings and claim links |
| `outputs/publication/work_package_e/accepted_output_inventory.csv` | All 60 accepted output files and hashes |
| `outputs/publication/work_package_e/aggregate_consistency.json` | Independent aggregate reconciliation and freeze checks |
| `outputs/publication/work_package_e/table_manifest.json` | Table titles, notes and claim IDs |
| `outputs/publication/work_package_e/figure_manifest.json` | Figure captions, formats and claim IDs |
| `outputs/publication/work_package_e/figure_captions.md` | Manuscript-ready figure captions |
| `outputs/publication/work_package_e/render_manifest.json` | Hashes of every generated publication file |
| `outputs/publication/manuscript_audit/manuscript_v3_disposition.csv` | 156 paragraph, seven table and eight figure decisions |
| `outputs/publication/manuscript_audit/manuscript_v3_audit.md` | Readable complete V3 audit |
| `outputs/publication/validation/public_checks.json` | Current-worktree public validation, installed versions and test summary |
| `outputs/publication/validation/clean_checkout.json` | Fresh clone, fresh Python/R dependency installation and public validation |
| `outputs/publication/validation/source_replay.json` | Preserved recovered source comparisons; historical complete-grid FAIL |
| `outputs/publication/validation/replay_discrepancies.csv` | Preserved exact 247 nonselected-candidate cells; no private records |
| `docs/manuscript_replacement_text.md` | Exact contribution, limitations, abstract, outcome paragraph and conclusion |
| `docs/publication_reproducibility.md` | Provenance, environment and inference limits |
| `docs/publication_terminology.md` | Final terminology contract |
| `docs/work_package_e_validation.md` | Fresh verification and qualified closure assessment |
| `docs/work_package_e_review.md` | Advisor review and acceptance checklist |
| `docs/work_package_e_colab.md` | Three exact Colab execution cells, required inputs and generated outputs |
| `docs/research_control_e_update.md` | Exact proposed canonical update; not applied automatically |

## Statistical table files

Under `outputs/publication/work_package_e/tables/`:

- `T01`, `T02`, `T03`, `T04`, `T05`, `T06a`, `T06b`, `T07`, `T08`, each with `.csv` and `.tex`.
- `statistical_tables.pdf`: nine vector pages with embedded fonts.
- `statistical_tables.html`: printable and editable table presentation.

## Figure files

Under `outputs/publication/work_package_e/figures/`, each stem has `.pdf`, `.svg`, `.png`
and `_data.csv`:

- `F01_measurement`
- `F02_candidate_partitions`
- `F03_descriptive_profiles`
- `F04_cgpa`
- `F05_observed_associations`

The main publication renderer creates exactly 50 files. V3 rendering adds two files. Verification
reports are separate so test/runtime metadata cannot silently change the scientific rendering
manifest. CSV/JSON retain exact accepted precision; printed statistical tables use four decimals.

Private source replay creates logs, copied immutable source mounts, reconstructed memberships
and a disposable checkout under the user-selected private work directory. These are diagnostic
working files, not publication outputs, and must never be committed or bundled.

## Recovery additions

| Path | Purpose |
|---|---|
| `config/publication_recovery.json` | Recovered archive identity and preserved report hashes |
| `src/mp1/recovery.py` | Checks all discrepancy cells and aggregate selection consequences without source fits |
| `tests/test_publication_recovery.py` | Six tests for the bounded exception and rejected retained-evidence changes |
| `docs/publication_discrepancy_register.md` | Exact unresolved differences, bounds and publication policy |
| `docs/publication_recovery_inventory.md` | What survived, what was reconstructed and what remains unavailable |
| `environment/recovery_build_dependencies.json` | Current recovery compiler/build provenance, not original dependency evidence |
| `outputs/publication/validation/recovery_discrepancy_check.json` | Fresh machine-readable boundary assessment |
| `outputs/publication/validation/recovered_run/` | Byte-preserved earlier checks and original hold assessment |
| ZIP root `BASELINE_MANIFEST.csv` | Complete tracked baseline inventory |
| ZIP root `CHANGED_FILES.csv` | Every applied path, before/after hash and recovery disposition |
| ZIP root `DELIVERY_VERIFICATION.json` | Fresh bundle, patch, rejection and preservation checks |
| ZIP root `FINAL_INSPECTION.json` | Per-artifact parse/content inspection and visual review record |

No source data or runtime binaries are shipped. `accepted_evidence/` at the ZIP root is a
read-only copy of all 60 accepted outputs for review; it is not applied as an overlay.
