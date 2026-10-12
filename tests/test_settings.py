"""Tests for the centralized Pydantic v2 configuration settings module."""

from pathlib import Path

import pytest
from pydantic import ValidationError

from src.core.settings import (
    GevsGeneralConfig,
    ProjectSettings,
    VariableBoundConfig,
    get_settings,
    reload_settings,
)


def test_load_settings_nominal() -> None:
    """Verifies that project settings load correctly from canonical configs directory."""
    settings = get_settings()

    # Material checks (AlSi10Mg)
    assert settings.alsi10mg.material.name == "AlSi10Mg"
    assert settings.alsi10mg.material.young_modulus_gpa == 68.0
    assert settings.alsi10mg.material.density_kg_m3 == 2680.0
    assert settings.alsi10mg.material.poisson_ratio == 0.33
    assert settings.alsi10mg.strength_limits.yield_strength_mpa == 230.0
    assert settings.alsi10mg.safety_factors.yield_factor == 1.25
    assert settings.alsi10mg.safety_factors.allowable_stress_yield_mpa == 184.0
    assert settings.alsi10mg.fatigue_properties.basquin_exponent_m == 6.8
    assert settings.alsi10mg.fatigue_properties.steinberg_cumulative_damage_limit == 0.25

    # NASA GEVS checks
    assert settings.gevs.general.standard == "NASA GSFC-STD-7000A"
    assert settings.gevs.general.duration_per_axis_seconds == 120.0
    assert settings.gevs.general.damping_ratio == 0.02
    assert settings.gevs.random_vibration_psd.overall_acceleration_grms == 14.1
    assert settings.gevs.stiffness_requirements.minimum_fundamental_frequency_hz == 100.0
    assert settings.gevs.interface_p_pod.rail_cross_section_mm == 8.5
    assert settings.gevs.interface_p_pod.rail_length_mm == 113.5

    # Prototyping Material checks (PLA)
    assert settings.pla.material.density_kg_m3 == 1250.0
    assert settings.pla.elastic_properties_isotropic_analogue.young_modulus_gpa == 3.5

    # Optimization Bounds checks
    assert "reentrant_angle_theta_deg" in settings.bounds.variables
    theta_cfg = settings.bounds.variables["reentrant_angle_theta_deg"]
    assert theta_cfg.min == 55.0
    assert theta_cfg.max == 80.0
    assert settings.bounds.dfam_constraints["rail_monolithic_width_mm"] == 8.5


def test_settings_singleton_and_reload() -> None:
    """Verifies cached singleton behavior and force-reloading."""
    s1 = get_settings()
    s2 = get_settings()
    assert s1 is s2

    s3 = reload_settings()
    assert s3 is not None
    assert s3.alsi10mg.material.young_modulus_gpa == 68.0


def test_validation_error_on_invalid_damping() -> None:
    """Verifies fail-fast validation when damping ratio is physically unreasonable."""
    with pytest.raises(ValidationError):
        GevsGeneralConfig(damping_ratio=0.50)  # Exceeds 20% limit

    with pytest.raises(ValidationError):
        GevsGeneralConfig(damping_ratio=0.001)  # Below 0.5% limit


def test_validation_error_on_invalid_bounds() -> None:
    """Verifies that upper bound smaller than or equal to lower bound raises ValidationError."""
    with pytest.raises(ValidationError):
        VariableBoundConfig(min=80.0, max=50.0, nominal=60.0)


def test_missing_directory_fallback(tmp_path: Path) -> None:
    """Verifies fallback to canonical defaults when loading from an empty directory."""
    empty_dir = tmp_path / "empty_configs"
    empty_dir.mkdir(parents=True, exist_ok=True)
    fallback_settings = ProjectSettings.load_from_directory(config_dir=empty_dir)

    assert fallback_settings.alsi10mg.material.young_modulus_gpa == 68.0
    assert fallback_settings.gevs.random_vibration_psd.overall_acceleration_grms == 14.10
    assert fallback_settings.gevs.stiffness_requirements.minimum_fundamental_frequency_hz == 100.0
