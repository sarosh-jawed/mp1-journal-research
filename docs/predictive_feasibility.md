# Work Package C: target, leakage and predictive feasibility

Reviewed 2026-09-27 against accepted main
`d8fdf7a6d9352b41baa8167d5ec7c9811d11c5ed`. The complete canonical Research Control,
repository source, scripts, tests, workflow and aggregate A/B evidence were read.
The current instruction authorizes C only. No predictive classifier was fitted.
A and B code, configuration and outputs are unchanged. No D or E analysis began.

## Decision

The psychological-correlate question is blocked by target leakage: all 25
psychological/behavioral items define the target. Only five contextual fields
pass feature leakage screening. Predicting descriptive membership from metadata
is a coherent question in principle, but the present release does not support a
defensible predictive comparison under the required held-out design. The smaller
class is dominated by one unresolved repeated full-record pattern, including its
metadata. The planned split would primarily test that already-seen pattern.

The retained alternative is a reproducible target audit and marginal metadata
description of the released records, for both full and quality-sensitivity
samples. This is not a new target, a classifier benchmark, or a psychological
explanation. It preserves all records and source-documentation limitations.

This is a C-specific methodological judgment, not a universal rule that metadata
cannot predict profiles or that identical anonymous records are duplicate people.
There is no arbitrary minimum-events threshold. The allocation obstruction below
is arithmetic. The concern about independent respondent prediction remains an
explicit, conservative judgment because independence cannot be established.

## Accepted target reconstruction

The attached CSV has the accepted D5 SHA-256
`3f8cf8f041a09b8d1bf1c89eb8e85abc439ff0d1a4c26f26d3c0b7be217e64e2`.
Its attachment suffix does not affect source identity. The complete flag file
also matches B's fingerprint. Every D5 flag field is independently recomputed
with A's `assess_responses`, after source, record-order and schema checks.

The reconstruction calls the unchanged B `ordinal_features` and `fit_partition`
functions: 25 ordinal items, four equal cumulative thresholds per item, division
by two, no fitted scaling, k=2, 50 initializations, seed 44 derived from the
accepted seed 42 plus k, maximum 500 iterations, tolerance 1e-6, one numerical
thread. It does not select a new k or rerun measurement. The D5-only input adapter
uses A's lossless CSV reader and flag reader, so C needs neither D3 raw data nor
the unrelated dictionary to reproduce an already accepted D5 target.

| Check | Full target | B sensitivity refit |
| --- | ---: | ---: |
| Records | 2613 | 2512 |
| D5_P1 | 2406 | 2307 |
| D5_P2 | 207 | 205 |
| ARI against accepted centroid assignments | 1.000000 | 1.000000 |
| Largest absolute centroid difference | 5.56e-17 | 5.56e-17 |
| Minimum squared-distance assignment margin | 0.013140 | 0.077626 |

D5_P1 and D5_P2 are neutral identifiers mapped to accepted B clusters 1 and 2.
They are not severity ranks. The target is the frozen full-sample B partition.

The accepted B row-membership file is intentionally absent from Git and was not
attached for this execution. Exact agreement was therefore verified against
nearest-centroid assignments from B's hash-verified saved centroids, with no
ambiguous ties, matching centroid values, and matching per-class counts. This
is stronger than checking only the size multiset, but is not a claim to have
read the original private memberships. The output explicitly marks that
comparison unavailable. If the original file exists in Colab, it is automatically
compared as well, with ARI=1 required and arbitrary class-label permutation allowed.
An explicit `--accepted-memberships` path is also supported. A supplied missing,
misaligned or disagreeing file fails; it is never silently skipped or overwritten.

The aggregate checks include ordered partition hashes. Source bytes, raw frame
values and record order remain unchanged. Config, accepted code and all accepted
manifest-referenced aggregates are checked before use. A separate C configuration
preserves B's configuration hash and evidence bindings.

## Predictor audit

`feature_eligibility.csv` contains one row for each of the 30 raw columns,
including every requested eligibility field. No column defaults to eligibility.

| Raw columns | Target-derived? | Decision and interpretation |
| --- | --- | --- |
| All 25 survey items | Direct target inputs | Ineligible. A classifier would partly reconstruct its own label definition. |
| Gender | No | Leakage-eligible contextual candidate; two recorded categories, no missing values. Not a psychological measure. |
| Age | No | Leakage-eligible contextual candidate; 11 integer text values from 18 to 28. Described by recorded value, without fitting a linear effect or inventing bins. |
| University Type | No | Leakage-eligible contextual candidate; three categories. Other has four records and is retained. It is not an institution identifier. |
| Academic Level | No | Leakage-eligible contextual candidate; undergraduate and postgraduate categories. No temporal or causal ordering is established. |
| Department/Discipline | No | Leakage-eligible contextual candidate; 35 literal labels. CSE and its expanded label, and EEE and its expanded label, remain separate without an authoritative mapping. |

