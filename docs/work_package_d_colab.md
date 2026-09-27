# Apply and execute Work Package D in Colab

This delivery targets `sarosh-jawed/mp1-journal-research` at main commit
`dad222a9a0143887e7e25a72e656ec21d0ebc253`. Read the canonical Research Control completely
before applying or rerunning it. A/B/C remain frozen; D does not resume predictive modeling.
The ZIP contains a safe patch, every changed/new file, baseline and delivery hashes, synthetic
tests, real aggregate outputs and scientific-review documents. Private inputs are not included.

Use a fresh Colab runtime. The cells below are executed in order. Repository-relative commands
also work in an existing configured environment. No cell commits, pushes or edits Research Control.

## Upload and safely extract the single delivery ZIP

```python
from google.colab import files
from pathlib import Path
import hashlib
import json
import os
import stat
import subprocess
import sys
import zipfile

uploaded = files.upload()
assert len(uploaded) == 1, "Select only MP1_Work_Package_D_Colab.zip"
zip_name = next(iter(uploaded))
DELIVERY = Path("/content/mp1_d_delivery")
assert not DELIVERY.exists(), "Use a fresh extraction directory"
with zipfile.ZipFile(zip_name) as archive:
    for member in archive.infolist():
        target = (DELIVERY / member.filename).resolve()
        assert target.is_relative_to(DELIVERY.resolve())
        assert not stat.S_ISLNK(member.external_attr >> 16)
    archive.extractall(DELIVERY)
inventory = json.loads((DELIVERY / "package_inventory.json").read_text())
for entry in inventory["files"]:
    path = DELIVERY / entry["path"]
    assert hashlib.sha256(path.read_bytes()).hexdigest() == entry["sha256"], entry["path"]
print("Delivery hashes verified")
```

## Check the exact baseline and apply

Use the existing checkout if present. If its HEAD or any baseline file differs, the application
helper refuses to apply. It also refuses untracked collisions and staged changes. Do not reset
local work to bypass the check. If main has advanced, stop and review the patch against the new
baseline before proposing an updated delivery.

```python
REPO = Path("/content/mp1-journal-research")
if not REPO.exists():
    subprocess.run(
        [
            "git",
            "clone",
            "--branch",
            "main",
            "--single-branch",
            "https://github.com/sarosh-jawed/mp1-journal-research.git",
            str(REPO),
        ],
        check=True,
    )
subprocess.run(
    [sys.executable, str(DELIVERY / "apply_work_package_d.py"), "--repo", str(REPO)], check=True
)
subprocess.run(
    [sys.executable, str(DELIVERY / "apply_work_package_d.py"), "--repo", str(REPO), "--apply"],
    check=True,
)
os.chdir(REPO)
```

The first invocation is a dry check. The second applies the verified patch. The helper verifies
all final file hashes and preserves unrelated ignored data. An already applied, exactly matching
delivery is reported without rewriting it. Complete replacement files are under `files/` for
inspection; do not copy them over a mismatched checkout.

## Install dependencies and run all synthetic checks

The existing Python requirements are unchanged. R is used only as an ordinal WLSMV measurement
engine because the threshold-identification and robust nested-comparison functionality is
required for a defensible invariance assessment. CI installs the same R packages and runs the
complete suite, including the synthetic ordinal tests. No private data are needed for tests.

```python
subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
subprocess.run(["apt-get", "update", "-qq"], check=True)
subprocess.run(
    [
        "apt-get",
        "install",
        "-y",
        "--no-install-recommends",
        "r-base-core",
        "r-cran-lavaan",
        "r-cran-semtools",
        "r-cran-jsonlite",
    ],
    check=True,
)
subprocess.run(
    [
        "R",
        "--vanilla",
        "--slave",
        "-e",
        "library(lavaan); library(semTools); library(jsonlite); sessionInfo()",
    ],
    check=True,
)
subprocess.run([sys.executable, "-m", "pytest", "-q"], check=True)
subprocess.run([sys.executable, "-m", "ruff", "check", "."], check=True)
subprocess.run([sys.executable, "-m", "ruff", "format", "--check", "."], check=True)
```

