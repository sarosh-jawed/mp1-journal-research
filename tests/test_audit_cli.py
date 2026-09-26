from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest


@pytest.mark.parametrize(
    "script,report",
    [
        ("provenance_audit.py", "provenance/provenance_summary.json"),
        ("response_quality.py", "response_quality/response_quality_summary.json"),
    ],
)
def test_cli_uses_configured_inputs(synthetic_project: Path, script: str, report: str) -> None:
    repository = Path(__file__).resolve().parents[1]
    result = subprocess.run(
        [sys.executable, str(repository / "scripts" / script), "--config", str(synthetic_project)],
        cwd=synthetic_project.parent.parent,
        env={**os.environ, "PYTHONPATH": str(repository / "src")},
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert (synthetic_project.parent.parent / "outputs" / report).is_file()
    assert len(result.stdout.splitlines()) == 1
    assert "m1" not in result.stdout
