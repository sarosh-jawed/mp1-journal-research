# MP1 Journal Research

MP1 studies what released survey records can support about generative AI use and dependence in
higher education. The journal analysis uses two Bangladesh releases, D5 (2,613 records) and
D3 (1,104 records), and a separate U.S.-Indonesia survey workbook for instrument compatibility.
See the [source provenance](docs/source_provenance_reconciliation.md) and
[dataset citations](docs/manuscript_replacement_text.md#required-positioning-and-source-citation).

## Verified journal analysis

| Work package | Methods and findings |
| --- | --- |
| A · [Data integrity](docs/data_integrity.md) | Verified released files and audited provenance, repeated records, and response quality. All released records were retained. |
| B · [Measurement and clustering](docs/measurement_cluster_structure.md) | Assessed reliability and ordinal factor structure, then compared K-means partitions and response-quality sensitivity. The proposed five-section measurement model lacked support, and each Bangladesh release yielded a descriptive two-profile partition. |
| C · [Predictive feasibility](docs/predictive_feasibility.md) | Reconstructed the D5 target and audited predictor leakage and split overlap. Near-total repeated-pattern overlap in the smaller held-out profile made the prespecified evaluation unsuitable, so classifier fitting and explainability analyses were withheld. |
| D · [Outcome and compatibility](docs/outcome_cross_cultural_validation.md) | Used rank-based comparisons for self-reported D3 CGPA bands and audited item and ordinal model comparability in the external workbook. The CGPA association was very small and inconclusive. The external audit did not establish cross-country measurement equivalence. |
| E · [Publication and reproducibility](docs/publication_reproducibility.md) | Froze the retained findings, mapped manuscript claims to evidence, and verified the publication tables and figures from accepted aggregate outputs. |

The profiles describe response patterns. Respondent independence and natural psychological
types remain unestablished. One exact released record pattern accounts for 200 of 207 records
in the smaller D5 profile. Source-documentation gaps remain, and the full historical replay
differs in 247 cells for nonselected B candidates (`k=3–6`). Selected `k=2` results and
selection decisions were preserved. See the [discrepancy register](docs/publication_discrepancy_register.md)
for the bounds and interpretation.

## Repository map

- [`src/mp1/`](src/mp1/) contains the analytical implementation. The entry points cover
  [provenance](scripts/provenance_audit.py), [response quality](scripts/response_quality.py),
  [psychometrics](scripts/psychometrics_analysis.py), [clustering](scripts/clustering_analysis.py),
  [predictive feasibility](scripts/predictive_audit.py), [CGPA](scripts/outcome_validation.py),
  and [external compatibility](scripts/external_validation.py).
- [`config/`](config/) defines input paths, analysis settings, and frozen evidence hashes. [`tests/`](tests/) contains the verification tests.
- [`outputs/`](outputs/) contains reviewed aggregates. Start with the [retained results](outputs/publication/work_package_e/retained_results_master.csv),
  [evidence map](outputs/publication/work_package_e/manuscript_evidence_map.md), and [publication inventory](docs/work_package_e_outputs.md).

## Reproduce the documented analysis

Use the [frozen journal commit](https://github.com/sarosh-jawed/mp1-journal-research/commit/0abdb6ea715e2341d0e28449e154ec4f9ad1f069)
in a disposable checkout and follow the [hash-locked Python and R setup](environment/README.md).
From the repository root, the public check uses accepted aggregates and synthetic tests, with
no respondent-level inputs:

```bash
PYTHONPATH=src .venv/bin/python scripts/check_publication.py
```

For source-level replay, supply the five authorized, hash-verified files listed in the
[publication freeze manifest](config/publication_freeze.json). The
[replay script](scripts/verify_publication_replay.py) takes the input directory via `--inputs`,
a new private directory via `--work`, and an aggregate report path via `--report`. It runs the
frozen A–D methods in a disposable baseline checkout. The
[reproducibility guide](docs/publication_reproducibility.md#verification-levels) explains each
check. Raw inputs and respondent-level artifacts are excluded from GitHub.

The original [E Colab delivery guide](docs/work_package_e_colab.md) documents the historical
overlay workflow and expects its earlier A–D base. Use the public check above for the complete
frozen journal checkout.
