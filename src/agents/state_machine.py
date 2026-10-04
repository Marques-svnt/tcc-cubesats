"""LangGraph deterministic state machine for concurrent aerospace engineering.

Coordinates CadDfamAgent -> NeuralSurrogateAgent -> GevsQualifierAgent -> GroundTruthFeaAgent
with strict conditional routing, audit logging, and closed-loop feedback.
"""

import logging
from typing import Any, Dict, Literal

from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from src.agents.specialists import (
    cad_dfam_agent,
    gevs_qualifier_agent,
    ground_truth_fea_agent,
    neural_surrogate_agent,
)
from src.agents.state import CubeSatState

logger = logging.getLogger(__name__)


def route_after_dfam(state: CubeSatState) -> Literal["neural_surrogate", "__end__"]:
    """Conditional router following CAD / DfAM manufacturing screening.

    Args:
        state: Current CubeSatState.

    Returns:
        Next node name: 'neural_surrogate' if valid, or '__end__' if rejected.
    """
    if state.get("dfam_valid", False):
        logger.info("Routing candidate %s to NeuralSurrogateAgent.", state.get("candidate_id"))
        return "neural_surrogate"

    logger.warning(
        "Candidate %s rejected at DfAM gate. Routing to END.", state.get("candidate_id")
    )
    return END


def route_after_gevs(state: CubeSatState) -> Literal["ground_truth_fea", "__end__"]:
    """Conditional router following NASA GEVS qualification check.

    Args:
        state: Current CubeSatState.

    Returns:
        Next node name: 'ground_truth_fea' if compliant, or '__end__' if non-compliant.
    """
    gevs_info = state.get("gevs_qualification", {})
    if gevs_info.get("nasa_gevs_compliant", False):
        logger.info("Routing candidate %s to GroundTruthFeaAgent for CAE confirmation.", state.get("candidate_id"))
        return "ground_truth_fea"

    logger.warning(
        "Candidate %s failed NASA GEVS qualification (MS=%.2f, D=%.5f). Routing to END.",
        state.get("candidate_id"),
        gevs_info.get("ms_yield", -1.0),
        gevs_info.get("fatigue_damage_d", 999.0),
    )
    return END


def build_cubesat_graph() -> CompiledStateGraph:
    """Builds and compiles the deterministic CubeSat multi-agent StateGraph.

    Returns:
        CompiledStateGraph executable instance.
    """
    workflow = StateGraph(CubeSatState)

    # 1. Register specialized agent nodes
    workflow.add_node("cad_dfam", cad_dfam_agent)
    workflow.add_node("neural_surrogate", neural_surrogate_agent)
    workflow.add_node("gevs_qualifier", gevs_qualifier_agent)
    workflow.add_node("ground_truth_fea", ground_truth_fea_agent)

    # 2. Define workflow topology and conditional transitions
    workflow.add_edge(START, "cad_dfam")
    workflow.add_conditional_edges(
        "cad_dfam",
        route_after_dfam,
        {"neural_surrogate": "neural_surrogate", END: END},
    )
    workflow.add_edge("neural_surrogate", "gevs_qualifier")
    workflow.add_conditional_edges(
        "gevs_qualifier",
        route_after_gevs,
        {"ground_truth_fea": "ground_truth_fea", END: END},
    )
    workflow.add_edge("ground_truth_fea", END)

    compiled_graph = workflow.compile()
    logger.info("Successfully compiled LangGraph CubeSat StateMachine.")
    return compiled_graph


def run_cubesat_screening_pipeline(
    t_strut: float,
    l_reentrant: float,
    theta_deg: float,
    h_vertical: float = 12.0,
    candidate_id: str = "candidate_001",
) -> CubeSatState:
    """Convenience entry point executing the full deterministic multi-agent pipeline.

    Args:
        t_strut: Cell strut thickness in mm.
        l_reentrant: Cell re-entrant wall length in mm.
        theta_deg: Cell re-entrant angle in degrees.
        h_vertical: Cell vertical strut height in mm.
        candidate_id: Unique candidate design identifier.

    Returns:
        Final CubeSatState dictionary.
    """
    app = build_cubesat_graph()

    initial_state: CubeSatState = {
        "candidate_id": candidate_id,
        "t_strut": float(t_strut),
        "l_reentrant": float(l_reentrant),
        "theta_deg": float(theta_deg),
        "h_vertical": float(h_vertical),
        "dfam_valid": False,
        "dfam_diagnostics": {},
        "surrogate_predictions": {},
        "gevs_qualification": {},
        "fea_ground_truth": None,
        "audit_trail": [],
        "status": "PENDING",
    }

    final_state: CubeSatState = app.invoke(initial_state)
    return final_state
