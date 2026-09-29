# Manuscript evidence map

Authority: canonical MP1 Research Control after D acceptance. A/B/D accepted; C frozen as the accepted predictive-feasibility blocker. E does not grant acceptance to itself.

All scientific references below are baseline outputs, not E-generated findings. CSV row numbers are one-based data rows (header excluded). Exact strings, including full numeric precision, are preserved in complete_evidence_register.csv.

Recovered source replay contains 247 differences confined to nonselected B k=3-6 diagnostic candidates. Accepted bytes are preserved. Selected k=2 results and all candidate ranks/screens/choices agree; complete candidate-grid numerical identity is not claimed. See docs/publication_discrepancy_register.md.

## A01: D5 and D3 active files match the supplied official releases.

Research question: What records were released?

Key evidence (display precision): D5: 2613 records, 30 columns; 42 repeated groups, 493 members, 451 excess repetitions, largest group 200. D3: 1104 records, 15 columns; 45 groups, 207 members, 162 excess, largest group 63. Both active/release hashes identical.

Permitted interpretation: Record counts, exact repeated patterns and release identity are established for the compared bytes.

Prohibited overclaim: Verified unique people; locally missing D5 respondent; authorization to deduplicate.

Manuscript placement: Methods: data sources; Table 1. Role: main.

Authoritative selectors:

- `outputs/provenance/source_reconciliation.json`: JSON pointer `/file_comparisons`

## A02: D5 metadata count and cleaning language, and D3 institution counts remain unresolved externally.

Research question: Are source descriptions complete?

Key evidence (display precision): D5 metadata 2614 vs release 2613; deduplication rule undocumented. D3 metadata 22 universities vs 30 literal labels. Seven closure questions retained with original status fields; later canonical A acceptance governs execution.

Permitted interpretation: A is accepted with explicitly retained external source limitations.

Prohibited overclaim: Reopening A solely because historical closure flags remain true; resolving discrepancies by assumption.

Manuscript placement: Methods: provenance; Limitations. Role: main.

Authoritative selectors:

- `outputs/provenance/source_closure_matrix.csv`: CSV selector `{}`; {} means all rows

## A03: D5 questionnaire coverage is partial; the supplied dictionary does not cover D3/D5.

Research question: What measurement documentation exists?

Key evidence (display precision): 25 D5 CSV items crosswalked against a partial three-page questionnaire supplement. No supplied D3/D5 dictionary section or supported reverse/scoring key.

Permitted interpretation: Use literal item responses and disclosed source-defined headings.

Prohibited overclaim: Invented scoring, reverse keys, validated scales or complete source documentation.

Manuscript placement: Methods: measures; Limitations. Role: main.

Authoritative selectors:

- `outputs/provenance/d5_questionnaire_coverage.csv`: CSV selector `{}`; {} means all rows
- `outputs/provenance/source_reconciliation.json`: JSON pointer `/codebook_follow_up`

## A04: Thirty literal D3 institution labels are preserved.

Research question: Can institutions be harmonized?

Key evidence (display precision): 30 unchanged literal labels; one possible constituent-college parent grouping yields 29, not 22; no aliases applied.

Permitted interpretation: Names are literal released labels; one constituent-college relationship does not explain the reported 22.

Prohibited overclaim: Thirty independently verified sampled universities; unsupported alias merges.

Manuscript placement: Methods: provenance; Supplement. Role: supplement.

Authoritative selectors:

- `outputs/provenance/d3_institution_reconciliation.csv`: CSV selector `{}`; {} means all rows

## B01: Full records remain primary; invariant-response exclusion is a sensitivity only.

Research question: What samples are analyzed?

Key evidence (display precision): D5 full/sensitivity 2613/2512, invariant-response flags 101. D3 1104/1099, flags 5. Permanent exclusions 0.

Permitted interpretation: D5 2613/2512 and D3 1104/1099 full/sensitivity records; no permanent exclusions.

Prohibited overclaim: Proven careless respondents; complete-case causal identification; deleted primary records.

Manuscript placement: Methods: response quality; Table 1. Role: main.

Authoritative selectors:

