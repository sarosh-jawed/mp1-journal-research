"""Verify a fresh baseline clone plus the E overlay, with a newly installed locked environment."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

BASELINE = "56b335c705ef15d5a261865382dd79991d2a93a2"


def run(command, cwd, log, env=None):
    with log.open("a") as stream:
        subprocess.run(
            [str(x) for x in command],
            cwd=cwd,
            env=env,
            stdout=stream,
            stderr=subprocess.STDOUT,
            check=True,
        )


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--work", type=Path, required=True, help="New directory outside source checkout")
    p.add_argument("--reuse-r", type=Path, help="Optional previously hash-built R 4.6.1 executable")
    p.add_argument(
        "--report", type=Path, default=Path("outputs/publication/validation/clean_checkout.json")
    )
    args = p.parse_args()
    root = Path(__file__).resolve().parents[1]
    if args.work.exists() or args.work.resolve().is_relative_to(root):
        raise ValueError("Use a new verification directory outside the source checkout.")
    work = args.work.resolve()
    work.mkdir(parents=True)
    clone, log = work / "checkout", work / "verification.log"
    run(["git", "clone", "--no-hardlinks", root, clone], root, log)
    run(["git", "checkout", "--detach", BASELINE], clone, log)
    changed = subprocess.check_output(
        ["git", "diff", "--name-only", BASELINE], cwd=root, text=True
    ).splitlines()
    added = subprocess.check_output(
        ["git", "ls-files", "--others", "--exclude-standard"], cwd=root, text=True
    ).splitlines()
    allowed = (
        "config/publication_",
        "config/manuscript_v3_",
        "environment/",
        "docs/publication_",
        "docs/work_package_e_",
        "docs/manuscript_",
        "docs/research_control_e_",
        "outputs/publication/",
        "tests/test_publication",
        "src/mp1/publication.py",
        "src/mp1/recovery.py",
    )
    scripts = {
        "scripts/install_locked_r.py",
        "scripts/check_publication.py",
        "scripts/verify_clean_checkout.py",
        "scripts/verify_publication_replay.py",
        "scripts/audit_manuscript_v3.py",
        "scripts/apply_publication_bundle.py",
    }
    mutable = {"README.md", "ASTRA_HANDOFF.md", ".github/workflows/quality.yml"}
    for name in sorted(set(changed + added)):
        if name not in mutable | scripts and not name.startswith(allowed):
            raise ValueError(f"Unreviewed overlay path: {name}")
        source = root / name
        if source.is_symlink() or not source.is_file():
            raise ValueError(f"Invalid overlay file: {name}")
        destination = clone / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, destination)
    run([sys.executable, "-m", "venv", clone / ".venv"], clone, log)
    python = clone / ".venv/bin/python"
    run(
        [python, "-m", "pip", "install", "--require-hashes", "-r", "environment/bootstrap.lock"],
        clone,
        log,
    )
    run(
        [
            python,
            "-m",
            "pip",
            "install",
            "--require-hashes",
            "--no-build-isolation",
            "-r",
            "environment/requirements.lock",
        ],
        clone,
        log,
    )
    command = [python, "scripts/install_locked_r.py"]
    if args.reuse_r:
        command += ["--reuse-r", args.reuse_r.resolve()]
    run(command, clone, log)
    env = {
        **os.environ,
        "PYTHONPATH": str(clone / "src"),
        "PYTHONHASHSEED": "0",
        "OPENBLAS_NUM_THREADS": "1",
        "OMP_NUM_THREADS": "1",
        "MKL_NUM_THREADS": "1",
    }
    env.pop("MP1_DRIVE_ROOT", None)
    run([python, "scripts/check_publication.py"], clone, log, env)
    report = json.loads((clone / "outputs/publication/validation/public_checks.json").read_text())
    report["clean_checkout"] = {
        "baseline_commit": BASELINE,
        "new_virtual_environment": True,
        "dependency_installation": "hash-checked bootstrap; no-build-isolation hash-checked lock",
        "private_sources_present": False,
        "R_source_reused": bool(args.reuse_r),
        "R_packages_installed_fresh": True,
        "overlay_files": len(set(changed + added)),
        "github_actions_run": "not triggered; no commit or push by Astra",
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2) + "\n")
    print("Clean-checkout installation, quality checks, synthetic tests and public render: PASS")


if __name__ == "__main__":
    main()
