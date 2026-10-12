"""Unit tests for Build123dEngine, TpmsLatticeGenerator, and NASA GEVS qualification utilities."""

import pytest
import numpy as np
from pathlib import Path

from src.cad.build123d_engine import Build123dEngine
from src.dfam.tpms_lattice import TpmsLatticeGenerator
from src.analysis.nasa_gevs_utils import (
    compute_gevs_margin_of_safety,
    compute_steinberg_fatigue_damage,
    verify_fundamental_frequency,
)


def test_build123d_engine_chassis_generation(tmp_path: Path) -> None:
    """Verifies that Build123dEngine generates valid solid and exports STEP file."""
    engine = Build123dEngine(min_wall_thickness_mm=0.40)
    chassis = engine.generate_cubesat_chassis(
        length_mm=50.0,
        width_mm=50.0,
        height_mm=60.0,
        wall_thickness_mm=1.0,
    )
    assert chassis is not None
    assert chassis.is_valid

    step_file = tmp_path / "test_chassis.step"
    result_path = engine.export_step(chassis, step_file)
    assert result_path.exists()
    assert result_path.stat().st_size > 0


def test_build123d_engine_invalid_wall_thickness() -> None:
    """Ensures DfAM validation raises ValueError when wall thickness violates threshold."""
    engine = Build123dEngine(min_wall_thickness_mm=0.50)
    with pytest.raises(ValueError, match="below DfAM limit"):
        engine.generate_cubesat_chassis(wall_thickness_mm=0.30)


def test_tpms_lattice_generator_evaluations() -> None:
    """Verifies field evaluation and relative density estimation for Gyroid, Schwarz P, Diamond."""
    generator = TpmsLatticeGenerator(unit_cell_size_mm=10.0)

    x = np.array([0.0, 2.5, 5.0])
    y = np.array([0.0, 2.5, 5.0])
    z = np.array([0.0, 2.5, 5.0])

    for l_type in ["gyroid", "schwarz_p", "diamond"]:
        field = generator.evaluate_field(x, y, z, lattice_type=l_type)
        assert field.shape == (3,)
        assert np.all(np.isfinite(field))

    # Test density estimation
    rho = generator.estimate_relative_density("gyroid", isovalue_c=0.0, grid_resolution=15)
    assert 0.40 <= rho <= 0.60  # Symmetric Gyroid isovalue=0 is close to 50% relative density


def test_nasa_gevs_margin_of_safety() -> None:
    """Validates structural Margin of Safety calculations against canonical cases."""
    # Allowable for AlSi10Mg = 230 / 1.25 = 184 MPa
    # If 3-sigma stress is 166.91 MPa -> MS = (184 / 166.91) - 1.0 = +0.10239
    ms = compute_gevs_margin_of_safety(
        sigma_3sigma_mpa=166.91,
        yield_strength_mpa=230.0,
        factor_of_safety=1.25,
    )
    assert ms == pytest.approx(0.10239, rel=1e-3)
    assert ms > 0.0

    # Negative margin test
    ms_fail = compute_gevs_margin_of_safety(
        sigma_3sigma_mpa=200.0,
        yield_strength_mpa=230.0,
        factor_of_safety=1.25,
    )
    assert ms_fail < 0.0


def test_steinberg_fatigue_and_frequency() -> None:
    """Tests Steinberg 3-band cumulative damage and launch frequency verification."""
    fatigue = compute_steinberg_fatigue_damage(f_natural_hz=579.62, t_seconds=120.0)
    assert fatigue["is_compliant"] is True
    assert 0.0 < fatigue["d_total"] < 1.0

    compliant, margin = verify_fundamental_frequency(f1_hz=579.62, min_required_hz=500.0)
    assert compliant is True
    assert margin == pytest.approx(79.62, rel=1e-3)

    fail_comp, fail_margin = verify_fundamental_frequency(f1_hz=420.0, min_required_hz=500.0)
    assert fail_comp is False
    assert fail_margin < 0.0


def test_build123d_canonical_1u_flight_chassis(tmp_path: Path) -> None:
    """Verifies generation of canonical 1U chassis with deployer rails, mass properties, and exports."""
    engine = Build123dEngine(min_wall_thickness_mm=0.40)
    chassis = engine.generate_1u_flight_chassis(
        length_mm=100.0,
        width_mm=100.0,
        height_mm=113.5,
        rail_width_mm=8.5,
        wall_thickness_mm=1.20,
        window_margin_mm=10.0,
        drain_hole_dia_mm=3.5,
    )
    assert chassis is not None
    assert chassis.is_valid

    # Check mass properties
    report = engine.compute_mass_properties(chassis)
    assert 40000.0 < report.volume_mm3 < 200000.0
    assert 0.10 < report.mass_kg < 0.45  # Standard 1U metallic frame is ~150g to 400g
    assert report.relative_density < 0.35
    assert len(report.center_of_mass_mm) == 3

    # Check STEP and STL export
    step_path = tmp_path / "flight_1u.step"
    stl_path = tmp_path / "flight_1u.stl"
    engine.export_step(chassis, step_path)
    engine.export_stl(chassis, stl_path)

    assert step_path.exists() and step_path.stat().st_size > 1000
    assert stl_path.exists() and stl_path.stat().st_size > 1000

    step_txt = step_path.read_text(encoding="utf-8", errors="ignore")
    assert "ISO-10303-21" in step_txt


