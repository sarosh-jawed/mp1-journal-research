"""Install the hash-locked ordinal runtime locally; never alter system R or scientific files."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import tarfile
import urllib.request
from pathlib import Path


def run(args, env=None, cwd=None):
    subprocess.run([str(x) for x in args], check=True, env=env, cwd=cwd)


def fetch(spec, cache):
    path = cache / spec["url"].rsplit("/", 1)[-1]
    if not path.exists():
        with urllib.request.urlopen(spec["url"], timeout=120) as response:
            path.write_bytes(response.read())
    if hashlib.sha256(path.read_bytes()).hexdigest() != spec["sha256"]:
        raise ValueError(f"Archive hash mismatch: {path.name}")
    return path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prefix", type=Path, default=Path(".venv/ordinal"))
    parser.add_argument("--reuse-r", type=Path)
    parser.add_argument("--jobs", type=int, default=2)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    lock = json.loads((root / "environment/R-lock.json").read_text())
    prefix = args.prefix.resolve()
    prefix.mkdir(parents=True, exist_ok=True)
    cache = prefix / "archives"
    cache.mkdir(exist_ok=True)
    r = args.reuse_r.resolve() if args.reuse_r else prefix / "runtime/bin/R"
    if not r.exists():
        for command in ["gcc", "gfortran", "make", "pkg-config"]:
            if not shutil.which(command):
                raise RuntimeError(f"Install documented build prerequisites: missing {command}")
        archive = fetch(lock["R"], cache)
        with tarfile.open(archive) as source:
            source.extractall(prefix, filter="data")
        build = prefix / ("R-" + lock["R"]["version"])
        run(
            [
                "./configure",
                f"--prefix={prefix / 'runtime'}",
                "--with-x=no",
                "--with-readline=no",
                "--with-recommended-packages=no",
            ],
            cwd=build,
        )
        run(["make", f"-j{args.jobs}"], cwd=build)
        run(["make", "install"], cwd=build)
    version = subprocess.check_output(
        [str(r), "--vanilla", "--slave", "-e", "cat(as.character(getRversion()))"], text=True
    ).strip()
    if version != lock["R"]["version"]:
        raise ValueError(f"R version mismatch: expected {lock['R']['version']}, got {version}")
    library = prefix / "library"
    library.mkdir(exist_ok=True)
    env = {**os.environ, "R_LIBS_USER": str(library), "R_LIBS_SITE": str(library)}
    for spec in lock["packages"]:
        run(
            [
                r,
                "CMD",
                "INSTALL",
                "--no-docs",
                "--no-html",
                "--no-help",
                f"--library={library}",
                fetch(spec, cache),
            ],
            env=env,
        )
    names = ",".join('"' + s["name"] + '"' for s in lock["packages"])
    code = (
        f"cat(jsonlite::toJSON(lapply(c({names}),"
        "function(x) as.character(packageVersion(x))),auto_unbox=TRUE))"
    )
    versions = json.loads(
        subprocess.check_output([str(r), "--vanilla", "--slave", "-e", code], env=env, text=True)
    )
    for spec, actual in zip(lock["packages"], versions, strict=True):
        if actual != spec["version"].replace("-", "."):
            raise ValueError(f"R package version mismatch: {spec['name']}: {actual}")
    (prefix / "runtime.json").write_text(
        json.dumps(
            {
                "R": str(r),
                "R_LIBS_USER": str(library),
                "version": version,
                "packages": dict(zip([s["name"] for s in lock["packages"]], versions, strict=True)),
            },
            indent=2,
        )
        + "\n"
    )
    print(f"Verified locked R runtime: {prefix / 'runtime.json'}")


if __name__ == "__main__":
    main()
