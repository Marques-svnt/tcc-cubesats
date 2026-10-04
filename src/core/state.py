"""State management module for CubeSat multi-agent optimization.

Defines Pydantic data schemas representing design parameters,
structural responses, compliance status, and the global graph state.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class GeometryParameters(BaseModel):
    """Geometric parameters defining the 3D re-entrant auxetic lattice unit cell."""

    theta_deg: float = Field(..., ge=45.0, le=85.0, description="Re-entrant angle in degrees")
    strut_thickness_mm: float = Field(..., ge=0.4, le=2.5, description="Strut wall thickness in mm")
    strut_length_l_mm: float = Field(..., ge=3.0, le=12.0, description="Inclined strut length in mm")
    strut_height_h_mm: float = Field(..., ge=5.0, le=20.0, description="Vertical strut height in mm")
    relative_density: float = Field(..., ge=0.05, le=0.50, description="Relative density rho*/rho_s")


class StructuralResponse(BaseModel):
    """Simulated or surrogate-predicted structural and dynamic response."""

    first_natural_freq_hz: float = Field(..., description="First fundamental natural frequency in Hz")
    modal_frequencies_hz: List[float] = Field(default_factory=list, description="First 5 natural frequencies")
    peak_3sigma_stress_mpa: float = Field(..., description="Maximum 3-sigma von Mises stress in MPa")
    payload_grms: float = Field(..., description="Root-mean-square acceleration at payload interface")
    transmissibility_ratio: float = Field(..., description="Ratio of payload Grms to base excitation Grms")
    margin_of_safety_yield: float = Field(..., description="Margin of Safety against yield stress")
    fatigue_damage_steinberg: float = Field(..., description="Cumulative Steinberg fatigue damage D <= 0.25")
    source: str = Field(default="surrogate", description="Source: 'surrogate' or 'high_fidelity_fea'")


class CubeSatDesignState(BaseModel):
    """Global state container for the LangGraph multi-agent decision cycle."""

    iteration_count: int = 0
    current_geometry: Optional[GeometryParameters] = None
    predicted_response: Optional[StructuralResponse] = None
    pareto_candidates: List[Dict[str, Any]] = Field(default_factory=list)
    verified_candidate: Optional[StructuralResponse] = None
    is_gevs_compliant: bool = False
    is_dfam_compliant: bool = False
    messages: List[str] = Field(default_factory=list)
    critic_notes: str = ""
