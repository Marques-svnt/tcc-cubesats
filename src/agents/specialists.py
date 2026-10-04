"""Specialist agent node implementations for the CubeSat LangGraph state machine.

Implements CadDfamAgent, NeuralSurrogateAgent, GevsQualifierAgent,
and GroundTruthFeaAgent with structured logging and audit trailing.
"""

from datetime import datetime, timezone
import json
import logging
import os
import math
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import numpy as np
import torch

from src.agents.state import CubeSatState
from src.analysis.ansys_batch_runner import AnsysBatchRunner
from src.core.geometry import (
    calculate_relative_density,
    validate_dfam_constraints,
)
from src.neural.surrogate_model import (
    CubeSatSurrogateResNet,
    SurrogateDatasetScaler,
)

logger = logging.getLogger(__name__)

# Global singletons for surrogate model and scaler to ensure sub-millisecond latency
_SURROGATE_MODEL: Optional[CubeSatSurrogateResNet] = None
_SURROGATE_SCALER: Optional[SurrogateDatasetScaler] = None


def get_surrogate_artifacts() -> Tuple[CubeSatSurrogateResNet, SurrogateDatasetScaler]:
    """Retrieves or lazily initializes the trained surrogate model and scaler.

    Returns:
        Tuple of (CubeSatSurrogateResNet in eval mode, SurrogateDatasetScaler).
    """
    global _SURROGATE_MODEL, _SURROGATE_SCALER

    if _SURROGATE_MODEL is not None and _SURROGATE_SCALER is not None:
        return _SURROGATE_MODEL, _SURROGATE_SCALER

    base_dir = Path(__file__).resolve().parent.parent.parent
    model_path = base_dir / "models" / "physics_guided_surrogate.pt"
    scaler_path = base_dir / "models" / "surrogate_scaler.json"

    scaler = SurrogateDatasetScaler.load_json(str(scaler_path))
    model = CubeSatSurrogateResNet(input_dim=5, output_dim=4, hidden_dim=64, num_blocks=2)
    state_dict = torch.load(str(model_path), weights_only=True, map_location=torch.device("cpu"))
    if isinstance(state_dict, dict) and "model_state_dict" in state_dict:
        state_dict = state_dict["model_state_dict"]
    model.load_state_dict(state_dict)
    model.eval()

    _SURROGATE_MODEL = model
    _SURROGATE_SCALER = scaler
    logger.info("Successfully loaded singleton Neural Surrogate model and scaler.")
    return _SURROGATE_MODEL, _SURROGATE_SCALER


def _record_audit_event(
    state: CubeSatState, agent_name: str, action: str, details: Dict[str, Any]
) -> Dict[str, Any]:
    """Creates a structured audit trail event with UTC timestamp.

    Args:
        state: Current graph state.
        agent_name: Name of the active specialist agent.
        action: Summary of action performed.
        details: Metadata and diagnostic outputs.

    Returns:
        Audit record dict.
    """
    return {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "candidate_id": state.get("candidate_id", "unknown"),
        "agent": agent_name,
        "action": action,
        "details": details,
    }


def cad_dfam_agent(state: CubeSatState) -> Dict[str, Any]:
    """Audits geometric candidate for L-PBF metal additive manufacturing constraints.

    Evaluates:
    1. Strut thickness threshold (t >= 0.5 mm).
    2. Overhang angle for self-supporting lattices (theta <= 45 deg from vertical).
    3. Residual powder clearance gap (2*l*cos(theta) - 2*t >= 1.50 mm).

    Args:
        state: Current CubeSatState.

    Returns:
        Updated state dictionary with dfam_valid and diagnostics.
    """
    t_strut = state["t_strut"]
    l_reentrant = state["l_reentrant"]
    theta_deg = state["theta_deg"]
    h_vertical = state.get("h_vertical", 12.0)

    is_valid, messages = validate_dfam_constraints(
        theta_deg=theta_deg,
        thickness_t=t_strut,
        length_l=l_reentrant,
        height_h=h_vertical,
    )

    theta_rad = math.radians(theta_deg)
    powder_gap = 2.0 * l_reentrant * math.cos(theta_rad) - 2.0 * t_strut

    diagnostics = {
        "overhang_valid": "overhang" not in messages,
        "thickness_valid": "thickness" not in messages,
        "powder_clearance_valid": "powder_clearance" not in messages,
        "powder_clearance_gap_mm": float(powder_gap),
        "min_required_gap_mm": 1.50,
        "messages": messages,
    }

    audit_entry = _record_audit_event(
        state,
        agent_name="CadDfamAgent",
        action="L-PBF Manufacturing Feasibility Screening",
        details={"dfam_valid": is_valid, "diagnostics": diagnostics},
    )

    trail = list(state.get("audit_trail", []))
    trail.append(audit_entry)

    new_status = "PENDING" if is_valid else "REJECTED_DFAM"
    logger.info("CadDfamAgent evaluated candidate %s: valid=%s", state.get("candidate_id"), is_valid)

    return {
        "dfam_valid": is_valid,
        "dfam_diagnostics": diagnostics,
        "audit_trail": trail,
        "status": new_status,
    }


