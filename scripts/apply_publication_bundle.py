"""Preflight and atomically apply complete E files to the exact accepted Git checkout.

Default is a read-only preflight. The bundle is extracted by Colab's guarded cell before this
script runs. No git add, commit, push, source-data operation or Research Control write occurs.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path, PurePosixPath

BASELINE = "56b335c705ef15d5a261865382dd79991d2a93a2"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def checked_relative(name):
    value = PurePosixPath(name)
    if not name or value.is_absolute() or ".." in value.parts or "\\" in name:
        raise ValueError(f"Unsafe bundle path: {name}")
    if value.parts[0] in {".git", ".venv", "data"}:
        raise ValueError(f"Private/runtime path is not allowed in the bundle: {name}")
    return Path(*value.parts)


def preflight(bundle, repo):
    manifest = json.loads((bundle / "bundle_manifest.json").read_text())
    if manifest["baseline_commit"] != BASELINE:
        raise ValueError("Unexpected accepted baseline in bundle.")
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo, text=True).strip()
    if head != BASELINE:
        raise ValueError(f"Checkout is not the required accepted baseline: {head}")
    dirty = subprocess.check_output(
        ["git", "status", "--porcelain", "--untracked-files=no"], cwd=repo, text=True
    )
    if dirty.strip():
        raise ValueError(
            "Tracked files are modified. Apply to a fresh clone; do not discard changes."
        )
    actual = {
        str(p.relative_to(bundle / "files"))
        for p in (bundle / "files").rglob("*")
        if p.is_file() or p.is_symlink()
    }
    if actual != set(manifest["files"]):
        raise ValueError("Bundle file inventory differs from its manifest.")
    for name, entry in manifest["files"].items():
        relative = checked_relative(name)
        source, destination = bundle / "files" / relative, repo / relative
        for parent in [source, *source.parents]:
            if parent == bundle:
                break
            if parent.is_symlink():
                raise ValueError("Bundle symlinks are prohibited.")
        for parent in [destination, *destination.parents]:
            if parent == repo:
                break
            if parent.is_symlink():
                raise ValueError("Destination symlinks are prohibited.")
        if digest(source) != entry["after_sha256"]:
            raise ValueError(f"Bundle content hash mismatch: {name}")
        before = entry["before_sha256"]
        if before is None:
            if destination.exists():
                raise ValueError(f"Untracked collision: {name}; use a fresh clone.")
        elif not destination.is_file() or digest(destination) != before:
            raise ValueError(f"Accepted destination changed: {name}")
    return manifest


def apply(bundle, repo, manifest):
    # Keep recoverable bytes outside the checkout. Roll back all replaced files on any failure.
    with tempfile.TemporaryDirectory(prefix="mp1-e-rollback-") as temporary:
        backup = Path(temporary)
        written = []
        try:
            for name, entry in manifest["files"].items():
                path = repo / checked_relative(name)
                path.parent.mkdir(parents=True, exist_ok=True)
                if entry["before_sha256"] is not None:
                    saved = backup / name
                    saved.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(path, saved)
                fd, staged = tempfile.mkstemp(prefix=".mp1-e-", dir=path.parent)
                os.close(fd)
                try:
                    shutil.copyfile(bundle / "files" / name, staged)
                    os.replace(staged, path)
                finally:
                    Path(staged).unlink(missing_ok=True)
                written.append(name)
            for name, entry in manifest["files"].items():
                if digest(repo / name) != entry["after_sha256"]:
                    raise ValueError(f"Post-application hash mismatch: {name}")
        except BaseException:
            for name in reversed(written):
                path = repo / name
                if manifest["files"][name]["before_sha256"] is None:
                    path.unlink(missing_ok=True)
                else:
                    shutil.copyfile(backup / name, path)
            raise


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--bundle", type=Path, required=True)
    p.add_argument("--repo", type=Path, required=True)
    p.add_argument("--apply", action="store_true")
    args = p.parse_args()
    bundle, repo = args.bundle.resolve(), args.repo.resolve()
    manifest = preflight(bundle, repo)
    if args.apply:
        apply(bundle, repo, manifest)
    print(
        f"E {'applied' if args.apply else 'preflight passed'}: {len(manifest['files'])} files. "
        "No commit or push performed."
    )


if __name__ == "__main__":
    main()
