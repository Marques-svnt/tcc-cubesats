"""Orchestration proxy module for backward compatibility with AGENTS.md governance.

Re-exports LangGraph deterministic state machine and contracts from src.agents.
"""

from src.agents.specialists import (
    cad_dfam_agent,
    gevs_qualifier_agent,
    ground_truth_fea_agent,
    neural_surrogate_agent,
)
from src.agents.state import CubeSatState
from src.agents.state_machine import (
    build_cubesat_graph,
    route_after_dfam,
    route_after_gevs,
    run_cubesat_screening_pipeline,
)

__all__ = [
    "CubeSatState",
    "build_cubesat_graph",
    "run_cubesat_screening_pipeline",
    "route_after_dfam",
    "route_after_gevs",
    "cad_dfam_agent",
    "neural_surrogate_agent",
    "gevs_qualifier_agent",
    "ground_truth_fea_agent",
]
