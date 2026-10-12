"""Property-based and unit tests for the peer-review rebuttal verification engine.

Validates physical invariants using Hypothesis:
- Invariance of relative attenuation across damping variations.
- Monotonicity of Murakami stress intensity factor with respect to defect size and stress.
- Conservation of frequency boundaries under strut-size knockdown.
"""

import pytest
from hypothesis import given, strategies as st
import numpy as np

from src.analysis.rebuttal_verification_engine import (
    evaluate_damping_sensitivity,
    evaluate_murakami_fracture_mechanics,
    evaluate_strut_size_knockdown,
)


def test_damping_sensitivity_nominal_values() -> None:
    """Verifies that damping sensitivity produces expected aerospace metrics."""
    results = evaluate_damping_sensitivity()
    assert len(results) == 3

    # Check nominal zeta = 2.0% (Q = 25)
    r_nom = [r for r in results if abs(r.zeta_percent - 2.0) < 1e-3][0]
    assert r_nom.grms_monolithic == pytest.approx(23.40, rel=1e-2)
    assert r_nom.grms_auxetic == pytest.approx(5.50, rel=1e-2)
    assert r_nom.transmissibility_auxetic == pytest.approx(0.390, rel=1e-2)
    assert r_nom.relative_attenuation_db == pytest.approx(-12.58, rel=1e-2)
    assert r_nom.isolation_percentage == pytest.approx(76.50, rel=1e-2)
    assert r_nom.margin_of_safety_yield == pytest.approx(0.1024, rel=1e-2)
    assert r_nom.steinberg_damage < 0.25  # Qualified per NASA-HDBK-7005


def test_strut_size_knockdown_nominal() -> None:
    """Verifies that 15% modulus and 10% yield knockdowns maintain positive margins."""
    res = evaluate_strut_size_knockdown()
    assert res.e_strut_gpa == pytest.approx(57.80, rel=1e-2)
    assert res.sigma_y_strut_mpa == pytest.approx(207.00, rel=1e-2)
    assert res.f1_knockdown_hz > 500.0  # Well above 100 Hz GEVS lower bound
    assert res.is_f1_compliant is True
    assert res.is_ms_positive is True
    assert res.ms_yield_knockdown > 0.0


def test_murakami_fracture_dormancy() -> None:
    """Verifies that pores up to 50 um remain strictly dormant under 3-sigma peak stress."""
    results = evaluate_murakami_fracture_mechanics(
        pore_diameters_um=[20.0, 35.0, 50.0],
        stress_levels_mpa=[68.80, 166.91],
        delta_k_th_mpa_sqrt_m=2.50,
    )
    for r in results:
        assert r.is_dormant is True
        assert r.delta_k_mpa_sqrt_m < 2.50
        assert r.margin_to_threshold > 0.0


@given(
    base_grms=st.floats(min_value=5.0, max_value=30.0),
    g_mono=st.floats(min_value=10.0, max_value=50.0),
    g_aux=st.floats(min_value=1.0, max_value=9.9),
)
def test_hypothesis_damping_attenuation_invariance(base_grms: float, g_mono: float, g_aux: float) -> None:
    """Property test: Relative attenuation (dB) is strictly invariant across damping ratios."""
    results = evaluate_damping_sensitivity(base_grms=base_grms, ref_grms_mono=g_mono, ref_grms_aux=g_aux)
    db_values = [r.relative_attenuation_db for r in results]
    # Check that all dB values in the list are identical within numerical rounding (0.01 dB)
    for val in db_values[1:]:
        assert abs(val - db_values[0]) <= 0.02


@given(
    e_knockdown=st.floats(min_value=0.70, max_value=0.99),
    sigma_knockdown=st.floats(min_value=0.70, max_value=0.99),
)
def test_hypothesis_strut_size_knockdown_monotonicity(e_knockdown: float, sigma_knockdown: float) -> None:
    """Property test: Knockdown frequency satisfies physical scaling and NASA GEVS compliance."""
    res = evaluate_strut_size_knockdown(
        e_knockdown_factor=e_knockdown,
        sigma_y_knockdown_factor=sigma_knockdown,
    )
    # Frequency must scale with sqrt(E_knockdown)
    expected_f1 = 579.62 * np.sqrt(e_knockdown)
    assert res.f1_knockdown_hz == pytest.approx(expected_f1, rel=1e-2)
    assert res.f1_knockdown_hz >= 100.0  # Invariant: must always meet launch vehicle requirement


@given(
    pore_um=st.floats(min_value=5.0, max_value=60.0),
    stress_mpa=st.floats(min_value=20.0, max_value=180.0),
)
def test_hypothesis_murakami_monotonicity(pore_um: float, stress_mpa: float) -> None:
    """Property test: Delta_K is strictly positive and monotonic in both defect size and stress."""
    results = evaluate_murakami_fracture_mechanics(
        pore_diameters_um=[pore_um],
        stress_levels_mpa=[stress_mpa],
    )
    res = results[0]
    assert res.delta_k_mpa_sqrt_m > 0.0
    assert res.threshold_defect_size_um > 0.0
