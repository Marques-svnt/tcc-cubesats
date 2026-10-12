"""Core physics, geometry, state, and settings package for CubeSat 1U optimization."""

from src.core.geometry import (
    calculate_analytical_poisson_ratio,
    calculate_relative_density,
    validate_dfam_constraints,
)
from src.core.physics import (
    calculate_gibson_ashby_modulus,
    calculate_margin_of_safety,
    calculate_steinberg_fatigue_damage,
)
from src.core.settings import ProjectSettings, get_settings, reload_settings

__all__ = [
    "calculate_analytical_poisson_ratio",
    "calculate_relative_density",
    "validate_dfam_constraints",
    "calculate_gibson_ashby_modulus",
    "calculate_margin_of_safety",
    "calculate_steinberg_fatigue_damage",
    "ProjectSettings",
    "get_settings",
    "reload_settings",
]
