"""Strongly-typed global state definition for the LangGraph multi-agent orchestration.

Governs data contracts between CadDfamAgent, NeuralSurrogateAgent,
GevsQualifierAgent, and GroundTruthFeaAgent.
"""

from typing import Any, Dict, List, Optional, TypedDict


class CubeSatState(TypedDict, total=False):
    """Global immutable state schema passed through the LangGraph StateMachine.

    Attributes:
        candidate_id: Unique string identifier for the design candidate.
        t_strut: Cell strut thickness in mm.
        l_reentrant: Cell re-entrant wall length in mm.
        theta_deg: Cell re-entrant angle in degrees.
        h_vertical: Cell vertical strut height in mm.
        dfam_valid: Boolean indicating whether L-PBF manufacturing constraints are met.
        dfam_diagnostics: Diagnostic details (overhang angle, min thickness, powder clearance).
        surrogate_predictions: Physics-Guided ResNet outputs (f1_hz, max_stress_mpa, grms_payload, transmissibility).
        gevs_qualification: Spaceflight qualification status under NASA GSFC-STD-7000A.
        fea_ground_truth: Full high-order FEA verification results from Ansys MAPDL runner.
        audit_trail: Traceable history of agent actions, decisions, and timestamps.
        status: Execution state ('PENDING', 'REJECTED_DFAM', 'REJECTED_GEVS', 'QUALIFIED').
    """

    candidate_id: str
    t_strut: float
    l_reentrant: float
    theta_deg: float
    h_vertical: float
    dfam_valid: bool
    dfam_diagnostics: Dict[str, Any]
    surrogate_predictions: Dict[str, float]
    gevs_qualification: Dict[str, Any]
    fea_ground_truth: Optional[Dict[str, Any]]
    audit_trail: List[Dict[str, Any]]
    status: str
