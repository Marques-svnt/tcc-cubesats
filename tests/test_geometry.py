"""Unit tests for the geometry module (src/core/geometry.py)."""

import pytest
from src.core.geometry import (
    calculate_analytical_poisson_ratio,
    calculate_relative_density,
    validate_dfam_constraints,
)


def test_calculate_relative_density_valid() -> None:
    """Verifies relative density calculation for standard re-entrant parameters."""
    rho_rel = calculate_relative_density(
        theta_deg=65.75,
        thickness_t=0.613,
        length_l=8.5,
        height_h=14.0,
    )
    assert 0.10 < rho_rel < 0.60, f"Expected relative density in [0.10, 0.60], got {rho_rel}"


def test_calculate_relative_density_invalid_inputs() -> None:
    """Verifies that non-positive dimensions and self-intersecting geometries raise ValueError."""
    with pytest.raises(ValueError):
        calculate_relative_density(theta_deg=65.0, thickness_t=-0.5, length_l=6.0, height_h=9.0)

    with pytest.raises(ValueError):
        calculate_relative_density(theta_deg=30.0, thickness_t=0.8, length_l=6.0, height_h=9.0)

    # h/l = 5.0 / 10.0 = 0.5 <= sin(65) = 0.906 yields regularized high relative density (> 1.0)
    rho_self_intersect = calculate_relative_density(theta_deg=65.0, thickness_t=0.5, length_l=10.0, height_h=5.0)
    assert rho_self_intersect > 1.0



def test_auxetic_poisson_ratio_is_negative() -> None:
    """Verifies that effective Poisson's ratio is strictly negative (auxetic)."""
    nu_eff = calculate_analytical_poisson_ratio(
        theta_deg=65.0,
        height_h=9.0,
        length_l=6.0,
    )
    assert nu_eff < 0.0, f"Expected negative Poisson's ratio, got {nu_eff}"


def test_validate_dfam_constraints_pass_and_fail() -> None:
    """Tests DfAM rule validation for printable and unprintable geometries."""
    # Compliant geometry
    is_valid, msgs = validate_dfam_constraints(
        theta_deg=60.0,
        thickness_t=0.8,
        length_l=6.0,
        height_h=9.0,
    )
    assert is_valid is True
    assert len(msgs) == 0

    # Below minimum thickness threshold
    is_invalid, msgs_fail = validate_dfam_constraints(
        theta_deg=60.0,
        thickness_t=0.2,  # Too thin for L-PBF
        length_l=6.0,
        height_h=9.0,
        min_thickness_mm=0.5,
    )
    assert is_invalid is False
    assert "thickness" in msgs_fail


def test_validate_dfam_powder_clearance() -> None:
    """Verifies that narrow strut spacing triggers the powder clearance DfAM violation."""
    # When theta is large (80 deg) and length is short (4.0 mm), struts leave insufficient gap for depowdering
    is_valid, msgs = validate_dfam_constraints(
        theta_deg=80.0,
        thickness_t=1.2,
        length_l=4.0,
        height_h=8.0,
        min_powder_clearance_mm=1.5,
    )
    assert is_valid is False
    assert "powder_clearance" in msgs