The five candidates are eligible by information origin. Their final use in this
delivery is descriptive only because the evaluation gate fails. They were not
selected by association strength or model performance.

`derived_information_policy.csv` excludes section scores, factor scores, PCA or
other embeddings, item transformations, centroid distances, silhouettes, margins,
alternate cluster encodings, full-record groups and response-quality indicators.
Every flag is a sensitivity or integrity control only. Positions, source hashes,
dataset identifiers and split/fold membership are also prohibited as predictors.
Only the record-pattern audit uses full rows, including target items; this never
becomes a model input. It is not a source of additional psychological variables.

## Evaluation gate and numerical evidence

One diagnostic stratified 80/20 split is generated with seed 42. Five diagnostic
training folds use seed 43. These are index and overlap audits only: no model,
preprocessor, hyperparameter search, performance metric or explanation sees the
design as a fitted experiment. The audit is conducted before any classifier
training. The test performance surface is never evaluated.

| Full-sample check | D5_P1 | D5_P2 |
| --- | ---: | ---: |
| Training records | 1924 | 166 |
| Test records | 482 | 41 |
| Exact full-record patterns in entire class | 2154 | 8 |
| Largest exact full-record group | 100 | 200 |
| Test records with an exact full record in training | 65 | 40 |
| Test records without an exact full record in training | 417 | 1 |

The 200-record group exceeds both minority allocations, 166 and 41. No allocation
with those class totals can keep that group intact. With it assigned entirely to
training, at most seven other minority records are available for testing. With
it entirely in test, at most seven remain for training. B sensitivity refitting
reduces that remainder to five. These are pattern-support counts, not estimates
of independent people or an effective sample size.

There are 105 exact-pattern-overlapping test records overall and 40/41 (97.56%)
in D5_P2. The same dependence issue appears in all five training folds. Grouping
could protect against this particular overlap, but would materially alter class
allocation and the evaluation question. No group split is searched until one
produces favorable performance. No pattern is deleted or downweighted.

The source may represent genuinely separate people with identical answers, a
release artifact, or another process. C does not choose among those explanations.
Nor does a source-level match prove independent respondent collection. A remains
closed for its accepted provenance analysis; the practical consequences for
prediction are now made explicit in C.

The full target was estimated from all D5 item responses in B. Even without the
record-concentration issue, a later internal classifier test would condition on
that dataset-defined partition. It would not externally validate the clustering,
discover psychological types, or prove prediction of future clinical outcomes.

## Sensitivity and descriptive alternative

All 2613 records remain in the primary analysis. Exactly 101 accepted invariance
flags define the 2512-record sensitivity sample. No record in the 200-pattern
group is removed by this control.

| Variant | D5_P1 | D5_P2 | Largest D5_P2 group | D5_P2 test overlap |
| --- | ---: | ---: | ---: | ---: |
| Full target, all records | 2406 | 207 | 200 | 40/41 |
| Fixed full target, sensitivity records | 2305 | 207 | 200 | 40/41 |
| Accepted B sensitivity refit | 2307 | 205 | 200 | 40/41 |

The same full-sample split and training-fold assignments are reused for all
variants by original record position. Filtered samples are not independently
re-stratified. The two retained records whose labels change under B's sensitivity
refit are both in the diagnostic training portion. The shared-record target ARI
is 0.9937792070102187, exactly reproducing B's stored comparison. The refit is
clearly labeled as a sensitivity target, never substituted for the primary target.

`metadata_profile_descriptions.csv` reports every single-variable category by
class, with counts, class denominators, category denominators and both conditional
proportions for all three variants. Counts are descriptive properties of these
released records. There are no p-values, odds ratios, confidence intervals,
feature-selection tests, causal effects or model-based explanations. No joint
demographic combinations or respondent-level data are released in Git.

For example, the full smaller class contains 200 records with recorded age 20
and seven with recorded age 24; its discipline marginals are 200 English and seven
CSE. The 200-record pattern accounts for the first category in each marginal.
The B sensitivity refit retains 200 and five respectively. Those distributions
are evidence of concentration in this file, not robust effects of age or discipline.
Persistence after removing invariant responses does not resolve the separate
repeated-record problem. There are no predictive results to claim survived.

## Explanation and manuscript boundaries

