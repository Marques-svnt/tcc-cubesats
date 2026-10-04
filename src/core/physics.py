"""Physics and structural mechanics module for CubeSat dynamic qualification.

Implements the Gibson-Ashby scaling laws for cellular solids, NASA GEVS
random vibration response estimation, Steinberg 3-band fatigue damage
accumulation (NASA-HDBK-7005), and aerospace margins of safety.
"""

import logging
import math
from typing import Dict, Tuple

logger = logging.getLogger(__name__)


def calculate_gibson_ashby_modulus(
    relative_density: float,
    solid_modulus_gpa: float = 68.0,
    constant_c: float = 1.0,
    exponent_n: float = 2.0,
) -> float:
    """Calculates the effective elastic modulus using the classical Gibson-Ashby model.

    E* = E_s * C * (rho* / rho_s)^n

    For bending-dominated cellular solids (e.g. re-entrant honeycombs), n ~= 2.0.

    Args:
        relative_density: Relative density (rho* / rho_s) in [0.01, 1.0].
        solid_modulus_gpa: Young's modulus of solid base material (AlSi10Mg = 68 GPa).
        constant_c: Geometric topological proportionality constant (typically 0.8 - 1.2).
        exponent_n: Deformation mode exponent (2.0 for bending, 1.0 for stretching).

    Returns:
        Effective Young's modulus E* in GPa.

    Raises:
        ValueError: If relative density is outside physical bounds (0, 1].
    """
    if not (0.0 < relative_density <= 1.0):
        logger.error("Relative density out of bounds: %.4f", relative_density)
        raise ValueError("Relative density must be in the range (0.0, 1.0].")

    effective_modulus = solid_modulus_gpa * constant_c * (relative_density**exponent_n)
    logger.debug(
        "Gibson-Ashby effective modulus: E*=%.3f GPa for rho_rel=%.3f",
        effective_modulus,
        relative_density,
    )
    return effective_modulus


def calculate_steinberg_fatigue_damage(
    f_natural_hz: float,
    peak_3sigma_stress_mpa: float,
    duration_seconds: float = 120.0,
    basquin_m: float = 6.8,
    basquin_c: float = 1.2e20,
) -> Tuple[float, Dict[str, float]]:
    """Calculates cumulative fatigue damage under random vibration using Steinberg's 3-band method.

    According to NASA-HDBK-7005 and Steinberg (2000), Gaussian random stress is divided into:
      - 1-sigma stress (68.3% of time): sigma_1 = peak_3sigma / 3.0
      - 2-sigma stress (27.1% of time): sigma_2 = 2.0 * peak_3sigma / 3.0
      - 3-sigma stress (4.33% of time): sigma_3 = peak_3sigma

    Palmgren-Miner cumulative damage D:
      D = (n_1 / N_1) + (n_2 / N_2) + (n_3 / N_3) <= 0.25 (for factor of safety = 2.0 on life)

    Args:
        f_natural_hz: Resonant fundamental frequency in Hz.
        peak_3sigma_stress_mpa: Maximum 3-sigma von Mises stress in MPa.
        duration_seconds: Qualification test duration in seconds (120 s per axis in GEVS).
        basquin_m: S-N curve Basquin slope exponent for AlSi10Mg.
        basquin_c: S-N curve Basquin fatigue coefficient.

    Returns:
        Tuple of (cumulative_damage_index, details_dict).
    """
    if f_natural_hz <= 0 or peak_3sigma_stress_mpa <= 0:
        logger.warning(
            "Non-positive input to Steinberg damage: fn=%.2f Hz, stress=%.2f MPa",
            f_natural_hz,
            peak_3sigma_stress_mpa,
        )
        return 0.0, {"damage_total": 0.0}

    # Stress levels for 1-sigma, 2-sigma, 3-sigma
    sigma_1 = peak_3sigma_stress_mpa / 3.0
    sigma_2 = (2.0 * peak_3sigma_stress_mpa) / 3.0
    sigma_3 = peak_3sigma_stress_mpa

    # Cycle counts in qualification duration
    n_1 = 0.683 * f_natural_hz * duration_seconds
    n_2 = 0.271 * f_natural_hz * duration_seconds
    n_3 = 0.0433 * f_natural_hz * duration_seconds

    # Allowable cycles to failure from Basquin relation: N = C * (sigma)^(-m)
    n_allow_1 = basquin_c * (sigma_1 ** (-basquin_m))
    n_allow_2 = basquin_c * (sigma_2 ** (-basquin_m))
    n_allow_3 = basquin_c * (sigma_3 ** (-basquin_m))

    damage_1 = n_1 / n_allow_1 if n_allow_1 > 0 else 1.0
    damage_2 = n_2 / n_allow_2 if n_allow_2 > 0 else 1.0
    damage_3 = n_3 / n_allow_3 if n_allow_3 > 0 else 1.0

    damage_total = damage_1 + damage_2 + damage_3

    logger.debug(
        "Steinberg fatigue: D_total=%.6f (D1=%.6f, D2=%.6f, D3=%.6f)",
        damage_total,
        damage_1,
        damage_2,
        damage_3,
    )

    details = {
        "sigma_1_mpa": sigma_1,
        "sigma_2_mpa": sigma_2,
        "sigma_3_mpa": sigma_3,
        "damage_band_1": damage_1,
        "damage_band_2": damage_2,
        "damage_band_3": damage_3,
        "damage_total": damage_total,
    }
    return damage_total, details


def calculate_margin_of_safety(
    applied_stress_mpa: float,
    allowable_stress_mpa: float,
) -> float:
    """Calculates standard aerospace Margin of Safety (MS).

    MS = (Allowable Stress / Applied Stress) - 1.0

    A structure is compliant when MS >= 0.0.

    Args:
        applied_stress_mpa: Maximum applied stress (e.g. 3-sigma peak stress).
        allowable_stress_mpa: Allowable stress (e.g. sigma_yield / FS_yield).

    Returns:
        Margin of Safety (scalar).
    """
    if applied_stress_mpa <= 0:
        return float("inf")

    margin = (allowable_stress_mpa / applied_stress_mpa) - 1.0
    logger.debug(
        "Margin of Safety: MS=%.3f (Allowable=%.2f, Applied=%.2f)",
        margin,
        allowable_stress_mpa,
        applied_stress_mpa,
    )
    return margin
