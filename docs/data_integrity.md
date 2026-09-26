# Data integrity and response quality

This work establishes what is present in the supplied D5 and D3 CSVs and produces
reproducible response-quality indicators. Every source record is retained. The
counts describe records, not verified unique people. The implementation does not
perform construct scoring or any later analysis.

## Source review and limitations

The canonical Research Control document, ASTRA_HANDOFF.md, all existing repository
files, both raw CSVs, the entire attached data dictionary, all six worksheets across
the two advisor workbooks, the one-page advisor plan, and Manuscript V3 were read.
The implementation was accepted at `dab1d4a2ca5eb76681ad58651299f2fc1b62c645`.
The subsequent source review is recorded in `docs/source_provenance_reconciliation.md`.

The public records inspected on 2026-09-26 are:

- D5 version 2: https://data.mendeley.com/datasets/7m94b7yr8w/2
- D3 version 1: https://data.mendeley.com/datasets/6s6nvmpgbb/1

Their descriptions are reference claims stored in configuration. Execution does
not silently fetch newer metadata. Supplied public release CSVs have now been
compared with the active files: both pairs are byte-identical. D5's public CSV
contains 2613 data records, despite the metadata claim of 2614. The reason for
that source-level discrepancy remains unknown. The configured release fingerprints
record this comparison; they do not retrieve or certify future releases.

The supplied DATA_DICTIONARY.md documents D1, engineered D1, and D2 only. It does
not provide D5/D3 definitions. The public D5 questionnaire supplement now documents
five named sections, five variable descriptions per section, and response labels
coded 1 through 5. It does not provide every exact item sentence, composite
scoring, reverse-keying, or cleaning rules. D5 codebook coverage is partially
resolved; D3 still lacks a dedicated codebook. Item eligibility remains grounded
in explicit raw question headers and labels. No scoring or numeric recoding is
implemented.

Research Control and the current user instruction govern the narrower scope.
The older extension workbook and PDF discuss later analyses; those instructions
are not implemented here. The repository currently reports public visibility,
despite the older private-repository wording in Research Control. Visibility and
Research Control were not changed.

## Verified schemas

| Dataset | Records | Columns | Background fields | Survey items |
| --- | ---: | ---: | --- | ---: |
| D5 | 2613 | 30 | Gender; Age; University Type; Academic Level; Department/Discipline | 25 |
| D3 | 1104 | 15 | Gender; Age; Name of University; Academic Level; Current CGPA; Daily AI Usage Time | 9 |

D5 Age contains integer text from 18 through 28. Its other 29 columns are text.
D3 Age contains age-band labels, and all 15 D3 columns are text. CSV has no
intrinsic type system: the audit retains every field as a string and separately
reports inferred lexical types. No respondent identifier or timestamp exists in
either supplied schema.

D5 has five questions under each literal header prefix: AI Usage, Cognitive
Dependence, Trust in AI, Critical Thinking, and Academic Decision-Making. D3 has
nine full-sentence question headers. The exact 45 column names are written to
`outputs/provenance/column_schema.csv`. The exact eligible question names are
listed in `config/analysis.yaml` and `eligible_survey_items.csv`.

All survey responses in these files belong to the five exact labels:
Strongly Disagree, Disagree, Neutral, Agree, Strongly Agree.

## Decisions implemented

- Read strict CSV records, preserving header text, leading zeros, whitespace,
  literal NA strings, field order, and record order. Reject duplicate headers,
  ragged records, malformed quoting, blank records, and missing required columns
  with an error. A header-only file has zero records and undefined proportions.
- Count empty fields, whitespace-only fields, and any exact configured missing
  tokens as missing. The default token list is empty. Do not replace, impute, or
  remove values. Literal NA is therefore a value unless explicitly configured.
- Report exact full-row duplicate groups, all their members, and repetitions
  beyond the first occurrence separately. Do not treat identical anonymous
  records as proof of duplicate people. No de-duplication is applied.
- Check respondent identifiers only when explicitly configured. A missing
  identifier is reported as not available, not as zero duplicate identifiers.
  Composite identifiers are supported; incomplete keys are counted separately.
- Preserve institution labels. NFKC, case folding, and whitespace collapse produce
  diagnostic comparison keys only. No fuzzy merge, affiliation inference, or alias
  is applied. A comparison key is not an approved canonical institution.
