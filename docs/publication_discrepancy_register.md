# Publication reproducibility discrepancy register

## Assessment

E can close as a retained-result publication lock with the documented limitation below,
after manual acceptance. This applies the user's 2026-09-28 recovery rule: a nonselected B
mismatch alone does not reopen or replace accepted B. It does not certify the complete
candidate grid. Canonical Research Control remains untouched; README and ASTRA_HANDOFF
continue to show D accepted / E active until manual acceptance is recorded.

The recovered source-replay JSON and 247-cell CSV remain byte-identical, including the
historical complete-grid FAIL. Fresh verification is separate in
`outputs/publication/validation/recovery_discrepancy_check.json`. Every accepted-side value,
row identity, signed difference and reported column bound matches the unchanged baseline
and surviving comparison evidence. No source analysis or clustering fit was rerun.

## E01 Nonselected B candidate replay differences

| File under outputs/clustering | Differing cells | Scope |
|---|---:|---|
| cluster_centroids.csv | 76 | D3 full k=6 item probabilities |
| cluster_metrics.csv | 48 | Nonselected fit and perturbation diagnostics |
| cluster_selection.csv | 48 | Repeated presentation of the same metrics |
| cluster_sizes.csv | 4 | Two counts and two fractions for D3 full k=6 |
| cluster_stability.csv | 69 | Nonselected cluster Jaccard summaries |
| quality_sensitivity.csv | 2 | D3 k=6 full/sensitivity agreement |
| Total | 247 | All k=3-6; zero selected k=2 cells |

Counts by k are 32 for k=3, 25 for k=4, 27 for k=5, and 163 for k=6. These are cells,
not independent findings; 48 metric cells repeat in the selection table. The unchanged
CSV register provides one-based data-row numbers, dataset/sample/k/cluster/item, field,
accepted/replayed values, signed differences and selected-k2 flags.

D3 full k=6 cluster 1 has accepted/replayed counts 247/246, and cluster 6 has 142/143.
These aggregate counts show a net one-record redistribution. Without candidate memberships,
they do not identify a person or prove that exactly one assignment changed. Sample totals
are unchanged. Maximum absolute differences include mean ARI 0.00891968012903166,
Jaccard mean 0.02474171705107464, Jaccard 10th percentile 0.0721236559139784, and
centroid probability 0.0068452674086476595. Every file/field maximum is in the current JSON.

All selected k=2 rows pass the recovered 1e-10 comparison, including sizes, centroids,
concentration, perturbation stability and quality sensitivity. A response-quality flags,
B measurement, C feasibility, D3 outcome and D external pass their stated recovered checks.
Iterative factor/ordinal outputs use 1e-5 absolute tolerance; counts and decisions remain exact.

Recovery inserted only the recorded metric differences into temporary in-memory copies
and applied unchanged `mp1.clustering.select_k`. For D5/D3 jointly across quality views
and separately in full/sensitivity views, all candidate ranks, mean ranks, screen decisions,
selection statuses and selected k=2 values remain identical. This is aggregate arithmetic,
not reanalysis. Sub-tolerance differences were not enumerated in the recovered report;
these diagnostic copies do not reconstruct the original replay tables byte for byte.

Publication treatment: preserve every accepted diagnostic value, disclose this limitation
beside F02 and B07/B09, and retain the selected results. Do not claim complete candidate-grid
source reproduction. The discrepancy does not alter the retained target or selection logic
and does not justify changing any accepted output to match a reconstructed environment.

## E02 Incomplete original numerical environment

Scientific versions are recovered from accepted manifests. The complete original Python
build, transitive packages, BLAS/OpenMP and thread configuration were not recorded. E supplies
a tested reconstruction. R 4.6.1, lavaan 0.7-2 and semTools 0.5-6 match accepted D;
other reconstructed dependencies are labeled accordingly. Numerical-runtime sensitivity
is a possible cause, not a demonstrated explanation. No environment or seed search was used.

The numerical cause remains unresolved. Recovering it is required for a stronger claim of
complete-grid identity, not for this qualified retained-result lock. Counts, resampling
statistics and accepted results have not been silently changed or given wider tolerances.

## E03 Surviving replay evidence limits

Detailed source comparisons and the per-cell register survived in the E ZIP. Original private
B memberships, private logs, full replayed aggregate files and the old execution environment
did not. Recovery verifies surviving evidence, not a new A-D source execution. The original
private memberships were already unavailable at C/D acceptance; their accepted centroid
reconstruction contract is preserved. No missing private artifact is invented.

## Accepted external limitations carried forward

| Limitation | Required treatment |
|---|---|
| D5 metadata 2614 versus released 2613; unclear duplicate-removal wording | Preserve discrepancy and hashes; no row correction |
| D3 metadata 22 universities versus 30 literal labels | Preserve labels; no invented alias mapping |
| Partial source documentation | No invented scoring or reverse keys |
| D5 smaller profile 207 records, 200 in one identical full pattern | Adjacent concentration caution; no unique-person or natural-type claim |
| Respondent independence unverified | Nominal D3 p values and explicitly conditional intervals |
| C predictive design blocked | No classifiers, SHAP/LIME, calibration or screening claims |
| External equivalence unsupported | Compatibility and within-country observed-item claims only |

V3 still requires the supplied revisions before submission. E supplies disposition and
replacement material; it does not claim that V3 has been edited or that a journal was selected.
