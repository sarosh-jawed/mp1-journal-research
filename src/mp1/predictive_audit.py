"""Audit predictive eligibility and report a descriptive alternative without fitting models."""

from __future__ import annotations

from importlib.metadata import version
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedKFold, train_test_split

from mp1.audit import missing_mask, repository_path, sha256_file, write_reports
from mp1.clustering import record_concentration
from mp1.target_audit import ReconstructedTarget, reconstruct_target


def feature_eligibility(frame: pd.DataFrame, items: list[str], review: dict) -> pd.DataFrame:
    """Account for every raw column; unreviewed columns never become eligible by default."""
    if set(items) & set(review) or len(items) != len(set(items)):
        raise ValueError("Target items and reviewed metadata must be distinct.")
    if set(frame.columns) != set(items) | set(review):
        raise ValueError("Every raw column requires an explicit target or metadata review.")
    missing = missing_mask(frame, [])
    rows = []
    for column in frame:
        target = column in items
        details = review.get(column, {})
        rows.append(
            {
                "column": column,
                "research_role": "target_defining_survey_item"
                if target
                else details["research_role"],
                "target_defining_information": "yes" if target else "no",
                "derived_from_target_defining_information": "no",
                "candidate_predictor": "no" if target else "yes",
                "reason": "Target-defining B item; using it as a predictor is circular."
                if target
                else details["interpretation"],
                "leakage_risk": "direct_target_leakage"
                if target
                else "no_target_derivation; unresolved_cross_partition_record_dependence",
                "final_eligibility_decision": "ineligible_for_prediction"
                if target
                else "leakage_eligible_context; prediction_withheld_by_evaluation_gate",
                "measurement_or_support_limitation": "Not independent of target construction."
                if target
                else details["limitation"],
                "missing_records": int(missing[column].sum()),
                "distinct_nonmissing_values": int(frame.loc[~missing[column], column].nunique()),
            }
        )
    return pd.DataFrame(rows)


def derived_information_policy() -> pd.DataFrame:
    """Exclude target derivatives and administrative controls from any future predictor list."""
    roles = [
        ("section_scores", "yes", "Any sums, means, or weighted composites of the 25 items."),
        (
            "factor_scores_or_embeddings",
            "yes",
            "Includes factors, PCA, encodings and learned representations.",
        ),
        (
            "centroid_distances_or_geometry",
            "yes",
            "Includes silhouettes, margins and cluster probabilities.",
        ),
        ("quality_straight_line", "yes", "Sensitivity control only, never a predictor."),
        (
            "include_sensitivity",
            "yes",
            "Complement of the straight-line flag; sensitivity control only.",
        ),
        ("quality_assessable", "yes", "Item-response quality control only."),
        ("has_missing_survey_response", "yes", "Item-response quality control only."),
        ("has_invalid_survey_response", "yes", "Item-response quality control only."),
        ("invariant_response", "yes", "Contains target-defining item content."),
        (
            "exact_record_or_item_pattern_group",
            "yes",
            "Dependence audit only; full records include all target items.",
        ),
        (
            "target_membership_or_relabeling",
            "yes",
            "The outcome itself, including alternate encodings.",
        ),
        (
            "source_record_number_or_index",
            "no",
            "Administrative position is not an independently measured predictor.",
        ),
        (
            "source_sha256_or_dataset",
            "no",
            "Provenance identifiers, not measured contextual variables.",
        ),
        ("include_full_sample", "no", "Constant retention control, never a predictor."),
        (
            "diagnostic_split_or_fold",
            "yes",
            "Design control stratified using the target, never a predictor.",
        ),
    ]
    return pd.DataFrame(
        [
            {
                "information": name,
                "derived_from_target_defining_information": derived,
                "candidate_predictor": "no",
                "final_eligibility_decision": "ineligible",
                "reason": reason,
            }
            for name, derived, reason in roles
        ]
    )


