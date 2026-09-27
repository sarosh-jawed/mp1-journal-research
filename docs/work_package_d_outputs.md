# Work Package D output inventory

All listed public outputs are aggregates. Paths are relative to the repository root.
CSV SHA-256 values are recorded in the adjacent outcome or external summary JSON.
The delivery also provides exact file sizes and hashes in its change and package manifests.

## D3 academic outcomes

Directory: `outputs/outcome_validation/work_package_d`.

| File | Rows | Meaning |
|---|---:|---|
| `cgpa_comparisons.csv` | 3 | Tie-corrected H, nominal p, rank epsilon squared and Cliff delta |
| `cgpa_distributions.csv` | 24 | Four recorded bands by profile and analytical view |
| `cgpa_eligibility.csv` | 4 | Recorded labels, eligibility and absence of midpoint imputation |
| `cgpa_profile_descriptions.csv` | 6 | Median and quartile bands without numerical grade means |
| `conditional_uncertainty.csv` | 9 | Nine conditional intervals with named units, seeds and resample counts |
| `profile_reconstruction.csv` | 2 | Exact accepted full/refit centroid agreement and optional membership comparison |
| `record_concentration.csv` | 6 | Retained complete-record multiplicities and largest-pattern shares |
| `sample_accounting.csv` | 3 | Explicit source, eligible and sensitivity denominators |
| `outcome_summary.json` | JSON | Source, settings, executed-code and artifact hashes; methods, versions and limitations |

## U.S.-Indonesia compatibility and measurement

Directory: `outputs/external_validation/work_package_d`.

| File | Rows | Meaning |
|---|---:|---|
| `bangladesh_item_coverage.csv` | 34 | All 34 accepted Bangladesh items and absence of direct anchors |
| `country_factor_correlations.csv` | 8 | Source-model factor correlations by country |
| `country_factor_diagnostics.csv` | 6 | Six country-specific ordinal ULS diagnostic fits and admissibility |
| `country_factor_loadings.csv` | 58 | Country-specific standardized item loadings |
| `field_audit.csv` | 41 | All 41 data fields and their Codebook roles |
| `item_category_support.csv` | 58 | Observed/absent categories and sparse marginal cells |
| `item_compatibility.csv` | 29 | All 29 external items, dimensions and Bangladesh thematic crosswalk |
| `item_distributions.csv` | 290 | Country-specific item category counts and proportions |
| `observed_item_associations.csv` | 4 | Four exploratory within-country correlations, conditional intervals and Holm p-values |
| `ordinal_equality_comparisons.csv` | 0 | Intentional zero-row equality table: real-data prerequisites failed |
| `ordinal_model_fit.csv` | 3 | Three GAID WLSMV configural fits and follow-up screens |
| `ordinal_model_parameters.csv` | 388 | Aggregate GAID parameters; group 1 is USA, group 2 is Indonesia in multigroup rows |
| `population_marginals.csv` | 103 | Country-specific source-label marginals for released and analytic samples |
| `sample_accounting.csv` | 2 | Explicit source, eligible and sensitivity denominators |
| `subdimension_reliability.csv` | 12 | Raw alpha for six source dimensions in each country; no validation claim |
| `workbook_inventory.csv` | 2 | Every-sheet structural inspection and complete cell coverage |
| `external_summary.json` | JSON | Source, settings, executed-code and artifact hashes; methods, versions and limitations |

## Private runtime artifacts, excluded from Git and ZIP

Under ignored `data/interim/work_package_d/`:

- `d3_memberships.csv`: reconstructed record-aligned D3 full/refit memberships.
- `d3_private_manifest.json`: private membership-file fingerprint.
- `external_model_input.csv`: private country and item rows supplied to R.
- `ordinal_request.json`: local paths and measurement-engine specification.
- `ordinal_result.json`: intermediate ordinal-engine response.
- `ordinal_engine.log`: captured R output for inspection.

Raw datasets, original workbook, accepted quality flags and original B memberships are
private inputs and are not included in this delivery. None is overwritten.

## Code, configuration and review material

- `config/work_package_d.yaml` and `config/work_package_d_crosswalk.csv`.
- `src/mp1/outcome_validation.py`, `src/mp1/cross_cultural.py` and `src/mp1/d_validation.py`.
- `scripts/outcome_validation.py`, `scripts/external_validation.py`,
  `scripts/ordinal_invariance.R` and `scripts/verify_work_package_d.py`.
- `tests/test_outcome_validation.py` and `tests/test_cross_cultural.py`.
- Scientific methods/results, Colab instructions, review checklist, proposed Control append
  and execution validation record in the new D documentation.
- README and handoff navigation updates; CI installs the scoped R measurement dependencies.

No existing accepted A/B/C aggregate file is replaced. Public D outputs are candidates for
versioning after review, not evidence of publication approval.
