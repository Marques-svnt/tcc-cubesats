"""Centralized, typed configuration and settings management using Pydantic v2.

This module provides immutable, validated configuration models for the CubeSat 1U
chassis optimization project, loading specifications directly from the canonical
YAML files in the configs/ directory.

Enforces fail-fast validation for physical parameters (NASA GSFC-STD-7000A, AlSi10Mg
LPBF material limits, and geometric optimization bounds), eliminating configuration
drift and hardcoding across solvers and agent pipelines.
"""

import logging
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, ConfigDict, Field, field_validator

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# NASA GEVS Specifications Schema (GSFC-STD-7000A)
# ---------------------------------------------------------------------------


class GevsGeneralConfig(BaseModel):
    """General environmental testing and qualification metadata."""

    model_config = ConfigDict(frozen=True)

    standard: str = Field(default="NASA GSFC-STD-7000A")
    qualification_level: str = Field(default="General Environmental Verification Standard")
    duration_per_axis_seconds: float = Field(default=120.0, gt=0.0)
    damping_ratio: float = Field(default=0.020, gt=0.0, lt=0.50)
    axes: list[str] = Field(default_factory=lambda: ["X", "Y", "Z"])

    @field_validator("damping_ratio")
    @classmethod
    def validate_damping_ratio(cls, v: float) -> float:
        """Ensures damping ratio corresponds to physical aerospace structures (0.5% to 20%)."""
        if not (0.005 <= v <= 0.20):
            raise ValueError(
                f"Damping ratio zeta={v} outside expected structural range [0.005, 0.20]."
            )
        return v


class PsdPointConfig(BaseModel):
    """Single frequency and PSD amplitude breakpoint."""

    model_config = ConfigDict(frozen=True)

    freq: float = Field(gt=0.0)
    psd: float = Field(ge=0.0)


class GevsPsdConfig(BaseModel):
    """NASA GEVS Random Vibration Power Spectral Density (PSD) Profile."""

    model_config = ConfigDict(frozen=True)

    overall_acceleration_grms: float = Field(default=14.10, gt=0.0)
    frequency_profile_hz: list[PsdPointConfig] = Field(default_factory=list)


class GevsStiffnessConfig(BaseModel):
    """Launcher-decoupling fundamental frequency constraints."""

    model_config = ConfigDict(frozen=True)

    minimum_fundamental_frequency_hz: float = Field(default=100.0, gt=0.0)


class GevsPPodInterfaceConfig(BaseModel):
    """CalPoly P-POD deployer geometric and mass envelope interface."""

    model_config = ConfigDict(frozen=True)

    rail_length_mm: float = Field(default=113.5, gt=0.0)
    rail_cross_section_mm: float = Field(default=8.5, gt=0.0)
    rail_tolerance_mm: float = Field(default=0.1, gt=0.0)
    max_total_mass_kg: float = Field(default=1.33, gt=0.0)
    max_structural_mass_kg: float = Field(default=0.35, gt=0.0)


class GevsSpecsConfig(BaseModel):
    """Root configuration for NASA GEVS requirements."""

    model_config = ConfigDict(frozen=True)

    general: GevsGeneralConfig = Field(default_factory=GevsGeneralConfig)
    random_vibration_psd: GevsPsdConfig = Field(default_factory=GevsPsdConfig)
    stiffness_requirements: GevsStiffnessConfig = Field(default_factory=GevsStiffnessConfig)
    interface_p_pod: GevsPPodInterfaceConfig = Field(default_factory=GevsPPodInterfaceConfig)


# ---------------------------------------------------------------------------
# Metallic Flight Material Schema (AlSi10Mg LPBF)
# ---------------------------------------------------------------------------


class AlSi10MgBaseConfig(BaseModel):
    """Base physical and elastic properties for AlSi10Mg additive alloy."""

    model_config = ConfigDict(frozen=True)

    name: str = Field(default="AlSi10Mg")
    process: str = Field(default="Laser Powder Bed Fusion (L-PBF)")
    condition: str = Field(default="Stress Relieved (300C / 2h)")
    density_kg_m3: float = Field(default=2680.0, gt=0.0)
    young_modulus_gpa: float = Field(default=68.0, gt=0.0)
    poisson_ratio: float = Field(default=0.33, gt=0.0, lt=0.50)
    shear_modulus_gpa: float = Field(default=25.5, gt=0.0)


