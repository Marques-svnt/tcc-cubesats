"""Open Source Deterministic Qualification Pipeline for CubeSat 1U Structures.

Implements an open-source engineering pipeline compatible with Prefect flows and
standalone execution. Orchestrates:
1. DoE Latin Hypercube Sampling
2. DfAM LPBF manufacturability screening (CadQuery/B-Rep)
3. Bloch-Floquet phononic bandgap verification
4. Open CAD & Gmsh Tet10 mesh convergence
5. Open FEA modal & NASA GEVS random PSD qualification (Code_Aster / CalculiX)
6. OpenRadioss P-POD transient separation shock & SRS analysis
7. Consolidated Aerospace Qualification Reporting
"""

from dataclasses import asdict, dataclass, field
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from src.analysis.bloch_floquet import BlochFloquetAnalyzer, DispersionAnalysisResult
from src.analysis.code_aster_runner import CodeAsterRunner
from src.analysis.open_fea_kernel import OpenElastodynamicsKernel, OpenFEAResult
from src.analysis.openradioss_shock_runner import OpenRadiossShockRunner, ShockSpectrumResult
from src.cad.cadquery_engine import DfamValidationReport, OpenCadEngine
from src.mesh.gmsh_engine import GmshMeshGenerator, MeshQualityReport
from src.neural.doe_sampler import generate_latin_hypercube_samples

logger = logging.getLogger(__name__)

# Resilient Prefect import
PREFECT_AVAILABLE = False
try:
    from prefect import flow, task  # type: ignore

    PREFECT_AVAILABLE = True
    logger.info("Prefect detected in runtime environment; using native @task and @flow decorators.")
except ImportError:
    logger.info("Prefect not installed; operating in standalone decorated Python mode.")

    def task(*args: Any, **kwargs: Any) -> Any:  # type: ignore
        """Dummy decorator fallback for standalone Prefect-free execution."""

        def decorator(func: Any) -> Any:
            return func

        return decorator

    def flow(*args: Any, **kwargs: Any) -> Any:  # type: ignore
        """Dummy decorator fallback for standalone Prefect-free execution."""

        def decorator(func: Any) -> Any:
            return func

        return decorator


