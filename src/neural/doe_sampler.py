"""Design of Experiments (DoE) sampler module using Latin Hypercube Sampling (LHS).

Generates statistically well-distributed geometric parameter points
across the 3D re-entrant auxetic design space for surrogate model training,
applies DfAM printability gates, computes physical properties, and exports
the input dataset for high-fidelity finite element analysis.
"""

import csv
import logging
import math
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import numpy as np

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

logger = logging.getLogger(__name__)


def generate_latin_hypercube_samples(
    num_samples: int = 250,
    random_seed: int = 42,
    bounds: Optional[Dict[str, Tuple[float, float]]] = None,
    solid_modulus_gpa: float = 68.0,
    solid_yield_mpa: float = 230.0,
    allowable_stress_mpa: float = 184.0,
) -> List[Dict[str, Any]]:
    """Generates Latin Hypercube samples across the auxetic design space with physics evaluation.

    Args:
        num_samples: Number of sample configurations to generate.
        random_seed: Random state seed for reproducibility.
        bounds: Dictionary mapping variable names to (min, max) bounds.
        solid_modulus_gpa: Young's modulus of solid AlSi10Mg in GPa.
        solid_yield_mpa: Yield strength of solid AlSi10Mg in MPa.
        allowable_stress_mpa: Maximum allowable stress (sigma_y / 1.25) in MPa.

    Returns:
        List of dictionaries with geometric, DfAM, and physics properties for each sample.
    """
    if bounds is None:
        bounds = {
            "theta_deg": (55.0, 80.0),
            "thickness_t": (0.50, 1.80),
            "length_l": (4.0, 10.0),
            "height_h": (6.0, 15.0),
        }

    rng = np.random.default_rng(random_seed)
    dim = len(bounds)
    var_names = list(bounds.keys())

    # Generate standard Latin Hypercube intervals
    intervals = np.zeros((num_samples, dim))
    for j in range(dim):
        perm = rng.permutation(num_samples)
        offset = rng.uniform(0.0, 1.0, size=num_samples)
        intervals[:, j] = (perm + offset) / num_samples

    samples: List[Dict[str, Any]] = []
    for i in range(num_samples):
        sample_dict: Dict[str, Any] = {}
        for j, name in enumerate(var_names):
            v_min, v_max = bounds[name]
            sample_dict[name] = float(v_min + intervals[i, j] * (v_max - v_min))

        # 1. DfAM compliance and analytical relative density
        is_dfam, dfam_msgs = validate_dfam_constraints(
            theta_deg=sample_dict["theta_deg"],
            thickness_t=sample_dict["thickness_t"],
            length_l=sample_dict["length_l"],
            height_h=sample_dict["height_h"],
        )

        rel_density = calculate_relative_density(
            theta_deg=sample_dict["theta_deg"],
            thickness_t=sample_dict["thickness_t"],
            length_l=sample_dict["length_l"],
            height_h=sample_dict["height_h"],
        )
        sample_dict["relative_density"] = float(rel_density)
        sample_dict["is_dfam_valid"] = 1.0 if is_dfam else 0.0

        # 2. In-plane negative Poisson's ratio
        nu_eff = calculate_analytical_poisson_ratio(
            theta_deg=sample_dict["theta_deg"],
            height_h=sample_dict["height_h"],
            length_l=sample_dict["length_l"],
        )
        sample_dict["poisson_ratio"] = float(nu_eff)

        # 3. Gibson-Ashby effective properties for AlSi10Mg
        clipped_rho = min(max(rel_density, 0.01), 1.0)
        e_effective = calculate_gibson_ashby_modulus(
            relative_density=clipped_rho,
            solid_modulus_gpa=solid_modulus_gpa,
        )
        sigma_y_effective = solid_yield_mpa * 0.3 * (clipped_rho**1.5)
        sample_dict["e_effective_gpa"] = float(e_effective)
        sample_dict["sigma_y_effective_mpa"] = float(sigma_y_effective)

        # 4. Hybrid CubeSat 1U chassis mass and stiffness proxy
        m_rails_kg = 0.088  # 4 monolithic solid rails (8.5 x 8.5 x 113.5 mm)
        m_panels_kg = 0.220 * clipped_rho
        m_total_kg = m_rails_kg + m_panels_kg

        k_rails_eff = 1.2e6  # N/m
        k_panels_eff = 2.5e6 * (e_effective / 10.0)
        k_total_eff = k_rails_eff + k_panels_eff

        fn_estimated = (1.0 / (2.0 * math.pi)) * math.sqrt(k_total_eff / m_total_kg)
        peak_3sigma_stress = 110.0 * (1.0 / (clipped_rho + 0.05)) * 0.25

        # 5. Margins of safety and Steinberg 3-band cumulative fatigue
        ms_yield = calculate_margin_of_safety(
            applied_stress_mpa=peak_3sigma_stress,
            allowable_stress_mpa=allowable_stress_mpa,
        )
        fatigue_damage, _ = calculate_steinberg_fatigue_damage(
            f_natural_hz=fn_estimated,
            peak_3sigma_stress_mpa=peak_3sigma_stress,
            duration_seconds=120.0,
        )

        sample_dict["m_total_kg"] = float(m_total_kg)
        sample_dict["fn_estimated_hz"] = float(fn_estimated)
        sample_dict["peak_3sigma_stress_mpa"] = float(peak_3sigma_stress)
        sample_dict["margin_of_safety"] = float(ms_yield)
        sample_dict["fatigue_damage_steinberg"] = float(fatigue_damage)

        # Qualification under NASA GSFC-STD-7000A
        is_compliant = (
            is_dfam
            and (0.05 <= rel_density <= 0.45)
            and (fn_estimated >= 100.0)
            and (ms_yield >= 0.0)
            and (fatigue_damage <= 0.25)
        )
        sample_dict["is_nasa_gevs_compliant"] = 1.0 if is_compliant else 0.0

        samples.append(sample_dict)

    logger.info(
        "Generated %d Latin Hypercube samples across %d dimensions (seed=%d)",
        num_samples,
        dim,
        random_seed,
    )
    return samples


