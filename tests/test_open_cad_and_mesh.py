"""Unit tests for Open Source CAD (CadQuery/B-Rep) and Meshing (Gmsh Tet10).

Verifies DfAM LPBF validation, STEP AP214 / STL export, Gmsh .geo generation,
and quadratic Tet10 mesh convergence criteria (>= 3 elements across thickness).
"""

from pathlib import Path
import pytest

from src.cad.cadquery_engine import OpenCadEngine
from src.mesh.gmsh_engine import GmshMeshGenerator


def test_open_cad_dfam_validation() -> None:
    """Verifies DfAM validation identifies compliant and non-compliant designs."""
    cad_engine = OpenCadEngine(output_dir="data/test_cad")

    # Valid flight design (theta=65.75 deg, t=0.613 mm, l=6.0 mm, h=9.0 mm)
    rep_valid = cad_engine.validate_lpbf_dfam(
        theta_deg=65.75,
        thickness_t=0.613,
        length_l=6.0,
        height_h=9.0,
    )
    assert rep_valid.is_compliant is True
    assert rep_valid.overhang_angle_deg >= 35.0
    assert rep_valid.min_thickness_mm >= 0.50
    assert rep_valid.relative_density > 0.05
    assert rep_valid.estimated_mass_kg > 0.05

    # Non-compliant design (thickness below 0.50 mm)
    rep_thin = cad_engine.validate_lpbf_dfam(
        theta_deg=65.75,
        thickness_t=0.35,
        length_l=6.0,
        height_h=9.0,
    )
    assert rep_thin.is_compliant is False
    assert any("thickness" in r.lower() for r in rep_thin.failure_reasons)

    # Non-compliant design (overhang angle < 35 deg)
    rep_steep = cad_engine.validate_lpbf_dfam(
        theta_deg=25.0,
        thickness_t=0.80,
        length_l=6.0,
        height_h=9.0,
    )
    assert rep_steep.is_compliant is False
    assert any("overhang" in r.lower() for r in rep_steep.failure_reasons)


def test_open_cad_step_and_stl_export(tmp_path: Path) -> None:
    """Verifies generation of neutral STEP AP214 and STL geometries."""
    cad_engine = OpenCadEngine(output_dir=tmp_path)

    step_file = cad_engine.export_step_model(
        theta_deg=65.75,
        thickness_t=0.613,
        length_l=6.0,
        height_h=9.0,
        output_step_path=tmp_path / "test_model.step",
    )
    assert step_file.exists()
    assert step_file.stat().st_size > 500
    content = step_file.read_text(encoding="utf-8")
    assert "ISO-10303-21" in content
    assert "AUTOMOTIVE_DESIGN" in content

    stl_file = cad_engine.export_stl_mesh(
        theta_deg=65.75,
        thickness_t=0.613,
        length_l=6.0,
        height_h=9.0,
        output_stl_path=tmp_path / "test_model.stl",
    )
    assert stl_file.exists()
    assert "endsolid" in stl_file.read_text(encoding="utf-8")


def test_gmsh_script_and_mesh_generation(tmp_path: Path) -> None:
    """Verifies generation of Gmsh .geo and quadratic Tet10 .msh files."""
    mesh_gen = GmshMeshGenerator(output_dir=tmp_path)

    # 1. Test .geo script generation
    geo_file = mesh_gen.generate_geo_script(
        theta_deg=65.75,
        thickness_t=0.613,
        length_l=6.0,
        height_h=9.0,
        output_geo_path=tmp_path / "test_mesh.geo",
        mesh_layers=3,
        notch_radius=0.50,
    )
    assert geo_file.exists()
    geo_txt = geo_file.read_text(encoding="utf-8")
    assert "Mesh.ElementOrder = 2" in geo_txt
    assert "Rails_Contact_Surfaces" in geo_txt
    assert "Bottom_Base_Z0" in geo_txt

    # 2. Test .msh generation with quadratic elements
    msh_file, report = mesh_gen.generate_msh_file(
        theta_deg=65.75,
        thickness_t=0.613,
        length_l=6.0,
        height_h=9.0,
        output_msh_path=tmp_path / "test_mesh.msh",
        mesh_layers=3,
    )
    assert msh_file.exists()
    assert report.num_nodes > 20
    assert report.num_elements_tet10 >= 3
    assert report.elements_across_thickness >= 3
    assert report.is_converged is True

    msh_txt = msh_file.read_text(encoding="utf-8")
    assert "$MeshFormat" in msh_txt
    assert "2.2 0 8" in msh_txt
    assert "$Elements" in msh_txt
