# Work Package E validation and closure assessment

The retained-result publication lock can close with the documented nonselected B limitation
after manual acceptance. Canonical status remains D accepted / E active until the user records
acceptance. No accepted A-D file or Research Control entry was changed.

The old blanket hold based solely on nonselected differences is superseded by the explicit
2026-09-28 recovery acceptance rule. This changes E's assessment, not B's results or tolerances.
The recovered full-grid source-replay report remains byte-identical and retains FAIL.
`docs/publication_discrepancy_register.md` gives the exact limitation and its publication treatment.

## Verification

| Check | Evidence origin and outcome |
|---|---|
| Baseline/frozen evidence | Fresh remote check; 123 frozen files and 60 accepted outputs match hashes and manifest links |
| Source replay | Recovered report: A quality, B measurement, C feasibility, D3 outcome and D external pass stated checks; full B candidate grid fails |
| Selected B rows | No k=2 mismatches in any compared B table at declared tolerance |
| Discrepancy bounds | Fresh cross-check of all 247 cells in six files, exact accepted row identities and signed differences |
| Selection consequences | Fresh aggregate recheck: every candidate rank, mean rank, screen and k=2 choice unchanged in six dataset/sample comparisons |
| Aggregate statistics | All sample/centroid/concentration/overlap identities; three independent D3 rank/effect calculations; four-test Holm correction pass |
| Evidence map | 31 retained findings; all 4,515 accepted CSV rows; exact source selectors and hashes |
| Manuscript | Exact current V3 hash, 156 paragraphs, seven tables and eight image anchors matched |
| Current public suite | 125 synthetic tests; Ruff lint/format; dependency checks; 50 byte-identical publication artifacts |
| Clean checkout | Fresh hash-locked Python/R packages, no private research data, full public verification |
| Delivery | Preflight, file/patch equivalence, collision/dirty-tree/hash rejection, and accepted-file preservation checked |

Current machine-readable reports are `public_checks.json`, `clean_checkout.json`,
`recovery_discrepancy_check.json` under `outputs/publication/validation/`, plus delivery-root
inspection and package-verification files. Earlier 119-test reports and their original hold
assessment remain explicitly archived under `validation/recovered_run/`.
The 125 tests comprise 112 accepted tests, seven recovered E tests and six recovery tests.

## Precision and unresolved issues

Frozen evidence uses exact SHA-256 identity. Counts, labels and scientific decisions are exact.
Noniterative numeric checks use absolute tolerance 1e-10; iterative polychoric/factor/ULS/WLSMV
checks use 1e-5. The recovered report records a historical correction to classify optimizer-derived
correlations/eigenvalues under iterative tolerance. Counts and resampling thresholds were not relaxed.

The 247 cells include 48 repeated metric presentations in the selection table. D3 full k=6
has counts 247/142 versus 246/143 in clusters 1/6. Mean ARI differs by at most 0.0089196801;
Jaccard 10th percentile by at most 0.0721236559. No categorical decision changes. The cause
remains unknown because the original complete numerical environment was not recorded.
Private replay logs and full replayed aggregates did not survive. Current recovery verifies
the detailed preserved comparison; it does not claim a new A-D source run or universal identity
across platforms. All limitations remain explicit in manuscript-facing material.

## Publication and preservation

All nine final table pages and five final figures were visually inspected. PDF/SVG are vector;
PNGs are 600 DPI. F02 and B07/B09 disclose candidate replay differences. D5 concentration is
adjacent to profile findings. D3 interval/rank displays state conditional inference and
unverified respondent independence. Every numeric display derives from accepted aggregates.

V3 is unchanged. Its complete disposition and replacement title, abstract, contribution,
outcome paragraph, limitations and conclusion are supplied. The D5 companion paper supplies
context only, never MP1 results. Integrating those revisions before submission is still needed;
this delivery does not pretend the original manuscript has already been corrected.

No source, accepted output, analytical configuration, seed or target changed. No classifier,
commit, push, live Research Control edit, journal shortlist or external message was performed.
GitHub Actions was not triggered on uncommitted work; equivalent commands ran in a clean clone.

Minimal remaining formal action: review the qualified lock and checklist, then record acceptance
if accepted. Historical runtime diagnosis is needed only before claiming exact reproduction
of the complete nonselected grid. It is not a reason to reopen or replace accepted A-D here.
