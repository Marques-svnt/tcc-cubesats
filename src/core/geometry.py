"""Geometry module for 3D re-entrant auxetic cellular metamaterials.

This module provides analytical calculations of geometric properties,
relative density, effective Poisson's ratio, and Design for Additive
Manufacturing (DfAM) constraints for CubeSat hybrid panels.
"""

import logging
import math
from typing import Dict, Tuple

logger = logging.getLogger(__name__)


def calculate_relative_density(
    theta_deg: float,
    thickness_t: float,
    length_l: float,
    height_h: float,
) -> float:
    """Calculates the analytical relative density (rho* / rho_s) of a re-entrant honeycomb.

    Based on the Gibson-Ashby analytical model extended by Cui et al. (2025)
    for 2D/3D re-entrant auxetic cellular cores.

    Args:
        theta_deg: Re-entrant angle in degrees (55 <= theta <= 80).
        thickness_t: Strut wall thickness in mm (t > 0).
        length_l: Length of the inclined re-entrant strut in mm (l > 0).
        height_h: Height of the vertical strut in mm (h > 0).

    Returns:
        Analytical relative density (rho* / rho_s) dimensionless scalar.

    Raises:
        ValueError: If geometric parameters are non-positive or theta is invalid.
    """
    if thickness_t <= 0 or length_l <= 0 or height_h <= 0:
        logger.error(
            "Non-positive geometric dimensions: t=%.3f, l=%.3f, h=%.3f",
            thickness_t,
            length_l,
            height_h,
        )
        raise ValueError("Geometric dimensions t, l, and h must be strictly positive.")

    if not (45.0 <= theta_deg <= 89.0):
        logger.error("Invalid re-entrant angle theta=%.2f deg", theta_deg)
        raise ValueError("Re-entrant angle theta must be between 45 and 89 degrees.")

    theta_rad = math.radians(theta_deg)
    cos_theta = math.cos(theta_rad)
    sin_theta = math.sin(theta_rad)
    ratio_h_l = height_h / length_l

    # Relative density analytical formulation
    numerator = (thickness_t / length_l) * (ratio_h_l + 2.0)
    denominator = 2.0 * cos_theta * (ratio_h_l + sin_theta)

    rel_density = numerator / denominator
    logger.debug(
        "Calculated relative density=%.4f for theta=%.2f deg, t=%.3f mm",
        rel_density,
        theta_deg,
        thickness_t,
    )
    return rel_density


def calculate_analytical_poisson_ratio(
    theta_deg: float,
    height_h: float,
    length_l: float,
) -> float:
    """Calculates the in-plane negative Poisson's ratio (nu_yx*) for a re-entrant cell.

    Under small elastic deformations where bending of the inclined struts dominates.

    Args:
        theta_deg: Re-entrant angle in degrees.
        height_h: Height of the vertical strut in mm.
        length_l: Length of the inclined strut in mm.

    Returns:
        Effective Poisson's ratio (negative scalar indicating auxeticity).
    """
    theta_rad = math.radians(theta_deg)
    cos_theta = math.cos(theta_rad)
    sin_theta = math.sin(theta_rad)
    ratio_h_l = height_h / length_l

    numerator = sin_theta * (ratio_h_l + sin_theta)
    denominator = cos_theta**2

    poisson_eff = -(numerator / denominator)
    logger.debug(
        "Calculated effective Poisson ratio=%.4f for theta=%.2f deg",
        poisson_eff,
        theta_deg,
    )
    return poisson_eff


def validate_dfam_constraints(
    theta_deg: float,
    thickness_t: float,
    length_l: float,
    height_h: float,
    min_thickness_mm: float = 0.50,
    min_overhang_angle_deg: float = 45.0,
) -> Tuple[bool, Dict[str, str]]:
    """Validates Design for Additive Manufacturing (DfAM) constraints for L-PBF printing.

    Checks self-supporting overhangs, minimum wall thickness, and geometry validity.

    Args:
        theta_deg: Re-entrant angle in degrees.
        thickness_t: Strut thickness in mm.
        length_l: Strut length in mm.
        height_h: Strut height in mm.
        min_thickness_mm: Minimum printable feature size for AlSi10Mg L-PBF.
        min_overhang_angle_deg: Minimum self-supporting angle relative to build plate.

    Returns:
        Tuple (is_valid, validation_messages_dict).
    """
    is_valid = True
    messages: Dict[str, str] = {}

    if thickness_t < min_thickness_mm:
        is_valid = False
        messages["thickness"] = (
            f"Strut thickness {thickness_t:.2f} mm is below L-PBF limit ({min_thickness_mm:.2f} mm)."
        )

    # The re-entrant strut inclination relative to the horizontal build plate is theta_deg
    overhang_angle = theta_deg
    if overhang_angle < min_overhang_angle_deg:
        is_valid = False
        messages["overhang"] = (
            f"Overhang angle {overhang_angle:.1f} deg is below self-supporting threshold "
            f"({min_overhang_angle_deg:.1f} deg). Internal supports would be required."
        )

    if height_h <= thickness_t or length_l <= thickness_t:
        is_valid = False
        messages["aspect_ratio"] = "Strut length or height is smaller than strut thickness."

    return is_valid, messages
