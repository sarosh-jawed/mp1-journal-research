"""Reconcile D aggregate evidence, executed code and optional private source fingerprints."""

import argparse
import json

from mp1.d_validation import verify_d_evidence


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="config/analysis.yaml")
    parser.add_argument("--settings", default="config/work_package_d.yaml")
    parser.add_argument("--d3-raw")
    parser.add_argument("--quality-flags")
    parser.add_argument("--external-workbook")
    args = parser.parse_args()
    try:
        result = verify_d_evidence(
            args.config, args.settings, args.d3_raw, args.quality_flags, args.external_workbook
        )
    except (OSError, ValueError, KeyError) as exc:
        parser.exit(1, f"D evidence verification failed: {exc}\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
