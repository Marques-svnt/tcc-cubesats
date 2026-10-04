"""Analytical module for auxetic metamaterial mechanics and random fatigue qualification.

Provides pure analytical functions to evaluate Gibson-Ashby scaling laws
for re-entrant cellular solids and Steinberg 3-band cumulative fatigue damage
under NASA GEVS random vibration spectrums.
"""

import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)

# Standard materials database for CubeSat prototyping and flight structures
MATERIAL_DATABASE: Dict[str, Dict[str, float]] = {
    "AlSi10Mg": {
        "solid_modulus_gpa": 68.0,
        "solid_yield_strength_mpa": 230.0,
        "solid_density_kg_m3": 2680.0,
        "poisson_ratio": 0.33,
    },
    "PLA": {
        "solid_modulus_gpa": 3.5,
        "solid_yield_strength_mpa": 50.0,
        "solid_density_kg_m3": 1250.0,
        "poisson_ratio": 0.36,
    },
}


def calculate_gibson_ashby_properties(
    relative_density: float,
    material: str = "AlSi10Mg",
    c1: float = 1.0,
    c2: float = 0.3,
) -> dict[str, float]:
    """Computes effective cellular properties via classical Gibson-Ashby scaling laws.

    For bending-dominated cellular networks (e.g., auxetic re-entrant honeycombs):
      E* = E_s * c1 * (rho_rel)^2
      sigma_y* = sigma_ys * c2 * (rho_rel)^1.5
      rho* = rho_s * rho_rel

    Args:
        relative_density: Relative density ratio (rho* / rho_s), bounded in (0.0, 1.0].
        material: Base material designation ('AlSi10Mg' for flight or 'PLA' for FDM prototype).
        c1: Geometric proportionality coefficient for elastic modulus (default 1.0).
        c2: Geometric proportionality coefficient for yield strength (default 0.3).

    Returns:
        Dictionary containing:
            - 'effective_modulus_gpa': E* in GPa.
            - 'effective_yield_strength_mpa': sigma_y* in MPa.
            - 'effective_density_kg_m3': rho* in kg/m^3.
            - 'relative_density': relative density input.
            - 'solid_modulus_gpa': base material Young's modulus E_s.
            - 'solid_yield_strength_mpa': base material yield strength sigma_ys.

    Raises:
        ValueError: If relative_density is not in (0.0, 1.0] or if material is not recognized.
    """
    if not (0.0 < relative_density <= 1.0):
        logger.error(
            "Invalid relative density: %.4f. Must be in range (0.0, 1.0].",
            relative_density,
        )
        raise ValueError(
            f"Relative density {relative_density:.4f} is outside the physical range (0.0, 1.0]."
        )

    if material not in MATERIAL_DATABASE:
        logger.error("Material '%s' not found in database.", material)
        available = list(MATERIAL_DATABASE.keys())
        raise ValueError(f"Unknown material '{material}'. Available options: {available}")

    mat_props = MATERIAL_DATABASE[material]
    e_s = mat_props["solid_modulus_gpa"]
    sigma_ys = mat_props["solid_yield_strength_mpa"]
    rho_s = mat_props["solid_density_kg_m3"]

    # Gibson-Ashby power laws for bending-dominated cellular honeycombs
    effective_modulus = e_s * c1 * (relative_density**2.0)
    effective_yield = sigma_ys * c2 * (relative_density**1.5)
    effective_density = rho_s * relative_density

    logger.debug(
        "Gibson-Ashby evaluation for %s (rho_rel=%.3f): E*=%.3f GPa, sigma_y*=%.2f MPa",
        material,
        relative_density,
        effective_modulus,
        effective_yield,
    )

    return {
        "effective_modulus_gpa": float(effective_modulus),
        "effective_yield_strength_mpa": float(effective_yield),
        "effective_density_kg_m3": float(effective_density),
        "relative_density": float(relative_density),
        "solid_modulus_gpa": float(e_s),
        "solid_yield_strength_mpa": float(sigma_ys),
    }


