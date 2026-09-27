"""Ordinal CGPA comparisons conditional on accepted descriptive D3 profiles."""

from __future__ import annotations

from importlib.metadata import version
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import kruskal
from sklearn.metrics import adjusted_rand_score
from threadpoolctl import threadpool_limits

from mp1.audit import read_raw_csv, repository_path, sha256_file, verify_unchanged, write_reports
from mp1.clustering import fit_partition, ordinal_features, record_concentration
from mp1.config import load_config
from mp1.paths import get_drive_root
from mp1.predictive_audit import exact_record_groups
from mp1.response_quality import assess_responses, read_quality_flags
from mp1.target_audit import align_partition


def verify_frozen(config_path: str | Path, settings_path: str | Path) -> tuple[dict, dict, dict]:
    """Require immutable accepted code, configuration and aggregate evidence."""
    config, settings = load_config(config_path), load_config(settings_path)
    fingerprints = {}
    for name, expected in settings["frozen_files"].items():
        path = repository_path(config_path, name)
        if sha256_file(path) != expected:
            raise ValueError(f"Frozen A/B/C file changed: {name}")
    for path in [Path(config_path).resolve(), Path(settings_path).resolve()]:
        fingerprints[path] = sha256_file(path)
    return config, settings, fingerprints


def audit_cgpa(series: pd.Series, categories: list[str]) -> tuple[np.ndarray, pd.DataFrame]:
    """Encode order only; preserve unrecognized text and distinguish missing outcomes."""
    if len(categories) < 2 or len(set(categories)) != len(categories):
        raise ValueError("CGPA categories must be distinct and explicitly ordered.")
    mapping = {label: i for i, label in enumerate(categories)}
    encoded = series.map(mapping).to_numpy(dtype=float, na_value=np.nan)
    rows = []
    for value, count in series.fillna("").value_counts(sort=False).items():
        status = "eligible_ordered_band" if value in mapping else "unrecognized_ineligible"
        if not str(value).strip():
            status = "missing_ineligible"
        rows.append(
            {
                "raw_value": value,
                "records": int(count),
                "status": status,
                "order_code": mapping.get(value),
                "exact_grade_observed": False,
                "midpoint_imputed": False,
            }
        )
    return encoded, pd.DataFrame(rows)


def category_counts(outcome: np.ndarray, labels: np.ndarray, categories: int) -> np.ndarray:
    """Return profile by ordered-outcome counts with explicit finite-domain checks."""
    outcome, labels = np.asarray(outcome), np.asarray(labels)
    if (
        outcome.ndim != 1
        or labels.shape != outcome.shape
        or not np.isin(outcome, np.arange(categories)).all()
        or not np.isin(labels, [0, 1]).all()
    ):
        raise ValueError(
            "Complete aligned binary profiles and valid ordered outcomes are required."
        )
    counts = np.zeros((2, categories), dtype=int)
    np.add.at(counts, (labels.astype(int), outcome.astype(int)), 1)
    if (counts.sum(axis=1) == 0).any():
        raise ValueError("Both profiles must contain eligible outcomes.")
    return counts


def rank_effect(counts: np.ndarray) -> np.ndarray:
    """Cliff delta: P(P2 > P1) minus P(P2 < P1), with ties contributing zero."""
    counts = np.asarray(counts, dtype=float)
    if counts.shape[-2] != 2 or np.any(counts < 0) or not np.isfinite(counts).all():
        raise ValueError("Nonnegative finite two-profile category counts are required.")
    p1, p2 = counts[..., 0, :], counts[..., 1, :]
    n1, n2 = p1.sum(axis=-1), p2.sum(axis=-1)
    if np.any(n1 == 0) or np.any(n2 == 0):
        raise ValueError("Both profiles require positive denominators.")
    lower = np.cumsum(p1, axis=-1) - p1
    higher = n1[..., None] - np.cumsum(p1, axis=-1)
    return np.sum(p2 * (lower - higher), axis=-1) / (n1 * n2)