- `outputs/psychometrics/measurement_summary.json`: JSON pointer `/samples`
- `outputs/modeling/work_package_c/predictive_audit_summary.json`: JSON pointer `/sensitivity`

## B02: No D5 source-defined section passes all prespecified screens in both samples.

Research question: Are the five sections validated?

Key evidence (display precision): Full raw alpha/ordinal omega U 0.479382/0.555266; CD 0.706187/0.725807; T 0.609962/0.641825; CT 0.556279/0.606111; AD 0.553421/0.579520. Sensitivity raw alpha 0.393744/0.670457/0.551257/0.487915/0.483975. Zero sections pass every screen in either sample. Exact unrounded coefficients in referenced rows.

Permitted interpretation: Report raw alpha and conditional ordinal omega together with item loading and residual screens.

Prohibited overclaim: Validated five-subscale instrument; omega as observed-score reliability; reliability alone as validity.

Manuscript placement: Results: measurement; Table 2; Figure 1. Role: main.

Authoritative selectors:

- `outputs/psychometrics/reliability.csv`: CSV selector `{}`; {} means all rows
- `outputs/psychometrics/item_diagnostics.csv`: CSV selector `{}`; {} means all rows
- `outputs/psychometrics/measurement_summary.json`: JSON pointer `/sections_passing_both_screens`

## B03: The five-section ULS CFA is inadmissible in both D5 samples.

Research question: Does the proposed five-factor structure hold?

Key evidence (display precision): full: proper=False, maximum factor correlation=1.0655661116781987; sensitivity: proper=False, maximum factor correlation=1.0777362053203807

Permitted interpretation: Factor correlations above one defeat interpretation of apparent fit.

Prohibited overclaim: A supported five-factor model; WLSMV or robust fit indices for this B analysis.

Manuscript placement: Results: measurement; Limitations. Role: main.

Authoritative selectors:

- `outputs/psychometrics/factor_models.csv`: CSV selector `{"model": "hypothesized_five_sections_uls"}`; {} means all rows
- `outputs/psychometrics/factor_correlations.csv`: CSV selector `{}`; {} means all rows

## B04: Parallel analysis retains five D5 factors and two D3 factors, but marker sufficiency fails.

Research question: What does exploratory measurement show?

Key evidence (display precision): Retained factors D5 5/5, D3 2/2 (full/sensitivity). Clear markers D5 [4,4,3,2,1]/[4,3,1,2,1]; D3 [7,2]/[7,2]. Marker-screen passes=False in all four samples.

Permitted interpretation: Exploratory factors describe these records; weakly defined factors do not supply scoring keys.

Prohibited overclaim: Five validated constructs; a validated D3 two-factor scale; independent confirmation.

Manuscript placement: Results: measurement; Supplement. Role: main.

Authoritative selectors:

- `outputs/psychometrics/parallel_analysis.csv`: CSV selector `{}`; {} means all rows
- `outputs/psychometrics/factor_loadings.csv`: CSV selector `{}`; {} means all rows
- `outputs/psychometrics/measurement_summary.json`: JSON pointer `/decisions`

## B05: Polychoric and item-distribution diagnostics are conditional measurement checks.

Research question: Are ordinal assumptions secure?

Key evidence (display precision): Four sample-level assumption rows, 672 pairwise item-correlation rows and 68 item-distribution rows retained in full; see exact-row register.

Permitted interpretation: Report finite-sample latent-normal assumptions and repeated-record limitations.

Prohibited overclaim: Confirmed latent normality or respondent independence; equidistant Likert scores.

Manuscript placement: Methods: measurement; Supplement. Role: supplement.

Authoritative selectors:

- `outputs/psychometrics/measurement_assumptions.csv`: CSV selector `{}`; {} means all rows
- `outputs/psychometrics/item_correlations.csv`: CSV selector `{}`; {} means all rows
- `outputs/psychometrics/item_distributions.csv`: CSV selector `{}`; {} means all rows
- `outputs/psychometrics/measurement_summary.json`: JSON pointer `/limitations`

## B06: All ordinal items enter equal-weight cumulative-threshold distances.

Research question: Which representation is defensible?

Key evidence (display precision): Four cumulative thresholds per item divided by two; squared distance is absolute ordinal-category difference summed over items / 4. D5 25 items, D3 9. No section scores or interpreted HTMT.

