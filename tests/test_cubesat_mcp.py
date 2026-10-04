"""Unit tests for the CubeSat MCP server and metamaterials analytics.

Tests cover:
- Gibson-Ashby effective properties scaling for AlSi10Mg and PLA.
- Steinberg 3-band Gaussian cumulative fatigue damage calculation.
- Edge cases, parameter boundary conditions, and invalid inputs.
- SolidWorks and Ansys MCP tool executions with simulated and mocked fallbacks.
- FastMCP tool registration and API contracts.
"""

from unittest.mock import MagicMock, patch
import pytest

from mcp_servers.cubesat_mcp import (
    calculate_gibson_ashby_properties,
    calculate_steinberg_random_fatigue,
    mcp,
    rebuild_cad_model,
    run_dynamic_fea_qualification,
)
from src.analysis.auxetic_analytics import (
    calculate_gibson_ashby_properties as calc_ga_props,
    calculate_steinberg_random_fatigue as calc_steinberg_fatigue,
)


# ============================================================================
# Gibson-Ashby Analytics Tests
# ============================================================================


def test_gibson_ashby_alsi10mg_nominal() -> None:
    """Verifies Gibson-Ashby scaling laws for flight alloy AlSi10Mg."""
    relative_density = 0.20
    results = calculate_gibson_ashby_properties(
        relative_density=relative_density,
        material="AlSi10Mg",
        c1=1.0,
        c2=0.3,
    )

    # Es = 68.0 GPa -> E* = 68.0 * 1.0 * (0.20)^2 = 2.72 GPa
    expected_modulus = 68.0 * (0.20**2.0)
    assert results["effective_modulus_gpa"] == pytest.approx(expected_modulus, rel=1e-3)

    # sigma_ys = 230.0 MPa -> sigma_y* = 230.0 * 0.3 * (0.20)^1.5 = 6.1715 MPa
    expected_yield = 230.0 * 0.3 * (0.20**1.5)
    assert results["effective_yield_strength_mpa"] == pytest.approx(expected_yield, rel=1e-3)

    # rho_s = 2680.0 kg/m^3 -> rho* = 2680.0 * 0.20 = 536.0 kg/m^3
    assert results["effective_density_kg_m3"] == pytest.approx(536.0, rel=1e-3)
    assert results["solid_modulus_gpa"] == 68.0
    assert results["solid_yield_strength_mpa"] == 230.0


def test_gibson_ashby_pla_prototyping() -> None:
    """Verifies Gibson-Ashby scaling laws for FDM polymer PLA."""
    relative_density = 0.30
    results = calculate_gibson_ashby_properties(
        relative_density=relative_density,
        material="PLA",
        c1=1.0,
        c2=0.3,
    )

    # Es = 3.5 GPa -> E* = 3.5 * (0.30)^2 = 0.315 GPa
    assert results["effective_modulus_gpa"] == pytest.approx(3.5 * (0.30**2), rel=1e-3)

    # sigma_ys = 50.0 MPa -> sigma_y* = 50.0 * 0.3 * (0.30)^1.5 = 2.4647 MPa
    assert results["effective_yield_strength_mpa"] == pytest.approx(
        50.0 * 0.3 * (0.30**1.5), rel=1e-3
    )
    assert results["effective_density_kg_m3"] == pytest.approx(1250.0 * 0.30, rel=1e-3)


def test_gibson_ashby_invalid_inputs() -> None:
    """Ensures proper exceptions are raised for invalid density or unknown material."""
    with pytest.raises(ValueError, match="physical range"):
        calculate_gibson_ashby_properties(relative_density=-0.1)

    with pytest.raises(ValueError, match="physical range"):
        calculate_gibson_ashby_properties(relative_density=0.0)

    with pytest.raises(ValueError, match="physical range"):
        calculate_gibson_ashby_properties(relative_density=1.5)

    with pytest.raises(ValueError, match="Unknown material"):
        calculate_gibson_ashby_properties(relative_density=0.2, material="TitaniumBeta")


# ============================================================================
# Steinberg 3-Band Random Fatigue Tests
# ============================================================================


def test_steinberg_random_fatigue_nominal() -> None:
    """Verifies cumulative damage computation and cycle distribution."""
    sn_params = {"basquin_m": 6.8, "basquin_c": 1.2e20}
    duration = 120.0
    dominant_freq = 150.0
    stress_3sigma = 120.0

    res = calculate_steinberg_random_fatigue(
        stress_3sigma_mpa=stress_3sigma,
        sn_curve_params=sn_params,
        duration_seconds=duration,
        dominant_freq_hz=dominant_freq,
    )

    # Verify stress decomposition
    assert res["stress_1sigma_mpa"] == pytest.approx(40.0, rel=1e-3)
    assert res["stress_2sigma_mpa"] == pytest.approx(80.0, rel=1e-3)
    assert res["stress_3sigma_mpa"] == pytest.approx(120.0, rel=1e-3)

    # Verify cycle counts according to Gaussian percentages
    assert res["cycles_band_1"] == pytest.approx(0.683 * 150.0 * 120.0, rel=1e-3)
    assert res["cycles_band_2"] == pytest.approx(0.271 * 150.0 * 120.0, rel=1e-3)
    assert res["cycles_band_3"] == pytest.approx(0.0433 * 150.0 * 120.0, rel=1e-3)

    # Verify damage accumulation
    assert res["cumulative_damage"] > 0.0
    assert res["cumulative_damage"] == pytest.approx(
        res["damage_band_1"] + res["damage_band_2"] + res["damage_band_3"], rel=1e-5
    )
    # With stress = 120 MPa, damage is well below 0.25 (NASA compliant)
    assert res["is_compliant_nasa"] == 1.0


