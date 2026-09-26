from __future__ import annotations

from pathlib import Path

import yaml


def load_config(path: str | Path = "config/analysis.yaml") -> dict:
    config_path = Path(path)
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file does not exist: {config_path}")

    with config_path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)

    if not isinstance(data, dict):
        raise ValueError("Analysis configuration must contain a mapping at the top level.")

    return data
