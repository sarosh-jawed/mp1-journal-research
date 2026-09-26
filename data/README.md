# Data locations

Research data are intentionally excluded from GitHub.

The fresh Google Drive workspace is the authoritative storage location.

Expected raw inputs:

- `Source Data/D5 Bangladesh/D5_cognitive_dependence_raw.csv`
- `Source Data/D3 Bangladesh/D3_dependency_vulnerability_raw.csv`
- `Source Data/US Indonesia/` for the approved external validation files

Never edit the raw source files in place. Derived datasets belong in the local or Colab `data/interim` and `data/processed` directories and must be reproducible from code.