- Flag invariance only when every explicitly listed survey item is nonmissing,
  in the allowed response set, and exactly equal to the other items. Use raw
  responses before any possible later reverse scoring, including for D3.
- Exclude background fields from the primary flag and compare membership with a
  diagnostic that includes all columns while retaining the same survey validity
  requirement. Report both the count and membership difference.
- Preserve every row in the primary sample. `include_sensitivity` is the Boolean
  complement of `quality_straight_line`. It does not write a filtered dataset.
- Keep incomplete or invalid survey vectors unassessable and retained. A false
  straight-line flag for such a record is not a certificate of response validity.
  `quality_assessable`, missing, and invalid indicators retain that distinction.
- Bind private flags to the full source SHA-256 and 1-based data-record position.
  These positions are not respondent IDs or physical line numbers.

## Reproduced observations

| Measure | D5 | D3 |
| --- | ---: | ---: |
| Full retained records | 2613 | 1104 |
| Missing cells | 0 | 0 |
| Invalid survey response cells | 0 | 0 |
| Identical full-row groups | 42 | 45 |
| Records belonging to those groups | 493 | 207 |
| Repetitions beyond the first occurrence | 451 | 162 |
| Largest identical group | 200 | 63 |
| Invariant survey vectors | 101 | 5 |
| Invariant percentage of all records | 3.8653% | 0.4529% |
| Invariant vectors when background fields are included | 0 | 0 |
| Records selected by the optional sensitivity indicator | 2512 | 1099 |

D5 has 100 all-Strongly-Agree vectors and one all-Agree vector. D3 has three
all-Agree vectors and two all-Neutral vectors. Invariance alone does not establish
carelessness or justify permanent exclusion.

D3 has 30 exact institution labels and 30 diagnostic comparison keys in both the
public and active files. The evidence review identifies 29 university names and
one constituent college of Dhaka University. Affiliation does not make the college
an alias of the university. Even a possible parent-university grouping would
produce 29 groups, not 22. No labels are merged. The authors' roster and counting
rule are still required; the observed labels do not prove respondent affiliations.

Source SHA-256 fingerprints:

```text
D5 3f8cf8f041a09b8d1bf1c89eb8e85abc439ff0d1a4c26f26d3c0b7be217e64e2
D3 ca92de616712be5ac129ed60040fccc78e6147119ce10c1806349e9c3240213d
```

These are observations for the supplied files, not expected results hard-coded
into the detection algorithm. Synthetic tests use different columns, values,
sample sizes, and historical claims.

## Running in Colab

Use the existing checkout and mounted Drive. Run from the repository root. The
configuration's `project.drive_root_env` is honored. Input paths are relative to
that root. Relative output paths are resolved from the directory containing
`config/`. Keep the configuration at `config/analysis.yaml` in the checkout.

Set or confirm the Drive location in a Python cell:

```python
import os
from pathlib import Path
import yaml

config = yaml.safe_load(Path("config/analysis.yaml").read_text())
env_name = config["project"]["drive_root_env"]
if not os.environ.get(env_name):
    os.environ[env_name] = input("Full path to the mounted MP1 Journal Research folder: ").strip()
drive_root = Path(os.environ[env_name]).expanduser().resolve()
required = [drive_root / config["data"][key] for key in ("d5_raw", "d3_raw", "data_dictionary")]
absent = [str(path) for path in required if not path.is_file()]
if absent:
    raise FileNotFoundError("Required inputs are missing: " + "; ".join(absent))
```

If Drive is not mounted, mount it first in a separate Python cell:

```python
from google.colab import drive
from pathlib import Path

mount_root = Path.home() / "mp1_drive"
drive.mount(str(mount_root))
```

Install the existing repository requirements if needed, then run the quality
commands before the real-data commands:

```bash
python -m pip install -r requirements.txt
pytest -q
ruff check .
ruff format --check .
PYTHONPATH=src python scripts/provenance_audit.py --config config/analysis.yaml
PYTHONPATH=src python scripts/response_quality.py --config config/analysis.yaml
```

In a Colab code cell, prefix each command with `!`, or put `%%bash` on the first
line of a cell containing shell commands. A Python-set environment variable is
inherited by those commands. No source file is copied, edited, or replaced by the
entry points.