Expected delivered suite: 112 passing tests. R/package versions are recorded in each real-data
manifest. The reference execution used R 4.3.3, lavaan 0.6.17 and semTools 0.5.6. Installation
versions may differ in Colab; do not suppress a failed synthetic test, reconstruction check,
warning or material numerical discrepancy. The Python environment is recorded separately in
`docs/work_package_d_validation.md` and `validation/environment.json` inside the ZIP.

## Mount private sources and verify availability

Edit the Drive root below to the actual mounted MP1 Journal Research directory. Source filenames
and subdirectories otherwise come from the frozen configuration. The external filename must be
`When Culture Meets AI - Survey Dataset.xlsx`. If the same verified source is stored elsewhere,
set `EXTERNAL` or `D3` to that existing private path instead of moving or rewriting raw data.

```python
from google.colab import drive

drive.mount("/content/drive")
os.environ["MP1_DRIVE_ROOT"] = "/content/drive/MyDrive/MP1 Journal Research"
sys.path.insert(0, str(REPO / "src"))
from mp1.config import load_config
from mp1.audit import sha256_file

config = load_config("config/analysis.yaml")
settings = load_config("config/work_package_d.yaml")
DRIVE_ROOT = Path(os.environ["MP1_DRIVE_ROOT"])
D3 = DRIVE_ROOT / config["data"]["d3_raw"]
EXTERNAL = (
    DRIVE_ROOT / config["data"]["us_indonesia_root"] / settings["external"]["workbook_filename"]
)
FLAGS = REPO / config["response_quality"]["private_flags"]
assert D3.is_file(), D3
assert EXTERNAL.is_file(), EXTERNAL
assert (
    sha256_file(D3)
    == config["integrity"]["datasets"]["D3"]["source_metadata"]["published_file_sha256"]
)
assert sha256_file(EXTERNAL) == settings["external"]["workbook_sha256"]
```