def ordinal_comparison(outcome: np.ndarray, labels: np.ndarray, categories: int) -> dict:
    """Compute tie-corrected H and a directional rank effect, without grade distances."""
    counts = category_counts(outcome, labels, categories)
    n = int(counts.sum())
    if np.count_nonzero(counts.sum(axis=0)) == 1:
        h, p, status = 0.0, 1.0, "all_outcomes_tied_no_rank_information"
    else:
        h, p = kruskal(outcome[labels == 0], outcome[labels == 1])
        status = "nominal_independent_record_reference"
    delta = float(rank_effect(counts))
    return {
        "n": n,
        "profile_1_n": int(counts[0].sum()),
        "profile_2_n": int(counts[1].sum()),
        "kruskal_h_tie_corrected": float(h),
        "df": 1,
        "nominal_p_value": float(p),
        "rank_epsilon_squared_H_over_N_minus_1": float(h / (n - 1)),
        "cliff_delta_P2_minus_P1": delta,
        "probability_P2_greater_plus_half_ties": (delta + 1) / 2,
        "inference_status": status,
        "independent_respondents_verified": False,
        "posthoc_status": "not_needed_two_profiles_one_comparison",
        "comparison_family_size": 1,
    }


def resampling_interval(
    outcome: np.ndarray,
    labels: np.ndarray,
    groups: np.ndarray,
    categories: int,
    repetitions: int,
    seed: int,
    confidence: float,
    stratified: bool,
) -> dict:
    """Resample intact units with all their multiplicities; keep the accepted profiles fixed."""
    category_counts(outcome, labels, categories)
    if len(groups) != len(outcome) or repetitions < 100 or not 0 < confidence < 1 or seed < 0:
        raise ValueError("Invalid resampling inputs or settings.")
    codes, names = pd.factorize(groups, sort=False)
    if (codes < 0).any():
        raise ValueError("Resampling units must be complete.")
    unit_counts = np.zeros((len(names), 2, categories), dtype=int)
    np.add.at(unit_counts, (codes, labels.astype(int), outcome.astype(int)), 1)
    if stratified and np.any((unit_counts.sum(axis=2) > 0).sum(axis=1) != 1):
        raise ValueError("Stratified resampling units cannot cross profiles.")
    strata = (
        [unit_counts[unit_counts[:, j].sum(axis=1) > 0] for j in [0, 1]]
        if stratified
        else [unit_counts]
    )
    if min(len(s) for s in strata) < 2:
        raise ValueError("At least two resampling units per stratum are required.")
    rng = np.random.default_rng(seed)
    samples, invalid = [], 0
    for start in range(0, repetitions, 250):
        size = min(250, repetitions - start)
        total = np.zeros((size, 2, categories), dtype=int)
        for stratum in strata:
            m = len(stratum)
            draws = rng.multinomial(m, np.full(m, 1 / m), size=size)
            total += (draws @ stratum.reshape(m, -1)).reshape(size, 2, categories)
        valid = (total.sum(axis=2) > 0).all(axis=1)
        invalid += int((~valid).sum())
        samples.extend(rank_effect(total[valid]).tolist())
    if invalid:
        raise ValueError("A resample lost an entire profile; uncertainty requires design review.")
    tail = (1 - confidence) / 2
    low, high = np.quantile(samples, [tail, 1 - tail])
    return {
        "cliff_delta": float(rank_effect(category_counts(outcome, labels, categories))),
        "conditional_percentile_lower": float(low),
        "conditional_percentile_upper": float(high),
        "confidence_level": confidence,
        "repetitions": repetitions,
        "seed": seed,
        "resampling_units": len(names),
        "stratified_by_frozen_profile": stratified,
        "invalid_replicates": invalid,
        "population_interval_validity_established": False,
        "profile_estimation_uncertainty_included": False,
    }


def compare_d3_memberships(
    path: Path, sample: str, positions: np.ndarray, labels: np.ndarray, digest: str
) -> float:
    """Require record-aligned private B membership agreement if the file is available."""
    data = pd.read_csv(path, dtype="string", keep_default_na=False)
    columns = ["dataset", "source_sha256", "source_record_number", "sample", "k", "cluster"]
    if list(data) != columns:
        raise ValueError("Accepted membership schema differs.")
    data = data[data.dataset.eq("D3") & data["sample"].eq(sample)]
    if (
        len(data) != len(labels)
        or not data.source_sha256.eq(digest).all()
        or data.source_record_number.tolist() != positions.astype(str).tolist()
        or not data.k.eq("2").all()
        or set(data.cluster) != {"1", "2"}
    ):
        raise ValueError("Accepted D3 memberships differ in source, order, sample or schema.")
    ari = float(adjusted_rand_score(labels, data.cluster.astype(int)))
    if ari != 1:
        raise ValueError("Accepted D3 memberships disagree with reconstruction.")
    return ari


