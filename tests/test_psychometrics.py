from __future__ import annotations

import numpy as np
import pytest
from scipy.integrate import quad
from scipy.special import ndtr

from mp1.ordinal import (
    check_correlation,
    minres,
    parallel_analysis,
    polychoric_matrix,
    rectangle_probabilities,
    validate_ordinal,
)
from mp1.psychometrics import alpha, cfa_uls, corrected_item_total, omega, reliability


def ordinal_fixture(n: int = 1500, p: int = 5) -> np.ndarray:
    rng = np.random.default_rng(827)
    latent = rng.normal(size=(n, 1)) * 0.8 + rng.normal(size=(n, p)) * 0.6
    return np.digitize(latent, [-1.2, -0.4, 0.3, 1.1]) + 1


@pytest.mark.parametrize("rho", [-0.9, -0.4, 0, 0.7, 0.98])
def test_ordinal_integration_against_independent_quadrature(rho: float) -> None:
    tx, ty = np.array([-1.3, -0.2, 0.5, 1.8]), np.array([-2, -0.7, 0.3, 1.2])
    probability = rectangle_probabilities(tx, ty, rho)
    expected, _ = quad(
        lambda z: (
            np.exp(-(z**2) / 2) / np.sqrt(2 * np.pi) * ndtr((ty[1] - rho * z) / np.sqrt(1 - rho**2))
        ),
        -np.inf,
        tx[2],
        epsabs=1e-11,
    )
    assert probability[:3, :2].sum() == pytest.approx(expected, abs=1e-8)
    assert probability.sum() == pytest.approx(1)
    assert np.all(probability >= 0)
    assert probability.sum(axis=1) == pytest.approx(np.diff([0, *ndtr(tx), 1]))


def test_polychorics_recover_ordinal_latent_correlation_and_are_deterministic() -> None:
    x = ordinal_fixture()
    first, diagnostics = polychoric_matrix(x)
    second, _ = polychoric_matrix(x)
    assert np.array_equal(first, second)
    assert np.mean(first[np.tril_indices(5, -1)]) == pytest.approx(0.64, abs=0.05)
    assert len(diagnostics) == 10
    assert not diagnostics.boundary.any()


@pytest.mark.parametrize(
    "invalid", [np.ones((30, 4)), np.full((30, 4), np.nan), np.full((30, 4), 6)]
)
def test_invalid_ordinal_inputs_fail_without_filtering(invalid: np.ndarray) -> None:
    with pytest.raises(ValueError):
        validate_ordinal(invalid)


def test_nonpositive_correlation_is_not_silently_smoothed() -> None:
    with pytest.raises(ValueError, match="no smoothing"):
        check_correlation(np.array([[1, 1.1], [1.1, 1]]))


def test_known_equicorrelation_reliability_and_corrected_item_total() -> None:
    r = np.eye(5) * 0.6 + 0.4
    expected_alpha = 5 * 0.4 / (1 + 4 * 0.4)
    assert alpha(r) == pytest.approx(expected_alpha)
    value, fit = omega(r)
    assert value == pytest.approx(expected_alpha, abs=1e-5)
    assert fit["rmsr_off_diagonal"] < 1e-6
    assert corrected_item_total(r) == pytest.approx(np.repeat(1.6 / np.sqrt(8.8), 5))


def test_deletion_diagnostic_identifies_unrelated_item() -> None:
    x = ordinal_fixture(n=2000)
    x[:, -1] = np.random.default_rng(3).integers(1, 6, len(x))
    r, _ = polychoric_matrix(x)
    result, items = reliability(x, r, list("abcde"))
    assert items.iloc[-1].alpha_if_deleted > result["alpha_raw"]
    assert items.iloc[-1].ordinal_omega_if_deleted > result["omega_ordinal_latent_response"]
    assert items.iloc[-1].corrected_item_total < 0.1


def test_cfa_recovers_known_correlated_factor_model() -> None:
    loading = np.zeros((10, 2))
    loading[:5, 0], loading[5:, 1] = 0.7, 0.8
    phi = np.array([[1, 0.3], [0.3, 1]])
    r = loading @ phi @ loading.T
    np.fill_diagonal(r, 1)
    fit = cfa_uls(r, {"A": [f"a{i}" for i in range(5)], "B": [f"b{i}" for i in range(5)]}, 1500)
    assert fit["proper"]
    assert fit["maximum_absolute_residual"] < 1e-4
    assert fit["maximum_factor_correlation"] == pytest.approx(0.3, abs=1e-4)
    assert fit["warnings"] == []


def test_parallel_analysis_uses_matching_ordinal_null_and_common_factors() -> None:
    x = ordinal_fixture(500, 4)
    r, _ = polychoric_matrix(x)
    retained, table = parallel_analysis(x, r, 20, 5)
    assert retained == 1
    assert table.columns.tolist() == [
        "factor_position",
        "observed_eigenvalue",
        "null_95_percentile",
        "retained",
    ]
    assert minres(r, retained)["uniqueness"].min() > 0