class AlSi10MgStrengthConfig(BaseModel):
    """Static strength limits for AlSi10Mg LPBF."""

    model_config = ConfigDict(frozen=True)

    yield_strength_mpa: float = Field(default=230.0, gt=0.0)
    ultimate_tensile_strength_mpa: float = Field(default=340.0, gt=0.0)
    elongation_percent: float = Field(default=5.5, ge=0.0)


class AlSi10MgSafetyFactorsConfig(BaseModel):
    """NASA safety factors and allowable design stress."""

    model_config = ConfigDict(frozen=True)

    yield_factor: float = Field(default=1.25, ge=1.0)
    ultimate_factor: float = Field(default=1.40, ge=1.0)
    allowable_stress_yield_mpa: float = Field(default=184.0, gt=0.0)


class AlSi10MgFatigueConfig(BaseModel):
    """Random vibration fatigue and Basquin parameters."""

    model_config = ConfigDict(frozen=True)

    fatigue_limit_runout_cycles: float = Field(default=1.0e7, gt=0.0)
    fatigue_strength_limit_mpa: float = Field(default=75.0, gt=0.0)
    basquin_exponent_m: float = Field(default=6.8, gt=1.0)
    basquin_constant_c: float = Field(default=1.2e20, gt=0.0)
    steinberg_cumulative_damage_limit: float = Field(default=0.25, gt=0.0, le=1.0)


class MaterialAlSi10MgConfig(BaseModel):
    """Root configuration for metallic flight material AlSi10Mg."""

    model_config = ConfigDict(frozen=True)

    material: AlSi10MgBaseConfig = Field(default_factory=AlSi10MgBaseConfig)
    strength_limits: AlSi10MgStrengthConfig = Field(default_factory=AlSi10MgStrengthConfig)
    safety_factors: AlSi10MgSafetyFactorsConfig = Field(default_factory=AlSi10MgSafetyFactorsConfig)
    fatigue_properties: AlSi10MgFatigueConfig = Field(default_factory=AlSi10MgFatigueConfig)


# ---------------------------------------------------------------------------
# Prototyping Polymer Material Schema (PLA FDM)
# ---------------------------------------------------------------------------


class PlaBaseConfig(BaseModel):
    """Physical properties for FDM PLA prototyping."""

    model_config = ConfigDict(frozen=True)

    name: str = Field(default="Polylactic Acid (PLA)")
    process: str = Field(default="Fused Deposition Modeling (FDM / FFF)")
    nozzle_diameter_mm: float = Field(default=0.4, gt=0.0)
    layer_height_mm: float = Field(default=0.2, gt=0.0)
    infill_density_percent: float = Field(default=100.0, gt=0.0, le=100.0)
    raster_angle_deg: list[int] = Field(default_factory=lambda: [0, 90])
    density_kg_m3: float = Field(default=1250.0, gt=0.0)


class PlaElasticConfig(BaseModel):
    """Isotropic analogue elastic constants for PLA."""

    model_config = ConfigDict(frozen=True)

    young_modulus_gpa: float = Field(default=3.5, gt=0.0)
    poisson_ratio: float = Field(default=0.36, gt=0.0, lt=0.50)
    shear_modulus_gpa: float = Field(default=1.28, gt=0.0)


class PlaStrengthConfig(BaseModel):
    """Strength limits for PLA."""

    model_config = ConfigDict(frozen=True)

    yield_strength_mpa: float = Field(default=50.0, gt=0.0)
    ultimate_tensile_strength_mpa: float = Field(default=60.0, gt=0.0)
    elongation_at_break_percent: float = Field(default=6.0, ge=0.0)


class MaterialPlaConfig(BaseModel):
    """Root configuration for polymer prototyping material PLA."""

    model_config = ConfigDict(frozen=True)

    material: PlaBaseConfig = Field(default_factory=PlaBaseConfig)
    elastic_properties_isotropic_analogue: PlaElasticConfig = Field(
        default_factory=PlaElasticConfig
    )
    strength_limits: PlaStrengthConfig = Field(default_factory=PlaStrengthConfig)


# ---------------------------------------------------------------------------
# Optimization Bounds & DfAM Schema
# ---------------------------------------------------------------------------


class VariableBoundConfig(BaseModel):
    """Continuous variable bounds for re-entrant cell."""

    model_config = ConfigDict(frozen=True)

    min: float
    max: float
    nominal: float
    unit: str = ""
    description: str = ""

    @field_validator("max")
    @classmethod
    def validate_max_gt_min(cls, v: float, info: Any) -> float:
        """Verifies upper bound exceeds lower bound."""
        min_val = info.data.get("min")
        if min_val is not None and v <= min_val:
            raise ValueError(f"Upper bound max={v} must strictly exceed lower bound min={min_val}.")
        return v


