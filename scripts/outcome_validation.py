"""Evaluate ordered D3 CGPA bands across accepted descriptive profiles."""

import argparse

from mp1.outcome_validation import run_outcome_validation


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="config/analysis.yaml")
    parser.add_argument("--settings", default="config/work_package_d.yaml")
    parser.add_argument("--d3-raw")
    parser.add_argument("--quality-flags")
    parser.add_argument("--accepted-memberships")
    args = parser.parse_args()
    try:
        destination = run_outcome_validation(
            args.config, args.settings, args.d3_raw, args.quality_flags, args.accepted_memberships
        )
    except (OSError, ValueError, RuntimeError, ArithmeticError, KeyError) as exc:
        parser.exit(1, f"Outcome validation failed: {exc}\n")
    print(f"D3 outcome evidence: {destination}")


if __name__ == "__main__":
    main()
