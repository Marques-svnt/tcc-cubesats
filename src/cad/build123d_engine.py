"""CAD Engine powered by build123d for CubeSat DfAM parametric modeling.

Provides exact B-Rep solid modeling with OpenCASCADE via build123d,
incorporating Design for Additive Manufacturing (DfAM) constraints for
AlSi10Mg Laser Powder Bed Fusion (L-PBF) and STEP export for Gmsh.
"""

from __future__ import annotations

from dataclasses import dataclass
import logging
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from build123d import (
    Box,
    Compound,
    Cylinder,
    Part,
    Pos,
    Rotation,
    export_step,
    export_stl,
)

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class MassPropertiesReport:
    """Summary of geometrical and mass properties derived from exact B-Rep solid."""

    volume_mm3: float
    mass_kg: float
    center_of_mass_mm: Tuple[float, float, float]
    relative_density: float
    envelope_dimensions_mm: Tuple[float, float, float]

    def to_dict(self) -> Dict[str, Any]:
        """Serializes report to dictionary."""
        return {
            "volume_mm3": self.volume_mm3,
            "mass_kg": self.mass_kg,
            "center_of_mass_mm": list(self.center_of_mass_mm),
            "relative_density": self.relative_density,
            "envelope_dimensions_mm": list(self.envelope_dimensions_mm),
        }


