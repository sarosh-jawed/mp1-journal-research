# Work Package D: academic outcome and cross-cultural validation

Review date: 2026-09-27 UTC. Baseline: `dad222a9a0143887e7e25a72e656ec21d0ebc253`.
This is a bounded D analysis awaiting scientific acceptance, not publication lock.
The canonical MP1 Research Control was read completely before analysis. Its document ID,
revision and extracted-text hash are recorded in `config/work_package_d.yaml`.

## Questions and scope

1. Do the accepted D3 descriptive profiles have different recorded Current CGPA distributions?
2. Which U.S.-Indonesia measures support a meaningful comparison with Bangladesh or between
   the two external samples, given the actual instruments and measurement evidence?

A/B/C decisions, configuration, source interpretations, quality flags, profiles and accepted
outputs are frozen. Eighty-one baseline files are fingerprinted by D. Only the README, handoff
and CI installation instructions are updated among existing files. No classifier, alternative
partition, predictive split, SHAP, LIME or new predictive analysis was fitted. Reusing unchanged
record-grouping and label-alignment helpers from C does not reopen its feasibility blocker.
Vietnam was not used. Research Control was not edited.

## Inputs and eligibility

| Input | Required content | SHA-256 |
|---|---|---|
| D3 CSV | Nine accepted survey items, Current CGPA, literal institution field and complete released records | `ca92de616712be5ac129ed60040fccc78e6147119ce10c1806349e9c3240213d` |
| Accepted quality flags | All original flag columns, source hash, row alignment and sensitivity inclusion | `322854f24cf209f46fb33a5cf71f54fe2ca72be0a60b32d6188ee4d1ed9c76e1` |
| When Culture Meets AI - Survey Dataset.xlsx | All 41 Survey Data columns and all 41 Codebook entries | `985c39bd5ad4e0f9278a059e6eaa8aa0ddacac51913b1996421880ad8062ff4a` |

