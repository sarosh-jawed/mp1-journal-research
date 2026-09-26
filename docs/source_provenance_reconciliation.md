# Source provenance reconciliation

Reviewed 2026-09-26 against accepted main commit `dab1d4a2ca5eb76681ad58651299f2fc1b62c645`. Its GitHub
quality workflow succeeded. The user confirmed the original Colab acceptance,
39 tests, Ruff checks, commit, and push. This review addresses only remaining
source provenance. No analytical algorithm, exclusion rule, or raw value changes.

## Evidence and source attribution

The user identifies the PUBLIC files as official Mendeley downloads. The new
attachments contained D3's public CSV and two byte-identical D5 questionnaire
PDFs, but no separately named D5 CSV. The D5 comparator was recovered, without
altering its bytes, from the already available public-release ZIP:

- Archive: `Dataset on Cognitive Dependence on Generative AI T.zip`.
- Archive SHA-256: `a3494d8971868be89219606ccaa64b7c2b7bdfdbb38badf03f4ec7827d7faf29`.
- Original CSV member basename: `_(AI_Cognitive_Dependence_Survey_Data_BD_StudentsResponses) - Sheet1.csv`.
- `PUBLIC_D5_Mendeley_v2.csv` is its local comparison label, not an assertion that
  this separately named file was present in the new attachments.

Release attribution follows the supplied download evidence and the user's source
designation. The comparison proves identity of the supplied bytes; it does not
authenticate the original respondent collection. No source downloads belong in Git.

The four attached aggregate CSVs match the hashes in the attached
`provenance_summary.json`. Its configuration hash matches accepted main. The
original attached reports are preserved as the pre-reconciliation record.

## Public metadata, public bytes, and active bytes

| Measure | D5 | D3 |
| --- | ---: | ---: |
| Metadata-reported records | 2614 | 1104 |
| Public CSV data records | 2613 | 1104 |
| Active CSV data records | 2613 | 1104 |
| Columns, both files | 30 | 15 |
| Byte length, both files | 803900 | 181067 |
| Exact repeated full-row groups, both files | 42 | 45 |
| Records belonging to repeated groups, both files | 493 | 207 |
| Repetitions beyond first occurrence, both files | 451 | 162 |
| Largest repeated group, both files | 200 | 63 |
| Differing data-record positions | 0 | 0 |

Each pair is byte-identical. An independent strict CSV comparison also confirmed
exact header order, data-record counts, all values, row order, complete row
multisets, and exact repeated-group membership and multiplicity. No respondent
values or individual row fingerprints are needed to report these results.

```text
D5 active and public: 3f8cf8f041a09b8d1bf1c89eb8e85abc439ff0d1a4c26f26d3c0b7be217e64e2
D3 active and public: ca92de616712be5ac129ed60040fccc78e6147119ce10c1806349e9c3240213d
```