Permitted interpretation: No latent or source-section scores are used; HTMT is not interpreted.

Prohibited overclaim: Validated latent scores; reliable section means rescued by HTMT.

Manuscript placement: Methods: descriptive clustering. Role: main.

Authoritative selectors:

- `outputs/psychometrics/item_inventory.csv`: CSV selector `{}`; {} means all rows
- `outputs/clustering/clustering_summary.json`: JSON pointer `/representation`
- `outputs/psychometrics/measurement_summary.json`: JSON pointer `/htmt`

## B07: The fixed selection rule selects k=2 independently in D5 and D3, in both samples.

Research question: How many descriptive profiles are retained?

Key evidence (display precision): k=2 selected for D5 and D3 in both samples from k=2,...,6. All 20 candidate-metric and selection rows retained. Full silhouette D5 0.19886669664785395; D3 exact value in source rows.

Permitted interpretation: Show all k=2 to 6 candidates and the fixed rule; k=2 is a descriptive partition. Nonselected k=3-6 diagnostic values have documented replay differences; preserve accepted values and disclose the register. Selected k=2 and all aggregate selection ranks/screens/decisions agree.

Prohibited overclaim: Four natural types or ordered severity tiers; external prediction from internal fit.

Manuscript placement: Results: descriptive structure; Table 3; Figure 2. Role: main.

Authoritative selectors:

- `outputs/clustering/cluster_selection.csv`: CSV selector `{}`; {} means all rows
- `outputs/clustering/cluster_metrics.csv`: CSV selector `{}`; {} means all rows
- `outputs/clustering/clustering_summary.json`: JSON pointer `/choices`

## B08: Within-dataset item endorsement profiles differ in the accepted k=2 partitions.

Research question: What do selected profiles describe?

Key evidence (display precision): D5 primary P1/P2 2406/207, sensitivity 2307/205; D3 primary 769/335, sensitivity 763/336. Every selected item centroid retained; probabilities refer to literal item endorsement.

Permitted interpretation: Use neutral D5_P1/P2 and D3_P1/P2 labels and literal item agreement probabilities.

Prohibited overclaim: Interchangeable profiles across instruments; severe or low-risk diagnoses; psychological types.

Manuscript placement: Results: descriptive structure; Table 3; Figure 3. Role: main.

Authoritative selectors:

- `outputs/clustering/cluster_sizes.csv`: CSV selector `{"k": 2}`; {} means all rows
- `outputs/clustering/cluster_centroids.csv`: CSV selector `{"k": 2}`; {} means all rows
- `outputs/clustering/selected_profiles.csv`: CSV selector `{}`; {} means all rows

## B09: Omitted-record perturbation stability and quality-sensitivity agreement are high, conditional on released multiplicities.

Research question: How stable are the descriptive partitions?

Key evidence (display precision): Mean primary omitted-record ARI D5 0.99441975014007; D3 0.997231 (rounded). Full/sensitivity common-record ARI D5 0.9937792070102187, D3 0.9962755251009426. 100 repetitions, fraction 0.8. Exact full candidate values in source rows.

Permitted interpretation: ARI/Jaccard describe perturbations against the full-record reference; percentiles are not confidence intervals. Nonselected k=3-6 diagnostic values have documented replay differences; preserve accepted values and disclose the register. Selected k=2 and all aggregate selection ranks/screens/decisions agree.

Prohibited overclaim: External replication; generalizable accuracy; independent people.

Manuscript placement: Results: descriptive structure; Figure 2; Supplement. Role: main.

Authoritative selectors:

- `outputs/clustering/cluster_stability.csv`: CSV selector `{}`; {} means all rows
- `outputs/clustering/quality_sensitivity.csv`: CSV selector `{}`; {} means all rows
- `outputs/clustering/clustering_summary.json`: JSON pointer `/stability_interpretation`

## B10: D5_P2 is dominated by one exact repeated pattern; D3 also contains concentrated repeated records.

Research question: How concentrated are the profiles?

Key evidence (display precision): D5 primary P2 200/207=0.966183574879227; sensitivity 200/205=0.975609756097561. D3 primary P2 largest pattern 63/335=0.1880597014925373. Anonymous patterns, not verified people.