class Build123dEngine:
    """Parametric CAD generator with DfAM verification and STEP/STL export powered by build123d."""

    # CalPoly CubeSat 1U Specification Constants
    DEFAULT_LENGTH_MM: float = 100.0
    DEFAULT_WIDTH_MM: float = 100.0
    DEFAULT_HEIGHT_MM: float = 113.5
    DEFAULT_RAIL_WIDTH_MM: float = 8.5
    ALSI10MG_DENSITY_KG_M3: float = 2680.0

    def __init__(
        self,
        min_wall_thickness_mm: float = 0.40,
        min_hole_clearance_mm: float = 2.0,
    ) -> None:
        """Initializes engine with additive manufacturing limits.

        Args:
            min_wall_thickness_mm: Minimum allowable wall thickness for AlSi10Mg L-PBF.
            min_hole_clearance_mm: Minimum hole diameter for unmelted powder evacuation.
        """
        self.min_wall_thickness_mm = min_wall_thickness_mm
        self.min_hole_clearance_mm = min_hole_clearance_mm
        logger.info(
            "Build123dEngine initialized (min_wall=%.2f mm, min_hole=%.2f mm)",
            min_wall_thickness_mm,
            min_hole_clearance_mm,
        )

    def generate_cubesat_chassis(
        self,
        length_mm: float = 100.0,
        width_mm: float = 100.0,
        height_mm: float = 113.5,
        wall_thickness_mm: float = 1.5,
    ) -> Compound:
        """Generates a hollow 1U CubeSat chassis solid compound (baseline shell).

        Args:
            length_mm: Outer dimension X (default 100.0 mm).
            width_mm: Outer dimension Y (default 100.0 mm).
            height_mm: Outer dimension Z (default 113.5 mm).
            wall_thickness_mm: Structural outer wall thickness.

        Returns:
            Compound solid representing the hollow chassis.

        Raises:
            ValueError: If wall thickness violates DfAM limits or dimensions are non-positive.
        """
        if wall_thickness_mm < self.min_wall_thickness_mm:
            raise ValueError(
                f"Wall thickness {wall_thickness_mm:.2f} mm is below DfAM limit "
                f"{self.min_wall_thickness_mm:.2f} mm"
            )
        if min(length_mm, width_mm, height_mm) <= 2 * wall_thickness_mm:
            raise ValueError("Dimensions must exceed double the wall thickness")

        outer = Box(length_mm, width_mm, height_mm)
        inner = Box(
            length_mm - 2.0 * wall_thickness_mm,
            width_mm - 2.0 * wall_thickness_mm,
            height_mm - 2.0 * wall_thickness_mm,
        )
        chassis = outer - inner
        logger.info(
            "Generated basic 1U chassis (%.1fx%.1fx%.1f mm, t=%.2f mm)",
            length_mm,
            width_mm,
            height_mm,
            wall_thickness_mm,
        )
        return chassis

    def generate_1u_flight_chassis(
        self,
        length_mm: float = 100.0,
        width_mm: float = 100.0,
        height_mm: float = 113.5,
        rail_width_mm: float = 8.5,
        wall_thickness_mm: float = 1.20,
        window_margin_mm: float = 10.0,
        drain_hole_dia_mm: float = 3.5,
    ) -> Compound:
        """Generates the canonical 1U CubeSat flight chassis with 4 solid deployer rails.

        Conforms strictly to California Polytechnic State University CubeSat Design Specification:
        - Outer envelope: length_mm x width_mm x height_mm (nominal 100 x 100 x 113.5 mm).
        - Four solid corner rails (rail_width_mm x rail_width_mm) along Z for P-POD interface.
        - Thin lateral structural shear panels with DfAM-compliant wall thickness.
        - Lateral access/lightweighting windows on X and Y faces.
        - Powder evacuation clearance holes (dia >= 2.0 mm) on base plates.

        Args:
            length_mm: Outer envelope length along X in mm.
            width_mm: Outer envelope width along Y in mm.
            height_mm: Outer envelope height along Z in mm.
            rail_width_mm: Contact rail width in mm (default 8.5 mm standard).
            wall_thickness_mm: Panel wall thickness in mm (>= min_wall_thickness_mm).
            window_margin_mm: Margin from rail edge to window opening in mm.
            drain_hole_dia_mm: Diameter of powder evacuation holes in mm.

        Returns:
            Compound representing the qualified 1U primary flight structure.

        Raises:
            ValueError: If parameters violate DfAM manufacturability or CalPoly geometry limits.
        """
        if wall_thickness_mm < self.min_wall_thickness_mm:
            raise ValueError(
                f"Wall thickness {wall_thickness_mm:.2f} mm is below DfAM limit {self.min_wall_thickness_mm:.2f} mm"
            )
        if drain_hole_dia_mm < self.min_hole_clearance_mm:
            raise ValueError(
                f"Drain hole diameter {drain_hole_dia_mm:.2f} mm is below DfAM limit {self.min_hole_clearance_mm:.2f} mm"
            )
        if rail_width_mm * 2 >= min(length_mm, width_mm):
            raise ValueError("Rail width exceeds allowable envelope bounds")

        # 1. Base hollow shell
        outer = Box(length_mm, width_mm, height_mm)
        inner = Box(
            length_mm - 2.0 * wall_thickness_mm,
            width_mm - 2.0 * wall_thickness_mm,
            height_mm - 2.0 * wall_thickness_mm,
        )
        chassis = outer - inner

        # 2. Add solid 8.5x8.5 mm deployer rails along the four Z corners
        rail_cx = length_mm / 2.0 - rail_width_mm / 2.0
        rail_cy = width_mm / 2.0 - rail_width_mm / 2.0

        r1 = Pos(rail_cx, rail_cy, 0.0) * Box(rail_width_mm, rail_width_mm, height_mm)
        r2 = Pos(-rail_cx, rail_cy, 0.0) * Box(rail_width_mm, rail_width_mm, height_mm)
        r3 = Pos(rail_cx, -rail_cy, 0.0) * Box(rail_width_mm, rail_width_mm, height_mm)
        r4 = Pos(-rail_cx, -rail_cy, 0.0) * Box(rail_width_mm, rail_width_mm, height_mm)

        chassis = chassis + r1 + r2 + r3 + r4

        # 3. Cut lateral access/mass-reduction windows on side faces (X and Y)
        win_w_x = width_mm - 2.0 * rail_width_mm - 2.0 * window_margin_mm
        win_w_y = length_mm - 2.0 * rail_width_mm - 2.0 * window_margin_mm
        win_h = height_mm - 2.0 * window_margin_mm

        if win_w_x > 0.0 and win_h > 0.0:
            cut_x = Box(length_mm + 10.0, win_w_x, win_h)
            chassis = chassis - cut_x

        if win_w_y > 0.0 and win_h > 0.0:
            cut_y = Box(win_w_y, width_mm + 10.0, win_h)
            chassis = chassis - cut_y

        # 4. Add depowdering drainage holes on top/bottom faces
        drain_offset_x = length_mm / 2.0 - rail_width_mm - drain_hole_dia_mm
        drain_offset_y = width_mm / 2.0 - rail_width_mm - drain_hole_dia_mm
        if drain_offset_x > 0 and drain_offset_y > 0:
            drain_cyl = Cylinder(radius=drain_hole_dia_mm / 2.0, height=height_mm + 10.0)
            chassis = chassis - (Pos(drain_offset_x, drain_offset_y, 0.0) * drain_cyl)
            chassis = chassis - (Pos(-drain_offset_x, -drain_offset_y, 0.0) * drain_cyl)

        logger.info(
            "Constructed canonical 1U flight chassis: V=%.2f mm3, Envelope=(%.1f, %.1f, %.1f) mm",
            chassis.volume,
            length_mm,
            width_mm,
            height_mm,
        )
        return chassis

    def generate_1u_hybrid_flight_chassis(
        self,
        length_mm: float = 100.0,
        width_mm: float = 100.0,
        height_mm: float = 113.5,
        rail_width_mm: float = 8.5,
        wall_thickness_mm: float = 1.20,
        auxetic_cell_thickness_mm: float = 0.613,
        panel_extrusion_depth_mm: float = 1.60,
    ) -> Compound:
        """Generates the qualified 1U hybrid flight chassis with integrated auxetic metamaterial panels.

        Fuses the canonical 1U primary chassis with four lateral auxetic re-entrant honeycomb
        panels (flight candidate #28: theta=68.60 deg, h=9.0 mm, l=6.0 mm, t=0.613 mm) for
        passive vibration attenuation and pyrotechnic shock suppression.

        Args:
            length_mm: Envelope length in X (default 100.0 mm).
            width_mm: Envelope width in Y (default 100.0 mm).
            height_mm: Envelope height in Z (default 113.5 mm).
            rail_width_mm: Contact rail width in mm.
            wall_thickness_mm: Primary frame wall thickness in mm.
            auxetic_cell_thickness_mm: Strut thickness of auxetic ribs in mm.
            panel_extrusion_depth_mm: Lateral panel thickness in mm.

        Returns:
            Compound representing the fully integrated 1U hybrid flight chassis.
        """
        import math

        # 1. Base canonical chassis frame
        base_chassis = self.generate_1u_flight_chassis(
            length_mm=length_mm,
            width_mm=width_mm,
            height_mm=height_mm,
            rail_width_mm=rail_width_mm,
            wall_thickness_mm=wall_thickness_mm,
        )

        # 2. Build auxetic re-entrant unit cell solid
        theta_h_rad = math.radians(21.40)
        l_strut = 6.0
        h_strut = 9.0
        t_strut = auxetic_cell_thickness_mm
        depth = panel_extrusion_depth_mm

        dx = l_strut * math.cos(theta_h_rad)
        dy = l_strut * math.sin(theta_h_rad)
        x_outer = dx + 1.20
        x_inner = x_outer - dx
        y_mid = dy

        nodes = {
            "L_top": (-x_outer, y_mid + h_strut / 2.0),
            "L_mid_top": (-x_outer, y_mid),
            "L_waist": (-x_inner, 0.0),
            "L_mid_bot": (-x_outer, -y_mid),
            "L_bot": (-x_outer, -y_mid - h_strut / 2.0),
            "R_top": (x_outer, y_mid + h_strut / 2.0),
            "R_mid_top": (x_outer, y_mid),
            "R_waist": (x_inner, 0.0),
            "R_mid_bot": (x_outer, -y_mid),
            "R_bot": (x_outer, -y_mid - h_strut / 2.0),
        }

        struts_topo = [
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
            dist = math.hypot(p2[0] - p1[0], p2[1] - p1[1]) + t_strut * 0.95
            ang = math.degrees(math.atan2(p2[1] - p1[1], p2[0] - p1[0]))
            return Pos((p1[0] + p2[0]) / 2.0, (p1[1] + p2[1]) / 2.0, 0) * Rotation(0, 0, ang) * Box(dist, t_strut, depth)

        solids = [build_strut(p1, p2) for p1, p2 in struts_topo]
        for pt in nodes.values():
            solids.append(Pos(pt[0], pt[1], 0) * Cylinder(radius=t_strut * 0.75, height=depth))

        cell = solids[0]
        for s in solids[1:]:
            cell = cell + s

        # 3. Assemble 4x5 cellular lattice panel
        nx, ny = 4, 5
        sp_x = 2.0 * (dx + 1.20) - 0.613
        sp_y = 2.0 * (dy + 4.50) - 0.613

        p_cells = []
        for ix in range(nx):
            for iy in range(ny):
                px = (ix - (nx - 1) / 2.0) * sp_x
                py = (iy - (ny - 1) / 2.0) * sp_y
                p_cells.append(Pos(px, py, 0) * cell)

        p_2d = p_cells[0]
        for c in p_cells[1:]:
            p_2d = p_2d + c

        # 4. Orient and fuse into four lateral access windows
        panel_offset = length_mm / 2.0 - depth / 2.0
        p_front = Pos(0, -panel_offset, 0) * Rotation(90, 0, 0) * p_2d
        p_back = Pos(0, panel_offset, 0) * Rotation(90, 0, 0) * p_2d
        p_left = Pos(-panel_offset, 0, 0) * Rotation(0, 90, 0) * p_2d
        p_right = Pos(panel_offset, 0, 0) * Rotation(0, 90, 0) * p_2d

        hybrid = base_chassis + p_front + p_back + p_left + p_right
        logger.info(
            "Constructed complete 1U hybrid flight chassis: V=%.2f mm3 (mass=%.3f kg)",
            hybrid.volume,
            float(hybrid.volume) * 1e-9 * self.ALSI10MG_DENSITY_KG_M3,
        )
        return hybrid

    def compute_mass_properties(
        self,
        solid: Compound | Part,
        density_kg_m3: float = ALSI10MG_DENSITY_KG_M3,
        envelope_dims: Optional[Tuple[float, float, float]] = None,
    ) -> MassPropertiesReport:
        """Calculates mass, center of gravity, and volume metrics via exact B-Rep geometry.

        Args:
            solid: build123d Compound or Part solid.
            density_kg_m3: Material mass density (default 2680.0 kg/m3 for AlSi10Mg).
            envelope_dims: Optional (length, width, height) tuple for relative density calculation.

        Returns:
            MassPropertiesReport dataclass.
        """
        vol_mm3 = float(solid.volume)
        mass_kg = float(vol_mm3 * 1.0e-9 * density_kg_m3)
        center_vec = solid.center()
        cog = (float(center_vec.X), float(center_vec.Y), float(center_vec.Z))

        if envelope_dims is None:
            envelope_dims = (self.DEFAULT_LENGTH_MM, self.DEFAULT_WIDTH_MM, self.DEFAULT_HEIGHT_MM)

        env_vol = envelope_dims[0] * envelope_dims[1] * envelope_dims[2]
        rel_density = float(vol_mm3 / env_vol) if env_vol > 0 else 0.0

        report = MassPropertiesReport(
            volume_mm3=vol_mm3,
            mass_kg=mass_kg,
            center_of_mass_mm=cog,
            relative_density=rel_density,
            envelope_dimensions_mm=envelope_dims,
        )
        logger.info(
            "Mass properties evaluated: mass=%.4f kg (%.2f g), rel_density=%.3f, CoG=(%.2f, %.2f, %.2f) mm",
            mass_kg,
            mass_kg * 1e3,
            rel_density,
            cog[0],
            cog[1],
            cog[2],
        )
        return report

    def export_step(self, solid: Compound | Part, output_path: Path | str) -> Path:
        """Exports compound solid to canonical STEP AP214 file for Gmsh meshing.

        Args:
            solid: Compound geometric object to export.
            output_path: Target filesystem path for the .step file.

        Returns:
            Absolute Path to written file.
        """
        target = Path(output_path).resolve()
        target.parent.mkdir(parents=True, exist_ok=True)
        export_step(solid, str(target))
        logger.info("Successfully exported canonical STEP model to %s (%d bytes)", target, target.stat().st_size)
        return target

    def export_stl(self, solid: Compound | Part, output_path: Path | str) -> Path:
        """Exports compound solid to standard triangulated STL file.

        Args:
            solid: Compound geometric object to export.
            output_path: Target filesystem path for the .stl file.

        Returns:
            Absolute Path to written file.
        """
        target = Path(output_path).resolve()
        target.parent.mkdir(parents=True, exist_ok=True)
        export_stl(solid, str(target))
        logger.info("Successfully exported triangulated STL model to %s (%d bytes)", target, target.stat().st_size)
        return target

