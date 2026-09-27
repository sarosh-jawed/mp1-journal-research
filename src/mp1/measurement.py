"""Reproducible measurement evidence from immutable inputs and accepted quality flags."""

from __future__ import annotations

from importlib.metadata import version
from pathlib import Path

import numpy as np
import pandas as pd
from threadpoolctl import threadpool_limits

from mp1.audit import (
    load_inputs,
    repository_path,
    sha256_file,
    source_fingerprints,
    write_reports,
)
from mp1.ordinal import minres, parallel_analysis, polychoric_matrix, validate_ordinal
from mp1.psychometrics import cfa_uls, reliability, section_decision
from mp1.response_quality import assess_responses, read_quality_flags


def load_measurement_inputs(config_path: str | Path) -> tuple:
    """Validate item coding and reuse the exact accepted response-quality definition."""
    config, raw, dictionary = load_inputs(config_path)
    if "measurement" not in config:
        raise ValueError("Required measurement configuration is missing.")
    seed = config["project"].get("random_seed")
    if not isinstance(seed, int) or seed < 0:
        raise ValueError("project.random_seed must be a nonnegative integer.")
    flag_path = repository_path(config_path, config["response_quality"]["private_flags"])
    if not flag_path.is_file():
        raise FileNotFoundError(
            "Accepted quality flags are missing. Run scripts/response_quality.py."
        )
    fingerprints = source_fingerprints(raw, dictionary)
    fingerprints[Path(config_path).resolve()] = sha256_file(config_path)
    fingerprints[flag_path] = sha256_file(flag_path)
    samples, inventory = {}, []
    for name, dataset in raw.items():
        spec = config["integrity"]["datasets"][name]
        expected = spec["source_metadata"].get("published_file_sha256")
        if expected and dataset.sha256 != expected:
            raise ValueError(f"{name}: source differs from the accepted release fingerprint.")
        labels = spec["allowed_responses"]
        if len(labels) != 5:
            raise ValueError(
                "Measurement analysis requires five explicitly ordered response labels."
            )
        flags = read_quality_flags(flag_path, name, dataset.sha256, len(dataset.frame))
        recomputed, _, _, _ = assess_responses(
            dataset, spec["survey_items"], labels, config["integrity"]["missing_tokens"]
        )
        if not np.array_equal(flags.quality_straight_line, recomputed.quality_straight_line):
            raise ValueError(f"{name}: accepted flags disagree with configured item eligibility.")
        numeric = dataset.frame[spec["survey_items"]].apply(
            lambda column, labels=labels: column.map(dict(zip(labels, range(1, 6), strict=True)))
        )
        x = validate_ordinal(numeric.to_numpy())
        if name == "D5":
            sections = config["measurement"]["d5_sections"]
            positions = [p for section in sections.values() for p in section["item_positions"]]
            if sorted(positions) != list(range(1, x.shape[1] + 1)):
                raise ValueError("D5 section membership must cover each survey item exactly once.")
            identifiers = {}
            for group, section in sections.items():
                for number, position in enumerate(section["item_positions"], 1):
                    identifiers[position] = (f"{group}{number}", group, section["label"])
        else:
            identifiers = {
                i + 1: (f"D3_{i + 1}", "unassigned", "No assumed scale") for i in range(x.shape[1])
            }
        ids = [identifiers[i + 1][0] for i in range(x.shape[1])]
        for i, column in enumerate(spec["survey_items"], 1):
            item, group, label = identifiers[i]
            inventory.append(
                {
                    "dataset": name,
                    "position": i,
                    "item": item,
                    "section": group,
                    "interpretation": label,
                    "raw_column": column,
                    "reverse_coded": False,
                }
            )
        mask = flags.include_sensitivity.to_numpy()
        samples[name] = {"full": x, "sensitivity": x[mask], "mask": mask, "items": ids}
    return config, raw, samples, pd.DataFrame(inventory), fingerprints


def execution_metadata(config_path: str | Path, raw: dict, config: dict) -> dict:
    return {
        "schema_version": "1.0",
        "config_sha256": sha256_file(config_path),
        "sources": {name: item.sha256 for name, item in raw.items()},
        "random_seed": config["project"]["random_seed"],
        "quality_flags_sha256": sha256_file(
            repository_path(config_path, config["response_quality"]["private_flags"])
        ),
        "measurement_code_sha256": {
            name: sha256_file(Path(__file__).with_name(name))
            for name in [
                "audit.py",
                "response_quality.py",
                "config.py",
                "paths.py",
                "ordinal.py",
                "psychometrics.py",
                "measurement.py",
            ]
        },
        "versions": {
            name: version(name)
            for name in ["numpy", "pandas", "scipy", "scikit-learn", "semopy", "factor-analyzer"]
        },
    }