class OptimizationBoundsConfig(BaseModel):
    """Root configuration for design variables and DfAM constraints."""

    model_config = ConfigDict(frozen=True)

    variables: dict[str, VariableBoundConfig] = Field(default_factory=dict)
    relative_density_bounds: dict[str, float] = Field(default_factory=dict)
    dfam_constraints: dict[str, float] = Field(default_factory=dict)


# ---------------------------------------------------------------------------
# Master Project Settings Singleton
# ---------------------------------------------------------------------------


class ProjectSettings(BaseModel):
    """Unified, strongly-typed project configuration root."""

    model_config = ConfigDict(frozen=True)

    gevs: GevsSpecsConfig = Field(default_factory=GevsSpecsConfig)
    alsi10mg: MaterialAlSi10MgConfig = Field(default_factory=MaterialAlSi10MgConfig)
    pla: MaterialPlaConfig = Field(default_factory=MaterialPlaConfig)
    bounds: OptimizationBoundsConfig = Field(default_factory=OptimizationBoundsConfig)

    @classmethod
    def load_from_directory(cls, config_dir: str | Path | None = None) -> "ProjectSettings":
        """Loads and validates all project YAML configuration files.

        Args:
            config_dir: Directory containing YAML files. Defaults to project configs/.

        Returns:
            Validated, immutable ProjectSettings instance.
        """
        if config_dir is None:
            # Default to repo root / configs
            base_dir = Path(__file__).resolve().parent.parent.parent
            cfg_path = base_dir / "configs"
        else:
            cfg_path = Path(config_dir)

        logger.info("Loading project configurations from: %s", cfg_path)

        # 1. Load gevs_specs.yaml
        gevs_file = cfg_path / "gevs_specs.yaml"
        gevs_dict: dict[str, Any] = {}
        if gevs_file.exists():
            with open(gevs_file, encoding="utf-8") as f:
                gevs_dict = yaml.safe_load(f) or {}
            logger.debug("Loaded %s successfully.", gevs_file.name)
        else:
            logger.warning("%s not found; using canonical default GEVS specs.", gevs_file)

        # 2. Load material_alsi10mg.yaml
        alsi10mg_file = cfg_path / "material_alsi10mg.yaml"
        alsi10mg_dict: dict[str, Any] = {}
        if alsi10mg_file.exists():
            with open(alsi10mg_file, encoding="utf-8") as f:
                alsi10mg_dict = yaml.safe_load(f) or {}
            logger.debug("Loaded %s successfully.", alsi10mg_file.name)
        else:
            logger.warning(
                "%s not found; using canonical default AlSi10Mg material.", alsi10mg_file
            )

        # 3. Load material_pla.yaml
        pla_file = cfg_path / "material_pla.yaml"
        pla_dict: dict[str, Any] = {}
        if pla_file.exists():
            with open(pla_file, encoding="utf-8") as f:
                pla_dict = yaml.safe_load(f) or {}
            logger.debug("Loaded %s successfully.", pla_file.name)
        else:
            logger.warning("%s not found; using canonical default PLA material.", pla_file)

        # 4. Load optimization_bounds.yaml
        bounds_file = cfg_path / "optimization_bounds.yaml"
        bounds_dict: dict[str, Any] = {}
        if bounds_file.exists():
            with open(bounds_file, encoding="utf-8") as f:
                bounds_dict = yaml.safe_load(f) or {}
            logger.debug("Loaded %s successfully.", bounds_file.name)
        else:
            logger.warning("%s not found; using canonical default bounds.", bounds_file)

        return cls(
            gevs=GevsSpecsConfig(**gevs_dict),
            alsi10mg=MaterialAlSi10MgConfig(**alsi10mg_dict),
            pla=MaterialPlaConfig(**pla_dict),
            bounds=OptimizationBoundsConfig(**bounds_dict),
        )


@lru_cache(maxsize=1)
def get_settings(config_dir: str | None = None) -> ProjectSettings:
    """Returns the cached global singleton ProjectSettings instance.

    Args:
        config_dir: Optional custom path to configs directory.

    Returns:
        ProjectSettings singleton.
    """
    return ProjectSettings.load_from_directory(config_dir=config_dir)


def reload_settings(config_dir: str | None = None) -> ProjectSettings:
    """Clears cache and forces reloading of project settings from disk.

    Args:
        config_dir: Optional custom path to configs directory.

    Returns:
        Refreshed ProjectSettings instance.
    """
    get_settings.cache_clear()
    return get_settings(config_dir=config_dir)
