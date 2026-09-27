# Measurement and cluster structure

Work Package B, independently implemented against main commit
`35ddfdf51823e54b4d13df7d8a9b05e7d3abb0f2`. The complete current Research Control and
repository were reread. No legacy analytical code was used. A remains closed for
execution, with its source documentation limitations intact. User review and
Research Control acceptance are pending; no later work package is started.

## Findings

No D5 section is established here as a validated scale. Cognitive Dependence is
the strongest tentative section; its reliability weakens in the quality
sensitivity sample. The hypothesized five-section CFA is inadmissible. The best
D5 K-Means candidate is a two-profile descriptive partition, with modest
separation and severe concentration of repeated records in its smaller profile.
D3 independently favors two profiles, but does not replicate D5's measurement
model or distinctive centroid pattern.

| D5 section | Raw alpha, full | Raw alpha, sensitivity | Ordinal omega, full | Ordinal omega, sensitivity |
| --- | ---: | ---: | ---: | ---: |
| AI Usage | .479 | .394 | .555 | .454 |
| Cognitive Dependence | .706 | .670 | .726 | .676 |
| Trust in AI | .610 | .551 | .642 | .569 |
| Reported reduction in independent thinking | .556 | .488 | .606 | .518 |
| Academic Decision-Making | .553 | .484 | .580 | .486 |

Ordinal omega estimates reliability of standardized latent responses conditional
on a one-factor model, not reliability of an observed 1-5 sum. Observed-score
alpha, standardized observed omega, ordinal alpha, item-rest correlations, and
both alpha and ordinal omega after each item deletion are saved separately.
No deletion recommendation is implemented. Cognitive Dependence's minimum
corrected item-total correlation falls from .318 to .272; its minimum ordinal
loading falls from .395 to .328. A marginal loading cutoff alone is not the basis
for rejecting validation: the sensitivity effect and inadmissible joint model
also matter. Four other sections have substantially weaker reliability.

The five-section ordinal-correlation CFA has factor correlations as high as
1.066 in the full sample and 1.078 in sensitivity, so its apparent residual fit
cannot establish a valid factor model. Common-factor parallel analysis retains
five exploratory D5 dimensions in both samples. These mix questionnaire sections;
their clear-marker counts are 4/4/3/2/1 and 4/3/1/2/1. Five retained dimensions
therefore do not validate five named sections. HTMT is not used to claim
discriminant validity for inadequately supported reflective scales.

| Dataset and sample | Selected k | Silhouette | Davies-Bouldin | Calinski-Harabasz | Mean omitted-record ARI |
| --- | ---: | ---: | ---: | ---: | ---: |
| D5 full, n=2613 | 2 | .199 | .841 | 331.95 | .994 |
| D5 sensitivity, n=2512 | 2 | .194 | .838 | 319.70 | .999 |
| D3 full, n=1104 | 2 | .380 | 1.035 | 747.73 | .997 |
| D3 sensitivity, n=1099 | 2 | .382 | 1.035 | 749.72 | .996 |

All k=2 through k=6 results are retained in cluster_metrics.csv. D5 k=3 through
k=5 have many negative individual silhouettes despite high stability; k=6 also
has poor resampling stability. k=2 has the best D5 silhouette, Davies-Bouldin,
Calinski-Harabasz and centroid separation among the tested candidates. Its size
imbalance remains a limitation, not evidence of clinically distinct minorities.

D5 full-sample profiles contain 2406 and 207 records. The smaller profile contains
200 identical full records, 96.6% of that profile, leaving only eight distinct
full-row patterns. In sensitivity, it contains 205 records, including the same
200-record group, 97.6%. These are anonymous record patterns, not verified people.
The result is reproducible under the released multiplicities, but its resampling
stability cannot demonstrate population subtypes or respondent independence.
No repeated record is deleted, downweighted, or called a duplicate person.

Names assigned only after inspecting the selected full-sample centroids:

- D5 profile 1: Broad AI-related endorsement. Agreement proportions across items
  are approximately .58-.72. This is a heterogeneous majority, not a diagnostic category.
- D5 profile 2: Selective regular-use and thinking-reduction endorsement. Nearly
  all agree with regular use and CT1/CT2/CT4/CT5, while agreement with the other
  items is near zero. This is the pattern dominated by the repeated full record.
- D3 profile 1: Greater dependency-related endorsement and lower verification or
  unaided-study endorsement, n=769.
- D3 profile 2: Greater verification and unaided-study endorsement with lower
  dependency-related endorsement, n=335.

Profile IDs are lexicographic centroid identifiers, not severity ranks. IDs are
specific to dataset and sample. Machine descriptions in selected_profiles.csv
identify the largest item contrasts; use the complete centroid table for meaning.