Permitted interpretation: Report 200/207 D5_P2 records (96.6184%) and 200/205 (97.5610%) in sensitivity beside stability.

Prohibited overclaim: Population prevalence of a distinct type; fraud or duplicate-person identification; deduplication.

Manuscript placement: Results: descriptive structure; Table 3; Figure 3; Limitations. Role: main.

Authoritative selectors:

- `outputs/clustering/cluster_record_concentration.csv`: CSV selector `{}`; {} means all rows

## C01: Accepted centroid reconstruction reproduces profile sizes and centroids within the fixed tolerance.

Research question: Can accepted targets be reconstructed?

Key evidence (display precision): Accepted sizes and centroid reconstruction pass fixed 1e-12 absolute tolerance in both samples. Original membership archive unavailable in accepted C/D invocation. Two changed D5 quality assignments; exact comparison in source.

Permitted interpretation: Reconstruction of the accepted descriptive target is an audit, not prediction; direct membership comparison only where supplied.

Prohibited overclaim: A trained classifier; held-out accuracy; proof of natural classes.

Manuscript placement: Methods: feasibility audit; Supplement. Role: main.

Authoritative selectors:

- `outputs/modeling/work_package_c/target_reconstruction.csv`: CSV selector `{}`; {} means all rows
- `outputs/modeling/work_package_c/quality_target_comparison.csv`: CSV selector `{}`; {} means all rows

## C02: All 25 D5 survey items define the target; only five contextual metadata fields avoid direct target construction.

Research question: Are independent psychological predictors available?

Key evidence (display precision): 25 direct-target survey fields excluded; 5 contextual fields eligible by information origin; independent psychological predictors=[]; 15 derived-information policies retained.

Permitted interpretation: Psychological correlate identification is unavailable under this target design.

Prohibited overclaim: Leakage-free prediction using trust, thinking or decision items that construct the target.

Manuscript placement: Results: predictive-feasibility boundary; Table 4. Role: main.

Authoritative selectors:

- `outputs/modeling/work_package_c/feature_eligibility.csv`: CSV selector `{}`; {} means all rows
- `outputs/modeling/work_package_c/derived_information_policy.csv`: CSV selector `{}`; {} means all rows

## C03: Forty of 41 D5_P2 held-out records share a full pattern with training.

Research question: Would a record-random split establish prediction?

Key evidence (display precision): Primary P2 train/test 166/41; 40 test records have training pattern overlap, 1 unseen; largest group=200 > both allocations. P1 train/test 1924/482 with 65 overlapping and 417 unseen records. All 36 split/fold overlap rows retained.

Permitted interpretation: The 200-record group exceeds both requested P2 allocations (166/41); the specified intact-pattern allocation is impossible.

Prohibited overclaim: Generalizable predictive performance; fabricated effective sample size; infeasibility of every imaginable future design.

Manuscript placement: Results: predictive-feasibility boundary; Table 4. Role: main.

Authoritative selectors:

- `outputs/modeling/work_package_c/evaluation_overlap.csv`: CSV selector `{}`; {} means all rows
- `outputs/modeling/work_package_c/group_allocation_feasibility.csv`: CSV selector `{}`; {} means all rows
- `outputs/modeling/work_package_c/record_concentration.csv`: CSV selector `{}`; {} means all rows

## C04: C stops at the accepted feasibility blocker; no model comparison, calibration or explanation was performed.

Research question: What predictive evidence was produced?

Key evidence (display precision): gate.status=blocked; modeling_performed=False; explainability_performed=False; best_model=null; performance/explanations not applicable.

Permitted interpretation: Retain the negative feasibility result and remove V3 prediction/XAI claims.

Prohibited overclaim: Classifier rankings, F1/AUC, SHAP, LIME, causal explanations or deployment readiness.

Manuscript placement: Results; Discussion; Conclusion. Role: main.

Authoritative selectors:

- `outputs/modeling/work_package_c/predictive_audit_summary.json`: JSON pointer `/gate`
- `outputs/modeling/work_package_c/predictive_audit_summary.json`: JSON pointer `/performance_metrics`
- `outputs/modeling/work_package_c/predictive_audit_summary.json`: JSON pointer `/explanations`

