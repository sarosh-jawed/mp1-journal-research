from __future__ import annotations

import os
from pathlib import Path


def get_drive_root(env_name: str = "MP1_DRIVE_ROOT") -> Path:
    value = os.getenv(env_name)
    if not value:
        raise RuntimeError(
            f"{env_name} is not set. Point it to the fresh MP1 Journal Research folder."
        )

    path = Path(value).expanduser().resolve()
    if not path.is_dir():
        raise NotADirectoryError(f"Configured Drive root is not a directory: {path}")

    return path