Full versus sensitivity assignment ARI on shared records is .994 in D5 and .996
in D3. Removing flagged invariance changes reliability appreciably but does not
change the preferred k=2 descriptive conclusion. It does not remove the large D5
repeated pattern, which is non-invariant across items. Higher-k D5 conclusions
are less robust; k=6 has shared-record ARI .353.

## Inputs, assumptions, and decisions

D5 has 2613 records, five background fields and 25 survey items. D3 has 1104
records, six background fields and nine survey items. Exact item headers and
analysis IDs appear in item_inventory.csv. All five response labels occur in
every item; there are no missing survey responses. The accepted raw SHA-256
fingerprints and flag order are verified before use. D5 has 101 flagged records;
D3 has five. Both full samples retain every source record.

The questionnaire documents 1=Strongly Disagree through 5=Strongly Agree but no
validated composites or reverse keys. Numeric coding is explicit and derived;
raw strings remain unchanged. D5 Critical Thinking wording concerns perceived
reduction in thinking, not demonstrated thinking ability. D3's first two items
are protective in wording, whereas its other items concern reliance or adverse
experiences. No reverse coding is required for the ordinal distance used here.

Measurement methods:

- Polychorics estimate thresholds from empirical marginal proportions and then
  maximize the bivariate normal correlation likelihood. Deterministic 64-node
  Gaussian quadrature avoids random CDF integration. Tests compare probabilities
  with independent adaptive quadrature and recover known latent correlations.
  Matrices must be positive definite; none is silently smoothed. Observed minimum
  eigenvalues exceed .22. No pair hits the correlation boundary.
- The latent-normal assumption remains conditional. Maximum fitted-versus-observed
  cell probability discrepancies are .079 in D5 and .067 in D3; sparse expected
  cells occur, particularly in D3. These are descriptive diagnostics, not evidence
  that latent normality has been validated.
- EFA uses MINRES with oblimin rotation. Retention compares leading common-factor
  eigenvalues, with squared multiple correlations on the diagonal, against the
  95th percentile from 100 independent within-item permutations. This preserves
  margins and uses polychorics for observed and null data. Clear markers require
  absolute loading >=.40, other loadings <.30 and a loading gap >=.20; three clear
  markers per factor are the declared scoring screen. No exploratory factor
  scores are used when that screen fails, and no independent confirmation is claimed.
- CFA fits the prespecified section membership by ULS to the polychoric matrix.
  The tested semopy 2.3.11 ordinal routine calls removed scipy.stats.mvn.mvnun;
  factor-analyzer 0.5.1 fitting calls an obsolete scikit-learn argument. Their
  affected paths are not used. semopy's tested covariance-input ULS and
  factor-analyzer's rotation interface are used. This is an ordinal correlation
  alternative, not WLSMV. No robust standard errors, chi-square p-values, CFI,
  TLI or RMSEA are reported. RMS residuals exclude the diagonal and are labeled
  explicitly, without applying normal-theory fit cutoffs to them.
- Section screening requires raw alpha and ordinal omega >=.70, item-total >=.30,
  loading >=.40, maximum local residual <=.10 and no boundary solution in both
  samples. These are transparent analysis heuristics, not universal validity
  criteria or preregistered tests. No section passes both screens.

Clustering representation and selection:

- Retain all raw items because section scores lack support and exploratory
  dimensions lack adequate simple markers. For response x, encode four indicators
  I(x>1), I(x>2), I(x>3), I(x>4), each divided by two. Squared Euclidean distance
  is sum(|x-y|)/4. Equal threshold weights are explicit analytic choices; the
  embedding preserves order without fitting latent scores. No variance scaling,
  metadata, university label, CGPA, or daily-use category enters clustering.
  Reversing one item's ordinal direction is an isometry of this representation,
  so protective wording does not require an invented source scoring key.
- K-Means uses 50 initializations for every reference and resampled fit, 500 maximum
  iterations, fixed tolerance, one numerical thread and seeds derived from the
  configured seed 42. Fit each k=2 through k=6 in both samples. Stability uses 100
  independent 80% subsamples without replacement and compares omitted-record
  nearest-centroid assignments with the reference partition using ARI and
  one-to-one matched Jaccard. Perturbation percentiles are not confidence intervals.
  The reference uses all records, so omitted-record agreement is not external validation.
