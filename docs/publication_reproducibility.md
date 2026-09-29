# Reproducibility and provenance statement

## Exact scope

The frozen scientific baseline is Git commit
`56b335c705ef15d5a261865382dd79991d2a93a2`. The canonical MP1 Research Control revision
modified on 2026-09-27 at 06:07:38.678 UTC accepts A, B and D and freezes C as the accepted
predictive-feasibility blocker. E does not revise that acceptance or start a new empirical
question. README and ASTRA_HANDOFF now show D accepted and E active.

`config/publication_freeze.json` records SHA-256 digests for all 123 accepted files except the
three permitted handoff/CI updates. It explicitly identifies the complete set of 60 accepted
output files. Historical pending-review strings and A closure flags are preserved as original
provenance, with their later canonical disposition recorded separately. They are not current
instructions to reopen an accepted work package.

All E numerical tables and figures are transformations of those accepted aggregates. The
31-finding manuscript map resolves every selector against the accepted-output allowlist and
checks the file hash before reading. The complete row register preserves every accepted CSV
row, its exact strings, one-based data-row position, source hash and applicable interpretation
constraints. No model is fitted by the publication renderer. All full-precision statistical
values remain available; display tables round to four decimal places and percentages to two.
The original V3, raw data, membership files, diagnostic split files and bootstrap replicates
are not distributed in the E bundle.

## Environment lock and its limits

Accepted B/C/D manifests record numpy 2.1.3, pandas 2.2.3, scipy 1.16.3, scikit-learn 1.6.1,
semopy 2.3.11 and factor-analyzer 0.5.1; the external manifest also records openpyxl 3.1.5.
Accepted D records R 4.6.1, lavaan 0.7.2 and semTools 0.5.6 (CRAN source versions 0.7-2 and
0.5-6). These versions are preserved. The historical D implementation-validation note describes
a different earlier runtime; the manifests accompanying accepted main are authoritative for
the executed result set.

The complete original transitive environment, Python build, BLAS/OpenMP libraries and thread
configuration were not captured. E therefore supplies a tested reconstruction, not a claim to
have recovered every original binary. Python 3.12.14 is used for the E verification runtime.
`environment/requirements.lock` pins all Python packages with distribution hashes;
`bootstrap.lock` pins pip, setuptools, wheel and their dependency. Install bootstrap first,
then the full lock with `--require-hashes --no-build-isolation`, so source builds use the
locked build tools. `R-lock.json` pins the R source archive and all required non-base R packages
with hashes and installation order. Suggested R packages are not used. The installer creates
a local library and verifies runtime and package versions; it never changes system R.
Publication fonts come from the pinned matplotlib distribution and are embedded in PDF.

Linux compiler/system-library prerequisites are documented and tested, but the original host
is not reconstructed as a bit-identical container. CI uses Ubuntu 24.04, Python 3.12.14 and the
same locks. It contains no Drive mount, research-source download, credentials or raw-data input.
GitHub Actions itself is not claimed to have run on this uncommitted delivery.

## Verification levels

1. **Frozen evidence integrity:** exact SHA-256 verification for accepted files and all manifest
   links. No tolerance applies to changes in the accepted artifact bytes.
2. **Aggregate reconciliation:** parse all accepted outputs; reconcile item and profile totals,
   all-k centroid probabilities against pooled item counts, concentration arithmetic, C overlap
   and allocation constraints, and D rank/effect calculations and four-test Holm adjustment.
   Empty ordinal-equality output is an intended scientific stop, not missing evidence.
3. **Publication reconstruction:** generate figures, tables, map and row register twice under
   the E lock, including from a fresh checkout, and compare output bytes. PDF/SVG dynamic dates
   are suppressed and SVG IDs are fixed. These checks require no private records.
4. **Scientific source replay:** run the unchanged accepted methods in a disposable baseline
   clone using byte-verified private sources. Preserve replayed aggregates for diagnosis, then
   restore only that clone's accepted output bytes before downstream frozen-input checks.
   Caller files and source inputs are hashed before and after. Retained interpretation and
   model-gate decisions must match exactly. Counts and categorical evidence must match exactly;
   noniterative arithmetic uses absolute tolerance 1e-10; iterative polychoric/factor/ULS/WLSMV
   outputs use 1e-5. Statistical tolerance is not a substitute for agreement of decisions.
5. **Manuscript provenance:** verify V3's complete file hash, all paragraph anchors and image
   hashes in document order. Every paragraph, table and figure has a disposition. The original
   manuscript is unchanged. Audit output reproduces from its frozen review specification in CI.

The first verifier mistakenly classified optimizer-derived polychorics and their eigenvalues
as exact arithmetic. The observed largest polychoric discrepancy was 4.19e-8, below the accepted
optimizer's 1e-7 stopping tolerance. That classification was corrected to the declared iterative
category. Discrete cluster counts and resampling statistics were not relaxed. Actual remaining
mismatches and their implications are reported in `docs/work_package_e_validation.md` and the
source-replay JSON. A positive synthetic/aggregate check is not a claim that every scientific
replay result passed.

## Source-access limits

D5/D3 active source CSVs, the external workbook, the supplied dictionary and V3 were available
and are hash-identified in the freeze. The two CSV hashes match the accepted public-release
comparisons. E can recheck their record and pattern arithmetic but cannot reconstruct author
cleaning logs, missing item-level codebooks, translation protocols or unique-person identities.
Those are accepted external limitations. Original private B membership files were not supplied;
C and D use their already accepted centroid reconstruction contract. Recomputed memberships
are preserved privately for diagnosis and are not misrepresented as the original membership
archive. No author contact or data-source change was made.

## Controlled recovery on 2026-09-28

The original E ZIP survived. Original source-replay evidence is preserved byte-identically;
its complete-grid FAIL is not rewritten. Current reports explicitly separate recovered
scientific replay evidence from fresh public checks. Source analyses were not rerun.
The new aggregate-only recovery check verifies all 247 differences and shows every candidate
rank, screen and retained choice unchanged. E may close as a retained-result lock with the
disclosed candidate-only limitation under the user's recovery rule. See the discrepancy
register for exact bounds, unknown numerical cause and missing private execution artifacts.

Local R was rebuilt from the unchanged source hash. Because system package installation
could not switch user in this container, compiler/development packages were extracted only
to a local directory, with hashes recorded in environment/recovery_build_dependencies.json.
These are current build details, not claims about the original accepted runtime. Standard
Colab/CI installation continues to use the documented compiler prerequisites and pinned R.
