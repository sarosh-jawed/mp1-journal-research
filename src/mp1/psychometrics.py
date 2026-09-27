"""Reliability diagnostics and ordinal correlation-based measurement models."""

from __future__ import annotations

import warnings

import numpy as np
import pandas as pd
from semopy import Model

from mp1.ordinal import check_correlation, minres


def alpha(covariance: np.ndarray) -> float:
    """Calculate coefficient alpha without truncating negative estimates."""
    covariance = np.asarray(covariance, dtype=float)
    p = len(covariance)
    if p < 2 or covariance.sum() <= 0:
        raise ValueError("Alpha requires multiple items and positive total-score variance.")
    return float(p / (p - 1) * (1 - np.trace(covariance) / covariance.sum()))


def corrected_item_total(covariance: np.ndarray) -> np.ndarray:
    """Correlate each item with the sum of the remaining items."""
    result = []
    for i in range(len(covariance)):
        keep = np.arange(len(covariance)) != i
        denominator = covariance[i, i] * covariance[np.ix_(keep, keep)].sum()
        if denominator <= 0:
            raise ValueError("Corrected item-total correlation has zero remaining variance.")
        result.append(covariance[i, keep].sum() / np.sqrt(denominator))
    return np.array(result)


def omega(correlation: np.ndarray) -> tuple[float, dict]:
    """Estimate standardized congeneric omega, conditional on a one-factor model."""
    model = minres(correlation, 1)
    loading = model["loadings"][:, 0]
    numerator = loading.sum() ** 2
    value = numerator / (numerator + model["uniqueness"].sum())
    return float(value), model


def reliability(
    values: np.ndarray, correlation: np.ndarray, item_ids: list[str]
) -> tuple[dict, pd.DataFrame]:
    """Report raw-score alpha, latent-response reliability, and deletion diagnostics."""
    covariance = np.cov(values, rowvar=False, ddof=1)
    pearson = np.corrcoef(values, rowvar=False)
    observed_omega, _ = omega(pearson)
    ordinal_omega, model = omega(correlation)
    item_total = corrected_item_total(covariance)
    ordinal_total = corrected_item_total(correlation)
    rows = []
    for i, item in enumerate(item_ids):
        keep = np.arange(len(item_ids)) != i
        deleted_omega, _ = omega(correlation[np.ix_(keep, keep)])
        rows.append(
            {
                "item": item,
                "corrected_item_total": float(item_total[i]),
                "ordinal_item_rest_correlation": float(ordinal_total[i]),
                "alpha_if_deleted": alpha(covariance[np.ix_(keep, keep)]),
                "ordinal_omega_if_deleted": deleted_omega,
                "ordinal_one_factor_loading": float(model["loadings"][i, 0]),
            }
        )
    return {
        "alpha_raw": alpha(covariance),
        "alpha_ordinal": alpha(correlation),
        "omega_standardized_observed": observed_omega,
        "omega_ordinal_latent_response": ordinal_omega,
        "minimum_corrected_item_total": float(item_total.min()),
        "minimum_ordinal_loading": float(model["loadings"].min()),
        "one_factor_rmsr": model["rmsr_off_diagonal"],
        "one_factor_maximum_residual": model["maximum_absolute_residual"],
        "one_factor_boundary": model["boundary"],
    }, pd.DataFrame(rows)


def cfa_uls(correlation: np.ndarray, groups: dict[str, list[str]], n: int) -> dict:
    """Fit a hypothesized CFA to polychorics without claiming WLSMV inference."""
    r = check_correlation(correlation)
    items = [item for group in groups.values() for item in group]
    if len(items) != len(r) or len(set(items)) != len(items):
        raise ValueError("CFA item membership must partition the correlation matrix.")
    syntax = "\n".join(f"{name} =~ " + " + ".join(group) for name, group in groups.items())
    model = Model(syntax)
    with warnings.catch_warnings(record=True) as captured:
        warnings.simplefilter("always")
        fit = model.fit(
            cov=pd.DataFrame(r, index=items, columns=items),
            n_samples=n,
            obj="ULS",
            solver="SLSQP",
            options={"maxiter": 3000, "ftol": 1e-10},
        )
        estimates = model.inspect(std_est=True, information=None)
    if not fit.success:
        raise RuntimeError(f"Ordinal correlation CFA failed to converge: {fit.message}")
    order = [model.vars["observed"].index(item) for item in items]
    covariance = model.calc_sigma()[0][np.ix_(order, order)]
    implied = covariance / np.sqrt(np.outer(np.diag(covariance), np.diag(covariance)))
    residual = (r - implied)[np.tril_indices(len(r), -1)]
    phi = model.mx_psi / np.sqrt(np.outer(np.diag(model.mx_psi), np.diag(model.mx_psi)))
    loadings = estimates.loc[estimates.op.eq("~"), ["lval", "rval", "Est. Std"]].rename(
        columns={"lval": "item", "rval": "factor", "Est. Std": "loading"}
    )
    uniqueness = np.diag(model.mx_theta)
    proper = bool(
        np.linalg.eigvalsh(phi).min() > 1e-8
        and uniqueness.min() > 1e-6
        and loadings.loading.abs().max() < 1
    )
    return {
        "converged": True,
        "proper": proper,
        "rmsr_off_diagonal": float(np.sqrt(np.mean(residual**2))),
        "maximum_absolute_residual": float(np.max(np.abs(residual))),
        "maximum_factor_correlation": float(np.max(np.abs(phi - np.eye(len(phi))))),
        "minimum_uniqueness": float(uniqueness.min()),
        "loadings": loadings,
        "factor_correlations": pd.DataFrame(
            phi, index=model.names_psi[0], columns=model.names_psi[0]
        ),
        "warnings": sorted({str(item.message) for item in captured}),
    }


def section_decision(result: dict, criteria: dict) -> tuple[bool, str]:
    """Apply declared screening criteria, never a claim of instrument validation."""
    failures = []
    if result["alpha_raw"] < criteria["minimum_alpha"]:
        failures.append("raw_alpha")
    if result["omega_ordinal_latent_response"] < criteria["minimum_omega"]:
        failures.append("ordinal_omega")
    if result["minimum_corrected_item_total"] < criteria["minimum_item_total"]:
        failures.append("item_total")
    if result["minimum_ordinal_loading"] < criteria["minimum_loading"]:
        failures.append("loading")
    if result["one_factor_maximum_residual"] > criteria["maximum_residual"]:
        failures.append("local_residual")
    if result["one_factor_boundary"]:
        failures.append("boundary")
    return not failures, ";".join(failures) or "passes_screen_only"
