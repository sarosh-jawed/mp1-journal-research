"""Run the configured provenance audit."""

from __future__ import annotations

import argparse

from mp1.audit import run_provenance


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="config/analysis.yaml")
    args = parser.parse_args()
    try:
        destination = run_provenance(args.config)
    except (OSError, ValueError, RuntimeError) as exc:
        parser.exit(1, f"Provenance audit failed: {exc}\n")
    print(f"Provenance reports: {destination}")


if __name__ == "__main__":
    main()
