"""Synthetic tests of publication evidence boundaries and precise source resolution."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from mp1.publication import resolve, safe_path


def synthetic_source(tmp_path):
    path = tmp_path / "aggregate.csv"
    path.write_text("profile,n,p\nP1,12,0.125\nP2,8,0.875\n")
    return path, {path.name: hashlib.sha256(path.read_bytes()).hexdigest()}


def test_exact_statistic_and_data_row_survive_resolution(tmp_path):
    path, accepted = synthetic_source(tmp_path)
    result = resolve(tmp_path, {"file": path.name, "where": {"profile": "P2"}}, accepted)
    assert result == [{"csv_data_row": 2, "profile": "P2", "n": "8", "p": "0.875"}]


def test_evidence_cannot_reference_an_unaccepted_rendering(tmp_path):
    path, _ = synthetic_source(tmp_path)
    with pytest.raises(ValueError, match="not an accepted output"):
        resolve(tmp_path, {"file": path.name}, {})


def test_frozen_evidence_tampering_is_rejected(tmp_path):
    path, accepted = synthetic_source(tmp_path)
    path.write_text("profile,n,p\nP1,13,0.125\n")
    with pytest.raises(ValueError, match="hash changed"):
        resolve(tmp_path, {"file": path.name}, accepted)


def test_empty_claim_selector_fails_closed(tmp_path):
    path, accepted = synthetic_source(tmp_path)
    with pytest.raises(ValueError, match="selector is empty"):
        resolve(tmp_path, {"file": path.name, "where": {"profile": "P3"}}, accepted)


def test_exact_json_pointer_handles_keys_and_array_indices(tmp_path):
    path = tmp_path / "source.json"
    path.write_text(json.dumps({"a/b": [{"value": False}, {"value": 0.002540820853}]}))
    accepted = {path.name: hashlib.sha256(path.read_bytes()).hexdigest()}
    assert (
        resolve(tmp_path, {"file": path.name, "pointer": "/a~1b/1/value"}, accepted)
        == 0.002540820853
    )


def test_path_escape_and_symlink_are_rejected(tmp_path):
    with pytest.raises(ValueError, match="Unsafe"):
        safe_path(tmp_path, "../outside.csv")
    link = tmp_path / "linked.csv"
    link.symlink_to(Path("/etc/passwd"))
    with pytest.raises(ValueError, match="Unsafe"):
        safe_path(tmp_path, "linked.csv")


def test_intentionally_empty_accepted_csv_remains_empty(tmp_path):
    path = tmp_path / "not_tested.csv"
    path.write_text("constraint,p\n")
    accepted = {path.name: hashlib.sha256(path.read_bytes()).hexdigest()}
    assert resolve(tmp_path, {"file": path.name}, accepted) == []
