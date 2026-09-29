# MP1 publication reconstruction environment

Python: 3.12.14. Linux x86-64 is the verified platform. Recorded scientific versions are
constraints in `accepted-constraints.txt`. New rendering and bootstrap packages are declared
in `requirements.in`; the complete, hash-checked transitive resolution is `requirements.lock`.
Do not compile a new lock during ordinary acceptance or silently upgrade a dependency.

Install into an empty virtual environment:

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install --require-hashes -r environment/bootstrap.lock
.venv/bin/python -m pip install --require-hashes --no-build-isolation -r environment/requirements.lock
```

Source builds use the pinned setuptools/wheel bootstrap. Package hashes authenticate source
archives or wheels; they do not imply identical compiler binaries across machines. The E
verification report records the actual installed versions and platform. The accepted original
runtime omitted some transitive and system details; this is an explicitly tested reconstruction.

R: 4.6.1. Install compiler/library prerequisites on Debian/Ubuntu, then use the local installer:

```bash
sudo apt-get update
sudo apt-get install -y --no-install-recommends build-essential gfortran pkg-config zlib1g-dev libbz2-dev liblzma-dev libpcre2-dev libcurl4-openssl-dev libtirpc-dev
.venv/bin/python scripts/install_locked_r.py
```

The installer checks every source-archive SHA-256 from `R-lock.json`, installs to
`.venv/ordinal/`, verifies versions, and writes `runtime.json`. R base packages come from the
locked R source; required non-base packages are MASS, mnormt, pbivnorm, numDeriv, quadprog,
lavaan, semTools and jsonlite. No suggested packages are required. `--reuse-r PATH` is allowed
only for a previously verified R 4.6.1 interpreter; package installation is still fresh and
hash-checked. No system R replacement occurs.

All checks set `PYTHONHASHSEED=0`, `OPENBLAS_NUM_THREADS=1`, `OMP_NUM_THREADS=1` and
`MKL_NUM_THREADS=1`. The original B runtime's thread/BLAS configuration was not recorded.
No attempt is made to tune these settings until a preferred empirical answer appears.

Lock maintenance (not an acceptance command): rebuild the lock with the recorded uv version
only after separately reviewing why an environment change is necessary. Keep the old lock
and evidence digests, rerun synthetic and aggregate checks, and re-evaluate source reproduction.
Scientific decisions and raw bytes do not change merely because a dependency update exists.
