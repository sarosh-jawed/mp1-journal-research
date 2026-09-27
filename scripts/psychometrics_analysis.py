"""Evaluate ordinal item measurement and response-quality sensitivity."""

import argparse

from mp1.measurement import run_measurement


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="config/analysis.yaml")
    args = parser.parse_args()
    try:
        destination = run_measurement(args.config)
    except (OSError, ValueError, RuntimeError, ArithmeticError) as exc:
        parser.exit(1, f"Measurement analysis failed: {exc}\n")
    print(f"Measurement evidence: {destination}")


if __name__ == "__main__":
    main()