def freeze_diagnostic_design(
    labels: np.ndarray,
    test_size: float,
    folds: int,
    split_seed: int,
    cv_seed: int,
) -> pd.DataFrame:
    """Freeze indices only; no preprocessing, model fitting, selection or test scoring occurs."""
    y = np.asarray(labels)
    if y.ndim != 1 or set(np.unique(y)) != {0, 1}:
        raise ValueError("A complete binary target with neutral codes 0 and 1 is required.")
    if not 0 < test_size < 1 or folds < 2 or min(split_seed, cv_seed) < 0:
        raise ValueError("Invalid diagnostic split settings.")
    train, test = train_test_split(
        np.arange(len(y)), test_size=test_size, stratify=y, random_state=split_seed
    )
    if np.bincount(y[train], minlength=2).min() < folds:
        raise ValueError("Training class counts cannot support the configured diagnostic folds.")
    split = np.full(len(y), "train", dtype=object)
    split[test] = "test"
    fold = np.full(len(y), -1, dtype=int)
    splitter = StratifiedKFold(n_splits=folds, shuffle=True, random_state=cv_seed)
    for number, (_, validation) in enumerate(splitter.split(train, y[train]), 1):
        fold[train[validation]] = number
    return pd.DataFrame(
        {
            "source_record_number": np.arange(1, len(y) + 1),
            "diagnostic_split": split,
            "training_validation_fold": fold,
        }
    )


def exact_record_groups(frame: pd.DataFrame, labels: np.ndarray) -> np.ndarray:
    """Use collision-free exact tuples, solely to diagnose unresolved dependence."""
    if len(frame) != len(labels) or frame.isna().any().any():
        raise ValueError("Dependence audit requires complete record-aligned data.")
    groups, _ = pd.factorize(pd.MultiIndex.from_frame(frame), sort=False)
    check = pd.DataFrame({"group": groups, "label": labels}).groupby("group").label.nunique()
    if (check > 1).any():
        raise ValueError(
            "Identical full records cannot have different deterministic target labels."
        )
    return groups


def partition_overlap(
    groups: np.ndarray,
    labels: np.ndarray,
    training: np.ndarray,
    validation: np.ndarray,
) -> pd.DataFrame:
    """Count validation records whose exact full-record pattern occurs in training."""
    if len(groups) != len(labels) or len(training) != len(groups) or len(validation) != len(groups):
        raise ValueError("Partition audit arrays must have identical lengths.")
    if training.dtype != bool or validation.dtype != bool or np.any(training & validation):
        raise ValueError("Training and validation masks must be disjoint boolean arrays.")
    seen = np.isin(groups, np.unique(groups[training]))
    rows = []
    for label in [0, 1]:
        train = training & (labels == label)
        held_out = validation & (labels == label)
        n = int(held_out.sum())
        overlap = int(np.sum(held_out & seen))
        rows.append(
            {
                "class_id": f"D5_P{label + 1}",
                "training_records": int(train.sum()),
                "validation_records": n,
                "training_distinct_full_patterns": len(np.unique(groups[train])),
                "validation_distinct_full_patterns": len(np.unique(groups[held_out])),
                "validation_records_with_pattern_in_training": overlap,
                "validation_records_without_pattern_in_training": n - overlap,
                "validation_overlap_fraction": overlap / n if n else None,
            }
        )
    return pd.DataFrame(rows)


def grouped_allocation_obstruction(
    groups: np.ndarray,
    labels: np.ndarray,
    is_test: np.ndarray,
) -> pd.DataFrame:
    """A pure-label group larger than both class allocations proves incompatibility."""
    if len(groups) != len(labels) or len(is_test) != len(labels) or is_test.dtype != bool:
        raise ValueError("Allocation audit arrays are incompatible.")
    table = pd.DataFrame({"group": groups, "label": labels})
    if (table.groupby("group").label.nunique() > 1).any():
        raise ValueError("The allocation bound requires pure-label full-record groups.")
    rows = []
    for label in [0, 1]:
        selected = labels == label
        counts = pd.Series(groups[selected]).value_counts()
        largest = int(counts.max()) if len(counts) else 0
        train, test = int(np.sum(selected & ~is_test)), int(np.sum(selected & is_test))
        impossible = largest > max(train, test)
        rows.append(
            {
                "class_id": f"D5_P{label + 1}",
                "class_records": int(selected.sum()),
                "distinct_full_record_patterns": len(counts),
                "largest_exact_record_group": largest,
                "records_outside_largest_group": int(selected.sum()) - largest,
                "requested_training_class_records": train,
                "requested_test_class_records": test,
                "proven_incompatible_with_intact_groups": impossible,
                "interpretation": "impossible_at_these_class_allocations"
                if impossible
                else "not_ruled_out_by_this_necessary_condition; feasibility_not_established",
            }
        )
    return pd.DataFrame(rows)