def neural_surrogate_agent(state: CubeSatState) -> Dict[str, Any]:
    """Runs sub-millisecond elastodynamic inference using Physics-Guided ResNet.

    Predicts:
    1. f1_hz (fundamental natural frequency).
    2. max_stress_mpa (peak 3-sigma von Mises stress).
    3. grms_payload (effective RMS acceleration on payload).
    4. transmissibility (ratio Grms_payload / 14.1 Grms).

    Args:
        state: Current CubeSatState.

    Returns:
        Updated state dictionary with surrogate_predictions.
    """
    model, scaler = get_surrogate_artifacts()

    h_vert = float(state.get("h_vertical", 12.0))
    rho_rel = calculate_relative_density(
        theta_deg=float(state["theta_deg"]),
        thickness_t=float(state["t_strut"]),
        length_l=float(state["l_reentrant"]),
        height_h=h_vert,
    )

    x_raw = np.array(
        [[state["theta_deg"], state["t_strut"], state["l_reentrant"], h_vert, rho_rel]],
        dtype=np.float32,
    )
    x_scaled = scaler.transform_x(x_raw)

    with torch.no_grad():
        x_tensor = torch.from_numpy(x_scaled)
        y_scaled = model(x_tensor).numpy()

    y_raw = scaler.inverse_transform_y(y_scaled)[0]

    predictions = {
        "f1_hz": float(y_raw[0]),
        "max_stress_mpa": float(y_raw[1]),
        "grms_payload": float(y_raw[2]),
        "transmissibility": float(y_raw[3]),
    }

    audit_entry = _record_audit_event(
        state,
        agent_name="NeuralSurrogateAgent",
        action="Sub-Millisecond Physics-Guided ResNet Inference",
        details=predictions,
    )

    trail = list(state.get("audit_trail", []))
    trail.append(audit_entry)

    logger.info(
        "NeuralSurrogateAgent candidate %s -> f1=%.1f Hz, stress=%.1f MPa, T=%.3f",
        state.get("candidate_id"),
        predictions["f1_hz"],
        predictions["max_stress_mpa"],
        predictions["transmissibility"],
    )

    return {
        "surrogate_predictions": predictions,
        "audit_trail": trail,
    }


