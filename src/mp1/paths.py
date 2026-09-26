from __future__ import annotations

import os
from pathlib import Path


def get_drive_root() -> Path:
    value = os.getenv("MP1_DRIVE_ROOT")
    if not value:
        raise RuntimeError(
            "MP1_DRIVE_ROOT is not set. Point it to the fresh MP1 Journal Research folder."
        )

    path = Path(value).expanduser().resolve()
    if not path.exists():
        raise FileNotFoundError(f"Configured Drive root does not exist: {path}")

    return path
