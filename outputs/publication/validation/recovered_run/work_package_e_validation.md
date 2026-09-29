# Work Package E validation and acceptance status

**WORK PACKAGE E MUST REMAIN OPEN.**

The publication evidence package is prepared, but scientific source replay does not reproduce
all frozen B candidate-partition and resampling outputs under the reconstructed environment.
The discrepancy is demonstrated, bounded and preserved. It does not justify replacing accepted
outputs, changing the research narrative, fitting new models or reopening C.

## Demonstrated blocker

`outputs/publication/validation/source_replay.json` records every comparison. The per-cell
register is `replay_discrepancies.csv`. It contains **247 differing aggregate table cells across
six B CSV files**, including duplicate presentation of metrics in the selection table. These
are not 247 independent findings. All discrepancies concern **nonselected k=3 to 6 candidates**.
Every selected k=2 value, selected profile size, item centroid, concentration statistic,
quality-sensitivity comparison, stability statistic and selection decision agrees within the
strict 1e-10 noniterative numeric check. No categorical scientific decision changes.

A concrete discrete mismatch occurs in the D3 full-record k=6 candidate:

| Candidate cluster | Accepted count | Replayed count |
|---|---:|---:|
| D3 full, k=6, cluster 1 | 247 | 246 |
| D3 full, k=6, cluster 6 | 142 | 143 |

The affected files are `cluster_centroids.csv`, `cluster_metrics.csv`,
`cluster_selection.csv`, `cluster_sizes.csv`, `cluster_stability.csv` and
`quality_sensitivity.csv` under `outputs/clustering/`. The maximum absolute differences include
0.0089196801 in mean ARI and 0.0721236559 in a cluster Jaccard 10th percentile. The complete
accepted and replayed values, data-row numbers, dataset/sample/k/item identifiers and signed
differences are provided; none is silently replaced or rounded away.

Recorded scientific package versions, seeds, raw hashes and accepted code/configuration match.
The original B Python build, complete transitive dependencies, BLAS/OpenMP configuration and
thread settings were not recorded. E uses a transparent reconstructed lock and fixed single
thread settings. Unrecorded numerical-runtime behavior is a possible cause, not a proven
explanation. No parameter, seed, k, item, record, distance, target or model is changed in E.
No environment search was performed to select favorable scientific results.

This blocks a claim that the **complete** accepted A-D aggregate set has passed source
reproduction. F02 and the all-k diagnostic supplement remain faithful renderings of accepted
outputs, but publication lock cannot be signed off merely because the primary k=2 conclusion
survives. The necessary next action is narrowly bounded reproducibility diagnosis: recover the
accepted B runtime/session details or establish and explicitly review the exact numerical
mechanism. If byte/numeric identity cannot be recovered, Dr. Taufique must explicitly adjudicate
an honest publication reproducibility policy. That decision is not supplied by Astra and is
not permission for new empirical research.

## Completed checks

- The entire canonical Research Control was reread before repository work. Current main and
  the accepted baseline were verified. README and ASTRA_HANDOFF now state D accepted / E active.
- All **123 frozen accepted files** and the complete **60-output** set retain their SHA-256
  bytes. All accepted manifest links verify. No accepted scientific file is edited.
- The map contains **31 retained findings** and the row register preserves all **4,515 accepted
  CSV data rows**. Every empirical source selector resolves only to the accepted-output allowlist.
- All aggregate files parse. Item totals, all-k sizes, all 5,440 cumulative centroid
  probabilities, pooled item distributions, concentration accounting, C split-overlap fractions
  and group-allocation obstruction reconcile. D rank statistics, Cliff delta, H/(N-1) and
  Holm-adjusted p values are independently recomputed from aggregate tables.
- Private-source replay: A response-quality flags match the accepted SHA-256 exactly;
  B measurement and all its scientific decisions pass the iterative tolerance; C and D3
  outcome replay pass; the external D replay passes, including the recorded R/lavaan/semTools
  versions. No performance or explanation model is fitted.
- All five supplied input files, including the two raw CSVs, external workbook, dictionary and
  V3, have identical SHA-256 before and after replay. Caller accepted files remain unchanged.
  The original membership archive is unavailable, so its absence is preserved honestly; C/D
  use their accepted centroid-reconstruction contract.
- **119 synthetic tests pass**, including the R ordinal-identification/support tests and seven
  new evidence-boundary tests. Ruff lint, Ruff format and dependency compatibility checks pass.
- The public renderer reproduces **all 50 publication files byte for byte** under the lock.
  The V3 disposition register also reproduces without the private manuscript in CI.
- Fresh-checkout verification installs the hash-locked Python environment in an empty virtual
  environment and installs the R packages freshly against the separately source-built, verified
  R 4.6.1 runtime. It runs every synthetic/quality check without private research files and
  reproduces the public rendering. Exact machine-readable evidence is in `clean_checkout.json`.
- CI uses only code, accepted aggregates and synthetic fixtures. No Drive credentials, private
  research-data download or raw-data requirement exists. No GitHub Actions run is claimed for
  these uncommitted changes; the equivalent commands were run locally in a clean checkout.
- Nine table PDF pages and five publication figures were visually inspected. Embedded fonts
  corrected an initial PDF font-substitution problem. Vector PDF/SVG and 600-DPI PNG companions
  retain identical plotted values. V3's eight original embedded images were inspected and are
  excluded from the delivery, especially the individual-case explanation graphics.
- The V3 audit covers all **156 paragraphs, seven tables and eight figures** using exact source
  hashes and document-order image anchors. The original DOCX is unchanged. Replacement text
  removes the unsupported narrative and cites the D5 companion paper without adding its results.

## Corrections during E verification

These were defects in new E packaging/verification code, not changes to A-D science:

- A source mount initially used symlinks whose resolved parent contained the disposable checkout;
  the accepted source-directory guard correctly rejected it. Replay now copies immutable bytes
  into a private source mount and requires a work directory outside the input directory.
- Initial tolerance classification wrongly put optimizer-derived polychorics and eigenvalues
  under exact-arithmetic tolerance. The largest polychoric discrepancy was 4.19e-8, smaller than
  the accepted 1e-7 optimizer stopping tolerance. These outputs now use the declared iterative
  1e-5 tolerance. Counts, clustering resampling statistics and decisions were not relaxed.
- Recomputed B memberships initially made C/D report an original-membership check that was absent
  at acceptance. They are now preserved separately as reconstructed private files and withheld
  from that optional check. They are not mislabeled as the original B membership archive.
- PDF creation metadata differed between direct function and CLI calls. A fixed source epoch
  now applies in both paths; publication bytes reproduce exactly. No statistical value changed.
- V3 image filenames are hashes, not figure numbers. The audit now follows document relationship
  order and verifies each image hash against its actual caption-number position.

## Preservation and action boundary

No raw/interim/processed/private respondent-level file is tracked or packaged. No source is
modified. Nothing is committed, pushed, published or sent to Dr. Taufique by Astra. No canonical
Research Control edit is performed; the exact proposed update records E as still active/open.
A/B/D acceptance and C's frozen blocker remain intact. Journal shortlisting is not started.