The [D5 version 2 metadata](https://data.mendeley.com/datasets/7m94b7yr8w/2)
states 2614 valid responses and describes removal of duplicated responses. The
file has 2613 data records, with no local loss relative to the supplied public
release. The reason for the metadata difference is unknown.

All 451 excess repetitions already occur in the D5 public release. This locates
their provenance but does not establish duplicate people or contradict a known
operational de-duplication rule: the source gives no such rule or cleaning log.
The duplicate-removal statement remains a source claim requiring clarification.

The [D3 version 1 metadata](https://data.mendeley.com/datasets/6s6nvmpgbb/1)
reports 1104 responses from 22 universities. Both files have 1104 records, the
same 30 institution labels with identical frequencies, and the same 162 excess
repeated full records. Their origin in the release is established. The cause of
the repeated patterns and the number of distinct people cannot be recovered from
anonymous rows. All records remain in the primary sample.

## D5 questionnaire coverage

All three pages of the attached supplement were read and visually checked. Both
attached copies have SHA-256
`4fce5c71cb20a7219f9ac4f263138a67ce136a7ac0b27fbd23412aea749f2f1e`.
The ZIP's questionnaire PDF has different bytes, SHA-256
`0454257bcf9120d3aed9a09c235652d7461c16ff606119771801f23e8bb37127`.
Its complete extracted text and the visually reviewed three pages agree with the
attachment. The reason for the PDF byte difference is not established.

| Topic | What the supplement establishes |
| --- | --- |
| Names | AI Usage; Cognitive Dependence; Trust in AI; Critical Thinking; Academic Decision-Making. These are source section names, not a new validation finding. |
| Item membership | Five descriptions explicitly grouped under each of Sections B-F. CSV header prefixes agree with those names. Correspondence by section and listed order is documented in d5_questionnaire_coverage.csv; the PDF has no explicit item IDs. |
| Exact wording | The PDF gives variable descriptions, not all full questionnaire sentences. For example, its comfort/confidence descriptions do not reproduce the CSV's uncomfortable/less-confident statements. Do not silently substitute the descriptions for the raw wording. |
| Likert coding | Page 3 explicitly gives 1=Strongly Disagree, 2=Disagree, 3=Neutral, 4=Agree, 5=Strongly Agree for all behavioral variables. No recoding was performed. |
| Composite scoring | Not documented. No sum, mean, weighting, cutoff, or missing-item scoring rule is specified. |
| Reverse-coded items | Not documented. Absence of a key does not mean that no items require reverse coding in a later scoring scheme. |
| Inclusion/exclusion and cleaning | Not documented in the PDF. Keep the separate Mendeley cleaning description as a source claim. |

Coverage is **partially resolved**. The supplement supports this work package's
item inventory and response-domain check. It does not replace a full item-level
codebook, and the supplied DATA_DICTIONARY.md still lacks D5/D3 sections. These
remaining scoring details do not require invention or later analysis to finish
the present raw-response audit.

## D3 institution evidence

`d3_institution_reconciliation.csv` contains every raw label with the requested
columns: raw_label, proposed_canonical_institution, evidence, status. Confirmed
means the institution name is supported by a public institutional source in the
Bangladesh survey context. It does not validate a respondent's attendance or the
source claim of 22. No proposal is applied to either source CSV.

The name-level review yields 30 distinct proposed entities: 29 university names
and one college. The shortened Stamford label can be expanded to Stamford
University Bangladesh, and Govt can be expanded to Government. Neither change
combines two observed labels. Gono's English alternative name and possible city
spelling variants also have no second raw label to combine.

The [Dhaka University constituent-college directory](https://web5.du.ac.bd/constituentColleges)
lists Government College of Applied Human Science, Azimpur, Dhaka separately.
The indexed official directory was available, while direct requests timed out.
The [2025-26 affiliated-college admissions page](https://collegeadmission.eis.du.ac.bd/en/b45de047fde97gsg488cadae3cfe8e88dc01)
also documents the Home Economics Unit admission process. Affiliation is not
institutional identity. This is the only supported within-list parent link found:

| raw_label | proposed_canonical_institution | evidence | status |
| --- | --- | --- | --- |
| Govt College of Applied Human Science | University of Dhaka, only for an author-approved parent-university grouping | DU constituent-college directory; the college remains a separately named entity | possible |

That proposed grouping would produce 29 groups, not 22. It has not been applied.
No defensible campus, renamed-institution, spelling, or alias consolidation found
in the other labels explains the missing seven groups. Jagannath and Jahangirnagar,
Independent and Islamic, and Primeasia and Asia Pacific are distinct named
institutions. [AUST's institutional page](https://www.aust.edu/) and
[BUET's history](https://me.buet.ac.bd/) also prevent confusion between AUST and
BUET's historical Ahsanullah Engineering College name.

The authors' institution roster and counting rule are required. Do not call
the 30 raw labels 30 verified respondent universities or force them to equal 22.

## Repository changes and regeneration

The existing published_file_sha256 configuration already supports the required
identity evidence. Both verified hashes are now populated. The metadata counts
2614 and 22 and the D5 duplicate-removal claim remain unchanged as source claims.
No src/mp1 or script changes are needed. Two synthetic tests cover matching and
mismatching configured public fingerprints, including preservation of other
warnings and all source rows.

The new machine-readable review files are:

- outputs/provenance/source_reconciliation.json
- outputs/provenance/source_closure_matrix.csv
- outputs/provenance/d3_institution_reconciliation.csv
- outputs/provenance/d5_questionnaire_coverage.csv

These are dated evidence records. Ordinary audit runs do not re-fetch public
pages or regenerate human institution judgments. The original generated
d3_institution_review.csv remains an unmodified raw-label review template.
Regenerate the ordinary provenance reports with the existing script after
applying the configuration. The two identity-unverified warnings should disappear.
The raw dictionary-heading warning remains factually true; the separate review
records its partial D5 supplementation. Generic repeated-record warnings remain
conservative diagnostics and do not supersede the release-origin findings here.

Run from the repository root with the configured Drive environment variable:

```bash
pytest -q
ruff check .
ruff format --check .
PYTHONPATH=src python scripts/provenance_audit.py --config config/analysis.yaml
```

Only the provenance report needs regeneration. The response-quality algorithm,
eligible items, raw fingerprints, and accepted private flags are unchanged.
Its older report remains tied to the original configuration fingerprint and
should not be presented as a newly generated report.

## Closure matrix

| Question | Status | Exact evidence | Prevents closure? |
| --- | --- | --- | --- |
| D5 public 2,614 versus active 2,613 | partially resolved | Mendeley v2 metadata states 2614. The supplied release CSV and active file each contain 2613 data records and are byte-identical. No local record loss is observed; the reason for the metadata count remains unknown. | Yes. Author correction or explanation of the published count. |
| D5 published-file identity | resolved | Both CSVs are 803900 bytes with SHA-256 3f8cf8f041a09b8d1bf1c89eb8e85abc439ff0d1a4c26f26d3c0b7be217e64e2. Headers, every value, order, and exact repeated-row groups agree. The public comparator was recovered from the available release ZIP. | No. None for the compared supplied release. |
| D5 repeated-record provenance and the public duplicate-removal statement | partially resolved | Both files contain the same 42 repeated full-row groups, 493 member records, and 451 excess repetitions; the largest group has 200 records. Repetitions are present in the supplied public release. The source does not define duplicated responses or provide the cleaning log. | Yes. Clarify the duplicate-removal definition and whether a corrected release exists. Retain all records meanwhile. |
| D5 questionnaire/codebook coverage | partially resolved | The complete three-page supplement gives five section names, five variable descriptions per section, and the 1-5 label coding. It does not give verbatim wording for all CSV items, explicit item IDs, composite scoring, reverse keys, or inclusion/exclusion and cleaning rules. The supplied DATA_DICTIONARY.md still has no D5 section. | No. Sufficient for the present raw-response invariance check. Preserve the limitation; do not infer scoring or reverse keys for later work. |
| D3 published-file identity | resolved | Both CSVs are 181067 bytes with SHA-256 ca92de616712be5ac129ed60040fccc78e6147119ce10c1806349e9c3240213d. Headers, all 1104 records, every value, ordering, and repeated groups agree. | No. None for the compared supplied release. |
| D3 22 universities versus 30 labels | unresolved | The public and active CSVs contain the same 30 labels with identical frequencies. The public evidence review identifies 29 university names and one constituent college of Dhaka University. No supported cross-label alias set explains 22. A possible parent-university grouping of that college alone would yield 29 groups. | Yes. Obtain the source authors' 22-institution roster, raw-label mapping, and counting rule. No merges are applied. |
| D3 repeated-record provenance | resolved | Both files contain the same 45 repeated full-row groups, 207 member records, and 162 excess repetitions; the largest group has 63 records. Their presence in the public release is established. Unique people and the cause of repetitions cannot be identified from anonymous rows. | No. None for release provenance. Retain all records; this result does not establish duplicate people or authorize deletion. |

## Questions for the source authors

Draft only; no message has been sent.

1. D5 v2 contains 2613 data records and 451 excess identical full records. Why does its metadata report 2614, what did duplicate removal mean, and is there a corrected release?
2. D3 v1 contains 30 institution labels. Please provide the stated 22-university roster, the raw-label mapping, and the counting rule, including affiliated colleges.

Separate, nonblocking codebook follow-up for future authorization: Is there a D5
item-level codebook giving exact wording and any scoring or reverse-keying rules?

No Research Control closure update is proposed while the blocking source
questions remain unanswered. Do not begin Work Package B.

WORK PACKAGE A MUST REMAIN OPEN