## C05: Accepted metadata marginals are descriptive only.

Research question: What contextual description can remain?

Key evidence (display precision): 318 accepted marginal rows across full, fixed-target quality and refitted-target quality variants; no hypothesis tests or released joint individual metadata.

Permitted interpretation: Single-field marginal counts by fixed target and sensitivity may appear in the supplement.

Prohibited overclaim: Demographic effects, joint individual records, significance, causal correlates or fairness validation.

Manuscript placement: Supplement: contextual marginals. Role: supplement.

Authoritative selectors:

- `outputs/modeling/work_package_c/metadata_profile_descriptions.csv`: CSV selector `{}`; {} means all rows

## D01: D3 records contain four ordered self-reported CGPA bands with 1104 eligible records.

Research question: What outcome is observed?

Key evidence (display precision): 1104 eligible records; ordered-band totals 8/204/649/243. P1 counts 6/138/443/182; P2 2/66/206/61. Recorded bands: Below 2.50, 2.51-3.00, 3.01-3.50, Above 3.50.

Permitted interpretation: Preserve the literal bands and unknown exact-2.50 boundary; compare nominal profiles.

Prohibited overclaim: Exact GPA means or midpoints; ordinal ordering of profiles; objective achievement.

Manuscript placement: Methods: outcome; Results: CGPA; Table 5; Figure 4. Role: main.

Authoritative selectors:

- `outputs/outcome_validation/work_package_d/cgpa_eligibility.csv`: CSV selector `{}`; {} means all rows
- `outputs/outcome_validation/work_package_d/sample_accounting.csv`: CSV selector `{}`; {} means all rows
- `outputs/outcome_validation/work_package_d/cgpa_distributions.csv`: CSV selector `{}`; {} means all rows
- `outputs/outcome_validation/work_package_d/cgpa_profile_descriptions.csv`: CSV selector `{}`; {} means all rows

## D02: The full-record rank comparison is very small and inconclusive.

Research question: Do D3 profiles differ in CGPA bands?

Key evidence (display precision): H(1)=2.8025254004; nominal p=0.0941159605; H/(N-1)=0.0025408209; Cliff delta(P2-P1)=-0.055901248 (display precision; exact source rows retained).

Permitted interpretation: Report H=2.8025254, nominal p=0.094116, H/(N-1)=0.00254082 and delta(P2-P1)=-0.0559012.

Prohibited overclaim: Established harm or benefit; no association, equivalence or a reversed hypothesis.

Manuscript placement: Results: CGPA; Table 6; Discussion. Role: main.

Authoritative selectors:

- `outputs/outcome_validation/work_package_d/cgpa_comparisons.csv`: CSV selector `{"variant": "full"}`; {} means all rows

## D03: Fixed-target and refitted-target sensitivities remain small and inconclusive.

Research question: Does quality sensitivity alter that outcome interpretation?

Key evidence (display precision): Fixed-label sensitivity n=1099, P1/P2=764/335; nominal p=0.0853273078, delta=-0.0574783152. Refit sensitivity P1/P2=763/336; p=0.1054489897, delta=-0.0540395057. Exact H/effect values in source rows.

Permitted interpretation: Distinguish fixed labels (764/335) from refitted labels (763/336); retain all primary records.

Prohibited overclaim: An independent replication; selecting the smallest p; ordered severity trends.

Manuscript placement: Results: CGPA; Table 6. Role: main.

Authoritative selectors:

- `outputs/outcome_validation/work_package_d/cgpa_comparisons.csv`: CSV selector `{}`; {} means all rows
- `outputs/outcome_validation/work_package_d/record_concentration.csv`: CSV selector `{}`; {} means all rows
- `outputs/outcome_validation/work_package_d/profile_reconstruction.csv`: CSV selector `{}`; {} means all rows

## D04: All nine conditional percentile intervals for Cliff delta include zero.

Research question: How dependent is uncertainty on sampling assumptions?

Key evidence (display precision): 9/9 intervals include zero; 10000 resamples each; invalid replicates=0. Primary record interval [-0.12106098247384663,0.007597383692719745]; pattern [-0.13092019268659044,0.018237741960858058]; institution [-0.1126954866080093,0.0765655748205707].

