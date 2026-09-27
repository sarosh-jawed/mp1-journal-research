"""Evaluate ordinal item-profile clusters and repeated resampling stability."""

import argparse

from mp1.clustering import run_clustering


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="config/analysis.yaml")
    args = parser.parse_args()
    try:
        destination = run_clustering(args.config)
    except (OSError, ValueError, RuntimeError, ArithmeticError) as exc:
        parser.exit(1, f"Clustering analysis failed: {exc}\n")
    print(f"Clustering evidence: {destination}")


if __name__ == "__main__":
    main()