def export_doe_dataset(
    samples: List[Dict[str, Any]],
    output_filepath: str | Path,
) -> Path:
    """Exports generated DoE samples to CSV format.

    Args:
        samples: List of sample dictionaries.
        output_filepath: Target destination file path (.csv).

    Returns:
        Path object pointing to the written file.

    Raises:
        ValueError: If samples list is empty.
    """
    if not samples:
        logger.error("Attempted to export empty samples list.")
        raise ValueError("Cannot export empty samples list.")

    target_path = Path(output_filepath)
    target_path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = list(samples[0].keys())
    with open(target_path, mode="w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        for sample in samples:
            writer.writerow(sample)

    logger.info("Successfully exported %d DoE samples to %s", len(samples), target_path)
    return target_path


def compute_doe_statistics(samples: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Computes summary descriptive statistics for the DoE dataset.

    Args:
        samples: List of sample dictionaries.

    Returns:
        Dictionary of aggregated metrics and qualification rates.
    """
    if not samples:
        return {}

    num_total = len(samples)
    dfam_valid_count = sum(1 for s in samples if s.get("is_dfam_valid", 0.0) == 1.0)
    gevs_compliant_count = sum(1 for s in samples if s.get("is_nasa_gevs_compliant", 0.0) == 1.0)

    rel_densities = [s["relative_density"] for s in samples]
    frequencies = [s["fn_estimated_hz"] for s in samples]
    stresses = [s["peak_3sigma_stress_mpa"] for s in samples]
    damages = [s["fatigue_damage_steinberg"] for s in samples]

    stats: Dict[str, Any] = {
        "num_total_samples": num_total,
        "dfam_valid_count": dfam_valid_count,
        "dfam_valid_percentage": (dfam_valid_count / num_total) * 100.0,
        "gevs_compliant_count": gevs_compliant_count,
        "gevs_compliant_percentage": (gevs_compliant_count / num_total) * 100.0,
        "relative_density_mean": float(np.mean(rel_densities)),
        "relative_density_min": float(np.min(rel_densities)),
        "relative_density_max": float(np.max(rel_densities)),
        "fn_estimated_mean_hz": float(np.mean(frequencies)),
        "fn_estimated_min_hz": float(np.min(frequencies)),
        "fn_estimated_max_hz": float(np.max(frequencies)),
        "peak_3sigma_stress_mean_mpa": float(np.mean(stresses)),
        "fatigue_damage_mean": float(np.mean(damages)),
    }
    return stats


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    logger.info("Running Latin Hypercube Sampling DoE generation for Sprint 1...")
    generated_samples = generate_latin_hypercube_samples(num_samples=250, random_seed=42)
    output_csv = Path(__file__).resolve().parent.parent.parent / "data" / "doe_samples_input.csv"
    export_doe_dataset(generated_samples, output_csv)
    summary_stats = compute_doe_statistics(generated_samples)
    logger.info("Sprint 1 DoE Summary Statistics: %s", summary_stats)