def metadata_profiles(frame: pd.DataFrame, labels: np.ndarray, columns: list[str]) -> pd.DataFrame:
    """Report marginal counts and proportions, without p-values or population inference."""
    if len(frame) != len(labels) or frame[columns].isna().any().any():
        raise ValueError("Metadata description requires complete aligned records.")
    rows = []
    for column in columns:
        for value in sorted(frame[column].unique()):
            member = frame[column].eq(value).to_numpy()
            total = int(member.sum())
            for label in [0, 1]:
                size = int(np.sum(labels == label))
                count = int(np.sum(member & (labels == label)))
                rows.append(
                    {
                        "column": column,
                        "value": value,
                        "class_id": f"D5_P{label + 1}",
                        "records": count,
                        "category_records": total,
                        "class_records": size,
                        "class_fraction_within_category": count / total,
                        "category_fraction_within_class": count / size if size else None,
                    }
                )
    return pd.DataFrame(rows)


def methodological_gate(eligibility: pd.DataFrame, feasibility: pd.DataFrame) -> dict:
    """Separate feature leakage eligibility from scientific evaluation feasibility."""
    candidates = eligibility.loc[eligibility.candidate_predictor.eq("yes"), "column"].tolist()
    obstruction = bool(feasibility.proven_incompatible_with_intact_groups.any())
    return {
        "status": "blocked" if not candidates or obstruction else "requires_methodological_review",
        "target_leakage_eligible_contextual_fields": candidates,
        "independent_psychological_predictors": [],
        "psychological_correlate_question_supported": False,
        "metadata_question_meaningful_in_principle": bool(candidates),
        "metadata_descriptive_comparison_defensible": bool(candidates),
        "predictive_comparison_defensible_under_current_design": False,
        "intact_pattern_stratification_obstruction": obstruction,
        "respondent_independence_established": False,
        "modeling_performed": False,
        "explainability_performed": False,
        "reason": (
            "Only contextual metadata avoids target construction. Repeated anonymous full records "
            "have unresolved dependence. Intact-pattern protection is incompatible with the "
            "requested class allocation when a group exceeds both allocations. A record-random "
            "benchmark would largely evaluate already-seen patterns. No independent psychological "
            "correlates can be identified. Retain descriptive metadata tables and request an "
            "advisor decision or source clarification before any predictive fitting."
        ),
    }