The exact external workbook is available at the [official release](https://zenodo.org/records/21013786),
under its Files section. Its expected SHA-256 is in the configuration. Do not substitute a
modified advisor workbook, a different release or the Vietnam fallback if the check fails.

### Restore the accepted private flags only if absent

An existing accepted flags file can be used by setting `FLAGS` to its path. For a fresh clone,
the following optional cell reconstructs only that ignored private file from the unchanged A
function, in the original D5/D3 order. It verifies the exact accepted byte fingerprint before
saving and writes no A/B/C aggregate output. The D5 raw CSV is needed only for this restoration
of the original combined flags file; D performs no D5 outcome or predictive analysis.

```python
import io
import pandas as pd
from mp1.audit import read_raw_csv, verify_unchanged, guard_output
from mp1.response_quality import assess_responses

expected_flags = json.loads((REPO / "outputs/clustering/clustering_summary.json").read_text())[
    "quality_flags_sha256"
]
if not FLAGS.exists():
    collected, originals = [], {}
    for name, spec in config["integrity"]["datasets"].items():
        path = DRIVE_ROOT / config["data"][spec["source_key"]]
        raw = read_raw_csv(path, name, config["integrity"]["csv_encoding"])
        assert raw.sha256 == spec["source_metadata"]["published_file_sha256"], name
        originals[raw.path] = raw.sha256
        flags, _, _, _ = assess_responses(
            raw,
            spec["survey_items"],
            spec["allowed_responses"],
            config["integrity"]["missing_tokens"],
        )
        collected.append(flags)
    buffer = io.StringIO()
    pd.concat(collected, ignore_index=True).to_csv(buffer, index=False, lineterminator="\n")
    payload = buffer.getvalue().encode("utf-8")
    assert hashlib.sha256(payload).hexdigest() == expected_flags
    guard_output(FLAGS, originals)
    verify_unchanged(originals)
    FLAGS.parent.mkdir(parents=True, exist_ok=True)
    with FLAGS.open("xb") as handle:
        handle.write(payload)
    verify_unchanged(originals)
assert sha256_file(FLAGS) == expected_flags
```

## Execute only D and reconcile results

The commands retain private memberships and temporary model input under ignored
`data/interim/work_package_d/`. Public outputs contain aggregates only. An existing original B
membership file at its accepted configured path is checked automatically. If stored elsewhere,
append `--accepted-memberships` and its path to the outcome command.

The external CLI starts a process with `PYTHONHASHSEED=0` to stabilize semopy's internal
parameter ordering. Programmatic callers should launch Python with that same setting. This is
an execution reproducibility setting; it changes no source, item definition or B implementation.

```python
env = {**os.environ, "PYTHONPATH": str(REPO / "src")}
subprocess.run(
    [
        sys.executable,
        "scripts/outcome_validation.py",
        "--config",
        "config/analysis.yaml",
        "--settings",
        "config/work_package_d.yaml",
        "--d3-raw",
        str(D3),
        "--quality-flags",
        str(FLAGS),
    ],
    env=env,
    check=True,
)
subprocess.run(
    [
        sys.executable,
        "scripts/external_validation.py",
        "--config",
        "config/analysis.yaml",
        "--settings",
        "config/work_package_d.yaml",
        "--external-workbook",
        str(EXTERNAL),
    ],
    env=env,
    check=True,
)
subprocess.run(
    [
        sys.executable,
        "scripts/verify_work_package_d.py",
        "--d3-raw",
        str(D3),
        "--quality-flags",
        str(FLAGS),
        "--external-workbook",
        str(EXTERNAL),
    ],
    env=env,
    check=True,
)
```

Expected verification: 81 frozen files, 24 aggregate CSV artifacts, three private source hashes,
three independently reconciled CGPA contrasts, four Holm-corrected external tests and no model
warnings. Do not run B or C to update their outputs as part of D. The accepted B reconstruction
must match; a mismatch is a blocker requiring review, not permission to refit new profiles.

## Inspect and preserve the run

Read `docs/outcome_cross_cultural_validation.md`, all aggregate tables listed in
`docs/work_package_d_outputs.md`, and `docs/work_package_d_review.md`. Expected reference values:

- Full CGPA H=2.8025254004, nominal p=0.0941159605, epsilon squared=0.0025408209,
  Cliff delta=-0.0559012480; sensitivity p=0.0853273078 and 0.1054489897.
- External analytic country counts 116 U.S. / 111 Indonesia; no common Bangladesh anchors.
- GAID configural screen fails for Indonesia and the multigroup model. CT and TP stop at
  category-support checks. The equality-comparison CSV has headers and no rows by design.
- No model warnings, unexpected missing outputs, imputed responses or deleted source records.

Use absolute tolerance 1e-10 for rank calculations and 1e-5 for WLSMV fit statistics when
comparing environments. Conditional interval endpoints can vary with numerical-library
versions; inspect and report differences, preserving recorded seeds. Country membership,
profile membership, categorical counts and methodological decisions must agree exactly.

Preserve the executed private `data/interim/work_package_d` folder in the private Drive workspace
if needed after Colab disconnects; never add it to Git. Public CSV/JSON files may be reviewed
and versioned according to repository policy. The proposed commit message and proposed Control
append are in `docs/work_package_d_review.md`. They are proposals, not automatically applied.

```python
subprocess.run(["git", "diff", "--check"], check=True)
subprocess.run(["git", "status", "--short"], check=True)
subprocess.run(
    [
        "git",
        "check-ignore",
        "data/interim/work_package_d/d3_memberships.csv",
        "data/interim/work_package_d/external_model_input.csv",
    ],
    check=True,
)
```

Stop after scientific review. This delivery contains no commit, push, publication-lock or final
manuscript command. A successful run documents the measurement blocker; it does not remove it.