def calculate_steinberg_random_fatigue(
    stress_3sigma_mpa: float,
    sn_curve_params: dict[str, float],
    duration_seconds: float = 120.0,
    dominant_freq_hz: float = 150.0,
) -> dict[str, float]:
    """Computes cumulative random fatigue damage using Steinberg's 3-band Gaussian method.

    According to NASA-HDBK-7005 and Steinberg's vibration analysis:
      - Band 1 (1-sigma stress): 68.3% of test duration -> sigma_1 = sigma_3sigma / 3.0
      - Band 2 (2-sigma stress): 27.1% of test duration -> sigma_2 = 2 * sigma_3sigma / 3.0
      - Band 3 (3-sigma stress): 4.33% of test duration -> sigma_3 = sigma_3sigma

    Cyclic life to failure N_i is obtained from Basquin's relationship:
      N_i = C * (sigma_i)^(-m)

    Cumulative Miner damage index:
      D = (n_1 / N_1) + (n_2 / N_2) + (n_3 / N_3)

    Args:
        stress_3sigma_mpa: Maximum 3-sigma peak stress from random vibration response (MPa).
        sn_curve_params: S-N parameters containing Basquin slope 'basquin_m' (or 'm')
            and coefficient 'basquin_c' (or 'c').
        duration_seconds: Qualification test duration per axis in seconds (default 120.0s).
        dominant_freq_hz: Fundamental/dominant resonant frequency in Hz (default 150.0 Hz).

    Returns:
        Dictionary containing:
            - 'cumulative_damage': Total Palmgren-Miner damage index D.
            - 'damage_band_1': Damage contribution from 1-sigma cycles.
            - 'damage_band_2': Damage contribution from 2-sigma cycles.
            - 'damage_band_3': Damage contribution from 3-sigma cycles.
            - 'cycles_band_1': Number of applied 1-sigma cycles n_1.
            - 'cycles_band_2': Number of applied 2-sigma cycles n_2.
            - 'cycles_band_3': Number of applied 3-sigma cycles n_3.
            - 'stress_1sigma_mpa': 1-sigma stress level in MPa.
            - 'stress_2sigma_mpa': 2-sigma stress level in MPa.
            - 'stress_3sigma_mpa': 3-sigma stress level in MPa.
            - 'is_compliant_nasa': 1.0 if D <= 0.25 else 0.0.

    Raises:
        ValueError: If duration or dominant frequency is non-positive, or if S-N params are missing.
    """
    if duration_seconds <= 0:
        logger.error("Duration must be strictly positive: %.2f", duration_seconds)
        raise ValueError("Duration in seconds must be greater than zero.")

    if dominant_freq_hz <= 0:
        logger.error("Dominant frequency must be strictly positive: %.2f", dominant_freq_hz)
        raise ValueError("Dominant frequency in Hz must be greater than zero.")

    if stress_3sigma_mpa < 0:
        logger.error("Stress must be non-negative: %.2f", stress_3sigma_mpa)
        raise ValueError("Stress 3-sigma must be non-negative.")

    # Retrieve Basquin parameters with flexible keys
    basquin_m = sn_curve_params.get(
        "basquin_m",
        sn_curve_params.get("m", 6.8),
    )
    basquin_c = sn_curve_params.get(
        "basquin_c",
        sn_curve_params.get("c", sn_curve_params.get("C", 1.2e20)),
    )

    if basquin_m <= 0 or basquin_c <= 0:
        logger.error("Invalid Basquin parameters: m=%.2f, C=%.2e", basquin_m, basquin_c)
        raise ValueError("Basquin parameters 'm' and 'c' must be strictly positive.")

    # If stress is zero, no fatigue damage is accumulated
    if stress_3sigma_mpa == 0.0:
        logger.info("Zero stress provided; cumulative damage is 0.0.")
        return {
            "cumulative_damage": 0.0,
            "damage_band_1": 0.0,
            "damage_band_2": 0.0,
            "damage_band_3": 0.0,
            "cycles_band_1": 0.0,
            "cycles_band_2": 0.0,
            "cycles_band_3": 0.0,
            "stress_1sigma_mpa": 0.0,
            "stress_2sigma_mpa": 0.0,
            "stress_3sigma_mpa": 0.0,
            "is_compliant_nasa": 1.0,
        }

    # Stress levels for 1-sigma, 2-sigma, and 3-sigma
    sigma_1 = stress_3sigma_mpa / 3.0
    sigma_2 = (2.0 * stress_3sigma_mpa) / 3.0
    sigma_3 = stress_3sigma_mpa

    # Total applied cycles split according to Gaussian probability distribution
    # Band 1: [-1sigma, +1sigma] -> 68.3%
    # Band 2: [-2sigma, -1sigma] U [+1sigma, +2sigma] -> 27.1%
    # Band 3: [-3sigma, -2sigma] U [+2sigma, +3sigma] -> 4.33%
    n_1 = 0.683 * dominant_freq_hz * duration_seconds
    n_2 = 0.271 * dominant_freq_hz * duration_seconds
    n_3 = 0.0433 * dominant_freq_hz * duration_seconds

    # Allowable cycles to failure via Basquin equation: N = C * sigma^(-m)
    n_allow_1 = basquin_c * (sigma_1 ** (-basquin_m))
    n_allow_2 = basquin_c * (sigma_2 ** (-basquin_m))
    n_allow_3 = basquin_c * (sigma_3 ** (-basquin_m))

    damage_1 = n_1 / n_allow_1 if n_allow_1 > 0 else 1.0
    damage_2 = n_2 / n_allow_2 if n_allow_2 > 0 else 1.0
    damage_3 = n_3 / n_allow_3 if n_allow_3 > 0 else 1.0

    cumulative_damage = damage_1 + damage_2 + damage_3
    is_compliant = 1.0 if cumulative_damage <= 0.25 else 0.0

    logger.debug(
        "Steinberg fatigue: D_total=%.6f (D1=%.6e, D2=%.6e, D3=%.6e), Compliant=%s",
        cumulative_damage,
        damage_1,
        damage_2,
        damage_3,
        bool(is_compliant),
    )

    return {
        "cumulative_damage": float(cumulative_damage),
        "damage_band_1": float(damage_1),
        "damage_band_2": float(damage_2),
        "damage_band_3": float(damage_3),
        "cycles_band_1": float(n_1),
        "cycles_band_2": float(n_2),
        "cycles_band_3": float(n_3),
        "stress_1sigma_mpa": float(sigma_1),
        "stress_2sigma_mpa": float(sigma_2),
        "stress_3sigma_mpa": float(sigma_3),
        "is_compliant_nasa": float(is_compliant),
    }