- Screen each candidate in both samples: smallest cluster >=5%, mean ARI >=.80,
  ARI 10th percentile >=.60, every cluster's mean Jaccard >=.75, negative-silhouette
  fraction <=25%, and each centroid pair differs by >=.10 in agreement probability
  on at least one item. Rank silhouette, Davies-Bouldin, Calinski-Harabasz, mean
  ARI, minimum size fraction and centroid separation equally, averaging ranks
  across samples. Choose the lowest mean rank, with smaller k breaking ties.
  If none passes, explicitly return a descriptive candidate with failure status.
  These rules were set before inspecting the cluster results. Agreement-profile
  contrast is an interpretability screen; substantive interpretation follows the
  full centroid review. A passing screen does not establish natural classes.

## D3 comparison boundary

| D3 content | Related D5 content | Permissible comparison |
| --- | --- | --- |
| D3_1, verifies AI information | T3, rarely verifies | Related behavior with opposite sentence direction; not identical items |
| D3_2, can work without AI | CD1/CD5, discomfort and confidence without AI | Broad autonomy theme; ability, discomfort and confidence are different claims |
| D3_3, asks AI before books or notes | CD2, relies on AI before thinking independently | Related first-response reliance, with different comparison behaviors |
| D3_7, confidence in writing/analysis without AI | CD5, confidence working without AI | Closest wording, but narrower D3 domain |
| D3_8, perceived weakened critical thinking | CT1/CT2/CT4 | Related self-report theme; ability change differs from reduced need or effort |
| D3_4/5/6/9, recall, speed versus understanding, modification and comprehension | No exact counterparts | Do not substitute for D5 constructs |
| D5 usage, trust and decision sections | No equivalent D3 batteries | No score harmonization or direct centroid transfer |

D3 parallel analysis retains two exploratory dimensions: seven reliance/adverse
experience items and two protective items, with opposite association. The second
dimension has only two clear markers. This is neither the D5 five-section model
nor sufficient evidence to create two validated D3 scales. Its item-level
partition is evaluated independently with the same rules. Coinciding k values do
not establish replication, measurement invariance, common profile prevalence,
or equivalent psychological types. No CGPA or other outcome comparison is made.

## Evidence and review

Machine-readable aggregates are under outputs/psychometrics/ and outputs/clustering/.
Their JSON manifests bind sources, configuration, code, quality flags, package
versions and artifact hashes. Private memberships remain under
data/interim/work_package_b/ and must not be committed. No raw data, source
downloads or quality flags belong in the delivery patch.

Review item meanings, inadmissible CFA correlations, conditional omega, weak
exploratory markers, all-k metrics, profile sizes, complete centroids, and especially
cluster_record_concentration.csv. Avoid claims of a validated five-subscale
instrument, measured cognitive deterioration, causal AI effects, clinical risk
tiers, discovered natural population classes, independent people inferred from
anonymous records, or direct D3 replication. High stability under the released
record multiplicities is a narrower result.

All 63 synthetic tests, Ruff lint and Ruff formatting passed. Numerical checks
cover source immutability, ordinal integration, known-factor recovery, deletion
diagnostics, record-bound flags, stable schemas, complete sample accounting,
deterministic resampling, multi-criterion selection, and repeated-record
concentration. Real-data execution and researcher review remain distinct from
synthetic test success. See the delivery guide for exact Colab and acceptance commands.

Method references: [polychoric estimation](https://cran.r-project.org/web/packages/polycor/polycor.pdf);
[ordinal reliability](https://files.eric.ed.gov/fulltext/EJ977577.pdf);
[omega](https://doi.org/10.1111/bjop.12046);
[ordinal parallel analysis](https://doi.org/10.1037/a0030005);
[ordinal WLSMV](https://lavaan.ugent.be/tutorial/cat.html);
[semopy ordinal limitations](https://semopy.com/ordinal.html);
[clusterwise stability](https://doi.org/10.1016/j.csda.2006.11.025);
[K-Means and metrics](https://scikit-learn.org/stable/modules/clustering.html).

Commit message: `Evaluate ordinal measurement and descriptive cluster structure`

Proposed Research Control progress entry, only after user acceptance:

2026-09-26 | Completed Work Package B measurement and cluster evaluation for full
and response-quality sensitivity samples. Five D5 sections were not validated;
ordinal item profiles favored k=2, with the smaller D5 profile dominated by a
released repeated-record pattern. D3 independently favored k=2 but did not provide
direct measurement or profile replication. No source records were changed. |
outputs/psychometrics/measurement_summary.json;
outputs/clustering/clustering_summary.json; docs/measurement_cluster_structure.md |
63 synthetic tests and Ruff checks passed; real-data outputs reviewed. | Limits:
conditional ordinal factor inference, D5 record concentration, non-equivalent D3
items, and previously recorded source documentation questions. | B accepted as
descriptive measurement and structure evidence; no authorization to begin C.
