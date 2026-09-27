# Work Package D execution and verification record

Executed on 2026-09-27 UTC from main commit
`dad222a9a0143887e7e25a72e656ec21d0ebc253`. Remote main was rechecked during packaging and
still matched. No commit or push was made. The canonical Research Control was read in full
before analysis and has not been edited. The proposal for its update is a separate review text.

## Verification results

| Check | Observed result |
|---|---|
| Original accepted synthetic suite before D | 88 passed |
| Complete suite after D | 112 passed, including real R ordinal synthetic fits |
| Ruff lint | All checks passed |
| Ruff formatting | All files pass the format check, including Colab Python fences |
| Real D3 execution | Full, quality-fixed and accepted quality-refit results produced |
| Real external execution | Full workbook audit, country diagnostics, WLSMV screen and four item tests produced |
| Independent numerical reconciliation | Three rank-sum H calculations, all-pairs Cliff effects, probabilities and Holm family agree |
| Frozen A/B/C protection | 81 accepted files verified byte-for-byte |
| Private source immutability | D3 source, accepted combined flags and official workbook hashes unchanged |
| Public aggregate integrity | 24 CSV fingerprints checked against two summary manifests |
| Repeat real-data execution | All 26 public CSV/JSON artifacts byte-identical after deterministic CLI configuration |
| D3 bootstrap diagnostics | No invalid replicate in any of nine 10,000-resample intervals |
| External bootstrap diagnostics | No invalid replicate in any of four 5,000-resample intervals |
| Numerical/model warnings | None outstanding in final real execution or ordinal synthetic checks |
| Colab guide | All seven Python cells parse; execution entry points run on real data locally |
| Privacy review | No respondent identifiers, source row numbers, raw sources or private memberships in public tables |

GitHub Actions itself was not invoked because this delivery is uncommitted. Its workflow was
inspected and updated only to install R/lavaan/semTools/jsonlite before the existing lint,
format and complete test commands. Those commands passed locally. Colab browser execution was
not claimed; the supplied cells and application helper are reviewable and use the executed code.

## Edge cases and numerical inspection

Synthetic checks cover tied outcomes, ordinal monotonic transformations, all-tied outcomes,
invalid CGPA domains, absent profiles, damaged sources/flags/accepted evidence, private-output
redirection, intact repeated-pattern multiplicities, mixed-profile resampling units,
deterministic intervals, workbook formulas, incomplete Codebooks, country-label changes,
noninteger responses, partial missingness, source eligibility conflicts and constant items.

The R synthetic evidence covers a correctly identified invariant five-category model and a
known item-threshold distortion. The equality sequence has the expected incremental degrees
of freedom (12 thresholds, five loadings, five intercepts for six indicators), uses robust
Satorra-2000 differences and detects the injected threshold problem. Missing category support
halts formal comparison. The real-data GAID configural limit is reported as a scientific
boundary, not a program error that should be suppressed.

Repeated execution initially exposed machine-precision ULS output differences (at most about
3.3e-16 in inspected diagnostic/loadings/correlation tables), attributable to semopy internal
set-based parameter ordering across Python processes. D's external CLI now restarts with
`PYTHONHASHSEED=0`; a new independent process reproduced every public artifact byte-for-byte.
No B code, model definition, source value, material estimate or scientific conclusion was
changed. Randomized inference uses explicit local NumPy generators and recorded seeds.

Source values and row order are checked in memory and source bytes checked before/after writes.
The accepted D3 centroid reconstruction is required before outcome testing. Aggregate counts,
tie correction, effect sign, finite results, denominators, multiple-testing adjustment and
artifact hashes are independently reconciled by `scripts/verify_work_package_d.py`.

## Reference environment

| Component | Version |
|---|---|
| Python | 3.12.14 |
| NumPy | 2.3.5 |
| pandas | 2.2.3 |
| SciPy | 1.17.0 |
| scikit-learn | 1.8.0 |
| statsmodels | 0.15.0 |
| semopy | 2.3.11 |
| factor-analyzer | 0.5.1 |
| openpyxl | 3.1.5 |
| PyYAML | 6.0.3 |
| threadpoolctl | 3.6.0 |
| pytest | 9.1.1 |
| Ruff | 0.16.9 |
| R | 4.3.3 |
| lavaan | 0.6.17 |
| semTools | 0.5.6 |

Exact execution evidence, application verification and full file hashes are also included in
the delivery's `validation/` directory and manifests. Environment versions are a reference
record; source/profile/count identity and numerical checks remain mandatory when reproducing
on another platform. Do not accept a material discrepancy merely because a command exits zero.
