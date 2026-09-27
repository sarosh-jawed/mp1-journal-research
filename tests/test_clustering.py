from __future__ import annotations

import numpy as np
import pandas as pd
import pytest
from sklearn.metrics import adjusted_rand_score
from threadpoolctl import threadpool_limits

from mp1.clustering import (
    canonical_labels,
    evaluate_partition,
    matched_jaccard,
    ordinal_features,
    record_concentration,
    select_k,
)


def settings() -> dict:
    return {
        "n_init": 5,
        "resampling_repetitions": 20,
        "resampling_fraction": 0.8,
        "minimum_cluster_fraction": 0.05,
        "minimum_mean_ari": 0.8,
        "minimum_ari_10_percentile": 0.6,
        "minimum_cluster_jaccard": 0.75,
        "minimum_profile_probability_difference": 0.1,
        "maximum_negative_silhouette_fraction": 0.25,
    }


def test_ordinal_embedding_has_declared_distance_and_no_metadata() -> None:
    x = np.random.default_rng(2).integers(1, 6, (40, 5))
    transformed = ordinal_features(x)
    assert transformed.shape == (40, 20)
    assert np.sum((transformed[0] - transformed[1]) ** 2) == pytest.approx(
        np.abs(x[0] - x[1]).sum() / 4
    )
    reversed_x = x.copy()
    reversed_x[:, 0] = 6 - reversed_x[:, 0]
    reversed_features = ordinal_features(reversed_x)
    assert np.sum((transformed[0] - transformed[1]) ** 2) == pytest.approx(
        np.sum((reversed_features[0] - reversed_features[1]) ** 2)
    )


def test_label_permutations_do_not_change_overlap() -> None:
    reference = np.repeat([0, 1, 2], 10)
    candidate = np.repeat([2, 0, 1], 10)
    assert matched_jaccard(reference, candidate, 3) == pytest.approx(np.ones(3))
    labels, centers = canonical_labels(np.array([0, 1, 2]), np.array([[2, 0], [0, 0], [1, 0]]))
    assert labels.tolist() == [2, 0, 1]
    assert centers[:, 0].tolist() == [0, 1, 2]


def test_record_concentration_preserves_multiplicity_without_person_inference() -> None:
    frame = pd.DataFrame({"metadata": ["a", "a", "a", "b", "c"], "q": [2, 2, 2, 4, 5]})
    before = frame.copy(deep=True)
    summary = record_concentration(frame, np.array([0, 0, 0, 1, 1]))
    assert summary.iloc[0].largest_exact_record_share == 1
    assert summary.iloc[0].duplicate_excess_rows == 2
    assert summary.iloc[1].largest_exact_record_share == 0.5
    assert summary.records.sum() == len(frame)
    pd.testing.assert_frame_equal(before, frame)


@threadpool_limits.wrap(limits=1)
def test_resampling_recovers_separated_profiles_deterministically() -> None:
    rng = np.random.default_rng(10)
    x = np.vstack([rng.integers(1, 3, (100, 5)), rng.integers(4, 6, (100, 5))])
    before = x.copy()
    first = evaluate_partition(x, 2, settings(), 42)
    second = evaluate_partition(x, 2, settings(), 42)
    assert first["metrics"] == second["metrics"]
    assert first["metrics"]["ari_mean"] > 0.95
    assert first["metrics"]["minimum_cluster_jaccard_mean"] > 0.95
    assert adjusted_rand_score(np.repeat([0, 1], 100), first["labels"]) == 1
    assert np.array_equal(x, before)
    assert first["sizes"].sum() == len(x)
    assert np.all((first["centers"] >= 0) & (first["centers"] <= 0.5 + 1e-12))


def test_selection_does_not_follow_silhouette_when_stability_fails() -> None:
    records = []
    for sample in ["full", "sensitivity"]:
        for k in [2, 3]:
            records.append(
                {
                    "sample": sample,
                    "k": k,
                    "silhouette": 0.4 if k == 2 else 0.8,
                    "davies_bouldin": 0.5,
                    "calinski_harabasz": 80,
                    "minimum_cluster_fraction": 0.2,
                    "ari_mean": 0.95 if k == 2 else 0.6,
                    "ari_10_percentile": 0.9 if k == 2 else 0.3,
                    "minimum_cluster_jaccard_mean": 0.9 if k == 2 else 0.6,
                    "minimum_pair_maximum_agreement_difference": 0.3,
                    "negative_silhouette_fraction": 0.01,
                    "centroid_separation_to_within_rms": 2,
                }
            )
    chosen, status, _ = select_k(pd.DataFrame(records), settings())
    assert chosen == 2
    assert status == "supported_descriptive_partition"
    for row in records:
        row["ari_mean"] = 0.2
    _, status, _ = select_k(pd.DataFrame(records), settings())
    assert status == "no_candidate_passes_all_screens"