The external workbook was obtained from the official [Zenodo release](https://zenodo.org/records/21013786).
Its MD5 `2dee3dc349339fdc312c63cefdd4cb62` agrees with that release. Both sheets were inspected in
full, including cells, metadata, eligibility fields, response domains and Codebook definitions,
before selecting analytical variables. The Survey Data sheet has 239 records and 41 columns;
the Codebook has 41 entries and six columns. There are no formulas, comments, hidden rows or
columns, merged cells or additional sheets. The raw workbook is never rewritten.

## D3 reconstruction and outcome audit

D3 retains all 1,104 released records. The accepted k=2 full and quality-refit partitions were
reconstructed using unchanged B ordinal-threshold features, seed 1044 and clustering settings.
They match the accepted centroid assignments exactly (ARI 1), accepted sizes and sensitivity
agreement. Maximum centroid discrepancies are approximately 5.6e-17. No assignment tie occurs.
Original private B memberships were unavailable in this execution; this is reported, not treated
as a direct membership-file comparison. A supplied or already present private B membership file
is automatically checked record by record, allowing only permutation of nominal profile labels.

Profile P1 (n=769) has relatively greater dependency-related endorsements and lower verification
and unaided-study endorsements. P2 (n=335) has relatively greater verification and unaided-study
endorsements and lower dependency-related endorsements. These remain descriptive configurations,
not validated types, ordered risk levels or externally established diagnoses.

`Current CGPA` contains four ordered **bands**, not numerical grades. All 1,104 values are eligible:
Below 2.50 (8), 2.51-3.00 (204), 3.01-3.50 (649), Above 3.50 (243). There are no missing or
unrecognized values. The labels do not document the handling of exactly 2.50. No boundary repair,
midpoint imputation or invented grade precision is applied. Codes 0-3 encode order only.

| Recorded CGPA band | P1 records (%) | P2 records (%) |
|---|---:|---:|
| Below 2.50 | 6 (0.78) | 2 (0.60) |
| 2.51-3.00 | 138 (17.95) | 66 (19.70) |
| 3.01-3.50 | 443 (57.61) | 206 (61.49) |
| Above 3.50 | 182 (23.67) | 61 (18.21) |

The median band is 3.01-3.50 in both profiles. Their inverse empirical-CDF first and third
quartile bands are also 3.01-3.50. This coarse outcome cannot resolve within-band differences.

### Rank methods and findings

Tie-corrected Kruskal-Wallis compares the nominal profiles without normality, equal score
distances or a linear profile-trend assumption. It is an omnibus distribution/rank comparison;
it does not establish a pure median shift when distributions differ in shape. With exactly two
accepted profiles it already tests the sole contrast. A separate Dunn test or post-hoc family
would add no distinct comparison, so no post-hoc tests were run.

Rank epsilon squared is explicitly defined as H/(N-1). It describes rank association, not a
fraction of numerical grade variance causally explained. Cliff's delta is P(P2 band > P1 band)
minus P(P2 band < P1 band), with tied pairs contributing zero. The profile order only defines
the sign; it imposes no substantive ordinal hierarchy.

| Analysis | P1 / P2 n | H (df=1) | Nominal p | H/(N-1) | Cliff delta, P2 minus P1 |
|---|---:|---:|---:|---:|---:|
| Full accepted profiles | 769 / 335 | 2.802525 | 0.094116 | 0.002541 | -0.055901 |
| Quality sensitivity, full labels retained | 764 / 335 | 2.960391 | 0.085327 | 0.002696 | -0.057478 |
| Quality sensitivity, accepted B refit | 763 / 336 | 2.621135 | 0.105449 | 0.002387 | -0.054040 |

No comparison reaches the nominal 0.05 threshold. The observed effect is very small: the
tie-adjusted probability that a randomly selected P2 record is in a higher band than a P1
record is 0.47205 (ties receive half weight), close to 0.5. These results do not establish
equivalence, absence of an association, a grade-point difference or a practically important
effect. No equivalence margin was supplied or tested.

The accepted sensitivity rule identifies five invariant item-response records, all in P1.
Their removal is an explicit sensitivity view, not a permanent source exclusion. Both the fixed
full-profile labels and the accepted B sensitivity refit are carried through every outcome
calculation. The refit changes one retained assignment; full-refit ARI is 0.996276. Neither
sensitivity changes the scientific conclusion.

### Repeated full records and uncertainty

There are 942 distinct complete released patterns, 45 repeated groups with 207 member records
and 162 excess occurrences. The largest pattern has 63 records, all in P2 (18.8% of P2).
Anonymous identical records are **not established duplicate people**. Every occurrence remains
in the point estimates. P1 and P2 contain 710 and 232 distinct full-record patterns respectively.

Kruskal-Wallis p-values above use an independent-record reference distribution. Independence
of unique respondents cannot be verified, so they are explicitly nominal, not certified
population-level inference. No effective sample size of 942 is asserted.

Ten thousand percentile bootstrap resamples provide separate, conditional uncertainty views:

| Full-sample resampling assumption | Units | 95% conditional interval for Cliff delta |
|---|---:|---:|
| Independent records, within fixed profiles | 1,104 | [-0.121061, 0.007597] |
| Independent complete-record patterns, within fixed profiles | 942 | [-0.130920, 0.018238] |
| Independent literal institution labels, sampled jointly across profiles | 30 | [-0.112695, 0.076566] |

Pattern resampling draws intact patterns with every original occurrence, preserving multiplicity;
it does not deduplicate or give each pattern equal record weight in the point estimate. Literal
institution labels are neither corrected nor equated to 30 verified universities. The unresolved
source assertion of 22 universities remains unchanged. Institution resampling is a sensitivity
scenario, not a validated sampling design. All nine intervals across the three analytical views
contain zero; none has an invalid replicate.

These intervals condition on the named units being independent and the accepted profiles being
fixed. They do not propagate profile estimation or selection uncertainty, resolve relatedness
between different records, verify respondent identities, correct selection bias or guarantee
population coverage. Repeated-pattern and institution scenarios do not establish independence
by themselves. The evidence supports an inconclusive, small observed association.

## Compatibility audit

`item_compatibility.csv` covers every external item and its possible Bangladesh thematic link;
`bangladesh_item_coverage.csv` separately accounts for all 25 D5 and nine D3 items. None is an
identical common anchor. Similar construct names and five response categories do not establish
equivalent meaning, direction, measurement units or populations.

| External source-defined construct | Items / subdimensions | Bangladesh compatibility | Permitted interpretation |
|---|---|---|---|
| GenAI dependency | GAID1-3 cognitive preoccupation; GAID4-7 negative consequences; GAID8-11 withdrawal | Partial themes overlap D5 dependence/decisions and D3 confidence, unaided work or perceived harm; no matching scale | Country-specific measurement diagnostics; limited item-level thematic comparison |
| Critical-thinking disposition | CT1-7 critical openness; CT8-11 reflective skepticism | General positive thinking disposition differs from D5 reported reduction in independent thinking and D3 AI-related behaviors | Do not reverse-code into, or equate with, the Bangladesh constructs |
| Self-rated work performance, labeled IWPQ Task Performance in Codebook | TP1-7, one source-defined dimension | No common academic achievement instrument or CGPA field; TP6 efficiency only loosely relates to D5 U5 | Self-reported item responses, never objective performance or academic grades |
| Bangladesh-only content | D5 AI use, AI trust and academic decisions; D3 recall, unmodified output use and submission without understanding | Many items have no external counterpart | No transferred profile or synthetic common score |

Specific near-matches remain substantively different: GAID1 versus D5 AD1 concerns general
versus academic decisions; GAID6 versus D5 CD5 and D3_7 concerns confidence in general abilities
versus work or writing/analysis; GAID7 versus D5 CT4 and D3_8 distinguishes perceived harm from
effort reduction or perceived weakened thinking. CT3/CT9 concern general sourcing/credibility,
whereas D3_1 concerns verifying AI information and D5 T3 concerns rarely verifying it. Different
reference objects and polarity prevent treating these as common anchors. No reverse coding is
introduced to manufacture overlap.

Both external country samples share the published Codebook's 29 item identifiers, membership
and 1=Strongly disagree through 5=Strongly agree coding. This supports analysis of corresponding
**observed responses** within each country. Original administered Indonesian wording and
translation-validation evidence are absent from this release. Shared published labels do not
prove semantic equivalence, invariance, comparable response styles or a common latent unit.

| Source | Recorded item-response scale | Scale-compatibility limit |
|---|---|---|
| Bangladesh D5 and D3 | Strongly Disagree, Disagree, Neutral, Agree, Strongly Agree, preserved in that order | Five agreement labels do not make different questions interchangeable |
| U.S. and Indonesia | Integers 1-5; Codebook states endpoints 1=Strongly disagree and 5=Strongly agree | The Codebook abbreviates the scale between endpoints and does not explicitly supply the verbal labels for 2-4; these labels are not invented |

The Codebook attributes the batteries to Goh, Hartanto and Majeed (2025), Sosu (2013) and
Koopmans (2014). These are source attributions, not confirmation that administered translations,
adaptations or all seven supplied performance items reproduce the original validated instruments.
The measurement models follow the supplied item membership provisionally and are tested as such.

Bangladesh D3 covers the accepted multi-institution academic sample and D5 the accepted Bangladesh
student sample; neither is matched to these external undergraduate business-related samples.
The external release has 122 U.S. and 117 Indonesian records, with source-flagged active users
of 116 and 111 respectively. The 12 source-excluded nonactive users (six per country) have all
29 items missing: six U.S. Rarely users; four Indonesian Rarely and two Never users. All 227
active records have every item observed. No item imputation or additional quality exclusion is
introduced. IDs are unique; there are no repeated complete records excluding the identifier in
the analytic sample. Country labels and source row order are retained throughout. Neither
country sample is claimed nationally representative or a randomized cultural exposure.

### Country measurement evidence and formal-test boundary

Country-specific polychoric ULS diagnostics use the source-defined factor structure, retaining
all items. They are diagnostic fits, not invariance tests. All six converge admissibly; no
polychoric boundary or numerical repair is needed. U.S. CT has substantial residual misfit
(RMSR 0.120, maximum residual 0.403) and raw alpha 0.484 / 0.372 for openness / skepticism.
Indonesian CT factors correlate 0.954. GAID cognitive-preoccupation alpha is 0.589 in the U.S.
and 0.733 in Indonesia. Reliability alone cannot establish validity, dimensional distinctness
or equivalence. Full diagnostics, item loadings and all six subdimension alphas are retained.

Formal ordinal testing requires estimators and identification that support thresholds and
latent response scales. Python orchestrates a narrowly scoped R bridge to `lavaan` and
`semTools`, using WLSMV, theta parameterization, `std.lv` factor identification and
Wu-Estabrook ordinal identification. This avoids mislabeling a continuous-score or ULS
comparison as ordinal measurement invariance. No B estimator or accepted result is changed.

Before any equality constraints, the declared screen requires admissible country-specific and
multigroup configural models, scaled CFI >=0.90, scaled RMSEA <=0.08 and SRMR <=0.08. These are
transparent screening heuristics, not universal pass/fail definitions of validity. Robust
CFI/RMSEA are also reported. No threshold was tuned after observing these fits.

GAID has all five categories in each country, allowing the source three-factor configural
model to be estimated. Sparse tail counts still limit precision and power.

| GAID model | Scaled CFI | Scaled RMSEA (90% interval) | SRMR | Robust CFI / RMSEA | Follow-up screen |
|---|---:|---:|---:|---:|---|
| U.S. | 0.984 | 0.047 [0.000, 0.084] | 0.059 | 0.951 / 0.065 | Pass |
| Indonesia | 0.968 | 0.121 [0.093, 0.149] | 0.080 | 0.898 / 0.128 | Fail |
| Multigroup | 0.973 | 0.091 [0.070, 0.113] | 0.069 | 0.911 / 0.101 | Fail |

The Indonesian and multigroup configural fits fail the declared screen. Accordingly, no GAID
threshold, loading or intercept equality comparisons are interpreted or attempted on real data.
CT and TP have absent response categories within countries, sometimes different missing
categories across countries. Their unchanged five-category threshold models lack the support
needed for the specified invariance sequence. No categories are collapsed, items dropped or
partial-invariance paths searched. The empty `ordinal_equality_comparisons.csv` is intentional.

The reusable engine correctly proceeds, when supported, from thresholds to additional loading
and intercept equality using Wu-Estabrook identification and scaled-shifted Satorra-2000 nested
comparisons. Synthetic data verify the sequence and detect known threshold non-equivalence.
This capability is not evidence that the real instruments passed it. Failure of a prerequisite
is not proof that every possible invariant model is false. Latent country means, factor scores
on a shared scale and claims of Bangladesh profile replication are unsupported.

### Defensible bounded alternative

No raw-score pooling, transferred composites, country z-scores or latent mean contrasts are
used. Within-country standardization cannot create missing common content or measurement
equivalence and would remove country mean differences by construction.

Two exploratory, content-selected item relationships were fixed before their correlations
were calculated: GAID6 (confidence without AI) with CT9 (source-credibility checking), and GAID6
with TP6 (self-rated efficient work). They address narrow dependency/verification/performance
themes without claiming validated composite scales. They are analyst-selected extensions, not
preregistered confirmatory hypotheses or an empirical replication of Bangladesh instruments.

Within each country, Spearman correlations use ties, 9,999 random permutations with a plus-one
two-sided p-value, 5,000 paired percentile bootstrap resamples, and Holm correction across all
four tests. Intervals are unadjusted marginal 95% intervals conditional on independent records;
they are not simultaneous familywise intervals. Exchangeability under independence is required
for the permutation reference. Source IDs and lack of repeated records cannot prove it.

| Country | Pair | Spearman rho | Conditional 95% interval | Holm p |
|---|---|---:|---:|---:|
| U.S., n=116 | GAID6 / CT9 | 0.0976 | [-0.0829, 0.2726] | 0.9105 |
| U.S., n=116 | GAID6 / TP6 | -0.0338 | [-0.2161, 0.1463] | 1.0000 |
| Indonesia, n=111 | GAID6 / CT9 | -0.0343 | [-0.2170, 0.1566] | 1.0000 |
| Indonesia, n=111 | GAID6 / TP6 | 0.1215 | [-0.0756, 0.3084] | 0.8196 |

All intervals include zero. These are inconclusive within-sample item associations. No test of
a country difference in correlations was performed; different signs or different significance
levels would not establish a cross-country difference. Permutation Monte Carlo standard errors
(0.0040-0.0046) and seeds are in the aggregate table; none is near a significance boundary.

## Supported claims, conflicts and advisor decisions

Supported: a very small, statistically inconclusive observed CGPA rank difference between the
accepted profiles, with the same conclusion in both accepted quality views and all conditional
uncertainty scenarios; explicit thematic compatibility without common Bangladesh anchors;
country-specific observed-item evidence and a documented formal measurement-testing boundary.

Avoid: causality; better/worse academic performance caused by AI; profile risk hierarchies;
equivalent profiles or latent country means; validated international scales; national or cultural
effects; proof of no relationship; practical equivalence; exact grade-point effects; independent
people inferred from record counts; counting repeated records as duplicate respondents; and
any predictive-performance claim.

One genuine advisor-guidance conflict is documented: external TP responses are self-reported
agreement items. Guidance that this workbook makes the outcome objective or less self-report-only
is not supported by the released data. No A/B/C result or source interpretation is altered.

No advisor choice is needed to complete this bounded D delivery. Advisor/source-author input
is needed only if stronger claims remain a goal: establish D3 respondent independence and
institution-label meaning; obtain original language forms and translation/adaptation evidence;
and decide whether to authorize a separately justified measurement redesign or additional
matched data. Any future category merging, partial invariance, new instruments or revised
profiles needs an explicit new methodological decision. Do not force such changes into D or
advance to E as a consequence of a successful software run.

## Verification and primary method references

The full synthetic suite, Ruff checks, real-data execution, source and frozen-file hashes, and
independent rank-sum/all-pairs calculations were checked. See `docs/work_package_d_validation.md`
for the execution record, `docs/work_package_d_colab.md` for commands and
`docs/work_package_d_review.md` for the manual scientific checklist.

- [SciPy Kruskal-Wallis documentation](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.kruskal.html): independent-sample reference, ties and omnibus interpretation.
- [lavaan categorical-data tutorial](https://lavaan.ugent.be/tutorial/cat.html): ordinal WLSMV estimation.
- [semTools measEq.syntax documentation](https://search.r-project.org/CRAN/refmans/semTools/html/measEq.syntax.html): Wu-Estabrook identification and ordered equality constraints.
- [Wu and Estabrook (2016)](https://doi.org/10.1007/s11336-016-9506-0): identification of ordinal CFA invariance models.