def _summary_text(
    target: ReconstructedTarget, feasibility: pd.DataFrame, overlap: pd.DataFrame
) -> str:
    focal = feasibility.loc[feasibility.variant.eq("full") & feasibility.class_id.eq("D5_P2")].iloc[
        0
    ]
    test = overlap.loc[
        overlap.variant.eq("full")
        & overlap.stage.eq("held_out_design")
        & overlap.class_id.eq("D5_P2")
    ].iloc[0]
    return (
        "# Work Package C: predictive feasibility\n\n"
        "The audit is complete; predictive modeling and explainability are blocked. "
        "All 25 target-defining items and their derivatives are ineligible predictors. "
        "The five metadata fields are leakage-eligible contextual information, not independent "
        "psychological measures. Their marginal descriptions remain defensible.\n\n"
        "Both accepted B partitions were reconstructed with ARI=1 against assignments from the "
        "stored accepted centroids, with no ambiguous ties. Original private B memberships, "
        "if available, are checked separately. See target_reconstruction.csv for that status.\n\n"
        f"The full smaller class has {focal.class_records} records, including an exact full-record "
        f"group of {focal.largest_exact_record_group}. The frozen diagnostic split allocates "
        f"{focal.requested_training_class_records} to training and "
        f"{focal.requested_test_class_records} to test. That group cannot fit intact in either "
        f"allocation. {test.validation_records_with_pattern_in_training} of "
        f"{test.validation_records} smaller-class test records have an exact pattern in training. "
        "This is unresolved dependence risk, not proof of duplicated people.\n\n"
        f"The accepted sensitivity control flags {target.sensitivity['straight_line_records']} "
        f"records and retains {target.sensitivity['retained_records']}. The fixed full target "
        f"and B sensitivity refit differ on {target.sensitivity['changed_assignment_records']} "
        "retained records. Both versions are described using the same diagnostic split and "
        "training folds. This comparison does not redefine the primary target.\n\n"
        "No classifiers, tuning, oversampling, calibration, performance confidence intervals, "
        "SHAP, LIME or interactions were run. No best model or explained psychological correlate "
        "exists in this package. No records were permanently excluded. A and B are preserved. "
        "Research Control acceptance remains pending; D and E were not started.\n"
    )


