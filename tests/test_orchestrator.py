"""Unit tests for the autonomous Skill Orchestrator."""

import pytest

from src.agents.orchestrator import (
    AntigravitySkill,
    CandidateDesign,
    CubeSatOrchestrator,
    MissionPhase,
    SkillDecisionEngine,
)


def test_skill_decision_engine_mapping() -> None:
    """Verifies that each mission phase maps to the appropriate Antigravity engineering skill."""
    assert SkillDecisionEngine.resolve_skill(MissionPhase.EXPLORATION) == AntigravitySkill.OPERATIONS_RESEARCH
    assert SkillDecisionEngine.resolve_skill(MissionPhase.MANUFACTURABILITY_GATE) == AntigravitySkill.AEROSPACE_STRUCTURES_DFAM
    assert SkillDecisionEngine.resolve_skill(MissionPhase.PHYSICS_EVALUATION) == AntigravitySkill.AEROSPACE_STRUCTURES_DFAM
    assert SkillDecisionEngine.resolve_skill(MissionPhase.GEVS_QUALIFICATION) == AntigravitySkill.AEROSPACE_STRUCTURES_DFAM
    assert SkillDecisionEngine.resolve_skill(MissionPhase.SYNTHESIS_AND_REPORTING) == AntigravitySkill.ACADEMIC_PAPER_LATEX


def test_orchestrator_sample_design_space() -> None:
    """Verifies sampling of the design space through DoE and audit trail recording."""
    orchestrator = CubeSatOrchestrator()
    candidates = orchestrator.sample_design_space(num_samples=10, random_seed=42)

    assert len(candidates) == 10
    assert len(orchestrator.execution_audit_trail) == 1
    record = orchestrator.execution_audit_trail[0]
    assert record.phase == MissionPhase.EXPLORATION
    assert record.skill_evoked == AntigravitySkill.OPERATIONS_RESEARCH
    assert record.telemetry["num_samples"] == 10


def test_orchestrator_evaluate_dfam_compliance() -> None:
    """Verifies DfAM rule screening for both compliant and non-compliant geometries."""
    orchestrator = CubeSatOrchestrator()

    # Valid candidate (overhang angle >= 45.0 deg, thickness >= 0.8 mm)
    valid_c = CandidateDesign(
        theta_deg=65.0,
        thickness_t=1.0,
        length_l=6.0,
        height_h=9.0,
        relative_density=0.20,
    )
    evaluated_valid = orchestrator.evaluate_dfam(valid_c)
    assert evaluated_valid.is_dfam_compliant is True

    # Invalid candidate (thickness < 0.5 mm)
    invalid_c = CandidateDesign(
        theta_deg=65.0,
        thickness_t=0.3,
        length_l=6.0,
        height_h=9.0,
        relative_density=0.20,
    )
    evaluated_invalid = orchestrator.evaluate_dfam(invalid_c)
    assert evaluated_invalid.is_dfam_compliant is False
    assert "thickness" in str(evaluated_invalid.dfam_reason).lower()


def test_orchestrator_physics_and_qualification() -> None:
    """Verifies evaluation of cellular mechanics and NASA GEVS qualification."""
    orchestrator = CubeSatOrchestrator(f1_min_threshold_hz=100.0, fatigue_max_damage=0.25)

    candidate = CandidateDesign(
        theta_deg=65.0,
        thickness_t=1.2,
        length_l=6.0,
        height_h=9.0,
        relative_density=0.22,
    )

    # 1. Evaluate mechanics
    candidate = orchestrator.compute_mechanics_and_dynamics(candidate, material="AlSi10Mg")
    assert candidate.effective_modulus_gpa is not None
    assert candidate.effective_modulus_gpa > 0.0
    assert candidate.poisson_ratio is not None
    assert candidate.poisson_ratio < 0.0  # Must be auxetic (negative)
    assert candidate.f1_natural_hz is not None
    assert candidate.peak_3sigma_stress_mpa is not None

    # 2. Qualify against GEVS criteria
    candidate = orchestrator.qualify_candidate_gevs(candidate, material="AlSi10Mg")
    assert candidate.fatigue_damage_steinberg is not None
    assert candidate.margin_of_safety is not None
    assert isinstance(candidate.is_qualified, bool)


def test_orchestrator_execute_autonomous_screening() -> None:
    """Verifies end-to-end execution of the autonomous screening workflow."""
    orchestrator = CubeSatOrchestrator()
    qualified, rejected = orchestrator.execute_autonomous_screening(num_samples=25, random_seed=42)

    total_screened = len(qualified) + len(rejected)
    assert total_screened == 25
    assert len(orchestrator.execution_audit_trail) > 25

    # Check that qualified candidates satisfy all NASA quality gates
    for q in qualified:
        assert q.is_dfam_compliant is True
        assert q.f1_natural_hz is not None and q.f1_natural_hz >= 100.0
        assert q.margin_of_safety is not None and q.margin_of_safety > 0.0
        assert q.fatigue_damage_steinberg is not None and q.fatigue_damage_steinberg <= 0.25


def test_orchestrator_latex_synthesis_table() -> None:
    """Verifies generation of publication-grade LaTeX synthesis table conforming to academic standards."""
    orchestrator = CubeSatOrchestrator()
    qualified, _ = orchestrator.execute_autonomous_screening(num_samples=20, random_seed=42)

    latex_table = orchestrator.generate_latex_synthesis_table(qualified, top_n=3)

    assert r"\begin{table}" in latex_table
    assert r"\toprule" in latex_table
    assert r"\midrule" in latex_table
    assert r"\bottomrule" in latex_table
    assert r"\end{table}" in latex_table
    assert r"S[table-format=" in latex_table
    # Check that vertical lines are avoided as per academic-paper-latex skill
    assert "|" not in latex_table