## Expected artifacts

`outputs/provenance/`:

- dataset_summary.csv
- column_schema.csv
- missingness_summary.csv
- duplicate_summary.csv
- categorical_values.csv
- d3_institution_review.csv
- metadata_comparisons.csv
- discrepancies.csv
- provenance_summary.json
- summary.md

`outputs/response_quality/`:

- response_quality_summary.csv
- flagged_response_patterns.csv
- invalid_response_values.csv
- eligible_survey_items.csv
- response_quality_summary.json
- summary.md

`data/processed/response_quality_flags.csv` contains minimal record-level flags
for both datasets. It is excluded from Git. It contains no demographic columns,
full response vectors, or respondent identifiers. Keep it private. Do not force
add it. The aggregate JSON reports contain output checksums and configuration
checksums so a report can be tied to its inputs and settings.

An empty invalid_response_values.csv still contains its header. Review any
unexpected response text before sharing that artifact. Review all aggregate
outputs before allowing them into the public repository.

## Output validation and manual review

For unchanged source fingerprints, confirm the observations in the table above.
If fingerprints differ, investigate the source version before comparing counts.
Do not edit values or rules to make new source versions match these observations.

Check these identities and definitions:

- Retained full-sample count equals raw record count; rows_removed equals zero.
- Missing counts equal their disjoint null, empty, whitespace, and configured-token
  components. Each missing proportion uses the full record count.
- Duplicate member count minus duplicate group count equals duplicate excess.
  Unique record count plus duplicate excess equals raw record count.
- Every original column appears once in column_schema.csv, in its original order.
- D5 has 25 eligible questions and D3 has nine. Background and identifier fields
  do not appear in eligible_survey_items.csv.
- Pattern counts sum to straight_line_rows. Full sample minus straight_line_rows
  equals sensitivity_rows. All proportions use the stated denominator.
- The private indicator contains one row per dataset/source-record pair and the
  matching source checksum. Attach flags before sorting or filtering source rows.
- Check all 30 D3 institution labels, especially possible institutional
  affiliations. Record evidence separately; generated review tables are
  regenerated and should not be the sole storage location for manual decisions.
- Review the 200-record and 63-record identical groups through the private source
  files. Seek source clarification; their existence is not a duplicate-person
  finding and does not authorize deleting them.
- Use source_reconciliation.json and the cited institution review for the current
  issue status. File identity is resolved for the supplied releases. The D5
  metadata count and duplicate-removal definition, D3 institution count, and
  incomplete codebook coverage remain explicitly documented. A matching source
  fingerprint does not resolve those separate questions.

Later code can consume verified flags without duplicating detection logic:

```python
from mp1.audit import load_inputs, repository_path
from mp1.response_quality import read_quality_flags

config, raw, _ = load_inputs("config/analysis.yaml")
d5 = raw["D5"]
flag_path = repository_path("config/analysis.yaml", config["response_quality"]["private_flags"])
flags = read_quality_flags(flag_path, "D5", d5.sha256, len(d5.frame))
```

This loads flags only. It does not authorize or execute a sensitivity analysis.

## Before any manual commit

Run `pytest -q`, `ruff check .`, and `ruff format --check .` again after applying
the files. Review `git diff --check`, `git diff`, and `git status --short`.
Confirm `git check-ignore -v data/processed/response_quality_flags.csv` identifies
an ignore rule. Select source, configuration, tests, documentation, and reviewed
aggregate reports explicitly. Inspect `git diff --cached --name-only` before
committing. Do not use a blanket add command or include source CSVs, private
flags, inspection files, downloaded references, or notebook data outputs.

Suggested commit message, only after the real-data run and review are accepted:

```text
Add immutable provenance and response quality audits
```

The implementation can pass its quality checks while source provenance remains
unresolved. Work Package A must remain active until the material source issues
are reconciled or their limitations and handling are explicitly accepted. Do not
begin the next work package automatically.

## Research Control status

The user has confirmed acceptance of the original implementation, its Colab
results, 39 passing tests, Ruff checks, and successful GitHub CI. Source
reconciliation is a separate acceptance question. See the seven-question closure
matrix in `docs/source_provenance_reconciliation.md` before proposing any closure
update. No Research Control changes are made by this code or the reconciliation
delivery, and no later work package is authorized.