No best model exists: logistic regression, Random Forest and XGBoost were not
trained. All requested performance metrics are explicitly not applicable to the
blocked gate, rather than reported as zero or omitted without explanation.
No calibration, resampling-based predictive confidence intervals, SHAP ranking,
logistic coefficients, LIME cases, counterfactuals or interactions were generated.
Consequently no explanation method supports a substantive claim in this delivery.

Allowed claims:

- The accepted descriptive D5 k=2 partition was exactly reconstructed against
  its saved representation, including its accepted response-quality sensitivity.
- All item-derived predictors were rejected as circular for this target.
- Five contextual fields have no direct target derivation, but the release's
  repeated-record structure prevents the planned credible predictive comparison.
- Marginal demographic/context distributions can be described conditionally on
  this release and its multiplicities, with explicit denominators and limitations.

Avoid claims of validated scales or psychological types, psychological risk
factors, independent psychological correlates, causal AI effects, demographic
determinants, clinical screening, calibrated risks, generalizable classification,
validated respondent independence, model superiority, stable SHAP explanations,
or D3 measurement/profile replication. Also avoid claiming that modeling is
mathematically impossible in every conceivable design: the demonstrated
obstruction concerns intact patterns and the requested class allocations.

## Advisor decision and smallest next change

Accept C's target/leakage audit and descriptive alternative as the present result,
while leaving predictive and explainability execution blocked. Obtain source
clarification about repeated records and, ideally, independent observations with
independently measured contextual or psychological predictors. Any later model
comparison needs a predeclared estimand and defensible dependence-aware evaluation.
Merely changing algorithms, weighting classes or using synthetic oversampling
does not resolve this problem. Ordinary row-bootstrap intervals would not
establish independent-person uncertainty; no such intervals are produced.

If the scientific objective must remain independent psychological correlates,
the current target consumes every available psychological item. An advisor could
approve a substantively narrower target using only a justified subset, leaving
genuinely distinct measures outside target construction, followed by renewed
measurement and target validation. Alternatively obtain independent measures or
an external criterion. None of those changes is implemented here. A narrower
target would be a new research decision and a justified reopening of relevant B
work, not a cosmetic relabeling of the accepted target. D and E remain untouched.

## Execution, outputs and review

From the repository root, use the unchanged accepted analysis configuration plus
`config/work_package_c.yaml`. Run `pytest -q`, `ruff check .`, and
`ruff format --check .` before the real-data command:

```bash
PYTHONPATH=src python scripts/predictive_audit.py --config config/analysis.yaml --audit-config config/work_package_c.yaml
```

The default resolves D5 through `MP1_DRIVE_ROOT` and the accepted private flags
through `data/processed/response_quality_flags.csv`. Explicit `--d5-raw` and
`--quality-flags` paths support the supplied attachments without modifying them.
The command exits successfully when it has produced a blocker report. A failed
integrity check exits nonzero and is a different condition. There is no training
override or automatic approval when this audit is rerun.

Aggregate outputs under `outputs/modeling/work_package_c/`:

- `feature_eligibility.csv` and `derived_information_policy.csv`.
- `target_reconstruction.csv` and `quality_target_comparison.csv`.
- `record_concentration.csv` and `group_allocation_feasibility.csv`.
- `evaluation_overlap.csv` and `metadata_profile_descriptions.csv`.
- `predictive_audit_summary.json` and generated `summary.md`.

Private, ignored outputs under `data/interim/work_package_c/` are
`target_memberships.csv`, `diagnostic_design.csv`, and `private_manifest.json`.
They must not enter the ZIP or Git. Original B memberships are never overwritten.

Synthetic tests cover label permutations, source/evidence/flag corruption,
optional membership checks, exact reconstruction, record-order identity, unknown
feature rejection, deterministic splitting, disjoint training folds, overlap
counts, the intact-group allocation bound, complete marginal accounting, output
hashes, source immutability, CLI behavior and Git ignore protection. The real-data
run separately checks exact centroids, counts, flags, no-tie assignment, sensitivity
agreement, overlap arithmetic and every marginal denominator.

Manually review the two exact reconstruction checks, 30-row eligibility table,
blocked gate, overlap table, allocation proof and limits of the descriptive
alternative. Accepting this audit does not mean accepting or running classifiers.
The delivery guide contains exact Colab application and validation commands.

Method sources, checked 2026-09-27:

- [scikit-learn StratifiedGroupKFold documentation](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.StratifiedGroupKFold.html)
  explains the non-overlapping group requirement and why very large groups can
  prevent stratification. It does not establish that D5 groups are the same person.
- [Kapoor and Narayanan, leakage in ML-based science](https://reproducible.cs.princeton.edu/)
  distinguishes clean evaluation and scientifically justified claims. The specific
  D5 blockage is this package's inference from the source data and audit evidence.