Permitted interpretation: Show record, intact full-pattern and literal-institution resampling assumptions; no population-coverage or selection-uncertainty guarantee.

Prohibited overclaim: Design-valid population confidence intervals; proof of equivalence or respondent independence.

Manuscript placement: Results: CGPA; Table 6; Figure 4; Limitations. Role: main.

Authoritative selectors:

- `outputs/outcome_validation/work_package_d/conditional_uncertainty.csv`: CSV selector `{}`; {} means all rows
- `outputs/outcome_validation/work_package_d/outcome_summary.json`: JSON pointer `/uncertainty`

## D05: Two nominal profiles yield only one contrast.

Research question: Is a post-hoc family needed?

Key evidence (display precision): Two nominal profiles, one sole pairwise contrast; no additional post-hoc family.

Permitted interpretation: The sole Cliff contrast accompanies the rank comparison; no additional pairwise search.

Prohibited overclaim: Undisclosed multiple-comparison fishing or unperformed post-hoc tests.

Manuscript placement: Methods: outcome. Role: supplement.

Authoritative selectors:

- `outputs/outcome_validation/work_package_d/outcome_summary.json`: JSON pointer `/posthoc`

## D06: The external workbook has 239 records and 227 source-flagged active users: USA 116 and Indonesia 111.

Research question: What is the external sample?

Key evidence (display precision): Workbook: 2 worksheets, 239 records, 41 fields, 41 codebook entries. USA 122 source /116 active; Indonesia 117/111. Six nonactive records per country, whole 29-item battery missing. No raw deletions.

Permitted interpretation: Keep the countries separate and report each six-record nonactive exclusion under the source flag.

Prohibited overclaim: Bangladesh population replication; representative country samples; new exclusions or Vietnam substitution.

Manuscript placement: Methods: external compatibility; Table 7. Role: main.

Authoritative selectors:

- `outputs/external_validation/work_package_d/workbook_inventory.csv`: CSV selector `{}`; {} means all rows
- `outputs/external_validation/work_package_d/field_audit.csv`: CSV selector `{}`; {} means all rows
- `outputs/external_validation/work_package_d/sample_accounting.csv`: CSV selector `{}`; {} means all rows
- `outputs/external_validation/work_package_d/population_marginals.csv`: CSV selector `{}`; {} means all rows

## D07: All 29 external items and 34 Bangladesh items are crosswalked; no exact common anchors exist.

Research question: Are instruments comparable?

Key evidence (display precision): 29 external items and 34 Bangladesh items covered. Exact common anchors=0. External domains GAID11/CT11/TP7; different wording and outcome meaning.

Permitted interpretation: External thinking items measure a different wording/domain; task performance is self-rated, not CGPA.

Prohibited overclaim: Bangladesh-to-USA/Indonesia latent equivalence; replicated profiles; objective performance.

Manuscript placement: Results: compatibility; Limitations. Role: main.

Authoritative selectors:

- `outputs/external_validation/work_package_d/item_compatibility.csv`: CSV selector `{}`; {} means all rows
- `outputs/external_validation/work_package_d/bangladesh_item_coverage.csv`: CSV selector `{}`; {} means all rows
- `outputs/external_validation/work_package_d/external_summary.json`: JSON pointer `/bangladesh_compatibility`

## D08: Original language instruments and translation/adaptation evidence are unavailable.

Research question: Are translations equivalent?

Key evidence (display precision): No original translated/adapted instruments available. Common English codebook alone cannot verify semantic equivalence.

Permitted interpretation: The common English workbook/codebook is insufficient to establish semantic equivalence.

Prohibited overclaim: Verified translation, shared response meaning, country latent mean comparison.

Manuscript placement: Methods; Limitations. Role: main.

Authoritative selectors:

- `outputs/external_validation/work_package_d/external_summary.json`: JSON pointer `/translation_evidence`

## D09: Country ULS fits and subdimension reliabilities show limitations and are not invariance tests.

Research question: What country-specific measurement checks were obtained?