def run_predictive_audit(
    config_path: str | Path = "config/analysis.yaml",
    audit_config_path: str | Path = "config/work_package_c.yaml",
    d5_path: str | Path | None = None,
    flags_path: str | Path | None = None,
    memberships_path: str | Path | None = None,
) -> Path:
    """Write reproducible aggregate gate evidence and ignored private target/design records."""
    target = reconstruct_target(
        config_path, audit_config_path, d5_path, flags_path, memberships_path
    )
    config, settings, raw = target.analysis, target.settings, target.raw
    private = repository_path(config_path, settings["outputs"]["private_directory"])
    destination = repository_path(config_path, settings["outputs"]["aggregate_directory"])
    if not private.is_relative_to(repository_path(config_path, "data/interim")):
        raise ValueError("Private C outputs must remain under the ignored data/interim directory.")
    if destination.is_relative_to(private) or private.is_relative_to(destination):
        raise ValueError("Private and aggregate C output directories must be separate.")
    flag_file = (
        Path(flags_path).resolve()
        if flags_path is not None
        else repository_path(config_path, config["response_quality"]["private_flags"])
    )
    spec = config["integrity"]["datasets"]["D5"]
    eligibility = feature_eligibility(raw.frame, spec["survey_items"], settings["metadata_review"])
    design_settings = settings["diagnostic_design"]
    design = freeze_diagnostic_design(
        target.labels["full"],
        config["modeling"]["test_size"],
        config["modeling"]["cv_folds"],
        design_settings["split_seed"],
        design_settings["cv_seed"],
    )
    mask = target.flags.include_sensitivity.to_numpy()
    variants = {
        "full": (np.ones(len(raw.frame), dtype=bool), target.labels["full"]),
        "sensitivity_fixed_target": (mask, target.labels["full"][mask]),
        "sensitivity_refit_target": (mask, target.labels["sensitivity"]),
    }
    profiles, concentration, overlaps, feasibility = [], [], [], []
    for variant, (keep, y) in variants.items():
        frame = raw.frame.loc[keep].reset_index(drop=True)
        subset = design.loc[keep].reset_index(drop=True)
        groups = exact_record_groups(frame, y)
        is_test = subset.diagnostic_split.eq("test").to_numpy()
        feasibility.append(
            grouped_allocation_obstruction(groups, y, is_test).assign(variant=variant)
        )
        overlaps.append(
            partition_overlap(groups, y, ~is_test, is_test).assign(
                variant=variant, stage="held_out_design", fold=0
            )
        )
        for fold in range(1, config["modeling"]["cv_folds"] + 1):
            validation = subset.training_validation_fold.eq(fold).to_numpy()
            training = ~is_test & ~validation
            overlaps.append(
                partition_overlap(groups, y, training, validation).assign(
                    variant=variant, stage="training_cv_design", fold=fold
                )
            )
        profiles.append(
            metadata_profiles(frame, y, spec["metadata_columns"]).assign(variant=variant)
        )
        counts = record_concentration(frame, y).rename(columns={"cluster": "class_id"})
        counts["class_id"] = counts.class_id.map(lambda c: f"D5_P{c}")
        counts["distinct_metadata_combinations"] = [
            len(frame.loc[y == label, spec["metadata_columns"]].drop_duplicates())
            for label in [0, 1]
        ]
        concentration.append(counts.assign(variant=variant))
    obstruction, overlap = (
        pd.concat(feasibility, ignore_index=True),
        pd.concat(overlaps, ignore_index=True),
    )
    gate = methodological_gate(eligibility, obstruction)
    summary = {
        "work_package": "C",
        "baseline_commit": settings["baseline_commit"],
        "research_control_read": settings["research_control"],
        "analysis_config_sha256": sha256_file(config_path),
        "audit_config_sha256": sha256_file(audit_config_path),
        "source_sha256": raw.sha256,
        "quality_flags_sha256": target.fingerprints[flag_file],
        "accepted_evidence": settings["accepted_evidence"],
        "code_sha256": {
            name: sha256_file(Path(__file__).with_name(name))
            for name in ["target_audit.py", "predictive_audit.py"]
        },
        "versions": {
            name: version(name)
            for name in ["numpy", "pandas", "scipy", "scikit-learn", "semopy", "factor-analyzer"]
        },
        "target": {
            "D5_P1": "Accepted B cluster 1, neutral identifier.",
            "D5_P2": "Accepted B cluster 2, neutral identifier.",
            "primary_definition": (
                "Accepted full-sample ordinal-item k=2 partition; fixed before the design audit."
            ),
            "new_population_validation": False,
        },
        "gate": gate,
        "diagnostic_design": {**design_settings, **config["modeling"]},
        "sensitivity": target.sensitivity,
        "performance_metrics": {"status": "not_applicable_gate_blocked", "best_model": None},
        "explanations": {"status": "not_applicable_gate_blocked", "causal_claims": False},
        "policies": {
            "raw_rows_modified": 0,
            "permanent_exclusions": 0,
            "deduplication": False,
            "reweighting": False,
            "hypothesis_tests": False,
            "joint_metadata_values_released": False,
            "test_performance_evaluated": False,
            "A_B_modified": False,
            "D_E_started": False,
        },
        "acceptance_status": (
            "audit_complete_pending_researcher_acceptance; predictive_work_blocked"
        ),
    }
    private_targets = pd.concat(
        [
            pd.DataFrame(
                {
                    "source_sha256": raw.sha256,
                    "source_record_number": np.flatnonzero(keep) + 1,
                    "variant": variant,
                    "class_id": [f"D5_P{label + 1}" for label in y],
                }
            )
            for variant, (keep, y) in variants.items()
        ],
        ignore_index=True,
    )
    write_reports(
        private,
        {
            "target_memberships.csv": private_targets,
            "diagnostic_design.csv": design.assign(source_sha256=raw.sha256),
        },
        {"source_sha256": raw.sha256, "purpose": "audit_only_no_models"},
        "private_manifest.json",
        target.fingerprints,
    )
    tables = {
        "feature_eligibility.csv": eligibility,
        "derived_information_policy.csv": derived_information_policy(),
        "target_reconstruction.csv": target.checks,
        "quality_target_comparison.csv": pd.DataFrame([target.sensitivity]),
        "record_concentration.csv": pd.concat(concentration, ignore_index=True),
        "evaluation_overlap.csv": overlap,
        "group_allocation_feasibility.csv": obstruction,
        "metadata_profile_descriptions.csv": pd.concat(profiles, ignore_index=True),
    }
    write_reports(
        destination,
        tables,
        summary,
        "predictive_audit_summary.json",
        target.fingerprints,
        _summary_text(target, obstruction, overlap),
    )
    return destination