def test_steinberg_zero_stress_and_edge_cases() -> None:
    """Checks behavior when stress is zero or inputs are invalid."""
    sn_params = {"m": 6.8, "c": 1.2e20}

    # Zero stress should yield 0 damage
    zero_res = calculate_steinberg_random_fatigue(
        stress_3sigma_mpa=0.0,
        sn_curve_params=sn_params,
    )
    assert zero_res["cumulative_damage"] == 0.0
    assert zero_res["is_compliant_nasa"] == 1.0

    # Negative stress
    with pytest.raises(ValueError, match="non-negative"):
        calculate_steinberg_random_fatigue(
            stress_3sigma_mpa=-10.0,
            sn_curve_params=sn_params,
        )

    # Invalid duration or frequency
    with pytest.raises(ValueError, match="Duration"):
        calculate_steinberg_random_fatigue(
            stress_3sigma_mpa=100.0,
            sn_curve_params=sn_params,
            duration_seconds=0.0,
        )

    with pytest.raises(ValueError, match="frequency"):
        calculate_steinberg_random_fatigue(
            stress_3sigma_mpa=100.0,
            sn_curve_params=sn_params,
            dominant_freq_hz=-5.0,
        )


# ============================================================================
# MCP Server Tools & Fallbacks Tests
# ============================================================================


def test_rebuild_cad_model_simulated_fallback() -> None:
    """Verifies that rebuild_cad_model safely falls back when SolidWorks is absent."""
    with patch("mcp_servers.cubesat_mcp._sw_connector.is_available", return_value=False), \
         patch("mcp_servers.cubesat_mcp._sw_connector.connect", return_value=False):
        res = rebuild_cad_model(
            cell_angle_deg=-20.0,
            strut_thickness_mm=1.2,
            export_step_path="outputs/cad_cell.step",
        )

        assert res["status"] == "success"
        assert res["execution_mode"] == "simulated_cad_fallback"
        assert res["dfam_compliant"] is True
        assert res["solidworks_connected"] is False
        assert res["export_step_path"] == "outputs/cad_cell.step"


def test_rebuild_cad_model_with_live_sw_mock() -> None:
    """Verifies that rebuild_cad_model interacts with live SolidWorks when connected."""
    mock_app = MagicMock()
    with patch("mcp_servers.cubesat_mcp._sw_connector.is_available", return_value=True), \
         patch("mcp_servers.cubesat_mcp._sw_connector.app", mock_app), \
         patch("mcp_servers.cubesat_mcp._sw_connector.export_to_step", return_value=True) as mock_export:
        res = rebuild_cad_model(
            cell_angle_deg=-15.0,
            strut_thickness_mm=1.0,
            export_step_path="outputs/live_cell.step",
        )

        assert res["status"] == "success"
        assert res["execution_mode"] == "live_solidworks_com"
        assert res["solidworks_connected"] is True
        mock_export.assert_called_once_with(
            part_path="models/cubesat_1u_auxetic.SLDPRT",
            output_step_path="outputs/live_cell.step",
        )


def test_rebuild_cad_model_dfam_constraint_violation() -> None:
    """Ensures DfAM violations (e.g. wall thickness < 0.8 mm) are flagged."""
    res = rebuild_cad_model(
        cell_angle_deg=-20.0,
        strut_thickness_mm=0.5,  # Violates t >= 0.8 mm
        export_step_path="outputs/invalid.step",
    )
    assert res["dfam_compliant"] is False


def test_run_dynamic_fea_qualification_nominal() -> None:
    """Verifies Ansys batch dynamic qualification under NASA GEVS."""
    res = run_dynamic_fea_qualification(
        apdl_script_path="scripts/modal_random_gevs.mac",
        damping_ratio=0.02,
    )

    assert res["status"] == "success"
    assert res["first_natural_freq_hz"] >= 100.0
    assert res["peak_3sigma_stress_mpa"] > 0.0
    assert res["margin_of_safety_yield"] > 0.0
    assert res["nasa_gevs_compliant"] is True
    assert res["damping_ratio"] == 0.02


def test_run_dynamic_fea_qualification_non_compliant_mock() -> None:
    """Ensures non-compliant dynamic response (f1 < 100 Hz or MS <= 0) is flagged."""
    mock_modal = {"first_natural_freq_hz": 75.0, "modal_frequencies_hz": [75.0, 110.0]}
    mock_psd = {
        "peak_3sigma_stress_mpa": 210.0,
        "payload_grms": 12.0,
        "transmissibility_ratio": 0.85,
    }

    with patch("mcp_servers.cubesat_mcp._ansys_connector.run_modal_analysis_script", return_value=mock_modal), \
         patch("mcp_servers.cubesat_mcp._ansys_connector.run_random_vibration_psd", return_value=mock_psd):
        res = run_dynamic_fea_qualification(
            apdl_script_path="scripts/suboptimal.mac",
        )

        assert res["first_natural_freq_hz"] == 75.0
        assert res["peak_3sigma_stress_mpa"] == 210.0
        # MS = 184 / 210 - 1 = -0.1238
        assert res["margin_of_safety_yield"] < 0.0
        assert res["nasa_gevs_compliant"] is False


def test_fastmcp_tools_registration() -> None:
    """Verifies that all 4 tools are registered and accessible via FastMCP."""
    if hasattr(mcp, "get_tools"):
        tools = mcp.get_tools()
        expected_tools = {
            "rebuild_cad_model",
            "run_dynamic_fea_qualification",
            "calculate_gibson_ashby_properties",
            "calculate_steinberg_random_fatigue",
        }
        for tool_name in expected_tools:
            assert tool_name in tools, f"Tool '{tool_name}' must be registered in FastMCP."
