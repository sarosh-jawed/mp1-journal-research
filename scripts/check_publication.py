"""Run all public, aggregate-only publication acceptance checks without private source access."""

from __future__ import annotations

import argparse
import importlib.metadata
import json
import os
import platform
import subprocess
import sys
import tempfile
from pathlib import Path

from mp1.publication import aggregate_checks, build, read_json, sha
from mp1.recovery import verify_recovered_replay


def execute(command, root, env):
    result = subprocess.run(command, cwd=root, env=env, capture_output=True, text=True, check=False)
    if result.returncode:
        raise RuntimeError(f"Check failed: {command}\n{result.stdout}\n{result.stderr}")
    return {
        "command": [str(x) for x in command],
        "exit_code": 0,
        "summary": result.stdout.strip()[-1800:],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runtime", type=Path, default=Path(".venv/ordinal/runtime.json"))
    parser.add_argument(
        "--report", type=Path, default=Path("outputs/publication/validation/public_checks.json")
    )
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    runtime = read_json(args.runtime)
    env = {
        **os.environ,
        "PYTHONPATH": str(root / "src"),
        "PYTHONHASHSEED": "0",
        "OPENBLAS_NUM_THREADS": "1",
        "OMP_NUM_THREADS": "1",
        "MKL_NUM_THREADS": "1",
        "MP1_R_EXECUTABLE": runtime["R"],
        "R_LIBS_USER": runtime["R_LIBS_USER"],
        "R_LIBS_SITE": runtime["R_LIBS_USER"],
    }
    env.pop("MP1_DRIVE_ROOT", None)
    report = {
        "status": "RUNNING",
        "private_data_required": False,
        "checks": [],
        "python": platform.python_version(),
        "platform": platform.platform(),
        "python_packages": {
            d.metadata["Name"]: d.version for d in importlib.metadata.distributions()
        },
        "R": {k: v for k, v in runtime.items() if k not in {"R", "R_LIBS_USER"}},
    }
    inherited_backend = "module://matplotlib_inline.backend_inline"
    backend_check = execute(
        [
            sys.executable,
            "-c",
            "import os\n"
            "from mp1.publication import matplotlib\n"
            "assert os.environ['MPLBACKEND'] == 'Agg'\n"
            "assert matplotlib.get_backend().lower() == 'agg'\n"
            "print('Inherited Colab backend overridden before import: PASS')",
        ],
        root,
        {**env, "MPLBACKEND": inherited_backend},
    )
    backend_check["command"][0] = "<locked-python>"
    report["backend_portability_check"] = {
        "inherited_backend": inherited_backend,
        "effective_backend": "Agg",
        **backend_check,
    }
    for command in [
        [sys.executable, "-m", "pip", "check"],
        [sys.executable, "-m", "ruff", "check", "."],
        [sys.executable, "-m", "ruff", "format", "--check", "."],
        [sys.executable, "-m", "pytest", "-q"],
    ]:
        check = execute(command, root, env)
        check["command"][0] = "<locked-python>"
        report["checks"].append(check)
    report["aggregate_consistency"] = aggregate_checks(root)
    report["recovered_replay_boundary"] = verify_recovered_replay(root)
    tracked = subprocess.check_output(["git", "ls-files", "-z"], cwd=root).decode().split("\0")
    forbidden = [
        name
        for name in tracked
        if name
        and (
            name.startswith(("data/raw/", "data/interim/", "data/processed/"))
            or Path(name).name
            in read_json(root / "config/publication_freeze.json")["private_input_sha256"]
        )
    ]
    if forbidden:
        raise ValueError(f"Private data tracked: {forbidden}")
    report["private_files_tracked"] = forbidden
    for folder in ["data/raw", "data/interim", "data/processed"]:
        if any(p.is_file() for p in (root / folder).rglob("*")):
            raise ValueError("Public checks must run in a checkout without respondent-level files.")
    with tempfile.TemporaryDirectory(prefix="mp1-public-render-") as temporary:
        destination = Path(temporary) / "render"
        build(root, destination)
        expected = read_json(root / "outputs/publication/work_package_e/render_manifest.json")
        actual = read_json(destination / "render_manifest.json")
        if actual != expected:
            differing = [
                name for name, h in expected["files"].items() if actual["files"].get(name) != h
            ]
            raise ValueError(f"Publication rendering not byte-reproducible: {differing}")
        report["publication_artifacts_byte_reproduced"] = len(expected["files"]) + 1
        auditdir = Path(temporary) / "audit"
        execute(
            [sys.executable, "scripts/audit_manuscript_v3.py", "--output", str(auditdir)], root, env
        )
        for path in auditdir.iterdir():
            if sha(path) != sha(root / "outputs/publication/manuscript_audit" / path.name):
                raise ValueError("V3 disposition register does not reproduce.")
    report["status"] = "PASS"
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2) + "\n")
    print(
        json.dumps(
            {
                "status": "PASS",
                "checks": len(report["checks"]),
                "private_data_required": False,
                "publication_artifacts_byte_reproduced": report[
                    "publication_artifacts_byte_reproduced"
                ],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
