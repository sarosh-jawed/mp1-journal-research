# Work Package E: complete Colab delivery

**Assessment:** E can close as a qualified retained-result publication lock after manual review.
The original complete-grid source replay remains FAIL, with 247 bounded nonselected B cells
disclosed. See `docs/publication_discrepancy_register.md`. No accepted A-D result is replaced.

Use a fresh Linux CPU Colab runtime. Open `MP1_Work_Package_E.ipynb` from the ZIP or paste the
three exact cells below in order. No GPU or private research sources are required. Allow time
for pinned Python/R installation and a second fresh environment. Network access to GitHub,
PyPI, Python downloads, Ubuntu packages and CRAN is required. The listed scientific packages
are hash-locked; Ubuntu compiler/development packages are build support and are not represented
as an original historical lock. Do not skip a failed command. No cell stages, commits or pushes.

## Required input and behavior

Upload the single complete `MP1_Work_Package_E_Colab_v2.zip`. Cell 1 requires GitHub main to remain
at the exact accepted baseline and refuses to overwrite an existing checkout. It preflights
and applies every complete payload file. Cell 2 installs locks, runs all public checks and
checks an independent baseline clone with fresh Python and R package libraries. It reuses the
locally hash-built R executable for that second environment; it does not rebuild R twice.
Cell 3 validates the preserved replay boundary, freezes accepted hashes again, and downloads
a complete public review ZIP containing the original delivery plus the new local check reports.

These cells do not replay A-D, mount Drive, request raw uploads, or overwrite the recovered
source-replay evidence. The Drive Publication Package folder was empty at recovery; the delivery
does not assume any source or package exists there. The generated review ZIP can be placed there
manually if desired.

## Exact execution cells

### Cell 1

```python
# Cell 1: upload the single ZIP, validate extraction, clone the exact baseline, apply complete files.
from google.colab import files
from pathlib import Path, PurePosixPath
import hashlib, json, os, shutil, stat, subprocess, sys, tempfile, uuid, zipfile

BASELINE = "56b335c705ef15d5a261865382dd79991d2a93a2"
uploaded = files.upload()
if len(uploaded) != 1:
    raise RuntimeError("Upload only MP1_Work_Package_E_Colab_v2.zip.")
name, payload = next(iter(uploaded.items()))
if name != "MP1_Work_Package_E_Colab_v2.zip":
    raise RuntimeError("Unexpected ZIP filename.")
ZIP_PATH = Path("/content") / name
ZIP_PATH.write_bytes(payload)
print("Delivery SHA-256:", hashlib.sha256(payload).hexdigest())
EXTRACT = Path(tempfile.mkdtemp(prefix="mp1-e-delivery-", dir="/content"))
with zipfile.ZipFile(ZIP_PATH) as archive:
    infos = archive.infolist()
    if sum(x.file_size for x in infos) > 100_000_000 or len(infos) > 500:
        raise RuntimeError("Unexpected archive size.")
    if len({x.filename for x in infos}) != len(infos):
        raise RuntimeError("Duplicate archive entries.")
    for info in infos:
        path = PurePosixPath(info.filename)
        if (
            path.is_absolute()
            or ".." in path.parts
            or "\\" in info.filename
            or not path.parts
            or path.parts[0] != "MP1_Work_Package_E"
            or stat.S_ISLNK(info.external_attr >> 16)
        ):
            raise RuntimeError("Unsafe archive path.")
    archive.extractall(EXTRACT)
BUNDLE = EXTRACT / "MP1_Work_Package_E"
REPO = Path("/content/mp1-publication-e")
if REPO.exists():
    raise RuntimeError(
        "Checkout already exists. Use a fresh Colab runtime; do not discard local work."
    )
subprocess.run(
    ["git", "clone", "https://github.com/sarosh-jawed/mp1-journal-research.git", str(REPO)],
    check=True,
)
remote_main = subprocess.check_output(
    ["git", "rev-parse", "origin/main"], cwd=REPO, text=True
).strip()
if remote_main != BASELINE:
    raise RuntimeError(
        "Remote main advanced. Review scope and baseline before applying; no automatic merge."
    )
subprocess.run(["git", "checkout", "--detach", BASELINE], cwd=REPO, check=True)
apply = [
    sys.executable,
    str(BUNDLE / "apply_publication_bundle.py"),
    "--bundle",
    str(BUNDLE),
    "--repo",
    str(REPO),
]
subprocess.run(apply, check=True)
subprocess.run(apply + ["--apply"], check=True)
os.chdir(REPO)
print(
    "Complete E files applied. Nothing committed or pushed. E remains active pending manual qualified acceptance."
)
```

### Cell 2