@threadpool_limits.wrap(limits=1)
def run_outcome_validation(
    config_path: str | Path = "config/analysis.yaml",
    settings_path: str | Path = "config/work_package_d.yaml",
    d3_path: str | Path | None = None,
    flags_path: str | Path | None = None,
    memberships_path: str | Path | None = None,
) -> Path:
    """Reconstruct accepted assignments and write aggregate ordinal outcome evidence."""
    config, settings, fingerprints = verify_frozen(config_path, settings_path)
    options = settings["d3"]
    spec = config["integrity"]["datasets"]["D3"]
    if d3_path is None:
        d3_path = get_drive_root(config["project"]["drive_root_env"]) / config["data"]["d3_raw"]
    flag_path = (
        Path(flags_path).resolve()
        if flags_path is not None
        else repository_path(config_path, config["response_quality"]["private_flags"])
    )
    raw = read_raw_csv(d3_path, "D3", config["integrity"]["csv_encoding"])
    if raw.sha256 != spec["source_metadata"]["published_file_sha256"]:
        raise ValueError("D3 source fingerprint differs from accepted A/B.")
    cluster_dir = repository_path(config_path, "outputs/clustering")
    import json

    evidence = json.loads((cluster_dir / "clustering_summary.json").read_text())
    if evidence["choices"]["D3"]["k"] != 2:
        raise ValueError("D3 outcome analysis requires the accepted binary partition.")
    if sha256_file(flag_path) != evidence["quality_flags_sha256"]:
        raise ValueError("Accepted quality flag fingerprint differs.")
    flags = read_quality_flags(flag_path, "D3", raw.sha256, len(raw.frame))
    recomputed, _, _, _ = assess_responses(
        raw, spec["survey_items"], spec["allowed_responses"], config["integrity"]["missing_tokens"]
    )
    if not flags.astype(str).equals(recomputed.astype(str)):
        raise ValueError("Quality flags disagree with unchanged A definitions.")
    fingerprints.update({raw.path: raw.sha256, flag_path: sha256_file(flag_path)})
    original = raw.frame.copy(deep=True)
    coding = dict(zip(spec["allowed_responses"], range(1, 6), strict=True))
    x = raw.frame[spec["survey_items"]].apply(lambda col: col.map(coding)).to_numpy()
    inventory = pd.read_csv(
        repository_path(config_path, "outputs/psychometrics/item_inventory.csv")
    )
    inventory = inventory[inventory.dataset.eq("D3")].sort_values("position")
    if inventory.raw_column.tolist() != spec["survey_items"]:
        raise ValueError("Accepted D3 item order differs from the configuration.")
    centroids = pd.read_csv(cluster_dir / "cluster_centroids.csv")
    sizes = pd.read_csv(cluster_dir / "cluster_sizes.csv")
    membership_file = (
        Path(memberships_path).resolve()
        if memberships_path is not None
        else repository_path(config_path, evidence["private_memberships"])
    )
    if memberships_path is not None and not membership_file.is_file():
        raise FileNotFoundError("Supplied accepted D3 memberships are missing.")
    if membership_file.is_file():
        fingerprints[membership_file] = sha256_file(membership_file)
    mask = flags.include_sensitivity.to_numpy()
    labels, checks, private = {}, [], []
    seed = (
        config["project"]["random_seed"]
        + 1000 * list(config["integrity"]["datasets"]).index("D3")
        + 2
    )
    for sample, keep in [("full", np.ones(len(x), dtype=bool)), ("sensitivity", mask)]:
        features = ordinal_features(x[keep])
        fitted, centers = fit_partition(features, 2, seed, config["clustering"]["n_init"])
        selected = centroids[
            centroids.dataset.eq("D3") & centroids["sample"].eq(sample) & centroids.k.eq(2)
        ]
        if len(selected) != 2 * len(inventory) or selected.duplicated(["cluster", "item"]).any():
            raise ValueError("Accepted D3 centroids are incomplete or duplicated.")
        reference = np.vstack(
            [
                selected[selected.cluster.eq(j)]
                .set_index("item")
                .loc[inventory.item, [f"probability_above_{t}" for t in range(1, 5)]]
                .to_numpy()
                .reshape(-1)
                / 2
                for j in [1, 2]
            ]
        )
        aligned, check = align_partition(
            features,
            fitted,
            centers,
            reference,
            options["centroid_tolerance"],
            options["minimum_assignment_margin"],
        )
        counts = np.bincount(aligned, minlength=2).tolist()
        stored = sizes[sizes.dataset.eq("D3") & sizes["sample"].eq(sample) & sizes.k.eq(2)]
        if (
            counts != stored.sort_values("cluster")["count"].tolist()
            or counts != options["expected_sizes"][sample]
        ):
            raise ValueError("D3 reconstructed sizes differ from accepted B.")
        positions = np.flatnonzero(keep) + 1
        private_ari = (
            compare_d3_memberships(membership_file, sample, positions, aligned, raw.sha256)
            if membership_file.is_file()
            else None
        )
        checks.append(
            {
                "sample": sample,
                "n": len(aligned),
                "profile_1_n": counts[0],
                "profile_2_n": counts[1],
                "fit_seed": seed,
                **check,
                "original_memberships_available": membership_file.is_file(),
                "ari_against_original_memberships": private_ari,
            }
        )
        labels[sample] = aligned
        private.append(
            pd.DataFrame(
                {
                    "dataset": "D3",
                    "source_sha256": raw.sha256,
                    "source_record_number": positions,
                    "sample": sample,
                    "k": 2,
                    "cluster": aligned + 1,
                }
            )
        )
    agreement = float(adjusted_rand_score(labels["full"][mask], labels["sensitivity"]))
    stored = pd.read_csv(cluster_dir / "quality_sensitivity.csv")
    expected = stored.loc[stored.dataset.eq("D3") & stored.k.eq(2), "full_sensitivity_ari"].item()
    if not np.isclose(agreement, expected, rtol=0, atol=1e-12):
        raise ValueError("Accepted D3 sensitivity agreement differs.")
    categories = options["categories"]
    outcome, audit = audit_cgpa(raw.frame[options["outcome"]], categories)
    if audit.status.eq("unrecognized_ineligible").any():
        raise ValueError("Unrecognized CGPA labels require a source review; no recoding applied.")
    eligible = np.isfinite(outcome)
    variants = {
        "full": (np.ones(len(x), dtype=bool), labels["full"]),
        "quality_fixed_profiles": (mask, labels["full"][mask]),
        "quality_refit_profiles": (mask, labels["sensitivity"]),
    }
    results, distributions, descriptions, intervals, concentration, accounting = (
        [],
        [],
        [],
        [],
        [],
        [],
    )
    for number, (variant, (keep, y)) in enumerate(variants.items()):
        available = eligible[keep]
        frame = raw.frame.loc[keep].loc[available].reset_index(drop=True)
        values, y = outcome[keep][available].astype(int), y[available]
        accounting.append(
            {
                "variant": variant,
                "source_records": len(raw.frame),
                "quality_records_retained": int(keep.sum()),
                "outcome_eligible_records": len(values),
                "missing_outcome_records": int((~available).sum()),
                "permanent_source_exclusions": 0,
            }
        )
        result = ordinal_comparison(values, y, len(categories))
        results.append({"variant": variant, **result})
        counts = category_counts(values, y, len(categories))
        for j in [0, 1]:
            n = int(counts[j].sum())
            cumulative = counts[j].cumsum()
            quantiles = [categories[np.searchsorted(cumulative, q * n)] for q in [0.25, 0.5, 0.75]]
            descriptions.append(
                {
                    "variant": variant,
                    "profile": f"D3_P{j + 1}",
                    "n": n,
                    "q1_band": quantiles[0],
                    "median_band": quantiles[1],
                    "q3_band": quantiles[2],
                    "quantile_rule": "inverse_empirical_cdf",
                }
            )
            for k, category in enumerate(categories):
                distributions.append(
                    {
                        "variant": variant,
                        "profile": f"D3_P{j + 1}",
                        "cgpa_band": category,
                        "order_code": k,
                        "records": int(counts[j, k]),
                        "profile_n": n,
                        "fraction": float(counts[j, k] / n),
                    }
                )
        groups = exact_record_groups(frame, y)
        for offset, (name, units, stratified) in enumerate(
            [
                ("independent_records_reference", np.arange(len(frame)), True),
                ("intact_full_record_patterns", groups, True),
                ("literal_institution_labels", frame[spec["institution_column"]].to_numpy(), False),
            ]
        ):
            interval = resampling_interval(
                values,
                y,
                units,
                len(categories),
                options["bootstrap_repetitions"],
                options["bootstrap_seed"] + number * 10 + offset,
                options["confidence_level"],
                stratified,
            )
            intervals.append({"variant": variant, "assumed_independent_units": name, **interval})
        concentration.append(record_concentration(frame, y).assign(variant=variant))
    destination = repository_path(config_path, options["output_directory"])
    private_dir = repository_path(config_path, options["private_directory"])
    if not private_dir.is_relative_to(repository_path(config_path, "data/interim")):
        raise ValueError("Private D records must stay in ignored data/interim.")
    write_reports(
        private_dir,
        {"d3_memberships.csv": pd.concat(private, ignore_index=True)},
        {"source_sha256": raw.sha256},
        "d3_private_manifest.json",
        fingerprints,
    )
    if not raw.frame.equals(original):
        raise RuntimeError("D3 source values or order changed.")
    summary = {
        "package": "D",
        "baseline_commit": settings["baseline_commit"],
        "source_sha256": raw.sha256,
        "quality_flags_sha256": sha256_file(flag_path),
        "settings_sha256": sha256_file(settings_path),
        "code_sha256": sha256_file(__file__),
        "versions": {name: version(name) for name in ["numpy", "pandas", "scipy", "scikit-learn"]},
        "outcome": (
            "Four ordered self-reported CGPA bands; exact grades and midpoints unavailable."
        ),
        "source_band_boundary_caution": (
            "Below 2.50 and 2.51-3.00 do not document assignment of exactly 2.50; "
            "retain recorded bands."
        ),
        "quality_sensitivity": {
            "flagged_records": int((~mask).sum()),
            "retained_records": int(mask.sum()),
            "full_refit_ari": agreement,
            "changed_retained_assignments": int(
                (labels["full"][mask] != labels["sensitivity"]).sum()
            ),
        },
        "method": (
            "Tie-corrected Kruskal-Wallis; H/(N-1) rank epsilon squared; Cliff delta P2 minus P1."
        ),
        "uncertainty": (
            "Percentile intervals condition on independent units named in each row and fixed "
            "profiles. Pattern and literal-institution resampling preserve multiplicities. "
            "They do not prove independence, recover unique people, "
            "or establish population coverage."
        ),
        "posthoc": (
            "Two accepted profiles give one comparison; no separate post-hoc family is justified."
        ),
        "scientific_limits": [
            "Nominal p-values assume independent records; source independence is unresolved.",
            "No grade-point magnitude, causal effect, equivalence, or validated types.",
            "No permanent exclusion, institution mapping, pooling, or predictive fitting.",
        ],
        "source_values_and_order_unchanged": True,
        "frozen_files_unchanged": True,
        "raw_records_removed": 0,
        "acceptance_status": "requires_manual_scientific_review",
    }
    tables = {
        "cgpa_eligibility.csv": audit,
        "profile_reconstruction.csv": pd.DataFrame(checks),
        "sample_accounting.csv": pd.DataFrame(accounting),
        "cgpa_distributions.csv": pd.DataFrame(distributions),
        "cgpa_profile_descriptions.csv": pd.DataFrame(descriptions),
        "cgpa_comparisons.csv": pd.DataFrame(results),
        "conditional_uncertainty.csv": pd.DataFrame(intervals),
        "record_concentration.csv": pd.concat(concentration, ignore_index=True),
    }
    write_reports(destination, tables, summary, "outcome_summary.json", fingerprints)
    verify_unchanged(fingerprints)
    verify_frozen(config_path, settings_path)
    return destination
