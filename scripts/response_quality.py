"""Run the configured response-quality assessment."""

from __future__ import annotations

import argparse

from mp1.response_quality import run_response_quality


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="config/analysis.yaml")
    args = parser.parse_args()
    try:
        destination = run_response_quality(args.config)
    except (OSError, ValueError, RuntimeError) as exc:
        parser.exit(1, f"Response-quality assessment failed: {exc}\n")
    print(f"Response-quality reports: {destination}")


if __name__ == "__main__":
    main()