```python
# Cell 2: install the locks, run all public checks, then verify a fresh checkout without private data.
SETUP_LOG = Path("/content/mp1_e_public_setup.log")


def run_logged(command, cwd=REPO, env=None):
    with SETUP_LOG.open("a") as stream:
        result = subprocess.run(
            [str(x) for x in command], cwd=cwd, env=env, stdout=stream, stderr=subprocess.STDOUT
        )
    if result.returncode:
        print(SETUP_LOG.read_text()[-6000:])
        raise RuntimeError("Command failed; see " + str(SETUP_LOG))


run_logged(
    [
        sys.executable,
        "-m",
        "pip",
        "install",
        "--require-hashes",
        "-r",
        "environment/colab-bootstrap.lock",
    ]
)
run_logged(["uv", "python", "install", "3.12.14"])
run_logged(["uv", "venv", "--python", "3.12.14", "--seed", ".venv"])
PY = REPO / ".venv/bin/python"
run_logged([PY, "-m", "pip", "install", "--require-hashes", "-r", "environment/bootstrap.lock"])
run_logged(
    [
        PY,
        "-m",
        "pip",
        "install",
        "--require-hashes",
        "--no-build-isolation",
        "-r",
        "environment/requirements.lock",
    ]
)
run_logged(["apt-get", "update", "-qq"])
run_logged(
    [
        "apt-get",
        "install",
        "-y",
        "--no-install-recommends",
        "build-essential",
        "gfortran",
        "pkg-config",
        "zlib1g-dev",
        "libbz2-dev",
        "liblzma-dev",
        "libpcre2-dev",
        "libcurl4-openssl-dev",
        "libtirpc-dev",
    ]
)
run_logged([PY, "scripts/install_locked_r.py"])
ENV = {
    **os.environ,
    "PYTHONPATH": str(REPO / "src"),
    "PYTHONHASHSEED": "0",
    "OPENBLAS_NUM_THREADS": "1",
    "OMP_NUM_THREADS": "1",
    "MKL_NUM_THREADS": "1",
}
ENV["MPLBACKEND"] = "Agg"
ENV.pop("MP1_DRIVE_ROOT", None)
run_logged([PY, "scripts/check_publication.py"], env=ENV)
runtime = json.loads((REPO / ".venv/ordinal/runtime.json").read_text())
CLEAN = Path("/content") / ("mp1-e-clean-" + uuid.uuid4().hex[:8])
run_logged(
    [PY, "scripts/verify_clean_checkout.py", "--work", CLEAN, "--reuse-r", runtime["R"]], env=ENV
)
public_report = json.loads(
    (REPO / "outputs/publication/validation/clean_checkout.json").read_text()
)
assert public_report["status"] == "PASS"
print("Clean installation, all synthetic tests, Ruff and aggregate/public rendering checks: PASS")
print("Private data were not required. The preserved source replay remains unchanged.")
```

### Cell 3

```python
# Cell 3: verify the recovered discrepancy boundary and download a complete public review copy.
run_logged([PY, "-m", "mp1.recovery"], env=ENV)
boundary = json.loads(
    (REPO / "outputs/publication/validation/recovery_discrepancy_check.json").read_text()
)
assert boundary["status"] == "PASS_WITH_DOCUMENTED_LIMITATION"
assert boundary["mismatch_cells"] == 247
assert boundary["selected_k2_mismatch_cells"] == 0
assert boundary["source_analyses_rerun"] == 0
run_logged([PY, "-m", "mp1.publication", "--check-only"], env=ENV)
REVIEW = Path("/content") / ("MP1_E_Verified_Review_" + uuid.uuid4().hex[:8])
REVIEW.mkdir(exist_ok=False)
shutil.copytree(BUNDLE, REVIEW / "delivery")
shutil.copytree(REPO / "outputs/publication", REVIEW / "verified_publication")
shutil.copytree(REPO / "environment", REVIEW / "verified_environment")
for pattern in [
    "work_package_e_*.md",
    "publication_*.md",
    "manuscript_*.md",
    "research_control_e_*.md",
]:
    for source in (REPO / "docs").glob(pattern):
        shutil.copy2(source, REVIEW / source.name)
REVIEW_ZIP = Path(shutil.make_archive(str(REVIEW), "zip", REVIEW))
print("Verified public review ZIP:", REVIEW_ZIP)
print("Public verification: PASS; retained-result lock: PASS WITH DOCUMENTED LIMITATION")
print("Historical complete candidate-grid replay: FAIL; 247 nonselected cells remain disclosed.")
print("No A-D source analyses were rerun. No source files or private logs are in this review.")
print(
    "E remains active until manual acceptance. Nothing committed, pushed or edited in Research Control."
)
files.download(str(REVIEW_ZIP))
```

## Expected checks and manual acceptance

Cell 2 must pass dependency checks, Ruff lint/format, 125 tests, all frozen/aggregate checks,
the 247-cell boundary verification, and regeneration of 50 byte-identical publication artifacts
plus both V3 disposition files. The clean-checkout report must show no private source data and
freshly installed Python/R packages. GitHub Actions is not triggered by this delivery.

Cell 3 must report zero selected k=2 mismatch cells and zero new source-analysis runs. Read
`docs/work_package_e_review.md`, `docs/work_package_e_validation.md`, and the complete discrepancy
register. Qualified acceptance does not turn the historical full-grid FAIL into PASS.
The proposed Research Control text is for manual review only. V3 itself remains unchanged and
requires the supplied corrections before submission. Journal shortlisting is not authorized.

## Optional future source replay, outside this recovery execution

The source replay script is preserved for reproducibility, but is deliberately not called by
the three cells. Only if a later task expressly authorizes it, use an empty private work folder,
the five exact source files/hash entries in `config/publication_freeze.json`, and a **new report
path outside the repository**. For example, with `PRIVATE_INPUTS` pointing to existing unchanged
sources and `PRIVATE_RUN` to a new private directory, run:

```bash
PYTHONPATH=src .venv/bin/python scripts/verify_publication_replay.py \
  --inputs "$PRIVATE_INPUTS" --work "$PRIVATE_RUN/work" \
  --report "$PRIVATE_RUN/source_replay.json"
```

Never delete or replace the preserved `outputs/publication/validation/source_replay.json` or
its discrepancy CSV. Missing original memberships/runtime provenance must remain disclosed.
No optional source replay is needed merely to accept the policy explicitly authorized here.
