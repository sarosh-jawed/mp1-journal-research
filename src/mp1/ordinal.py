"""Ordinal correlations and diagnostic common-factor analysis."""

from __future__ import annotations

from itertools import combinations

import numpy as np
import pandas as pd
from factor_analyzer.rotator import Rotator
from numpy.polynomial.legendre import leggauss
from scipy.optimize import minimize, minimize_scalar
from scipy.special import ndtr, ndtri

_NODES, _WEIGHTS = leggauss(64)


def validate_ordinal(values: np.ndarray) -> np.ndarray:
    """Require complete, nonconstant five-category item vectors."""
    x = np.asarray(values, dtype=float)
    if x.ndim != 2 or x.shape[0] < 20 or x.shape[1] < 2:
        raise ValueError("Ordinal analysis requires at least 20 records and two items.")
    if not np.isfinite(x).all() or not np.isin(x, np.arange(1, 6)).all():
        raise ValueError("Items must contain only complete integer responses from 1 through 5.")
    if np.any(np.ptp(x, axis=0) == 0):
        raise ValueError("A constant item cannot enter correlation or factor analysis.")
    return x.astype(int)


def rectangle_probabilities(tx: np.ndarray, ty: np.ndarray, rho: float) -> np.ndarray:
    """Integrate the bivariate normal CDF deterministically over correlation."""
    if not -0.995 <= rho <= 0.995:
        raise ValueError("Polychoric correlation must lie within [-0.995, 0.995].")
    a, b = np.asarray(tx)[:, None, None], np.asarray(ty)[None, :, None]
    t = (rho / 2) * (_NODES + 1)
    integrand = np.exp(-(a * a - 2 * t * a * b + b * b) / (2 * (1 - t * t)))
    integrand /= 2 * np.pi * np.sqrt(1 - t * t)
    interior = ndtr(a[..., 0]) * ndtr(b[..., 0])
    interior += (rho / 2) * (integrand @ _WEIGHTS)
    cdf = np.zeros((len(tx) + 2, len(ty) + 2))
    cdf[1:-1, 1:-1] = interior
    cdf[-1, 1:-1], cdf[1:-1, -1], cdf[-1, -1] = ndtr(ty), ndtr(tx), 1
    probabilities = np.diff(np.diff(cdf, axis=0), axis=1)
    if probabilities.min() < -1e-10:
        raise ArithmeticError("Bivariate integration produced a negative cell probability.")
    return np.maximum(probabilities, 0)


def polychoric_pair(x: np.ndarray, y: np.ndarray) -> tuple[float, dict]:
    """Estimate thresholds from margins, then maximize the correlation likelihood."""
    _, ix = np.unique(x, return_inverse=True)
    _, iy = np.unique(y, return_inverse=True)
    table = np.zeros((ix.max() + 1, iy.max() + 1), dtype=int)
    np.add.at(table, (ix, iy), 1)
    if min(table.shape) < 2:
        raise ValueError("Polychoric estimation requires nonconstant items.")
    tx = ndtri(table.sum(axis=1).cumsum()[:-1] / len(x))
    ty = ndtri(table.sum(axis=0).cumsum()[:-1] / len(x))

    def objective(rho: float) -> float:
        probabilities = rectangle_probabilities(tx, ty, rho)
        return float(-np.sum(table * np.log(np.maximum(probabilities, 1e-15))))

    fitted = minimize_scalar(
        objective, bounds=(-0.995, 0.995), method="bounded", options={"xatol": 1e-7}
    )
    if not fitted.success or not np.isfinite(fitted.fun):
        raise RuntimeError("Polychoric likelihood failed to converge.")
    probabilities = rectangle_probabilities(tx, ty, fitted.x)
    return float(fitted.x), {
        "boundary": bool(abs(fitted.x) > 0.99),
        "empty_cells": int((table == 0).sum()),
        "expected_cells_below_five": int((len(x) * probabilities < 5).sum()),
        "cell_probability_rmse": float(np.sqrt(np.mean((table / len(x) - probabilities) ** 2))),
        "maximum_cell_probability_error": float(np.max(np.abs(table / len(x) - probabilities))),
    }


def polychoric_matrix(values: np.ndarray) -> tuple[np.ndarray, pd.DataFrame]:
    """Estimate all pairs without smoothing or replacing correlations."""
    x = validate_ordinal(values)
    correlation = np.eye(x.shape[1])
    diagnostics = []
    for i, j in combinations(range(x.shape[1]), 2):
        rho, info = polychoric_pair(x[:, i], x[:, j])
        correlation[i, j] = correlation[j, i] = rho
        diagnostics.append({"item_i": i, "item_j": j, "polychoric_r": rho, **info})
    return correlation, pd.DataFrame(diagnostics)