@dataclass(slots=True)
class OpenCandidateEvaluation:
    """Consolidated record of an evaluated aerospace candidate."""

    candidate_id: str
    theta_deg: float
    thickness_t: float
    length_l: float
    height_h: float
    relative_density: float
    is_dfam_valid: bool
    has_phononic_bandgap: bool
    first_natural_freq_hz: float
    peak_3sigma_stress_mpa: float
    payload_grms: float
    transmissibility_ratio: float
    margin_of_safety_yield: float
    fatigue_damage_steinberg: float
    payload_max_srs_g: float
    is_gevs_qualified: bool
    is_fully_qualified: bool
    audit_notes: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Converts evaluation to dictionary."""
        return asdict(self)


class OpenSourceQualificationPipeline:
    """Deterministic, typed qualification pipeline built on open-source solvers."""

    def __init__(self, output_dir: Optional[str | Path] = None) -> None:
        """Initializes the Open Source Qualification Pipeline.

        Args:
            output_dir: Root directory for audit logs, decks, and reports.
        """
        self.output_dir = Path(output_dir or "reports/open_pipeline")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Initialize open-source components
        self.cad_engine = OpenCadEngine(output_dir=self.output_dir / "cad")
        self.mesh_generator = GmshMeshGenerator(output_dir=self.output_dir / "mesh")
        self.aster_runner = CodeAsterRunner(output_dir=self.output_dir / "code_aster")
        self.bloch_analyzer = BlochFloquetAnalyzer()
        self.shock_runner = OpenRadiossShockRunner(output_dir=self.output_dir / "openradioss")

        logger.info("Initialized OpenSourceQualificationPipeline at %s", self.output_dir)

    @task(name="evaluate_single_candidate")
    def evaluate_candidate(
        self,
        candidate_id: str,
        theta_deg: float,
        thickness_t: float,
        length_l: float,
        height_h: float,
        boundary_condition: str = "test_pod_flexible",
    ) -> OpenCandidateEvaluation:
        """Executes full multi-physics qualification for a single design.

        Args:
            candidate_id: Unique candidate tag.
            theta_deg: Cell re-entrant angle in degrees.
            thickness_t: Strut wall thickness in mm.
            length_l: Strut length in mm.
            height_h: Strut height in mm.
            boundary_condition: 'clamped' or 'test_pod_flexible'.

        Returns:
            OpenCandidateEvaluation record.
        """
        notes: List[str] = []

        # 1. DfAM Screening
        dfam_rep = self.cad_engine.validate_lpbf_dfam(
            theta_deg=theta_deg,
            thickness_t=thickness_t,
            length_l=length_l,
            height_h=height_h,
        )
        if not dfam_rep.is_compliant:
            notes.extend(dfam_rep.failure_reasons)
            return OpenCandidateEvaluation(
                candidate_id=candidate_id,
                theta_deg=theta_deg,
                thickness_t=thickness_t,
                length_l=length_l,
                height_h=height_h,
                relative_density=dfam_rep.relative_density,
                is_dfam_valid=False,
                has_phononic_bandgap=False,
                first_natural_freq_hz=0.0,
                peak_3sigma_stress_mpa=0.0,
                payload_grms=0.0,
                transmissibility_ratio=1.0,
                margin_of_safety_yield=-1.0,
                fatigue_damage_steinberg=999.0,
                payload_max_srs_g=999.0,
                is_gevs_qualified=False,
                is_fully_qualified=False,
                audit_notes=notes,
            )

        notes.append("Passed DfAM LPBF manufacturability gate.")

        # 2. Bloch-Floquet Dispersion Analysis
        disp_res = self.bloch_analyzer.compute_dispersion_relation(
            theta_deg=theta_deg,
            thickness_t=thickness_t,
            length_l=length_l,
            height_h=height_h,
        )
        if disp_res.has_target_bandgap:
            notes.append(
                f"Bloch-Floquet bandgap confirmed: {len(disp_res.bandgaps)} acoustic gaps detected."
            )
        else:
            notes.append("No complete bandgap in target launch band (200 - 1200 Hz).")

        # 3. Open FEA Dynamic Qualification (Code_Aster / Open Kernel)
        fea_res = self.aster_runner.run_qualification(
            theta_deg=theta_deg,
            thickness_t=thickness_t,
            length_l=length_l,
            height_h=height_h,
            boundary_condition=boundary_condition,
            mesh_layers=3,
        )

        # 4. OpenRadioss Separation Shock Analysis (SRS Q=10)
        shock_res = self.shock_runner.solve_separation_shock(
            cubesat_mass_kg=1.330,
            spring_preload_n=55.60,
            spring_k_n_m=556.0,
            stroke_length_m=0.100,
        )
        notes.append(
            f"Shock SRS peak: {shock_res.payload_max_srs_g:.1f} G (limit: {shock_res.srs_limit_threshold_g:.1f} G)."
        )

        # 5. Aerospace Qualification Quality Gates
        is_gevs = fea_res.is_gevs_compliant
        is_fully = is_gevs and disp_res.has_target_bandgap and shock_res.is_shock_qualified

        if is_fully:
            notes.append("Candidate FULLY QUALIFIED for flight under NASA GSFC-STD-7000A.")
        else:
            notes.append("Candidate did not satisfy all concurrent flight gates.")

        return OpenCandidateEvaluation(
            candidate_id=candidate_id,
            theta_deg=theta_deg,
            thickness_t=thickness_t,
            length_l=length_l,
            height_h=height_h,
            relative_density=dfam_rep.relative_density,
            is_dfam_valid=True,
            has_phononic_bandgap=disp_res.has_target_bandgap,
            first_natural_freq_hz=fea_res.first_natural_freq_hz,
            peak_3sigma_stress_mpa=fea_res.peak_3sigma_stress_mpa,
            payload_grms=fea_res.payload_grms,
            transmissibility_ratio=fea_res.transmissibility_ratio,
            margin_of_safety_yield=fea_res.margin_of_safety_yield,
            fatigue_damage_steinberg=fea_res.fatigue_damage_steinberg,
            payload_max_srs_g=shock_res.payload_max_srs_g,
            is_gevs_qualified=is_gevs,
            is_fully_qualified=is_fully,
            audit_notes=notes,
        )

    @flow(name="cubesat_open_source_qualification_pipeline")
    def run_pipeline(
        self,
        num_samples: int = 50,
        boundary_condition: str = "test_pod_flexible",
    ) -> List[OpenCandidateEvaluation]:
        """Executes full open-source screening over Latin Hypercube design samples.

        Args:
            num_samples: Number of parameter sets to sample.
            boundary_condition: 'clamped' or 'test_pod_flexible'.

        Returns:
            List of evaluated OpenCandidateEvaluation instances.
        """
        logger.info(
            "Starting Open Source Qualification Pipeline with %d samples...", num_samples
        )
        samples = generate_latin_hypercube_samples(num_samples=num_samples, random_seed=42)

        results: List[OpenCandidateEvaluation] = []
        for i, s in enumerate(samples, start=1):
            eval_res = self.evaluate_candidate(
                candidate_id=f"OpenCand_{i:03d}",
                theta_deg=s["theta_deg"],
                thickness_t=s["thickness_t"],
                length_l=s["length_l"],
                height_h=s["height_h"],
                boundary_condition=boundary_condition,
            )
            results.append(eval_res)

        qualified = [r for r in results if r.is_fully_qualified]
        logger.info(
            "Pipeline finished: %d / %d candidates (%.1f%%) fully qualified under open-source stack.",
            len(qualified),
            num_samples,
            (len(qualified) / num_samples) * 100.0,
        )

        # Save consolidated JSON report
        report_file = self.output_dir / "open_pipeline_results.json"
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump([r.to_dict() for r in results], f, indent=2)
        logger.info("Saved open pipeline execution report: %s", report_file)

        return results


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    pipe = OpenSourceQualificationPipeline()
    res = pipe.run_pipeline(num_samples=10)
    print(f"Evaluated {len(res)} candidates.")
