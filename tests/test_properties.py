"""Property-based invariant testing suite using Hypothesis.

Verifies mechanical and mathematical invariants for 3D re-entrant auxetic geometry,
Gibson-Ashby scaling laws, Steinberg fatigue damage accumulation, and DfAM constraints
across arbitrary continuous spaces.
"""

import math

import hypothesis.strategies as st
import pytest
from hypothesis import assume, given, settings

from src.core.geometry import (
    calculate_analytical_poisson_ratio,
    calculate_relative_density,
    validate_dfam_constraints,
)
from src.core.physics import (
    calculate_gibson_ashby_modulus,
    calculate_margin_of_safety,
    calculate_steinberg_fatigue_damage,
    calculate_ultimate_margin_of_safety,
)
from src.core.settings import get_settings

_SETTINGS = get_settings()


# ===========================================================================
# Strategies for Continuous Parameter Exploration
# ===========================================================================

# Canonical auxetic parameter ranges
st_theta = st.floats(min_value=50.0, max_value=85.0, allow_nan=False, allow_infinity=False)
st_thickness = st.floats(min_value=0.50, max_value=1.80, allow_nan=False, allow_infinity=False)
st_length = st.floats(min_value=6.00, max_value=15.00, allow_nan=False, allow_infinity=False)
st_height = st.floats(min_value=8.00, max_value=20.00, allow_nan=False, allow_infinity=False)

# Extended search space for fuzzing
st_extended_theta = st.floats(min_value=46.0, max_value=88.0, allow_nan=False, allow_infinity=False)
st_positive_density = st.floats(
    min_value=0.01, max_value=0.99, allow_nan=False, allow_infinity=False
)
st_stress = st.floats(min_value=1.0, max_value=500.0, allow_nan=False, allow_infinity=False)
st_freq = st.floats(min_value=20.0, max_value=2000.0, allow_nan=False, allow_infinity=False)


# ===========================================================================
# Property Invariant Tests
# ===========================================================================


@given(theta=st_extended_theta, thickness_t=st_thickness, length_l=st_length, height_h=st_height)
@settings(max_examples=100)
def test_property_relative_density_is_positive(
    theta: float, thickness_t: float, length_l: float, height_h: float
) -> None:
    """Invariant: Analytical relative density must always be strictly positive."""
    assume(height_h / length_l > math.sin(math.radians(theta)) + 1e-3)
    rho_rel = calculate_relative_density(theta, thickness_t, length_l, height_h)
    assert rho_rel > 0.0
    assert not math.isnan(rho_rel)
    assert not math.isinf(rho_rel)


@given(theta=st_extended_theta, length_l=st_length, height_h=st_height)
@settings(max_examples=100)
def test_property_poisson_ratio_is_strictly_negative(
    theta: float, length_l: float, height_h: float
) -> None:
    """Invariant: Re-entrant cell in-plane Poisson ratio must be strictly negative (auxetic)."""
    nu_eff = calculate_analytical_poisson_ratio(theta, height_h, length_l)
    assert nu_eff < 0.0
    assert not math.isnan(nu_eff)
    assert not math.isinf(nu_eff)


@given(
    rho1=st_positive_density,
    delta=st.floats(min_value=0.001, max_value=0.30, allow_nan=False, allow_infinity=False),
)
@settings(max_examples=100)
def test_property_gibson_ashby_modulus_is_strictly_monotonic(rho1: float, delta: float) -> None:
    """Invariant: Effective Young's modulus must increase monotonically with relative density."""
    rho2 = min(0.999, rho1 + delta)
    if rho2 <= rho1:
        return

    e_star1 = calculate_gibson_ashby_modulus(rho1, solid_modulus_gpa=68.0)
    e_star2 = calculate_gibson_ashby_modulus(rho2, solid_modulus_gpa=68.0)

    assert e_star1 < e_star2
    assert e_star1 > 0.0