Key evidence (display precision): Six country ULS diagnostics; 12 subdimension-reliability rows. USA CT maximum residual=0.4028139446185877 and RMSR=0.12029828837050682; Indonesia CT maximum factor correlation=0.9535404533652998. All diagnostics retained, including TP residuals.

Permitted interpretation: Retain all six diagnostics, including USA thinking residual misfit and Indonesia thinking factor correlation.

Prohibited overclaim: Pooled measurement validity; reliable scale scores inferred from one fit index.

Manuscript placement: Results: compatibility; Supplement. Role: main.

Authoritative selectors:

- `outputs/external_validation/work_package_d/subdimension_reliability.csv`: CSV selector `{}`; {} means all rows
- `outputs/external_validation/work_package_d/country_factor_diagnostics.csv`: CSV selector `{}`; {} means all rows
- `outputs/external_validation/work_package_d/country_factor_loadings.csv`: CSV selector `{}`; {} means all rows
- `outputs/external_validation/work_package_d/country_factor_correlations.csv`: CSV selector `{}`; {} means all rows

## D10: GAID configural follow-up fails for Indonesia and the multigroup fit.

Research question: Can ordinal equality testing proceed?

Key evidence (display precision): GAID follow-up pass USA=True, Indonesia=False, multigroup=False. Scaled RMSEA 0.047488040604628454/0.12112118223059988/0.091470 (last rounded); scaled/robust indices and all 388 parameter rows retained.

Permitted interpretation: Report scaled and robust indices without substituting one convention; stop before equality constraints.

Prohibited overclaim: Established threshold/loading/intercept invariance or latent mean comparability.

Manuscript placement: Results: compatibility; Table 7. Role: main.

Authoritative selectors:

- `outputs/external_validation/work_package_d/ordinal_model_fit.csv`: CSV selector `{}`; {} means all rows
- `outputs/external_validation/work_package_d/ordinal_model_parameters.csv`: CSV selector `{}`; {} means all rows
- `outputs/external_validation/work_package_d/external_summary.json`: JSON pointer `/ordinal_engine/decisions`

## D11: Category support blocks CT and TP ordinal invariance testing; the equality table is intentionally empty.

Research question: Why are other equality tests absent?

Key evidence (display precision): 58 item-country category-support rows; CT/TP blocked; ordinal equality-comparison table has 0 data rows. No item deletion or category merging.

Permitted interpretation: No merging response categories, dropping items or changing constructs to obtain invariance.

Prohibited overclaim: Missing tests as support for invariance; successful country scale validation.

Manuscript placement: Results: compatibility; Table 7; Supplement. Role: main.

Authoritative selectors:

- `outputs/external_validation/work_package_d/item_category_support.csv`: CSV selector `{}`; {} means all rows
- `outputs/external_validation/work_package_d/item_distributions.csv`: CSV selector `{}`; {} means all rows
- `outputs/external_validation/work_package_d/ordinal_equality_comparisons.csv`: CSV selector `{}`; {} means all rows
- `outputs/external_validation/work_package_d/external_summary.json`: JSON pointer `/invariance_interpretation`

## D12: Four within-country observed-item associations are small, uncertain and nonsignificant after Holm adjustment.

Research question: What bounded observed associations remain?

Key evidence (display precision): USA n116: GAID6-CT9 rho=0.09763037786486334, Holm p=0.9105; GAID6-TP6 rho=-0.03382755893719395, Holm p=1. Indonesia n111: rho=-0.034280 (rounded), Holm p=1; rho=0.121467 (rounded), Holm p=0.8196. Four fixed tests; 9999 permutations and 5000 bootstrap draws. Full exact statistics in source rows.

Permitted interpretation: Report exact item pairs, n, rho, permutation p, four-test Holm p and conditional intervals; exploratory only.

Prohibited overclaim: Cross-country differences; replicated Bangladesh mechanisms; absence of effects; latent or causal associations.

Manuscript placement: Results: observed-item context; Table 8; Figure 5. Role: main.

Authoritative selectors:

- `outputs/external_validation/work_package_d/observed_item_associations.csv`: CSV selector `{}`; {} means all rows
- `outputs/external_validation/work_package_d/external_summary.json`: JSON pointer `/relationship_scope`
