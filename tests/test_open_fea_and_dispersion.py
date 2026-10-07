"""Unit tests for Open FEA Solvers (Code_Aster / CalculiX) and Bloch-Floquet Dispersion.

Verifies command deck generation, eigenvalue extraction, stochastic 3-sigma
stress under NASA GEVS, and phononic bandgap detection across Brillouin zone.
"""

from pathlib import Path
import pytest

from src.analysis.bloch_floquet import BlochFloquetAnalyzer
from src.analysis.calculix_runner import CalculixRunner
from src.analysis.code_aster_runner import CodeAsterRunner
from src.analysis.open_fea_kernel import OpenElastodynamicsKernel


def test_code_aster_comm_deck_generation(tmp_path: Path) -> None:
    """Verifies generation of authentic Code_Aster .comm file."""
    runner = CodeAsterRunner(output_dir=tmp_path)
    comm_path = tmp_path / "cubesat_test.comm"

    out_file = runner.generate_comm_deck(
        mesh_msh_path="data/meshes/test.msh",
        output_comm_path=comm_path,
        num_modes=10,
        boundary_condition="test_pod_flexible",
    )
    assert out_file.exists()
    content = out_file.read_text(encoding="utf-8")
    assert "CALC_MODES" in content
    assert "DYNA_ALEA_MODAL" in content
    assert "ALSI10MG" in content
    assert "LIRE_MAILLAGE" in content


def test_calculix_inp_deck_generation(tmp_path: Path) -> None:
    """Verifies generation of CalculiX .inp file."""
    runner = CalculixRunner(output_dir=tmp_path)
    inp_path = tmp_path / "cubesat_test.inp"

    out_file = runner.generate_inp_deck(
        mesh_msh_path="data/meshes/test.msh",
        output_inp_path=inp_path,
        num_modes=10,
        boundary_condition="clamped",
    )
    assert out_file.exists()
    content = out_file.read_text(encoding="utf-8")
    assert "*FREQUENCY" in content
    assert "C3D10" in content
    assert "ALSI10MG" in content


def test_open_fea_kernel_evaluations() -> None:
    """Verifies modal frequencies and GEVS margins for both boundary conditions."""
    kernel = OpenElastodynamicsKernel()

    # 1. Clamped boundary mode (upper bound benchmark)
    res_clamped = kernel.evaluate_candidate(
        theta_deg=65.75,
        thickness_t=0.613,
        boundary_condition="clamped",
        mesh_layers=3,
    )
    assert res_clamped.first_natural_freq_hz > 500.0
    assert len(res_clamped.modal_frequencies_hz) == 10
    assert res_clamped.margin_of_safety_yield > 0.0
    assert res_clamped.fatigue_damage_steinberg < 0.25
    assert res_clamped.is_gevs_compliant is True

    # 2. Flight Test POD flexible mounting mode
    res_flexible = kernel.evaluate_candidate(
        theta_deg=65.75,
        thickness_t=0.613,
        boundary_condition="test_pod_flexible",
        mesh_layers=3,
    )
    assert 250.0 <= res_flexible.first_natural_freq_hz <= 400.0
    assert res_flexible.is_gevs_compliant is True


def test_bloch_floquet_dispersion_and_bandgaps() -> None:
    """Verifies Bloch-Floquet dispersion computation and acoustic bandgap detection."""
    analyzer = BlochFloquetAnalyzer()

    disp_res = analyzer.compute_dispersion_relation(
        theta_deg=65.75,
        thickness_t=0.613,
        length_l=6.0,
        height_h=9.0,
        num_k_samples=30,
        num_modes=6,
    )

    assert len(disp_res.dispersion_bands_hz) == 6
    assert len(disp_res.wave_vectors_k) > 20
    assert disp_res.relative_density > 0.0
    assert disp_res.effective_poisson_ratio < 0.0  # Auxetic Poisson ratio
    assert len(disp_res.bandgaps) >= 1
    assert disp_res.has_target_bandgap is True
