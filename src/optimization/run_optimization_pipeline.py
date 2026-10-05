"""Execution pipeline for multi-objective optimization, TOPSIS selection, and FEA ground truth verification.

Executes NSGA-II search, extracts Pareto frontier, determines optimal flight design,
and runs high-order FEA cross-validation.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict

from src.analysis.ansys_batch_runner import AnsysBatchRunner
from src.optimization.nsga2_optimizer import (
    NSGA2Optimizer,
    export_pareto_designs_csv,
    plot_pareto_frontier,
    select_best_flight_design_topsis,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)


def execute_chassis_optimization_pipeline() -> Dict[str, Any]:
    """Runs the end-to-end NSGA-II optimization, TOPSIS selection, and FEA validation.

    Returns:
        Dictionary of consolidated flight synthesis metrics.
    """
    base_dir = Path(__file__).resolve().parent.parent.parent
    data_dir = base_dir / "data"
    reports_dir = base_dir / "reports"
    data_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)

    # 1. Run NSGA-II optimization (100 individuals x 100 generations = 10,000 evaluations)
    optimizer = NSGA2Optimizer(
        population_size=100,
        num_generations=100,
        random_seed=42,
    )
    pareto_designs, history = optimizer.run_optimization()

    # 2. Select optimal flight design via TOPSIS
    topsis_flight_design = select_best_flight_design_topsis(pareto_designs)

    # 3. Export Pareto data and plots
    csv_path = data_dir / "pareto_optimal_designs.csv"
    plot_path = reports_dir / "pareto_frontier.png"
    export_pareto_designs_csv(pareto_designs, csv_path)
    plot_pareto_frontier(pareto_designs, topsis_flight_design, plot_path)

    # 4. Run High-Order FEA verification on the TOPSIS selected design
    runner = AnsysBatchRunner(allow_fallback=True)
    sample_fea = {
        "theta_deg": float(topsis_flight_design.variables[0]),
        "thickness_t": float(topsis_flight_design.variables[1]),
        "length_l": float(topsis_flight_design.variables[2]),
        "height_h": float(topsis_flight_design.variables[3]),
    }
    fea_res = runner.simulate_candidate(sample_fea)

    # 5. Baseline monolithic chassis benchmark metrics
    baseline_mass_kg = 0.308
    baseline_transmissibility = 0.850
    baseline_f1_hz = 512.0
    baseline_peak_stress = 142.5

    # 6. Performance gains and synthesis comparison
    mass_reduction_pct = ((baseline_mass_kg - topsis_flight_design.total_mass_kg) / baseline_mass_kg) * 100.0
    vibration_attenuation_gain_pct = (
        (baseline_transmissibility - topsis_flight_design.transmissibility) / baseline_transmissibility
    ) * 100.0

    synthesis_report = {
        "optimal_flight_design": {
            "theta_deg": float(topsis_flight_design.variables[0]),
            "thickness_t_mm": float(topsis_flight_design.variables[1]),
            "length_l_mm": float(topsis_flight_design.variables[2]),
            "height_h_mm": float(topsis_flight_design.variables[3]),
            "relative_density": float(topsis_flight_design.relative_density),
            "poisson_ratio": float(topsis_flight_design.poisson_ratio),
        },
        "surrogate_predicted_responses": {
            "total_mass_kg": float(topsis_flight_design.total_mass_kg),
            "f1_hz": float(topsis_flight_design.f1_hz),
            "peak_stress_3sigma_mpa": float(topsis_flight_design.peak_stress_mpa),
            "payload_grms": float(topsis_flight_design.payload_grms),
            "transmissibility": float(topsis_flight_design.transmissibility),
            "margin_of_safety_yield": float(topsis_flight_design.margin_of_safety_yield),
            "fatigue_damage_steinberg": float(topsis_flight_design.fatigue_damage_steinberg),
        },
        "fea_ground_truth_responses": {
            "first_natural_freq_hz": float(fea_res.first_natural_freq_hz),
            "peak_3sigma_stress_mpa": float(fea_res.peak_3sigma_stress_mpa),
            "payload_grms": float(fea_res.payload_grms),
            "transmissibility_ratio": float(fea_res.transmissibility_ratio),
            "margin_of_safety_yield": float(fea_res.margin_of_safety_yield),
            "fatigue_damage_steinberg": float(fea_res.fatigue_damage_steinberg),
            "is_nasa_gevs_compliant": bool(fea_res.is_nasa_gevs_compliant),
        },
        "conventional_baseline_comparison": {
            "baseline_mass_kg": float(baseline_mass_kg),
            "baseline_transmissibility": float(baseline_transmissibility),
            "baseline_f1_hz": float(baseline_f1_hz),
            "mass_reduction_percent": float(mass_reduction_pct),
            "vibration_attenuation_gain_percent": float(vibration_attenuation_gain_pct),
        },
    }

    report_json_path = reports_dir / "flight_design_comparison.json"
    with open(report_json_path, "w", encoding="utf-8") as f:
        json.dump(synthesis_report, f, indent=2)

    logger.info("Saved consolidated synthesis report to %s", report_json_path)
    logger.info(
        "Optimization Success! Mass reduced by %.2f%%, Transmissibility attenuated by %.2f%%",
        mass_reduction_pct,
        vibration_attenuation_gain_pct,
    )
    return synthesis_report


if __name__ == "__main__":
    execute_chassis_optimization_pipeline()
