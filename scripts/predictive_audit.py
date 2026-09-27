"""Audit the accepted D5 target, predictor eligibility and predictive feasibility."""

import argparse

from mp1.predictive_audit import run_predictive_audit


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="config/analysis.yaml")
    parser.add_argument("--audit-config", default="config/work_package_c.yaml")
    parser.add_argument("--d5-raw", help="Optional immutable D5 CSV path.")
    parser.add_argument("--quality-flags", help="Optional accepted response-quality CSV path.")
    parser.add_argument(
        "--accepted-memberships", help="Optional original private B memberships CSV."
    )
    args = parser.parse_args()
    try:
        destination = run_predictive_audit(
            args.config,
            args.audit_config,
            args.d5_raw,
            args.quality_flags,
            args.accepted_memberships,
        )
    except (OSError, ValueError, RuntimeError, ArithmeticError, KeyError) as exc:
        parser.exit(1, f"Predictive feasibility audit failed: {exc}\n")
    print(f"Predictive feasibility evidence: {destination}")


if __name__ == "__main__":
    main()
