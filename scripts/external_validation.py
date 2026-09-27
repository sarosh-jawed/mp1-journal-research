"""Audit U.S.-Indonesia compatibility and limited country-specific item associations."""

import argparse
import os
import sys

from mp1.cross_cultural import run_external_validation


def main() -> None:
    # Fixed hashing stabilizes semopy's internal set-based parameter ordering.
    if os.environ.get("PYTHONHASHSEED") != "0":
        os.execve(
            sys.executable, [sys.executable, *sys.argv], {**os.environ, "PYTHONHASHSEED": "0"}
        )
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="config/analysis.yaml")
    parser.add_argument("--settings", default="config/work_package_d.yaml")
    parser.add_argument("--external-workbook")
    args = parser.parse_args()
    try:
        destination = run_external_validation(args.config, args.settings, args.external_workbook)
    except (OSError, ValueError, RuntimeError, ArithmeticError, KeyError) as exc:
        parser.exit(1, f"External validation failed: {exc}\n")
    print(f"Cross-cultural evidence: {destination}")


if __name__ == "__main__":
    main()