@given(f_hz=st_freq, stress=st_stress)
@settings(max_examples=100)
def test_property_steinberg_damage_is_non_negative_and_monotonic(
    f_hz: float, stress: float
) -> None:
    """Invariant: Steinberg fatigue damage D >= 0 and strictly increases with peak stress."""
    d1, _ = calculate_steinberg_fatigue_damage(f_hz, stress, duration_seconds=120.0)
    d2, _ = calculate_steinberg_fatigue_damage(f_hz, stress * 1.05, duration_seconds=120.0)

    assert d1 >= 0.0
    assert d2 > d1
    assert not math.isnan(d1)


@given(stress=st_stress)
@settings(max_examples=100)
def test_property_margin_of_safety_monotonicity_and_root(stress: float) -> None:
    """Invariant: Margin of safety decreases monotonically with applied stress, and MS(sigma_adm) == 0."""
    allowable = 184.0  # MPa
    ms1 = calculate_margin_of_safety(stress, allowable_stress_mpa=allowable)
    ms2 = calculate_margin_of_safety(stress * 1.10, allowable_stress_mpa=allowable)

    assert ms1 > ms2
    assert math.isclose(calculate_margin_of_safety(allowable, allowable), 0.0, abs_tol=1e-7)


@given(
    theta=st.floats(min_value=20.0, max_value=44.9, allow_nan=False, allow_infinity=False),
    thickness_t=st_thickness,
    length_l=st_length,
    height_h=st_height,
)
@settings(max_examples=50)
def test_property_dfam_rejects_subcritical_overhang(
    theta: float, thickness_t: float, length_l: float, height_h: float
) -> None:
    """Invariant: DfAM validation must reject any overhang angle below threshold (45 deg)."""
    is_valid, messages = validate_dfam_constraints(
        theta_deg=theta,
        thickness_t=thickness_t,
        length_l=length_l,
        height_h=height_h,
        min_overhang_angle_deg=45.0,
    )
    assert not is_valid
    assert "overhang" in messages


@given(
    theta=st_theta,
    thickness_t=st.floats(min_value=0.01, max_value=0.49, allow_nan=False, allow_infinity=False),
    length_l=st_length,
    height_h=st_height,
)
@settings(max_examples=50)
def test_property_dfam_rejects_subcritical_thickness(
    theta: float, thickness_t: float, length_l: float, height_h: float
) -> None:
    """Invariant: DfAM validation must reject strut thicknesses below printable limit (0.50 mm)."""
    is_valid, messages = validate_dfam_constraints(
        theta_deg=theta,
        thickness_t=thickness_t,
        length_l=length_l,
        height_h=height_h,
        min_thickness_mm=0.50,
    )
    assert not is_valid
    assert "thickness" in messages


@given(
    bad_dim=st.floats(max_value=0.0, allow_nan=False, allow_infinity=False),
)
@settings(max_examples=25)
def test_property_relative_density_raises_on_non_positive_dimensions(bad_dim: float) -> None:
    """Invariant: calculate_relative_density raises ValueError for non-positive dimensions."""
    with pytest.raises(ValueError, match="strictly positive"):
        calculate_relative_density(65.0, bad_dim, 10.0, 15.0)

    with pytest.raises(ValueError, match="strictly positive"):
        calculate_relative_density(65.0, 1.0, bad_dim, 15.0)

    with pytest.raises(ValueError, match="strictly positive"):
        calculate_relative_density(65.0, 1.0, 10.0, bad_dim)


@given(stress=st_stress)
@settings(max_examples=100)
def test_property_ultimate_margin_of_safety_monotonicity_and_root(stress: float) -> None:
    """Invariant: Ultimate margin of safety decreases monotonically with stress and MS_ult(allowable) == 0."""
    allowable_ult = 340.0 / 1.40  # 242.857 MPa
    ms1 = calculate_ultimate_margin_of_safety(stress, ultimate_strength_mpa=340.0, safety_factor_ultimate=1.40)
    ms2 = calculate_ultimate_margin_of_safety(stress * 1.10, ultimate_strength_mpa=340.0, safety_factor_ultimate=1.40)
    assert ms1 > ms2
    assert math.isclose(
        calculate_ultimate_margin_of_safety(allowable_ult, ultimate_strength_mpa=340.0, safety_factor_ultimate=1.40),
        0.0,
        abs_tol=1e-5,
    )