def check_correlation(correlation: np.ndarray) -> np.ndarray:
    r = np.asarray(correlation, dtype=float)
    if r.ndim != 2 or r.shape[0] != r.shape[1] or not np.isfinite(r).all():
        raise ValueError("A finite square correlation matrix is required.")
    if not np.allclose(r, r.T) or not np.allclose(np.diag(r), 1):
        raise ValueError("Correlation matrix must be symmetric with a unit diagonal.")
    if np.linalg.eigvalsh(r).min() <= 1e-8:
        raise ValueError("Correlation matrix is not positive definite; no smoothing is applied.")
    return r


def common_eigenvalues(correlation: np.ndarray) -> np.ndarray:
    """Use squared multiple correlations on the diagonal for common-factor retention."""
    reduced = check_correlation(correlation).copy()
    np.fill_diagonal(reduced, 1 - 1 / np.diag(np.linalg.inv(reduced)))
    return np.linalg.eigvalsh(reduced)[::-1]


def parallel_analysis(
    values: np.ndarray, correlation: np.ndarray, repetitions: int, seed: int
) -> tuple[int, pd.DataFrame]:
    """Compare common-factor eigenvalues with independently permuted ordinal items."""
    if repetitions < 20:
        raise ValueError("Parallel analysis requires at least 20 permutations.")
    x = validate_ordinal(values)
    rng = np.random.default_rng(seed)
    null = []
    for _ in range(repetitions):
        permuted = np.column_stack([rng.permutation(column) for column in x.T])
        r, _ = polychoric_matrix(permuted)
        null.append(common_eigenvalues(r))
    observed = common_eigenvalues(correlation)
    threshold = np.quantile(null, 0.95, axis=0)
    retained = np.cumprod((observed > threshold) & (observed > 0)).astype(bool)
    return int(retained.sum()), pd.DataFrame(
        {
            "factor_position": np.arange(1, x.shape[1] + 1),
            "observed_eigenvalue": observed,
            "null_95_percentile": threshold,
            "retained": retained,
        }
    )


def minres(correlation: np.ndarray, factors: int) -> dict:
    """Fit minimum residual factors with explicit uniqueness bounds and oblimin rotation."""
    r = check_correlation(correlation)
    p = len(r)
    if not 1 <= factors < p:
        raise ValueError("Factor count must be positive and smaller than the item count.")
    off = np.tril_indices(p, -1)

    def loadings(uniqueness: np.ndarray) -> np.ndarray:
        eigenvalues, vectors = np.linalg.eigh(r - np.diag(uniqueness))
        return vectors[:, -factors:] * np.sqrt(np.maximum(eigenvalues[-factors:], 0))

    def objective(uniqueness: np.ndarray) -> float:
        loading = loadings(uniqueness)
        return float(np.sum((r - loading @ loading.T)[off] ** 2))

    start = np.clip(1 / np.diag(np.linalg.inv(r)), 0.005, 0.995)
    fit = minimize(objective, start, method="L-BFGS-B", bounds=[(0.005, 1)] * p)
    if not fit.success:
        raise RuntimeError(f"Minimum residual factor optimization failed: {fit.message}")
    loading = loadings(fit.x)
    phi = np.eye(factors)
    if factors > 1:
        rotation = Rotator(method="oblimin", max_iter=2000, tol=1e-7)
        loading = rotation.fit_transform(loading)
        phi = rotation.phi_
    order = np.argsort(-(loading**2).sum(axis=0), kind="stable")
    loading, phi = loading[:, order], phi[np.ix_(order, order)]
    signs = np.sign(loading[np.argmax(np.abs(loading), axis=0), np.arange(factors)])
    loading, phi = loading * signs, phi * np.outer(signs, signs)
    common = loading @ phi @ loading.T
    residual = (r - common)[off]
    return {
        "loadings": loading,
        "factor_correlations": phi,
        "uniqueness": 1 - np.diag(common),
        "rmsr_off_diagonal": float(np.sqrt(np.mean(residual**2))),
        "maximum_absolute_residual": float(np.max(np.abs(residual))),
        "boundary": bool(np.any(fit.x <= 0.0051) or np.any(np.diag(common) >= 0.995)),
    }
