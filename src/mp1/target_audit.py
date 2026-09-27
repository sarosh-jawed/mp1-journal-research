"""Reconstruct the accepted D5 target without altering Work Package B evidence."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import linear_sum_assignment
from sklearn.metrics import adjusted_rand_score
from threadpoolctl import threadpool_limits

from mp1.audit import RawDataset, read_raw_csv, repository_path, sha256_file, verify_unchanged
from mp1.clustering import fit_partition, ordinal_features
from mp1.config import load_config
from mp1.paths import get_drive_root
from mp1.response_quality import assess_responses, read_quality_flags


@dataclass
class ReconstructedTarget:
    """Private record-aligned target data and aggregate reconstruction evidence."""

    analysis: dict
    settings: dict
    raw: RawDataset
    flags: pd.DataFrame
    labels: dict[str, np.ndarray]
    checks: pd.DataFrame
    sensitivity: dict
    fingerprints: dict[Path, str]


def verified_manifest(path: Path, expected: str, fingerprints: dict[Path, str]) -> dict:
    """Check a pinned manifest and every referenced aggregate before using its content."""
    if sha256_file(path) != expected:
        raise ValueError(f"Accepted manifest fingerprint differs: {path.name}")
    fingerprints[path.resolve()] = expected
    manifest = json.loads(path.read_text(encoding="utf-8"))
    for name, digest in manifest["artifact_sha256"].items():
        relative = Path(name)
        if relative.is_absolute() or len(relative.parts) != 1:
            raise ValueError("Manifest artifacts must be simple filenames.")
        artifact = (path.parent / name).resolve()
        if sha256_file(artifact) != digest:
            raise ValueError(f"Accepted artifact fingerprint differs: {name}")
        fingerprints[artifact] = digest
    return manifest


def align_partition(
    features: np.ndarray,
    labels: np.ndarray,
    centers: np.ndarray,
    reference_centers: np.ndarray,
    tolerance: float,
    minimum_margin: float,
) -> tuple[np.ndarray, dict]:
    """Require exact assignments against saved centroids, allowing label permutation."""
    if centers.shape != reference_centers.shape or centers.shape[0] != 2:
        raise ValueError("The accepted binary centroid dimensions do not match.")
    if not np.isfinite(reference_centers).all():
        raise ValueError("Accepted centroids must be finite.")
    cost = ((centers[:, None, :] - reference_centers[None, :, :]) ** 2).sum(axis=2)
    rows, columns = linear_sum_assignment(cost)
    mapping = np.empty(2, dtype=int)
    mapping[rows] = columns
    error = float(np.max(np.abs(centers[rows] - reference_centers[columns])))
    distances = ((features[:, None, :] - reference_centers[None, :, :]) ** 2).sum(axis=2)
    margin = float(np.min(np.abs(distances[:, 0] - distances[:, 1])))
    reference = distances.argmin(axis=1)
    aligned = mapping[labels]
    ari = float(adjusted_rand_score(aligned, reference))
    if error > tolerance or margin <= minimum_margin or not np.array_equal(aligned, reference):
        raise ValueError("Reconstructed target does not exactly match accepted B centroids.")
    return aligned, {
        "ari_against_accepted_centroid_assignments": ari,
        "identical_accepted_centroid_assignments": True,
        "maximum_centroid_absolute_error": error,
        "minimum_squared_distance_assignment_margin": margin,
        "ordered_partition_sha256": hashlib.sha256(aligned.astype("int8").tobytes()).hexdigest(),
    }


def compare_private_memberships(
    path: Path,
    sample: str,
    positions: np.ndarray,
    labels: np.ndarray,
    source_sha256: str,
) -> float:
    """Compare original B memberships if supplied, without confusing row order with IDs."""
    frame = pd.read_csv(path, dtype="string", keep_default_na=False)
    expected_columns = [
        "dataset",
        "source_sha256",
        "source_record_number",
        "sample",
        "k",
        "cluster",
    ]
    if list(frame.columns) != expected_columns:
        raise ValueError("Accepted membership schema is incompatible.")
    selected = frame.loc[frame.dataset.eq("D5") & frame["sample"].eq(sample)]
    if (
        len(selected) != len(labels)
        or not selected.source_sha256.eq(source_sha256).all()
        or not selected.k.eq("2").all()
        or selected.source_record_number.tolist() != positions.astype(str).tolist()
        or set(selected.cluster) != {"1", "2"}
    ):
        raise ValueError("Accepted memberships differ in source, sample, order, or target schema.")
    ari = float(adjusted_rand_score(labels, selected.cluster.astype(int).to_numpy()))
    if ari != 1.0:
        raise ValueError("Accepted private memberships do not agree exactly with reconstruction.")
    return ari


def _reference_centers(table: pd.DataFrame, sample: str, items: list[str]) -> np.ndarray:
    selected = table.loc[table.dataset.eq("D5") & table["sample"].eq(sample) & table.k.eq(2)]
    if len(selected) != 2 * len(items) or selected.duplicated(["cluster", "item"]).any():
        raise ValueError("Accepted centroid table has incomplete or duplicated D5 entries.")
    probabilities = [f"probability_above_{i}" for i in range(1, 5)]
    return np.vstack(
        [
            selected.loc[selected.cluster.eq(cluster)]
            .set_index("item")
            .loc[items, probabilities]
            .to_numpy()
            .reshape(-1)
            / 2
            for cluster in [1, 2]
        ]
    )


@threadpool_limits.wrap(limits=1)
def reconstruct_target(
    config_path: str | Path,
    audit_config_path: str | Path,
    d5_path: str | Path | None = None,
    flags_path: str | Path | None = None,
    memberships_path: str | Path | None = None,
) -> ReconstructedTarget:
    """Reuse B's representation, fit, seeds and flags; read only D5 source data."""
    config_path, audit_config_path = Path(config_path), Path(audit_config_path)
    config, settings = load_config(config_path), load_config(audit_config_path)
    accepted = settings["accepted_evidence"]
    fingerprints = {
        config_path.resolve(): sha256_file(config_path),
        audit_config_path.resolve(): sha256_file(audit_config_path),
    }
    if fingerprints[config_path.resolve()] != accepted["analysis_config_sha256"]:
        raise ValueError("The accepted analysis configuration has changed; do not rewrite B.")
    manifests = {
        name: verified_manifest(repository_path(config_path, name), digest, fingerprints)
        for name, digest in accepted["manifests"].items()
    }
    measurement = manifests[accepted["measurement_manifest"]]
    clustering = manifests[accepted["clustering_manifest"]]
    for manifest in [measurement, clustering]:
        if manifest["config_sha256"] != sha256_file(config_path):
            raise ValueError("Accepted evidence and configuration are inconsistent.")
        for name, digest in manifest["measurement_code_sha256"].items():
            path = Path(__file__).with_name(name).resolve()
            if sha256_file(path) != digest:
                raise ValueError(f"Accepted A/B implementation changed: {name}")
            fingerprints[path] = digest
    clustering_code = Path(__file__).with_name("clustering.py").resolve()
    if sha256_file(clustering_code) != clustering["clustering_code_sha256"]:
        raise ValueError("Accepted B clustering implementation changed.")
    fingerprints[clustering_code] = clustering["clustering_code_sha256"]
    if (
        clustering["choices"]["D5"]["k"] != 2
        or measurement["representation"] != "ordinal_item_thresholds"
        or config["clustering"] != clustering["settings"]
    ):
        raise ValueError("The accepted target is not the configured ordinal binary partition.")
    spec = config["integrity"]["datasets"]["D5"]
    if d5_path is None:
        root = get_drive_root(config["project"]["drive_root_env"])
        d5_path = root / config["data"][spec["source_key"]]
    flag_file = (
        Path(flags_path).resolve()
        if flags_path is not None
        else repository_path(config_path, config["response_quality"]["private_flags"])
    )
    raw = read_raw_csv(d5_path, "D5", config["integrity"]["csv_encoding"])
    if not (
        raw.sha256
        == spec["source_metadata"]["published_file_sha256"]
        == measurement["sources"]["D5"]
        == clustering["sources"]["D5"]
    ):
        raise ValueError("D5 differs from the accepted source fingerprint.")
    flag_digest = sha256_file(flag_file)
    if not flag_digest == measurement["quality_flags_sha256"] == clustering["quality_flags_sha256"]:
        raise ValueError("Quality flag file differs from the accepted B fingerprint.")
    fingerprints.update({raw.path: raw.sha256, flag_file: flag_digest})
    original_frame = raw.frame.copy(deep=True)
    flags = read_quality_flags(flag_file, "D5", raw.sha256, len(raw.frame))
    recomputed, _, _, _ = assess_responses(
        raw, spec["survey_items"], spec["allowed_responses"], config["integrity"]["missing_tokens"]
    )
    if not flags.astype(str).equals(recomputed.astype(str)):
        raise ValueError("Accepted flags disagree with the complete recomputed A flag definition.")
    coding = dict(zip(spec["allowed_responses"], range(1, 6), strict=True))
    values = raw.frame[spec["survey_items"]].apply(lambda column: column.map(coding)).to_numpy()
    inventory = pd.read_csv(
        repository_path(config_path, accepted["measurement_manifest"]).parent / "item_inventory.csv"
    )
    inventory = inventory.loc[inventory.dataset.eq("D5")].sort_values("position")
    if inventory.raw_column.tolist() != spec["survey_items"]:
        raise ValueError("Accepted item order and configured target items differ.")
    cluster_dir = repository_path(config_path, accepted["clustering_manifest"]).parent
    centroids = pd.read_csv(cluster_dir / "cluster_centroids.csv")
    sizes = pd.read_csv(cluster_dir / "cluster_sizes.csv")
    membership_file = (
        Path(memberships_path).resolve()
        if memberships_path is not None
        else repository_path(config_path, clustering["private_memberships"])
    )
    if memberships_path is not None and not membership_file.is_file():
        raise FileNotFoundError(f"Supplied accepted memberships are missing: {membership_file}")
    if membership_file.is_file():
        fingerprints[membership_file] = sha256_file(membership_file)
    seed = (
        config["project"]["random_seed"]
        + 1000 * list(config["integrity"]["datasets"]).index("D5")
        + 2
    )
    labels, checks = {}, []
    for sample in ["full", "sensitivity"]:
        mask = (
            np.ones(len(values), dtype=bool)
            if sample == "full"
            else flags.include_sensitivity.to_numpy()
        )
        features = ordinal_features(values[mask])
        fitted, centers = fit_partition(features, 2, seed, config["clustering"]["n_init"])
        reference = _reference_centers(centroids, sample, inventory.item.tolist())
        aligned, result = align_partition(
            features,
            fitted,
            centers,
            reference,
            accepted["centroid_absolute_tolerance"],
            accepted["minimum_assignment_margin"],
        )
        counts = np.bincount(aligned, minlength=2)
        stored = sizes.loc[sizes.dataset.eq("D5") & sizes["sample"].eq(sample) & sizes.k.eq(2)]
        stored = stored.sort_values("cluster")["count"].to_numpy()
        if (
            len(aligned) != accepted["expected_rows"][sample]
            or len(aligned) != measurement["samples"]["D5"][sample]
            or not np.array_equal(counts, stored)
            or counts.tolist() != accepted["expected_sizes"][sample]
        ):
            raise ValueError(f"Reconstructed {sample} sample sizes differ from accepted B.")
        positions = np.flatnonzero(mask) + 1
        original_ari = (
            compare_private_memberships(membership_file, sample, positions, aligned, raw.sha256)
            if membership_file.is_file()
            else None
        )
        labels[sample] = aligned
        checks.append(
            {
                "sample": sample,
                "n": len(aligned),
                "D5_P1_records": int(counts[0]),
                "D5_P2_records": int(counts[1]),
                "reference_fit_seed": seed,
                **result,
                "original_memberships_available": membership_file.is_file(),
                "ari_against_original_memberships": original_ari,
                "source_values_and_order_unchanged": raw.frame.equals(original_frame),
                "all_quality_flag_fields_recomputed_equal": True,
            }
        )
    common = labels["full"][flags.include_sensitivity.to_numpy()]
    sensitivity_ari = float(adjusted_rand_score(common, labels["sensitivity"]))
    comparison = pd.read_csv(cluster_dir / "quality_sensitivity.csv")
    accepted_ari = comparison.loc[
        comparison.dataset.eq("D5") & comparison.k.eq(2), "full_sensitivity_ari"
    ]
    if len(accepted_ari) != 1 or not np.isclose(
        sensitivity_ari, accepted_ari.iloc[0], rtol=0, atol=1e-12
    ):
        raise ValueError("Full/sensitivity target agreement differs from accepted B.")
    sensitivity = {
        "full_records": len(raw.frame),
        "straight_line_records": int(flags.quality_straight_line.sum()),
        "retained_records": len(common),
        "permanent_exclusions": 0,
        "fixed_target_P1_records": int((common == 0).sum()),
        "fixed_target_P2_records": int((common == 1).sum()),
        "refit_target_P1_records": int((labels["sensitivity"] == 0).sum()),
        "refit_target_P2_records": int((labels["sensitivity"] == 1).sum()),
        "changed_assignment_records": int((common != labels["sensitivity"]).sum()),
        "full_sensitivity_ari": sensitivity_ari,
    }
    if not raw.frame.equals(original_frame):
        raise RuntimeError("Raw source values or record order changed during reconstruction.")
    verify_unchanged(fingerprints)
    return ReconstructedTarget(
        config, settings, raw, flags, labels, pd.DataFrame(checks), sensitivity, fingerprints
    )
