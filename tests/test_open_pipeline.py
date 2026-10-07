"""Unit tests for the Open Source Qualification Pipeline and FastMCP Tools.

Verifies end-to-end execution of the open-source pipeline, screening rates,
and tool calls registered on the unified FastMCP server.
"""

from pathlib import Path
import pytest

from mcp_servers.cubesat_mcp import (
    calculate_bloch_floquet_dispersion,
    generate_gmsh_tet10_mesh,
    generate_open_cad_step,
    run_code_aster_qualification,
    run_open_source_pipeline,
    simulate_p_pod_ejection_shock_srs,
)
from src.pipeline.open_orchestrator import OpenSourceQualificationPipeline


def test_open_pipeline_single_candidate(tmp_path: Path) -> None:
    """Verifies single candidate evaluation through the open-source pipeline."""
    pipeline = OpenSourceQualificationPipeline(output_dir=tmp_path)

    # Valid candidate evaluation
    res = pipeline.evaluate_candidate(
        candidate_id="Test_Cand_001",
        theta_deg=65.75,
        thickness_t=0.613,
        length_l=6.0,
        height_h=9.0,
        boundary_condition="test_pod_flexible",
    )

    assert res.candidate_id == "Test_Cand_001"
    assert res.is_dfam_valid is True
    assert res.has_phononic_bandgap is True
    assert res.first_natural_freq_hz >= 100.0
    assert res.margin_of_safety_yield > 0.0
    assert res.fatigue_damage_steinberg <= 0.25
    assert res.is_gevs_qualified is True
    assert res.is_fully_qualified is True
    assert len(res.audit_notes) >= 3


def test_open_pipeline_batch_run(tmp_path: Path) -> None:
    """Verifies batch LHS execution and JSON report output."""
    pipeline = OpenSourceQualificationPipeline(output_dir=tmp_path)
    results = pipeline.run_pipeline(num_samples=5, boundary_condition="test_pod_flexible")

    assert len(results) == 5
    report_file = tmp_path / "open_pipeline_results.json"
    assert report_file.exists()


def test_mcp_open_tools_execution(tmp_path: Path) -> None:
    """Verifies FastMCP tools execute properly and return expected payloads."""
    # 1. Open CAD tool
    cad_res = generate_open_cad_step(
        theta_deg=65.75,
        thickness_t=0.613,
        export_step_path=str(tmp_path / "mcp_test.step"),
    )
    assert cad_res["status"] == "success"
    assert cad_res["is_dfam_compliant"] is True
    assert Path(cad_res["step_path"]).exists()

    # 2. Gmsh tool
    mesh_res = generate_gmsh_tet10_mesh(
        theta_deg=65.75,
        thickness_t=0.613,
        output_msh_path=str(tmp_path / "mcp_test.msh"),
        mesh_layers=3,
    )
    assert mesh_res["status"] == "success"
    assert mesh_res["mesh_quality"]["num_elements_tet10"] >= 3

    # 3. Code_Aster tool
    aster_res = run_code_aster_qualification(
        theta_deg=65.75,
        thickness_t=0.613,
        boundary_condition="test_pod_flexible",
    )
    assert aster_res["first_natural_freq_hz"] >= 100.0
    assert aster_res["is_gevs_compliant"] is True

    # 4. Bloch-Floquet tool
    bloch_res = calculate_bloch_floquet_dispersion(theta_deg=65.75, thickness_t=0.613)
    assert bloch_res["has_target_bandgap"] is True

    # 5. Separation shock tool
    shock_res = simulate_p_pod_ejection_shock_srs(cubesat_mass_kg=1.330)
    assert shock_res["is_shock_qualified"] is True

    # 6. Pipeline tool
    pipe_res = run_open_source_pipeline(num_samples=3)
    assert pipe_res["status"] == "success"
    assert pipe_res["total_evaluated"] == 3
