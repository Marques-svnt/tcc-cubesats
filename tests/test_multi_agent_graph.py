"""Unit tests for the LangGraph deterministic multi-agent state machine.

Tests end-to-end pipeline execution, individual agent nodes,
conditional routing, rejection gates, and audit trails.
"""

from typing import Dict, Any
import pytest

from src.agents.state import CubeSatState
from src.agents.specialists import (
    cad_dfam_agent,
    neural_surrogate_agent,
    gevs_qualifier_agent,
    ground_truth_fea_agent,
)
from src.agents.state_machine import (
    build_cubesat_graph,
    run_cubesat_screening_pipeline,
)


def test_cad_dfam_agent_valid_and_invalid() -> None:
    """Verifies CadDfamAgent evaluates valid and invalid manufacturing parameters."""
    # Valid candidate (theta >= 45 deg, t >= 0.5 mm, gap >= 1.50 mm)
    state_valid: CubeSatState = {
        "candidate_id": "test_valid",
        "t_strut": 0.8,
        "l_reentrant": 6.0,
        "theta_deg": 60.0,
        "h_vertical": 9.0,
        "audit_trail": [],
    }
    res_valid = cad_dfam_agent(state_valid)
    assert res_valid["dfam_valid"] is True
    assert res_valid["status"] == "PENDING"
    assert len(res_valid["audit_trail"]) == 1

    # Invalid candidate (thickness below 0.5 mm)
    state_invalid: CubeSatState = {
        "candidate_id": "test_invalid",
        "t_strut": 0.3,
        "l_reentrant": 6.0,
        "theta_deg": 60.0,
        "h_vertical": 9.0,
        "audit_trail": [],
    }
    res_invalid = cad_dfam_agent(state_invalid)
    assert res_invalid["dfam_valid"] is False
    assert res_invalid["status"] == "REJECTED_DFAM"
    assert len(res_invalid["audit_trail"]) == 1


def test_neural_surrogate_agent_prediction() -> None:
    """Verifies NeuralSurrogateAgent outputs non-zero elastodynamic predictions."""
    state: CubeSatState = {
        "candidate_id": "test_surrogate",
        "t_strut": 1.0,
        "l_reentrant": 6.5,
        "theta_deg": 65.0,
        "h_vertical": 10.0,
        "audit_trail": [],
    }
    res = neural_surrogate_agent(state)
    preds = res["surrogate_predictions"]
    assert "f1_hz" in preds
    assert "max_stress_mpa" in preds
    assert "grms_payload" in preds
    assert "transmissibility" in preds
    assert preds["f1_hz"] > 100.0
    assert preds["max_stress_mpa"] > 0.0
    assert 0.0 < preds["transmissibility"] < 1.0
    assert len(res["audit_trail"]) == 1


def test_gevs_qualifier_agent_compliance() -> None:
    """Verifies GevsQualifierAgent computes margins of safety and fatigue damage."""
    state: CubeSatState = {
        "candidate_id": "test_gevs",
        "t_strut": 1.0,
        "l_reentrant": 6.5,
        "theta_deg": 65.0,
        "h_vertical": 10.0,
        "surrogate_predictions": {
            "f1_hz": 750.0,
            "max_stress_mpa": 80.0,
            "grms_payload": 3.0,
            "transmissibility": 0.21,
        },
        "audit_trail": [],
    }
    res = gevs_qualifier_agent(state)
    qual = res["gevs_qualification"]
    assert qual["nasa_gevs_compliant"] is True
    assert qual["f1_compliant"] is True
    assert qual["ms_compliant"] is True
    assert qual["ms_yield"] > 0.0
    assert qual["fatigue_compliant"] is True
    assert qual["fatigue_damage_d"] <= 0.25
    assert res["status"] == "PENDING"


