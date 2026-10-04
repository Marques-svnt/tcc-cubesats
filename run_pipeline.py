"""Main demonstration pipeline for CubeSat auxetic structure optimization.

Runs the Design of Experiments (DoE) generation, evaluates geometric
parameters against DfAM rules, computes Gibson-Ashby effective properties,
and verifies structural compliance against NASA GEVS qualification thresholds.
"""

import logging
import sys
from typing import Dict, List

from src.core.geometry import calculate_analytical_poisson_ratio, validate_dfam_constraints
from src.core.physics import (
    calculate_gibson_ashby_modulus,
    calculate_margin_of_safety,
    calculate_steinberg_fatigue_damage,
)
from src.neural.doe_sampler import generate_latin_hypercube_samples

# Setup structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("cubesat_pipeline")


def run_doe_and_screening(
    num_samples: int = 100,
    f_natural_target_hz: float = 100.0,
    allowable_stress_mpa: float = 184.0,
) -> List[Dict[str, float]]:
    """Runs DoE parameter generation and screens for DfAM and structural criteria.

    Args:
        num_samples: Number of LHS points to generate.
        f_natural_target_hz: NASA GEVS minimum frequency threshold (100 Hz).
        allowable_stress_mpa: Maximum allowable stress (sigma_yield / 1.25).

    Returns:
        List of compliant candidates.
    """
    logger.info("Generating %d Latin Hypercube design samples...", num_samples)
    samples = generate_latin_hypercube_samples(num_samples=num_samples, random_seed=42)

    compliant_candidates: List[Dict[str, float]] = []

    for i, sample in enumerate(samples):
        # 1. DfAM and porosity validation
        is_dfam, _ = validate_dfam_constraints(
            theta_deg=sample["theta_deg"],
            thickness_t=sample["thickness_t"],
            length_l=sample["length_l"],
            height_h=sample["height_h"],
        )
        if not is_dfam or not (0.05 <= sample["relative_density"] <= 0.45):
            continue

        # 2. Physics & stiffness scaling
        e_effective = calculate_gibson_ashby_modulus(
            relative_density=sample["relative_density"],
            solid_modulus_gpa=68.0,  # AlSi10Mg
        )

        nu_effective = calculate_analytical_poisson_ratio(
            theta_deg=sample["theta_deg"],
            height_h=sample["height_h"],
            length_l=sample["length_l"],
        )

        # 3. Dynamic proxy estimation for hybrid chassis (4 monolithic rails + auxetic panels)
        # Rails provide baseline stiffness (K_rails) while panels provide shear/vibrational damping
        m_rails_kg = 0.088  # 4 rails (8.5x8.5x113.5 mm) in AlSi10Mg
        m_panels_kg = 0.220 * sample["relative_density"]  # 4 lattice panel faces
        m_total_kg = m_rails_kg + m_panels_kg

        k_rails_eff = 1.2e6  # N/m
        k_panels_eff = 2.5e6 * (e_effective / 10.0)
        k_total_eff = k_rails_eff + k_panels_eff

        # fn = (1 / 2pi) * sqrt(k_eff / m_eff)
        fn_estimated = (1.0 / (2.0 * 3.14159)) * (k_total_eff / m_total_kg) ** 0.5
        peak_3sigma_stress = 110.0 * (1.0 / (sample["relative_density"] + 0.05)) * 0.25

        # 4. Aerospace margins and fatigue
        ms_yield = calculate_margin_of_safety(
            applied_stress_mpa=peak_3sigma_stress,
            allowable_stress_mpa=allowable_stress_mpa,
        )

        fatigue_damage, _ = calculate_steinberg_fatigue_damage(
            f_natural_hz=fn_estimated,
            peak_3sigma_stress_mpa=peak_3sigma_stress,
        )

        sample_eval = {
            **sample,
            "e_effective_gpa": e_effective,
            "nu_effective": nu_effective,
            "fn_estimated_hz": fn_estimated,
            "peak_3sigma_stress_mpa": peak_3sigma_stress,
            "margin_of_safety": ms_yield,
            "fatigue_damage_steinberg": fatigue_damage,
        }

        # Check NASA GEVS criteria
        if fn_estimated >= f_natural_target_hz and ms_yield >= 0.0 and fatigue_damage <= 0.25:
            compliant_candidates.append(sample_eval)

    logger.info(
        "Screening complete: %d / %d samples (%.1f%%) fully compliant with NASA GEVS & DfAM.",
        len(compliant_candidates),
        num_samples,
        (len(compliant_candidates) / num_samples) * 100.0,
    )
    return compliant_candidates


if __name__ == "__main__":
    logger.info("Starting CubeSat Auxetic Qualification Pipeline...")
    results = run_doe_and_screening(num_samples=100)
    if results:
        best_candidate = min(results, key=lambda x: x["relative_density"])
        logger.info(
            "Optimal lightweight compliant candidate: "
            "theta=%.1f deg, t=%.2f mm, rho_rel=%.3f, fn=%.1f Hz, MS=%.2f, Damage=%.6f",
            best_candidate["theta_deg"],
            best_candidate["thickness_t"],
            best_candidate["relative_density"],
            best_candidate["fn_estimated_hz"],
            best_candidate["margin_of_safety"],
            best_candidate["fatigue_damage_steinberg"],
        )
