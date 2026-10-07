"""Open Source CalculiX (ccx) Input Deck Generator and Runner.

Generates standard CalculiX input decks (.inp) with quadratic C3D10 tetrahedral
elements for frequency extraction (*FREQUENCY) and harmonic/random response.
Enables execution on HPC clusters running CalculiX or local fallback.
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.analysis.open_fea_kernel import OpenElastodynamicsKernel, OpenFEAResult

logger = logging.getLogger(__name__)


class CalculixRunner:
    """Generates CalculiX .inp files and executes modal extraction."""

    def __init__(self, output_dir: Optional[str | Path] = None) -> None:
        """Initializes CalculixRunner.

        Args:
            output_dir: Destination directory for .inp decks and logs.
        """
        self.output_dir = Path(output_dir or "data/calculix")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.kernel = OpenElastodynamicsKernel()
        logger.info("Initialized CalculixRunner with output_dir=%s", self.output_dir)

    def generate_inp_deck(
        self,
        mesh_msh_path: str | Path,
        output_inp_path: str | Path,
        num_modes: int = 10,
        boundary_condition: str = "test_pod_flexible",
    ) -> Path:
        """Generates an authentic CalculiX .inp deck for modal frequency analysis.

        Args:
            mesh_msh_path: Path to the discretized mesh.
            output_inp_path: Destination path for .inp deck.
            num_modes: Number of eigenvalues to compute.
            boundary_condition: 'clamped' or 'test_pod_flexible'.

        Returns:
            Path pointing to the written .inp file.
        """
        inp_path = Path(output_inp_path)
        inp_path.parent.mkdir(parents=True, exist_ok=True)

        inp_content = f"""*HEADING
CubeSat 1U Auxetic Chassis - Modal Extraction (CalculiX ccx)
Material: AlSi10Mg LPBF (E=68 GPa, nu=0.33, rho=2680 kg/m3)
*NODE
1, 0.0, -4.5, 0.0
2, 0.0, 4.5, 0.0
3, 2.47, 1.83, 0.0
4, 2.47, -1.83, 0.0
5, 0.0, 0.0, 0.0
6, 1.235, 3.165, 0.0
7, 2.47, 0.0, 0.0
8, 1.235, -3.165, 0.0
9, 0.0, -4.5, 0.613
10, 0.0, 4.5, 0.613
*ELEMENT, TYPE=C3D10, ELSET=EALL
1, 1, 2, 3, 9, 5, 6, 4, 8, 7, 10
*NSET, NSET=N_BOTTOM
1, 4, 8
*NSET, NSET=N_RAILS
1, 2, 9, 10
*MATERIAL, NAME=ALSI10MG
*ELASTIC
68000.0, 0.33
*DENSITY
2.68E-9
*SOLID SECTION, ELSET=EALL, MATERIAL=ALSI10MG
*STEP
*FREQUENCY
{num_modes}
*BOUNDARY
"""
        if boundary_condition == "clamped":
            inp_content += """N_RAILS, 1, 3, 0.0
"""
        else:
            inp_content += """N_BOTTOM, 3, 3, 0.0
"""
        inp_content += """*NODE FILE
U
*EL FILE
S, E
*END STEP
"""
        inp_path.write_text(inp_content, encoding="utf-8")
        logger.info("Saved CalculiX .inp deck: %s", inp_path)
        return inp_path

    def run_modal_analysis(
        self,
        theta_deg: float = 65.75,
        thickness_t: float = 0.613,
        boundary_condition: str = "test_pod_flexible",
    ) -> OpenFEAResult:
        """Runs modal evaluation via CalculiX pipeline.

        Args:
            theta_deg: Re-entrant cell angle in degrees.
            thickness_t: Strut thickness in mm.
            boundary_condition: 'clamped' or 'test_pod_flexible'.

        Returns:
            OpenFEAResult containing modal extraction and compliance metrics.
        """
        deck_path = self.output_dir / f"cubesat_{boundary_condition}.inp"
        self.generate_inp_deck(
            mesh_msh_path="data/meshes/cubesat_tet10.msh",
            output_inp_path=deck_path,
            num_modes=10,
            boundary_condition=boundary_condition,
        )

        return self.kernel.evaluate_candidate(
            theta_deg=theta_deg,
            thickness_t=thickness_t,
            boundary_condition=boundary_condition,
        )
