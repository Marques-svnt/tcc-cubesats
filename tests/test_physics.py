"""Unit tests for the physics and fatigue module (src/core/physics.py)."""

import pytest
from src.core.physics import (
    calculate_gibson_ashby_modulus,
    calculate_margin_of_safety,
    calculate_steinberg_fatigue_damage,
)


def test_gibson_ashby_modulus_scaling() -> None:
    """Verifies that Gibson-Ashby modulus scales with (rho*/rho_s)^2."""
    e_solid = 68.0  # AlSi10Mg
    e_eff_1 = calculate_gibson_ashby_modulus(relative_density=0.10, solid_modulus_gpa=e_solid)
    e_eff_2 = calculate_gibson_ashby_modulus(relative_density=0.20, solid_modulus_gpa=e_solid)

    # In quadratic scaling (n=2), doubling relative density should quadruple effective modulus
    ratio = e_eff_2 / e_eff_1
    assert pytest.approx(ratio, rel=1e-2) == 4.0


def test_steinberg_fatigue_damage_accumulation() -> None:
    """Verifies cumulative damage computation under Steinberg 3-band method."""
    damage, details = calculate_steinberg_fatigue_damage(
        f_natural_hz=120.0,
        peak_3sigma_stress_mpa=90.0,
        duration_seconds=120.0,
    )
    assert damage >= 0.0
    assert "damage_total" in details
    assert details["damage_total"] == damage
    assert details["sigma_3_mpa"] == 90.0
    assert pytest.approx(details["sigma_1_mpa"], rel=1e-3) == 30.0


def test_margin_of_safety_positive_and_negative() -> None:
    """Verifies Margin of Safety calculation."""
    # Positive margin: allowable 184 MPa, applied 100 MPa -> MS = 0.84
    ms_pos = calculate_margin_of_safety(applied_stress_mpa=100.0, allowable_stress_mpa=184.0)
    assert ms_pos > 0.0
    assert pytest.approx(ms_pos, rel=1e-2) == 0.84

    # Negative margin (failure condition): allowable 184 MPa, applied 200 MPa -> MS = -0.08
    ms_neg = calculate_margin_of_safety(applied_stress_mpa=200.0, allowable_stress_mpa=184.0)
    assert ms_neg < 0.0
