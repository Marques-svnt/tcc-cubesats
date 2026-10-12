"""TPMS and Cellular Metamaterial Generator for DfAM CubeSat Structures.

Implements implicit level-set equations for Triply Periodic Minimal Surfaces (TPMS):
- Gyroid: sin(X)*cos(Y) + sin(Y)*cos(Z) + sin(Z)*cos(X) = c
- Schwarz Primitive (P): cos(X) + cos(Y) + cos(Z) = c
- Diamond (D): sin(X)*sin(Y)*sin(Z) + sin(X)*cos(Y)*cos(Z) + cos(X)*sin(Y)*cos(Z) + cos(X)*cos(Y)*sin(Z) = c

Provides spatial discretization and volumetric porosity estimation adhering to
Gibson-Ashby scaling laws for cellular additive manufacturing.
"""

from __future__ import annotations

import logging
from typing import Dict, Literal, Tuple
import numpy as np

logger = logging.getLogger(__name__)

TpmsType = Literal["gyroid", "schwarz_p", "diamond"]


class TpmsLatticeGenerator:
    """Evaluates TPMS continuous level-set functions across 3D coordinates."""

    def __init__(self, unit_cell_size_mm: float = 10.0) -> None:
        """Initializes generator with unit cell size.

        Args:
            unit_cell_size_mm: Length of a single periodic unit cell in millimeters.

        Raises:
            ValueError: If unit cell size is non-positive.
        """
        if unit_cell_size_mm <= 0.0:
            raise ValueError(f"Unit cell size must be positive, got {unit_cell_size_mm}")
        self.unit_cell_size_mm = unit_cell_size_mm
        self.wave_number_k = 2.0 * np.pi / unit_cell_size_mm
        logger.info("TpmsLatticeGenerator initialized with L_cell=%.2f mm", unit_cell_size_mm)

    def evaluate_field(
        self,
        x: np.ndarray,
        y: np.ndarray,
        z: np.ndarray,
        lattice_type: TpmsType = "gyroid",
    ) -> np.ndarray:
        """Evaluates triply periodic scalar field at spatial coordinates (x, y, z).

        Args:
            x: Array of X coordinates in millimeters.
            y: Array of Y coordinates in millimeters.
            z: Array of Z coordinates in millimeters.
            lattice_type: Morphology type ("gyroid", "schwarz_p", "diamond").

        Returns:
            NumPy array of scalar field values matching input coordinate shapes.

        Raises:
            ValueError: If coordinates cannot be broadcast or lattice_type is unrecognized.
        """
        X = self.wave_number_k * x
        Y = self.wave_number_k * y
        Z = self.wave_number_k * z

        if lattice_type == "gyroid":
            field = np.sin(X) * np.cos(Y) + np.sin(Y) * np.cos(Z) + np.sin(Z) * np.cos(X)
        elif lattice_type == "schwarz_p":
            field = np.cos(X) + np.cos(Y) + np.cos(Z)
        elif lattice_type == "diamond":
            field = (
                np.sin(X) * np.sin(Y) * np.sin(Z)
                + np.sin(X) * np.cos(Y) * np.cos(Z)
                + np.cos(X) * np.sin(Y) * np.cos(Z)
                + np.cos(X) * np.cos(Y) * np.sin(Z)
            )
        else:
            raise ValueError(f"Unsupported TPMS lattice type: {lattice_type}")

        return field

    def estimate_relative_density(
        self,
        lattice_type: TpmsType,
        isovalue_c: float,
        grid_resolution: int = 50,
    ) -> float:
        """Estimates relative solid density (rho* / rho_s) by Monte Carlo volume sampling.

        Args:
            lattice_type: Morphology type ("gyroid", "schwarz_p", "diamond").
            isovalue_c: Threshold value defining the solid-void interface boundary.
            grid_resolution: Discretization count per unit axis.

        Returns:
            Relative density in interval (0.0, 1.0).
        """
        coords = np.linspace(0.0, self.unit_cell_size_mm, grid_resolution)
        gx, gy, gz = np.meshgrid(coords, coords, coords, indexing="ij")
        field = self.evaluate_field(gx, gy, gz, lattice_type=lattice_type)

        # In skeletal TPMS, region field <= isovalue_c corresponds to solid phase
        solid_voxels = np.sum(field <= isovalue_c)
        total_voxels = field.size
        rel_density = float(solid_voxels / total_voxels)

        logger.info(
            "Estimated relative density for %s (isovalue=%.3f): %.4f",
            lattice_type,
            isovalue_c,
            rel_density,
        )
        return rel_density

    def compute_effective_mechanical_properties(
        self,
        lattice_type: TpmsType,
        relative_density: float,
        solid_modulus_gpa: float = 68.0,
        solid_yield_mpa: float = 230.0,
        solid_poisson: float = 0.33,
    ) -> Dict[str, float]:
        """Calculates homogenized effective mechanical properties using Gibson-Ashby scaling laws.

        Mathematical formulations for bending-dominated cellular solids:
            E* / E_s = C_1 * (rho* / rho_s) ^ n_1
            sigma_y* / sigma_ys = C_2 * (rho* / rho_s) ^ n_2
            nu* = nu_s * [1.0 - 0.5 * (1.0 - rho* / rho_s)]

        Parameters are calibrated for TPMS metallic L-PBF structures:
        - Gyroid: C1=0.65, n1=1.95, C2=0.45, n2=1.50
        - Schwarz Primitive: C1=0.55, n1=2.10, C2=0.38, n2=1.55
        - Diamond: C1=0.70, n1=1.90, C2=0.48, n2=1.48

        Args:
            lattice_type: TPMS morphology ("gyroid", "schwarz_p", "diamond").
            relative_density: Volume fraction rho* / rho_s in range (0.01, 1.0].
            solid_modulus_gpa: Base solid Young's modulus (AlSi10Mg = 68.0 GPa).
            solid_yield_mpa: Base solid yield strength (AlSi10Mg = 230.0 MPa).
            solid_poisson: Base solid Poisson's ratio (AlSi10Mg = 0.33).

        Returns:
            Dictionary with homogenized properties:
            e_eff_gpa, sigma_y_eff_mpa, nu_eff, relative_density.

        Raises:
            ValueError: If relative_density is non-positive or exceeds 1.0.
        """
        if not (0.0 < relative_density <= 1.0):
            raise ValueError(f"Relative density must be in (0, 1], got {relative_density}")

        if lattice_type == "gyroid":
            c1, n1, c2, n2 = 0.65, 1.95, 0.45, 1.50
        elif lattice_type == "schwarz_p":
            c1, n1, c2, n2 = 0.55, 2.10, 0.38, 1.55
        elif lattice_type == "diamond":
            c1, n1, c2, n2 = 0.70, 1.90, 0.48, 1.48
        else:
            raise ValueError(f"Unsupported lattice type: {lattice_type}")

        e_eff = solid_modulus_gpa * c1 * (relative_density**n1)
        sigma_y_eff = solid_yield_mpa * c2 * (relative_density**n2)
        nu_eff = solid_poisson * (1.0 - 0.5 * (1.0 - relative_density))

        logger.info(
            "Effective properties for %s (rho_rel=%.3f): E*=%.2f GPa, sigma_y*=%.2f MPa, nu*=%.3f",
            lattice_type,
            relative_density,
            e_eff,
            sigma_y_eff,
            nu_eff,
        )

        return {
            "e_eff_gpa": float(e_eff),
            "sigma_y_eff_mpa": float(sigma_y_eff),
            "nu_eff": float(nu_eff),
            "relative_density": float(relative_density),
        }

    def generate_functionally_graded_field(
        self,
        x: np.ndarray,
        y: np.ndarray,
        z: np.ndarray,
        z_min: float = 0.0,
        z_max: float = 113.5,
        lattice_type: TpmsType = "gyroid",
        isovalue_base: float = 0.0,
        isovalue_top: float = 0.50,
    ) -> np.ndarray:
        """Evaluates Functionally Graded Lattice (FGL) field along height axis Z.

        Varies the solid threshold boundary c(z) linearly from base to top:
            c(z) = isovalue_base + (isovalue_top - isovalue_base) * ((z - z_min) / (z_max - z_min))
            Phi_FGL(x, y, z) = field(x, y, z) - c(z)

        Enables targeted elastic wave damping at satellite mounting interfaces.

        Args:
            x: X coordinates in mm.
            y: Y coordinates in mm.
            z: Z coordinates in mm.
            z_min: Base Z coordinate (default 0.0 mm).
            z_max: Top Z coordinate (default 113.5 mm).
            lattice_type: TPMS morphology.
            isovalue_base: Threshold at bottom base.
            isovalue_top: Threshold at top payload interface.

        Returns:
            Shifted continuous level-set array where solid phase corresponds to value <= 0.
        """
        raw_field = self.evaluate_field(x, y, z, lattice_type=lattice_type)
        z_clipped = np.clip(z, z_min, z_max)
        span = max(z_max - z_min, 1e-6)
        c_z = isovalue_base + (isovalue_top - isovalue_base) * ((z_clipped - z_min) / span)
        return raw_field - c_z