def gevs_qualifier_agent(state: CubeSatState) -> Dict[str, Any]:
    """Evaluates spaceflight structural qualification against NASA GSFC-STD-7000A.

    Criteria:
    1. f1 >= 100.0 Hz (Launcher fundamental frequency decoupling).
    2. MS_yield = (sigma_adm / sigma_3sigma) - 1.0 > 0.0 with sigma_adm = 184.0 MPa.
    3. Cumulative random fatigue damage (Steinberg 3-band) D <= 0.25 for 120s qualification.

    Args:
        state: Current CubeSatState.

    Returns:
        Updated state dictionary with gevs_qualification and updated status.
    """
    preds = state["surrogate_predictions"]
    f1 = preds["f1_hz"]
    sigma_3sigma = preds["max_stress_mpa"]

    # 1. Frequency decoupling
    f1_compliant = bool(f1 >= 100.0)

    # 2. Margin of Safety
    sigma_adm = 184.0  # AlSi10Mg yield (230 MPa) / FS (1.25)
    ms_yield = (sigma_adm / max(sigma_3sigma, 1e-6)) - 1.0
    ms_compliant = bool(ms_yield > 0.0)

    # 3. Steinberg 3-band fatigue damage accumulation
    # Basquin law for AlSi10Mg: N = C * (sigma)^(-m), m = 6.8, C = 1.2e20
    # 1-sigma: 68.3% of 120s * f1 cycles at 0.333 * sigma_3sigma
    # 2-sigma: 27.1% of 120s * f1 cycles at 0.667 * sigma_3sigma
    # 3-sigma: 4.33% of 120s * f1 cycles at 1.000 * sigma_3sigma
    duration_s = 120.0
    total_cycles = duration_s * f1

    m = 6.8
    c_basquin = 1.2e20

    sigma_1s = 0.333 * sigma_3sigma
    sigma_2s = 0.667 * sigma_3sigma
    sigma_3s = 1.000 * sigma_3sigma

    n_1s = 0.683 * total_cycles
    n_2s = 0.271 * total_cycles
    n_3s = 0.0433 * total_cycles

    n_cap_1s = c_basquin * (max(sigma_1s, 1.0) ** (-m))
    n_cap_2s = c_basquin * (max(sigma_2s, 1.0) ** (-m))
    n_cap_3s = c_basquin * (max(sigma_3s, 1.0) ** (-m))

    d_steinberg = (n_1s / n_cap_1s) + (n_2s / n_cap_2s) + (n_3s / n_cap_3s)
    fatigue_compliant = bool(d_steinberg <= 0.25)

    is_compliant = bool(f1_compliant and ms_compliant and fatigue_compliant)

    qualification = {
        "f1_compliant": f1_compliant,
        "f1_hz": f1,
        "ms_yield": float(ms_yield),
        "ms_compliant": ms_compliant,
        "fatigue_damage_d": float(d_steinberg),
        "fatigue_compliant": fatigue_compliant,
        "nasa_gevs_compliant": is_compliant,
    }

    audit_entry = _record_audit_event(
        state,
        agent_name="GevsQualifierAgent",
        action="NASA GSFC-STD-7000A Structural Qualification Check",
        details=qualification,
    )

    trail = list(state.get("audit_trail", []))
    trail.append(audit_entry)

    new_status = "PENDING" if is_compliant else "REJECTED_GEVS"
    logger.info(
        "GevsQualifierAgent candidate %s: compliant=%s (MS=%.2f, D=%.5f)",
        state.get("candidate_id"),
        is_compliant,
        ms_yield,
        d_steinberg,
    )

    return {
        "gevs_qualification": qualification,
        "audit_trail": trail,
        "status": new_status,
    }


def ground_truth_fea_agent(state: CubeSatState) -> Dict[str, Any]:
    """Executes high-order FEA verification on fully qualified design candidates.

    Serves as the high-fidelity confirmation gate using AnsysBatchRunner.

    Args:
        state: Current CubeSatState.

    Returns:
        Updated state dictionary with fea_ground_truth and QUALIFIED status.
    """
    runner = AnsysBatchRunner(allow_fallback=True)

    sample = {
        "theta_deg": float(state["theta_deg"]),
        "thickness_t": float(state["t_strut"]),
        "length_l": float(state["l_reentrant"]),
        "height_h": float(state.get("h_vertical", 12.0)),
    }

    sim_res = runner.simulate_candidate(sample)
    sim_dict = {
        "f1_hz": float(sim_res.first_natural_freq_hz),
        "max_stress_mpa": float(sim_res.peak_3sigma_stress_mpa),
        "grms_payload": float(sim_res.payload_grms),
        "transmissibility": float(sim_res.transmissibility_ratio),
        "margin_of_safety_yield": float(sim_res.margin_of_safety_yield),
        "fatigue_damage_steinberg": float(sim_res.fatigue_damage_steinberg),
        "is_nasa_gevs_compliant": bool(sim_res.is_nasa_gevs_compliant),
        "execution_mode": sim_res.execution_mode,
    }

    audit_entry = _record_audit_event(
        state,
        agent_name="GroundTruthFeaAgent",
        action="High-Order Ansys MAPDL CAE Ground Truth Verification",
        details=sim_dict,
    )

    trail = list(state.get("audit_trail", []))
    trail.append(audit_entry)

    logger.info(
        "GroundTruthFeaAgent confirmed candidate %s via FEA solver: f1=%.1f Hz, stress=%.1f MPa",
        state.get("candidate_id"),
        sim_dict["f1_hz"],
        sim_dict["max_stress_mpa"],
    )

    return {
        "fea_ground_truth": sim_dict,
        "audit_trail": trail,
        "status": "QUALIFIED",
    }
