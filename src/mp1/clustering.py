"""Ordinal item-profile K-Means with repeated resampling and explicit selection rules."""

from __future__ import annotations

import json
from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import linear_sum_assignment
from scipy.spatial.distance import pdist
from sklearn.cluster import KMeans
from sklearn.metrics import (
    adjusted_rand_score,
    calinski_harabasz_score,
    davies_bouldin_score,
    silhouette_samples,
)
from threadpoolctl import threadpool_limits

from mp1.audit import duplicate_counts, repository_path, sha256_file, write_reports
from mp1.measurement import execution_metadata, load_measurement_inputs
from mp1.ordinal import validate_ordinal


def ordinal_features(values: np.ndarray) -> np.ndarray:
    """Embed each ordinal item as four equally weighted threshold indicators."""
    x = validate_ordinal(values)
    return (x[:, :, None] > np.arange(1, 5)).reshape(len(x), -1).astype(float) / 2


def canonical_labels(labels: np.ndarray, centers: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Assign reproducible profile IDs by lexicographic centroid order, without tier claims."""
    order = np.array(sorted(range(len(centers)), key=lambda i: tuple(centers[i])))
    inverse = np.empty(len(order), dtype=int)
    inverse[order] = np.arange(len(order))
    return inverse[labels], centers[order]


def matched_jaccard(reference: np.ndarray, candidate: np.ndarray, k: int) -> np.ndarray:
    """Match partitions one-to-one by maximum total Jaccard overlap."""
    table = np.zeros((k, k), dtype=int)
    np.add.at(table, (reference, candidate), 1)
    unions = table.sum(axis=1)[:, None] + table.sum(axis=0)[None, :] - table
    jaccard = np.divide(table, unions, out=np.zeros((k, k), dtype=float), where=unions > 0)
    rows, columns = linear_sum_assignment(-jaccard)
    matched = np.zeros(k)
    matched[rows] = jaccard[rows, columns]
    return matched


def record_concentration(frame: pd.DataFrame, labels: np.ndarray) -> pd.DataFrame:
    """Describe exact record multiplicity without identifying or excluding people."""
    if len(frame) != len(labels):
        raise ValueError("Cluster labels and source records must have the same length.")
    rows = []
    for cluster in np.unique(labels):
        selected = frame.iloc[np.flatnonzero(labels == cluster)]
        counts = duplicate_counts(selected)
        rows.append(
            {
                "cluster": int(cluster + 1),
                "records": len(selected),
                **counts,
                "largest_exact_record_share": counts["largest_group_size"] / len(selected),
            }
        )
    return pd.DataFrame(rows)


def fit_partition(features: np.ndarray, k: int, seed: int, n_init: int) -> tuple:
    if len(np.unique(features, axis=0)) < k:
        raise ValueError("Fewer distinct item vectors than requested clusters.")
    model = KMeans(n_clusters=k, n_init=n_init, random_state=seed, max_iter=500, tol=1e-6)
    labels = model.fit_predict(features)
    if len(np.unique(labels)) != k:
        raise RuntimeError("K-Means did not recover the requested number of nonempty clusters.")
    if model.n_iter_ >= 500:
        raise RuntimeError("K-Means reached the iteration limit.")
    centers = np.vstack([features[labels == cluster].mean(axis=0) for cluster in range(k)])
    labels, centers = canonical_labels(labels, centers)
    return labels, centers


def resampling_stability(
    features: np.ndarray, reference: np.ndarray, k: int, settings: dict, seed: int
) -> tuple[dict, pd.DataFrame]:
    """Refit on 80% samples and compare omitted records with the full-data partition."""
    repetitions = settings["resampling_repetitions"]
    fraction = settings["resampling_fraction"]
    if repetitions < 20 or not 0.5 <= fraction <= 0.9:
        raise ValueError("Stability requires at least 20 repeats and a fraction from 0.5 to 0.9.")
    rng = np.random.default_rng(seed)
    size = int(np.floor(len(features) * fraction))
    ari, overlaps, omitted_counts = [], [], []
    for _ in range(repetitions):
        training = rng.choice(len(features), size=size, replace=False)
        omitted = np.ones(len(features), dtype=bool)
        omitted[training] = False
        _, centers = fit_partition(
            features[training], k, int(rng.integers(2**31)), settings["n_init"]
        )
        distances = ((features[omitted, None, :] - centers[None, :, :]) ** 2).sum(axis=2)
        predicted = distances.argmin(axis=1)
        ref = reference[omitted]
        ari.append(adjusted_rand_score(ref, predicted))
        overlaps.append(matched_jaccard(ref, predicted, k))
        omitted_counts.append(np.bincount(ref, minlength=k))
    overlap = np.array(overlaps)
    counts = np.array(omitted_counts)
    if np.any(counts == 0):
        raise ValueError(
            "A reference cluster is absent from an omitted sample; stability is undefined."
        )
    table = pd.DataFrame(
        {
            "cluster": np.arange(1, k + 1),
            "jaccard_mean": overlap.mean(axis=0),
            "jaccard_10_percentile": np.quantile(overlap, 0.1, axis=0),
            "jaccard_90_percentile": np.quantile(overlap, 0.9, axis=0),
            "minimum_omitted_cluster_records": counts.min(axis=0),
        }
    )
    return {
        "resampling_repetitions": repetitions,
        "resampling_fraction": fraction,
        "ari_mean": float(np.mean(ari)),
        "ari_sd": float(np.std(ari, ddof=1)),
        "ari_10_percentile": float(np.quantile(ari, 0.1)),
        "ari_90_percentile": float(np.quantile(ari, 0.9)),
        "minimum_cluster_jaccard_mean": float(overlap.mean(axis=0).min()),
    }, table


def evaluate_partition(values: np.ndarray, k: int, settings: dict, seed: int) -> dict:
    features = ordinal_features(values)
    labels, centers = fit_partition(features, k, seed, settings["n_init"])
    silhouette = silhouette_samples(features, labels, metric="euclidean")
    sizes = np.bincount(labels, minlength=k)
    agreement = np.vstack([(values[labels == c] >= 4).mean(axis=0) for c in range(k)])
    contrast = min(
        float(np.max(np.abs(agreement[a] - agreement[b]))) for a, b in combinations(range(k), 2)
    )
    within = np.mean(np.sum((features - centers[labels]) ** 2, axis=1))
    if within <= 0:
        raise ValueError("Within-cluster variance is zero; standardized separation is undefined.")
    separation = float(pdist(centers).min() / np.sqrt(within))
    stability, cluster_stability = resampling_stability(features, labels, k, settings, seed + 10000)
    metrics = {
        "k": k,
        "n": len(values),
        "silhouette": float(silhouette.mean()),
        "davies_bouldin": float(davies_bouldin_score(features, labels)),
        "calinski_harabasz": float(calinski_harabasz_score(features, labels)),
        "minimum_cluster_fraction": float(sizes.min() / len(values)),
        "largest_to_smallest_ratio": float(sizes.max() / sizes.min()),
        "negative_silhouette_fraction": float(np.mean(silhouette < 0)),
        "centroid_separation_to_within_rms": separation,
        "minimum_pair_maximum_agreement_difference": contrast,
        **stability,
    }
    return {
        "metrics": metrics,
        "labels": labels,
        "centers": centers,
        "sizes": sizes,
        "agreement": agreement,
        "stability": cluster_stability,
    }


def select_k(metrics: pd.DataFrame, settings: dict) -> tuple[int, str, pd.DataFrame]:
    """Screen both samples, then balance six metrics with an explicit parsimony tie break."""
    table = metrics.copy()
    table["passes_screen"] = (
        (table.minimum_cluster_fraction >= settings["minimum_cluster_fraction"])
        & (table.ari_mean >= settings["minimum_mean_ari"])
        & (table.ari_10_percentile >= settings["minimum_ari_10_percentile"])
        & (table.minimum_cluster_jaccard_mean >= settings["minimum_cluster_jaccard"])
        & (
            table.minimum_pair_maximum_agreement_difference
            >= settings["minimum_profile_probability_difference"]
        )
        & (table.negative_silhouette_fraction <= settings["maximum_negative_silhouette_fraction"])
    )
    metric_directions = {
        "silhouette": False,
        "davies_bouldin": True,
        "calinski_harabasz": False,
        "ari_mean": False,
        "minimum_cluster_fraction": False,
        "centroid_separation_to_within_rms": False,
    }
    ranks = []
    for metric, ascending in metric_directions.items():
        rank = table.groupby("sample")[metric].rank(ascending=ascending, method="average")
        table[f"rank_{metric}"] = rank
        ranks.append(rank.to_numpy())
    table["mean_metric_rank"] = np.mean(ranks, axis=0)
    overall = table.groupby("k").agg(
        passes_both_samples=("passes_screen", "all"),
        mean_rank=("mean_metric_rank", "mean"),
    )
    supported = overall[overall.passes_both_samples]
    status = (
        "supported_descriptive_partition" if len(supported) else "no_candidate_passes_all_screens"
    )
    eligible = supported if len(supported) else overall
    chosen = int(eligible.reset_index().sort_values(["mean_rank", "k"]).iloc[0].k)
    table["selected"] = table.k.eq(chosen)
    return chosen, status, table


def load_measurement_evidence(config_path: str | Path, config: dict, raw: dict) -> dict:
    directory = repository_path(config_path, config["outputs"]["root"]) / "psychometrics"
    path = directory / "measurement_summary.json"
    if not path.is_file():
        raise FileNotFoundError("Run scripts/psychometrics_analysis.py before clustering.")
    summary = json.loads(path.read_text())
    if summary["config_sha256"] != sha256_file(config_path):
        raise ValueError("Measurement evidence is stale for the current configuration.")
    if summary["sources"] != {name: source.sha256 for name, source in raw.items()}:
        raise ValueError("Measurement evidence does not match the current source files.")
    current_code = execution_metadata(config_path, raw, config)["measurement_code_sha256"]
    if summary.get("measurement_code_sha256") != current_code:
        raise ValueError("Measurement evidence is stale for the current implementation.")
    for name, fingerprint in summary["artifact_sha256"].items():
        if sha256_file(directory / name) != fingerprint:
            raise ValueError(f"Measurement artifact changed: {name}")
    if summary["representation"] != "ordinal_item_thresholds":
        raise ValueError("Only the documented ordinal item representation is implemented.")
    return summary


@threadpool_limits.wrap(limits=1)
def run_clustering(config_path: str | Path = "config/analysis.yaml") -> Path:
    """Evaluate full and quality-sensitivity profiles separately in D5 and D3."""
    config, raw, samples, inventory, fingerprints = load_measurement_inputs(config_path)
    measurement = load_measurement_evidence(config_path, config, raw)
    settings = config["clustering"]
    if settings["k_values"] != [2, 3, 4, 5, 6]:
        raise ValueError("Work Package B requires k=2 through k=6.")
    metrics_rows, centroids, sizes, stability_rows, selection_rows = [], [], [], [], []
    comparisons, profiles, private_rows, choices, concentration_rows = [], [], [], {}, []
    for d, (dataset, sample_data) in enumerate(samples.items()):
        fits = {}
        for sample in ["full", "sensitivity"]:
            for k in settings["k_values"]:
                seed = config["project"]["random_seed"] + 1000 * d + k
                result = evaluate_partition(sample_data[sample], k, settings, seed)
                fits[sample, k] = result
                context = {"dataset": dataset, "sample": sample, "k": k}
                metrics_rows.append({**context, **result["metrics"]})
                stability_rows.extend(
                    [{**context, **row} for row in result["stability"].to_dict("records")]
                )
                for cluster in range(k):
                    member = result["labels"] == cluster
                    sizes.append(
                        {
                            **context,
                            "cluster": cluster + 1,
                            "count": int(member.sum()),
                            "fraction": float(member.mean()),
                        }
                    )
                    probabilities = (result["centers"][cluster] * 2).reshape(-1, 4)
                    for i, item in enumerate(sample_data["items"]):
                        centroids.append(
                            {
                                **context,
                                "cluster": cluster + 1,
                                "item": item,
                                **{
                                    f"probability_above_{t + 1}": float(probabilities[i, t])
                                    for t in range(4)
                                },
                                "agreement_proportion": float(result["agreement"][cluster, i]),
                            }
                        )
        dataset_metrics = pd.DataFrame([row for row in metrics_rows if row["dataset"] == dataset])
        k, status, selection = select_k(dataset_metrics, settings)
        selection_rows.extend(selection.to_dict("records"))
        choices[dataset] = {
            "k": k,
            "status": status,
            "individually_preferred_k": {
                sample: select_k(dataset_metrics[dataset_metrics["sample"].eq(sample)], settings)[0]
                for sample in ["full", "sensitivity"]
            },
        }
        for candidate in settings["k_values"]:
            reference = fits["full", candidate]["labels"][sample_data["mask"]]
            sensitivity = fits["sensitivity", candidate]["labels"]
            comparisons.append(
                {
                    "dataset": dataset,
                    "k": candidate,
                    "common_records": len(reference),
                    "full_sensitivity_ari": adjusted_rand_score(reference, sensitivity),
                    "minimum_matched_jaccard": float(
                        matched_jaccard(reference, sensitivity, candidate).min()
                    ),
                    "selected": candidate == k,
                }
            )
        full_result = fits["full", k]
        overall = (sample_data["full"] >= 4).mean(axis=0)
        for cluster in range(k):
            delta = full_result["agreement"][cluster] - overall
            order = np.argsort(-np.abs(delta), kind="stable")[:3]
            descriptor = "; ".join(
                f"{'higher' if delta[i] > 0 else 'lower'} {sample_data['items'][i]} agreement"
                for i in order
            )
            profiles.append(
                {
                    "dataset": dataset,
                    "cluster": cluster + 1,
                    "selected_k": k,
                    "profile_description": descriptor,
                    "interpretation": "Relative to this dataset; descriptive only.",
                }
            )
        for sample in ["full", "sensitivity"]:
            positions = np.arange(1, len(sample_data["full"]) + 1)
            if sample == "sensitivity":
                positions = positions[sample_data["mask"]]
            concentration = record_concentration(
                raw[dataset].frame.iloc[positions - 1], fits[sample, k]["labels"]
            )
            concentration_rows.extend(
                [
                    {"dataset": dataset, "sample": sample, "k": k, **row}
                    for row in concentration.to_dict("records")
                ]
            )
            private_rows.extend(
                {
                    "dataset": dataset,
                    "source_sha256": raw[dataset].sha256,
                    "source_record_number": int(position),
                    "sample": sample,
                    "k": k,
                    "cluster": int(label + 1),
                }
                for position, label in zip(positions, fits[sample, k]["labels"], strict=True)
            )
    summary = {
        **execution_metadata(config_path, raw, config),
        "measurement_config_sha256": measurement["config_sha256"],
        "clustering_code_sha256": sha256_file(Path(__file__)),
        "choices": choices,
        "representation": (
            "Four cumulative ordinal thresholds per item, each divided by two. Squared "
            "distance equals the sum of absolute category differences divided by four. "
            "No section averages, factor scores or variance standardization."
        ),
        "selection_rule": (
            "Screen size, omitted-record stability, profile contrast and negative "
            "silhouette in both samples. Rank six metrics equally across both samples; "
            "choose lowest mean rank, then smaller k. If none qualifies, report the "
            "best descriptive candidate and explicit failure status."
        ),
        "stability_interpretation": (
            "Repeated subsamples without replacement using configured repetitions and "
            "fraction; compare nearest-centroid assignments on omitted records with the "
            "reference fit. Percentiles describe perturbation variability, not confidence "
            "intervals. The reference uses all records; this is not external validation."
        ),
        "d3_comparison": (
            "Same ordinal representation and selection logic on nine D3 items. Instruments "
            "differ; no direct centroid transfer, profile equivalence or invariance claim."
        ),
        "source_concentration_caution": (
            "Inspect cluster_record_concentration.csv. Stability is conditional on the "
            "released multiplicities and does not prove independent respondents or "
            "natural population classes. No repeated record is removed or downweighted."
        ),
        "settings": settings,
        "private_memberships": "data/interim/work_package_b/cluster_memberships.csv",
        "acceptance_status": "requires_researcher_review",
    }
    destination = repository_path(config_path, config["outputs"]["root"]) / "clustering"
    tables = {
        "cluster_metrics.csv": pd.DataFrame(metrics_rows),
        "cluster_selection.csv": pd.DataFrame(selection_rows),
        "cluster_sizes.csv": pd.DataFrame(sizes),
        "cluster_centroids.csv": pd.DataFrame(centroids),
        "cluster_stability.csv": pd.DataFrame(stability_rows),
        "quality_sensitivity.csv": pd.DataFrame(comparisons),
        "selected_profiles.csv": pd.DataFrame(profiles),
        "cluster_record_concentration.csv": pd.DataFrame(concentration_rows),
    }
    private = repository_path(config_path, "data/interim/work_package_b")
    write_reports(
        private,
        {"cluster_memberships.csv": pd.DataFrame(private_rows)},
        execution_metadata(config_path, raw, config),
        "membership_manifest.json",
        fingerprints,
    )
    write_reports(destination, tables, summary, "clustering_summary.json", fingerprints)
    return destination