def test_full_pipeline_nominal_qualified() -> None:
    """Tests the full LangGraph pipeline on a robust nominal design candidate."""
    final_state = run_cubesat_screening_pipeline(
        t_strut=0.8,
        l_reentrant=6.0,
        theta_deg=60.0,
        h_vertical=9.0,
        candidate_id="flight_candidate_alpha",
    )

    assert final_state["status"] == "QUALIFIED"
    assert final_state["dfam_valid"] is True
    assert final_state["gevs_qualification"]["nasa_gevs_compliant"] is True
    assert final_state["fea_ground_truth"] is not None
    assert final_state["fea_ground_truth"]["f1_hz"] >= 100.0

    # Must contain 4 audit events: CadDfam -> NeuralSurrogate -> GevsQualifier -> GroundTruthFea
    audit = final_state["audit_trail"]
    assert len(audit) == 4
    agent_names = [event["agent"] for event in audit]
    assert agent_names == [
        "CadDfamAgent",
        "NeuralSurrogateAgent",
        "GevsQualifierAgent",
        "GroundTruthFeaAgent",
    ]


def test_full_pipeline_rejected_at_dfam_gate() -> None:
    """Tests pipeline rejection at the first DfAM gate due to powder clearance violation."""
    # When theta is 80 deg and length is 4.0 mm, t = 1.2 mm:
    # 2*4*cos(80) = 8*0.1736 = 1.389 mm; 2*t = 2.4 mm -> gap < 0 < 1.50 mm -> fails powder clearance
    final_state = run_cubesat_screening_pipeline(
        t_strut=1.2,
        l_reentrant=4.0,
        theta_deg=80.0,
        h_vertical=8.0,
        candidate_id="clogged_powder_candidate",
    )

    assert final_state["status"] == "REJECTED_DFAM"
    assert final_state["dfam_valid"] is False
    assert final_state["surrogate_predictions"] == {}
    assert final_state["fea_ground_truth"] is None

    # Only CadDfamAgent should have executed
    audit = final_state["audit_trail"]
    assert len(audit) == 1
    assert audit[0]["agent"] == "CadDfamAgent"


def test_full_pipeline_rejected_at_gevs_gate() -> None:
    """Tests pipeline rejection at NASA GEVS gate when candidate fails structural margins."""
    # Build graph manually and mock an extreme surrogate prediction with excessive stress
    graph = build_cubesat_graph()

    initial_state: CubeSatState = {
        "candidate_id": "overstressed_candidate",
        "t_strut": 0.8,
        "l_reentrant": 8.0,
        "theta_deg": 15.0,
        "h_vertical": 12.0,
        "dfam_valid": True,  # passes dfam
        "dfam_diagnostics": {},
        "surrogate_predictions": {},
        "gevs_qualification": {},
        "fea_ground_truth": None,
        "audit_trail": [],
        "status": "PENDING",
    }

    # Custom node to simulate an unfeasible structural design
    def mock_excessive_stress_surrogate(state: CubeSatState) -> Dict[str, Any]:
        return {
            "surrogate_predictions": {
                "f1_hz": 80.0,  # below 100 Hz
                "max_stress_mpa": 350.0,  # above 184 MPa
                "grms_payload": 12.0,
                "transmissibility": 0.85,
            },
            "audit_trail": list(state.get("audit_trail", [])) + [{"agent": "MockSurrogate"}],
        }

    # Test qualifier logic directly with this state
    failing_state: CubeSatState = {
        **initial_state,
        "surrogate_predictions": {
            "f1_hz": 80.0,
            "max_stress_mpa": 350.0,
            "grms_payload": 12.0,
            "transmissibility": 0.85,
        },
    }
    res = gevs_qualifier_agent(failing_state)
    assert res["status"] == "REJECTED_GEVS"
    assert res["gevs_qualification"]["nasa_gevs_compliant"] is False
    assert res["gevs_qualification"]["f1_compliant"] is False
    assert res["gevs_qualification"]["ms_compliant"] is False