def test_gmsh_mesh_step_model_execution(tmp_path: Path) -> None:
    """Verifies that GmshMeshGenerator discretizes a STEP file into quadratic Tet10 elements."""
    from src.mesh.gmsh_engine import GmshMeshGenerator

    engine = Build123dEngine(min_wall_thickness_mm=0.40)
    chassis = engine.generate_cubesat_chassis(
        length_mm=40.0,
        width_mm=40.0,
        height_mm=45.0,
        wall_thickness_mm=1.5,
    )
    step_file = tmp_path / "small_chassis.step"
    engine.export_step(chassis, step_file)

    mesh_gen = GmshMeshGenerator(output_dir=tmp_path)
    msh_file, report = mesh_gen.mesh_step_model(
        step_path=step_file,
        output_msh_path=tmp_path / "small_chassis.msh",
        mesh_order=2,
        cl_scale=2.0,
    )

    assert msh_file.exists()
    assert report.num_nodes > 10
    assert report.num_elements_tet10 > 0
    msh_content = msh_file.read_text(encoding="utf-8", errors="ignore")
    assert "$MeshFormat" in msh_content
    assert "$Nodes" in msh_content
    assert "$Elements" in msh_content


def test_tpms_effective_properties_and_fgl() -> None:
    """Verifies Gibson-Ashby effective properties and functionally graded lattice fields."""
    generator = TpmsLatticeGenerator(unit_cell_size_mm=10.0)

    for l_type in ["gyroid", "schwarz_p", "diamond"]:
        props = generator.compute_effective_mechanical_properties(
            lattice_type=l_type,
            relative_density=0.25,
            solid_modulus_gpa=68.0,
            solid_yield_mpa=230.0,
        )
        assert 0.0 < props["e_eff_gpa"] < 68.0
        assert 0.0 < props["sigma_y_eff_mpa"] < 230.0
        assert 0.0 < props["nu_eff"] < 0.33
        assert props["relative_density"] == 0.25

    # Check FGL field
    x = np.linspace(0, 10, 5)
    y = np.linspace(0, 10, 5)
    z = np.linspace(0, 113.5, 5)
    fgl = generator.generate_functionally_graded_field(
        x=x,
        y=y,
        z=z,
        z_min=0.0,
        z_max=113.5,
        lattice_type="gyroid",
        isovalue_base=0.0,
        isovalue_top=0.6,
    )
    assert fgl.shape == (5,)
    assert np.all(np.isfinite(fgl))


def test_nasa_gevs_spectral_psd_and_miles() -> None:
    """Verifies continuous NASA GEVS PSD evaluation and Miles equation acceleration."""
    from src.analysis.nasa_gevs_utils import evaluate_nasa_gevs_psd, compute_miles_acceleration_grms

    # Points on the NASA GEVS curve
    psd_20 = evaluate_nasa_gevs_psd(20.0)
    assert psd_20 == pytest.approx(0.013, rel=1e-2)

    psd_100 = evaluate_nasa_gevs_psd(100.0)
    assert psd_100 == pytest.approx(0.080, rel=1e-2)

    psd_800 = evaluate_nasa_gevs_psd(800.0)
    assert psd_800 == pytest.approx(0.080, rel=1e-2)

    psd_2000 = evaluate_nasa_gevs_psd(2000.0)
    # 0.080 * (2000 / 800) ^ -2 = 0.080 * 0.0625 = 0.0050 ~ 0.0053
    assert 0.0045 <= psd_2000 <= 0.0060

    # Outside bounds
    assert evaluate_nasa_gevs_psd(10.0) == 0.0
    assert evaluate_nasa_gevs_psd(2500.0) == 0.0

    # Miles equation
    grms_500 = compute_miles_acceleration_grms(f_natural_hz=500.0, q_factor=25.0)
    assert grms_500 > 10.0  # Significant dynamic amplification in the plateau band


def test_pynastran_bdf_export(tmp_path: Path) -> None:
    """Verifies generation of authentic NASA Nastran BDF bulk data deck."""
    from src.analysis.nasa_gevs_utils import export_canonical_nastran_bdf

    bdf_file = tmp_path / "nasa_cubesat.bdf"
    result = export_canonical_nastran_bdf(bdf_file)
    assert result.exists()
    assert result.stat().st_size > 200

    content = result.read_text(encoding="utf-8", errors="ignore")
    assert "GRID" in content
    assert "CTETRA" in content
    assert "MAT1" in content
    assert "PSOLID" in content
    assert "SPC1" in content