def factor_markers(loadings: np.ndarray, settings: dict) -> tuple[list[int], list[bool]]:
    absolute = np.abs(loadings)
    primary = np.argmax(absolute, axis=1)
    highest = absolute.max(axis=1)
    second = np.sort(absolute, axis=1)[:, -2] if absolute.shape[1] > 1 else np.zeros(len(absolute))
    clear = (
        (highest >= settings["factor_salient_loading"])
        & (second < settings["factor_cross_loading"])
        & (highest - second >= settings["factor_loading_gap"])
    )
    return [int(np.sum(clear & (primary == j))) for j in range(absolute.shape[1])], clear.tolist()


@threadpool_limits.wrap(limits=1)
def run_measurement(config_path: str | Path = "config/analysis.yaml") -> Path:
    """Write ordinal measurement evidence before any clustering representation is used."""
    config, raw, samples, inventory, fingerprints = load_measurement_inputs(config_path)
    settings = config["measurement"]
    seed = config["project"]["random_seed"]
    reliability_rows, item_rows, distributions = [], [], []
    model_rows, loading_rows, phi_rows, parallel_rows, assumption_rows = [], [], [], [], []
    correlation_rows, decisions, warning_rows = [], {}, []
    for d, (dataset, sample_data) in enumerate(samples.items()):
        ids = sample_data["items"]
        for s, sample in enumerate(["full", "sensitivity"]):
            x = sample_data[sample]
            context = {"dataset": dataset, "sample": sample, "n": len(x)}
            r, pair_info = polychoric_matrix(x)
            pearson = np.corrcoef(x, rowvar=False)
            assumption_rows.append(
                {
                    **context,
                    "item_count": len(ids),
                    "minimum_category_count": int(
                        min(np.bincount(col, minlength=6)[1:].min() for col in x.T)
                    ),
                    "minimum_polychoric_eigenvalue": float(np.linalg.eigvalsh(r).min()),
                    "boundary_correlations": int(pair_info.boundary.sum()),
                    "median_cell_probability_rmse": float(pair_info.cell_probability_rmse.median()),
                    "maximum_cell_probability_error": float(
                        pair_info.maximum_cell_probability_error.max()
                    ),
                    "pairs_with_expected_cells_below_five": int(
                        pair_info.expected_cells_below_five.gt(0).sum()
                    ),
                    "maximum_polychoric_pearson_difference": float(np.max(np.abs(r - pearson))),
                }
            )
            for i, item in enumerate(ids):
                counts = np.bincount(x[:, i], minlength=6)[1:]
                distributions.append(
                    {
                        **context,
                        "item": item,
                        **{f"count_{j + 1}": int(count) for j, count in enumerate(counts)},
                    }
                )
                for j in range(i):
                    correlation_rows.append(
                        {
                            **context,
                            "item_i": item,
                            "item_j": ids[j],
                            "polychoric": r[i, j],
                            "pearson": pearson[i, j],
                        }
                    )
            retained, parallel = parallel_analysis(
                x, r, settings["parallel_repetitions"], seed + 100 * d + s
            )
            parallel_rows.extend([{**context, **row} for row in parallel.to_dict("records")])
            result_key = f"{dataset}_{sample}"
            decisions[result_key] = {"retained_factors": retained, "section_screens": {}}
            if retained:
                efa = minres(r, retained)
                markers, clear = factor_markers(efa["loadings"], settings)
                decisions[result_key].update(
                    {
                        "clear_markers_per_factor": markers,
                        "clear_items": int(sum(clear)),
                        "efa_boundary": efa["boundary"],
                        "efa_marker_screen_passes": bool(
                            not efa["boundary"]
                            and min(markers) >= settings["minimum_markers_per_factor"]
                        ),
                    }
                )
                model_rows.append(
                    {
                        **context,
                        "model": "exploratory_minres_oblimin",
                        "factors": retained,
                        "proper": not efa["boundary"],
                        "rmsr_off_diagonal": efa["rmsr_off_diagonal"],
                        "maximum_absolute_residual": efa["maximum_absolute_residual"],
                    }
                )
                for i, item in enumerate(ids):
                    for j in range(retained):
                        loading_rows.append(
                            {
                                **context,
                                "model": "exploratory_minres_oblimin",
                                "item": item,
                                "factor": f"F{j + 1}",
                                "loading": efa["loadings"][i, j],
                                "clear_marker": clear[i],
                            }
                        )
                for i in range(retained):
                    for j in range(i):
                        phi_rows.append(
                            {
                                **context,
                                "model": "exploratory_minres_oblimin",
                                "factor_i": f"F{i + 1}",
                                "factor_j": f"F{j + 1}",
                                "correlation": efa["factor_correlations"][i, j],
                            }
                        )
            if dataset == "D5":
                groups = {}
                for group, section in settings["d5_sections"].items():
                    positions = np.array(section["item_positions"]) - 1
                    group_ids = [ids[i] for i in positions]
                    groups[group] = group_ids
                    rel, item = reliability(
                        x[:, positions], r[np.ix_(positions, positions)], group_ids
                    )
                    passes, reason = section_decision(rel, settings["section_screen"])
                    decisions[result_key]["section_screens"][group] = passes
                    reliability_rows.append(
                        {
                            **context,
                            "section": group,
                            **rel,
                            "passes_screen": passes,
                            "screen_reason": reason,
                        }
                    )
                    item_rows.extend(
                        [{**context, "section": group, **row} for row in item.to_dict("records")]
                    )
                models = {"hypothesized_five_sections_uls": groups, "one_factor_uls": {"G": ids}}
            else:
                models = {"diagnostic_one_factor_uls": {"G": ids}}
            for label, groups in models.items():
                fitted = cfa_uls(r, groups, len(x))
                for message in fitted["warnings"]:
                    warning_rows.append({**context, "analysis": label, "message": message})
                model_rows.append(
                    {
                        **context,
                        "model": label,
                        "factors": len(groups),
                        **{
                            key: fitted[key]
                            for key in [
                                "proper",
                                "rmsr_off_diagonal",
                                "maximum_absolute_residual",
                                "maximum_factor_correlation",
                                "minimum_uniqueness",
                            ]
                        },
                    }
                )
                loading_rows.extend(
                    [
                        {**context, "model": label, **row, "clear_marker": None}
                        for row in fitted["loadings"].to_dict("records")
                    ]
                )
                phi = fitted["factor_correlations"]
                for i in range(len(phi)):
                    for j in range(i):
                        phi_rows.append(
                            {
                                **context,
                                "model": label,
                                "factor_i": phi.index[i],
                                "factor_j": phi.index[j],
                                "correlation": phi.iloc[i, j],
                            }
                        )
                if label == "hypothesized_five_sections_uls":
                    decisions[result_key]["five_factor_supported"] = bool(
                        fitted["proper"]
                        and fitted["maximum_absolute_residual"] <= settings["cfa_maximum_residual"]
                    )
    robust_sections = [
        group
        for group in settings["d5_sections"]
        if all(
            decisions[f"D5_{sample}"]["section_screens"][group]
            for sample in ["full", "sensitivity"]
        )
    ]
    if len(robust_sections) == len(settings["d5_sections"]):
        raise ValueError(
            "All section screens now pass. Reconsider the declared item representation."
        )
    summary = {
        **execution_metadata(config_path, raw, config),
        "samples": {
            name: {sample: len(data[sample]) for sample in ["full", "sensitivity"]}
            for name, data in samples.items()
        },
        "decisions": decisions,
        "sections_passing_both_screens": robust_sections,
        "representation": settings["clustering_representation"],
        "representation_reason": (
            "Section scores are not supported across both samples. "
            "Retain all ordinal items with equal item weight, without estimating latent scores."
        ),
        "htmt": {
            "status": "not_interpreted",
            "reason": (
                "The hypothesized reflective sections fail measurement screening; "
                "HTMT cannot rescue invalid section measurement."
            ),
        },
        "estimator": (
            "Empirical-threshold polychorics; MINRES/oblimin EFA; "
            "correlation-based ULS CFA. No WLSMV, robust standard errors, CFI, TLI, RMSEA "
            "or model p-values are claimed."
        ),
        "limitations": [
            "Polychorics assume bivariate latent normality. Cell probability discrepancies "
            "are descriptive assumption diagnostics.",
            "Ordinal omega concerns standardized latent responses, not observed 1-5 sums; "
            "it is conditional on the fitted one-factor model.",
            "All repeated anonymous records remain. Resampling describes the released records "
            "and cannot establish respondent independence.",
            "EFA is exploratory on these same records. No independent confirmation "
            "or measurement invariance is established.",
            "No item deletion, imputation, reverse coding, aliasing or permanent "
            "quality exclusion is applied.",
        ],
        "warnings": warning_rows,
        "scientific_warnings": [
            "Five-section CFA is inadmissible when proper=False; ignore its apparent fit.",
            "A retained exploratory factor is not a validated construct or a scoring key.",
            "Raw alpha and conditional ordinal omega can change with invariant responses.",
            "Cell probability discrepancies and repeated records limit latent-normal inference.",
        ],
    }
    tables = {
        "item_inventory.csv": inventory,
        "item_distributions.csv": pd.DataFrame(distributions),
        "measurement_assumptions.csv": pd.DataFrame(assumption_rows),
        "reliability.csv": pd.DataFrame(reliability_rows),
        "item_diagnostics.csv": pd.DataFrame(item_rows),
        "item_correlations.csv": pd.DataFrame(correlation_rows),
        "parallel_analysis.csv": pd.DataFrame(parallel_rows),
        "factor_models.csv": pd.DataFrame(model_rows),
        "factor_loadings.csv": pd.DataFrame(loading_rows),
        "factor_correlations.csv": pd.DataFrame(phi_rows),
    }
    destination = repository_path(config_path, config["outputs"]["root"]) / "psychometrics"
    write_reports(destination, tables, summary, "measurement_summary.json", fingerprints)
    return destination
