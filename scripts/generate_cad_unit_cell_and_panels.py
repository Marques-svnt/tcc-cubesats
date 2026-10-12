"""Generates high-fidelity 3D CAD B-Rep solid STEP and STL models for auxetic unit cells and lattice panels.

Powered by build123d and OpenCASCADE kernel. Produces exact solids compliant with
ISO-10303-21 STEP AP214 and triangulated stereolithography (STL) for FreeCAD,
SolidWorks, and FEA meshing pipelines.
"""

from __future__ import annotations

import logging
import math
from pathlib import Path

from build123d import (
    Box,
    Compound,
    Cylinder,
    Pos,
    Rotation,
    export_step,
    export_stl,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("generate_cad_unit_cell_and_panels")


def create_auxetic_unit_cell_solid(
    height_h: float = 9.0,
    length_l: float = 6.0,
    theta_horizontal_deg: float = 21.40,
    strut_thickness_t: float = 0.613,
    extrusion_depth: float = 8.0,
) -> Compound:
    """Generates an exact 3D B-Rep solid of the re-entrant auxetic unit cell (flight design #28).

    Args:
        height_h: Vertical strut height in mm.
        length_l: Inclined re-entrant strut length in mm.
        theta_horizontal_deg: Angle of inclined strut relative to horizontal in degrees.
        strut_thickness_t: Wall thickness of the ribs in mm.
        extrusion_depth: Extrusion thickness along Z axis in mm.

    Returns:
        Fused Compound representing the solid auxetic unit cell.
    """
    theta_rad = math.radians(theta_horizontal_deg)
    dx = length_l * math.cos(theta_rad)
    dy = length_l * math.sin(theta_rad)

    x_outer = dx + 1.20
    x_inner = x_outer - dx
    y_mid = dy

    nodes = {
        "L_top": (-x_outer, y_mid + height_h / 2.0),
        "L_mid_top": (-x_outer, y_mid),
        "L_waist": (-x_inner, 0.0),
        "L_mid_bot": (-x_outer, -y_mid),
        "L_bot": (-x_outer, -y_mid - height_h / 2.0),
        "R_top": (x_outer, y_mid + height_h / 2.0),
        "R_mid_top": (x_outer, y_mid),
        "R_waist": (x_inner, 0.0),
        "R_mid_bot": (x_outer, -y_mid),
        "R_bot": (x_outer, -y_mid - height_h / 2.0),
    }

    struts_topology = [
        (nodes["L_top"], nodes["L_mid_top"]),
        (nodes["L_mid_top"], nodes["L_waist"]),
        (nodes["L_waist"], nodes["L_mid_bot"]),
        (nodes["L_mid_bot"], nodes["L_bot"]),
        (nodes["R_top"], nodes["R_mid_top"]),
        (nodes["R_mid_top"], nodes["R_waist"]),
        (nodes["R_waist"], nodes["R_mid_bot"]),
        (nodes["R_mid_bot"], nodes["R_bot"]),
    ]

    def build_strut(p1: tuple[float, float], p2: tuple[float, float]) -> Box:
        dist = math.hypot(p2[0] - p1[0], p2[1] - p1[1]) + strut_thickness_t * 0.95
        ang = math.degrees(math.atan2(p2[1] - p1[1], p2[0] - p1[0]))
        mid_x = (p1[0] + p2[0]) / 2.0
        mid_y = (p1[1] + p2[1]) / 2.0
        return Pos(mid_x, mid_y, 0) * Rotation(0, 0, ang) * Box(dist, strut_thickness_t, extrusion_depth)

    solids = [build_strut(p1, p2) for p1, p2 in struts_topology]
    for pt in nodes.values():
        solids.append(Pos(pt[0], pt[1], 0) * Cylinder(radius=strut_thickness_t * 0.75, height=extrusion_depth))

    cell = solids[0]
    for s in solids[1:]:
        cell = cell + s

    logger.info(
        "Constructed unit cell B-Rep solid: volume=%.2f mm^3, bbox=%s",
        cell.volume,
        cell.bounding_box(),
    )
    return cell


def main() -> None:
    """Exports candidate #28 unit cell and 2x2 lattice panels to STEP and STL."""
    output_dir = Path(__file__).resolve().parent.parent / "models" / "cad"
    output_dir.mkdir(parents=True, exist_ok=True)

    # 1. Single Re-entrant Unit Cell
    cell = create_auxetic_unit_cell_solid()
    step_cell = output_dir / "cubesat_auxetic_unit_cell_flight28.step"
    stl_cell = output_dir / "cubesat_auxetic_unit_cell_flight28.stl"
    export_step(cell, str(step_cell))
    export_stl(cell, str(stl_cell))
    logger.info("Saved unit cell STEP (%d bytes) and STL (%d bytes)", step_cell.stat().st_size, stl_cell.stat().st_size)

    # 2. 2x2 Tessellated Lattice Metamaterial Panel
    dx = 6.0 * math.cos(math.radians(21.40))
    dy = 6.0 * math.sin(math.radians(21.40))
    spacing_x = 2.0 * (dx + 1.20) - 0.613
    spacing_y = 2.0 * (dy + 4.50) - 0.613

    cells = []
    for ix in range(2):
        for iy in range(2):
            pos_x = (ix - 0.5) * spacing_x
            pos_y = (iy - 0.5) * spacing_y
            cells.append(Pos(pos_x, pos_y, 0) * cell)

    lattice = cells[0]
    for c in cells[1:]:
        lattice = lattice + c

    step_lattice = output_dir / "cubesat_auxetic_lattice_panel_2x2.step"
    stl_lattice = output_dir / "cubesat_auxetic_lattice_panel_2x2.stl"
    export_step(lattice, str(step_lattice))
    export_stl(lattice, str(stl_lattice))
    logger.info("Saved 2x2 lattice STEP (%d bytes) and STL (%d bytes)", step_lattice.stat().st_size, stl_lattice.stat().st_size)

    # 3. Complete 1U Hybrid Flight Chassis (Chassis + 4 Integrated Auxetic Panels)
    from src.cad.build123d_engine import Build123dEngine
    cad_engine = Build123dEngine()
    chassis = cad_engine.generate_1u_flight_chassis()

    panel_cell = create_auxetic_unit_cell_solid(
        height_h=9.0,
        length_l=6.0,
        theta_horizontal_deg=21.40,
        strut_thickness_t=0.613,
        extrusion_depth=1.60,
    )

    nx, ny = 4, 5
    sp_x = 2.0 * (6.0 * math.cos(math.radians(21.40)) + 1.20) - 0.613
    sp_y = 2.0 * (6.0 * math.sin(math.radians(21.40)) + 4.50) - 0.613

    p_cells = []
    for ix in range(nx):
        for iy in range(ny):
            px = (ix - (nx - 1) / 2.0) * sp_x
            py = (iy - (ny - 1) / 2.0) * sp_y
            p_cells.append(Pos(px, py, 0) * panel_cell)

    p_2d = p_cells[0]
    for c in p_cells[1:]:
        p_2d = p_2d + c

    # Place on 4 lateral faces
    p_front = Pos(0, -49.2, 0) * Rotation(90, 0, 0) * p_2d
    p_back = Pos(0, 49.2, 0) * Rotation(90, 0, 0) * p_2d
    p_left = Pos(-49.2, 0, 0) * Rotation(0, 90, 0) * p_2d
    p_right = Pos(49.2, 0, 0) * Rotation(0, 90, 0) * p_2d

    hybrid_chassis = chassis + p_front + p_back + p_left + p_right
    step_hybrid = output_dir / "cubesat_1u_hybrid_chassis_flight28.step"
    stl_hybrid = output_dir / "cubesat_1u_hybrid_chassis_flight28.stl"
    export_step(hybrid_chassis, str(step_hybrid))
    export_stl(hybrid_chassis, str(stl_hybrid))
    logger.info("Saved 1U hybrid chassis STEP (%d bytes) and STL (%d bytes)", step_hybrid.stat().st_size, stl_hybrid.stat().st_size)


if __name__ == "__main__":
    main()
