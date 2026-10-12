"""Monte Carlo Uncertainty Quantification for 1U CubeSat Auxetic Chassis.

Propagates additive manufacturing dimensional tolerances (LPBF layer variations)
through the Physics-Guided ResNet surrogate model to compute rigorous stochastic
confidence intervals for fundamental frequency, peak stress, transmissibility,
margins of safety (Yield & Ultimate), and fatigue damage under NASA GSFC-STD-7000A.
"""

import logging
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import numpy as np
import torch

from src.core.settings import get_settings
from src.neural.surrogate_model import CubeSatSurrogateResNet, SurrogateDatasetScaler

logger = logging.getLogger(__name__)

_SETTINGS = get_settings()


@dataclass(slots=True)
class ToleranceSpec:
    """Standard manufacturing dimensional tolerances for LPBF process.

    Default standard deviations represent calibrated industrial LPBF processes
    for AlSi10Mg (EOS M 290 / SLM 280) with +/- 3-sigma tolerance envelopes.
    """

    sigma_thickness_mm: float = 0.015  # +/- 45 um 3-sigma thickness variation
    sigma_theta_deg: float = 0.50  # +/- 1.5 deg 3-sigma angular deviation
    sigma_length_mm: float = 0.020  # +/- 60 um 3-sigma rib length variation
    sigma_height_mm: float = 0.020  # +/- 60 um 3-sigma rib height variation


@dataclass(slots=True)
class MetricStats:
    """Summary statistics and percentile confidence intervals for a response."""

    mean: float
    std: float
    p025: float
    p500: float
    p975: float
    min_val: float
    max_val: float


@dataclass(slots=True)
class UncertaintyResult:
    """Comprehensive stochastic evaluation across Monte Carlo realizations."""

    nominal_inputs: dict[str, float]
    tolerances: dict[str, float]
    num_samples: int
    f1_hz: MetricStats
    peak_stress_mpa: MetricStats
    payload_grms: MetricStats
    transmissibility: MetricStats
    margin_of_safety_yield: MetricStats
    margin_of_safety_ultimate: MetricStats
    fatigue_damage: MetricStats
    prob_f1_compliant: float  # P(f1 >= 100 Hz)
    prob_ms_yield_positive: float  # P(MS_yield > 0)
    prob_ms_ultimate_positive: float  # P(MS_ultimate > 0)
    prob_fatigue_qualified: float  # P(D <= 0.25)
    execution_time_sec: float

    def to_dict(self) -> dict[str, Any]:
        """Converts result dataclass to a serializable dictionary."""
        return asdict(self)


class UncertaintyQuantifier:
    """Deep module for Monte Carlo Uncertainty Quantification on surrogate models.

    Hides all stochastic sampling, vectorized forward passes, covariance scaling,
    and percentile derivations behind a single, highly leveraged propagate() interface.
    """

    def __init__(
        self,
        model: CubeSatSurrogateResNet | None = None,
        scaler: SurrogateDatasetScaler | None = None,
        model_path: Path | str | None = None,
        scaler_path: Path | str | None = None,
    ) -> None:
        """Initializes the UncertaintyQuantifier.

        Args:
            model: Optional pre-loaded CubeSatSurrogateResNet model.
            scaler: Optional pre-loaded SurrogateDatasetScaler.
            model_path: Path to serialized PyTorch model weights (.pt).
            scaler_path: Path to serialized scaler parameters (.json).
        """
        base_dir = Path(__file__).resolve().parent.parent.parent

        if scaler is not None:
            self.scaler = scaler
        else:
            s_path = (
                Path(scaler_path) if scaler_path else base_dir / "models" / "surrogate_scaler.json"
            )
            self.scaler = SurrogateDatasetScaler.load_json(s_path)

        if model is not None:
            self.model = model
        else:
            m_path = (
                Path(model_path)
                if model_path
                else base_dir / "models" / "physics_guided_surrogate.pt"
            )
            self.model = CubeSatSurrogateResNet(
                input_dim=5, output_dim=3, hidden_dim=64, num_blocks=2
            )
            state_dict = torch.load(
                str(m_path), weights_only=True, map_location=torch.device("cpu")
            )
            if isinstance(state_dict, dict) and "model_state_dict" in state_dict:
                state_dict = state_dict["model_state_dict"]
            self.model.load_state_dict(state_dict)
            self.model.eval()

        logger.info("UncertaintyQuantifier initialized successfully.")

    @staticmethod
    def _compute_stats(samples: np.ndarray) -> MetricStats:
        """Computes summary statistics for a 1D array of stochastic samples."""
        return MetricStats(
            mean=float(np.mean(samples)),
            std=float(np.std(samples)),
            p025=float(np.percentile(samples, 2.5)),
            p500=float(np.percentile(samples, 50.0)),
            p975=float(np.percentile(samples, 97.5)),
            min_val=float(np.min(samples)),
            max_val=float(np.max(samples)),
        )

    def propagate(
        self,
        theta_deg: float,
        thickness_t: float,
        length_l: float,
        height_h: float,
        num_samples: int = 10_000,
        tolerances: ToleranceSpec | None = None,
        random_seed: int | None = 42,
    ) -> UncertaintyResult:
        """Propagates geometric manufacturing tolerances via Monte Carlo simulation.

        Args:
            theta_deg: Nominal re-entrant angle in degrees.
            thickness_t: Nominal rib thickness in mm.
            length_l: Nominal inclined rib length in mm.
            height_h: Nominal vertical rib height in mm.
            num_samples: Number of Monte Carlo draws (default 10,000).
            tolerances: Optional ToleranceSpec defining standard deviations.
            random_seed: Random seed for reproducibility.

        Returns:
            UncertaintyResult containing statistical distributions and flight margins.
        """
        start_time = time.perf_counter()
        tol = tolerances or ToleranceSpec()

        if random_seed is not None:
            np.random.seed(random_seed)

        # 1. Sample perturbed Gaussian distributions with physical truncation
        theta_samples = np.clip(
            np.random.normal(theta_deg, tol.sigma_theta_deg, size=num_samples),
            50.0,
            85.0,
        )
        t_samples = np.clip(
            np.random.normal(thickness_t, tol.sigma_thickness_mm, size=num_samples),
            0.50,
            2.00,
        )
        l_samples = np.clip(
            np.random.normal(length_l, tol.sigma_length_mm, size=num_samples),
            5.00,
            16.00,
        )
        h_samples = np.clip(
            np.random.normal(height_h, tol.sigma_height_mm, size=num_samples),
            7.00,
            22.00,
        )

        # 2. Vectorized analytical relative density calculation
        theta_rad = np.radians(theta_samples)
        cos_theta = np.cos(theta_rad)
        sin_theta = np.sin(theta_rad)
        ratio_h_l = h_samples / l_samples

        numerator = (t_samples / l_samples) * (ratio_h_l + 2.0)
        denominator = 2.0 * cos_theta * (ratio_h_l + sin_theta)
        rho_rel_samples = np.clip(numerator / np.maximum(denominator, 1e-6), 0.01, 0.95)

        # 3. Vectorized batch surrogate inference
        x_raw = np.column_stack([theta_samples, t_samples, l_samples, h_samples, rho_rel_samples])
        x_scaled = self.scaler.transform_x(x_raw)

        with torch.no_grad():
            x_tensor = torch.from_numpy(x_scaled).float()
            y_scaled = self.model(x_tensor).numpy()

        y_raw = self.scaler.inverse_transform_y(y_scaled)

        f1_samples = y_raw[:, 0]
        stress_samples = np.maximum(y_raw[:, 1], 1.0)
        grms_samples = y_raw[:, 2]
        trans_samples = grms_samples / 14.1

        # 4. Aerospace Margins of Safety (Yield and Ultimate)
        allowable_yield = _SETTINGS.alsi10mg.safety_factors.allowable_stress_yield_mpa
        ms_yield_samples = (allowable_yield / stress_samples) - 1.0

        uts = _SETTINGS.alsi10mg.strength_limits.ultimate_tensile_strength_mpa
        fs_ult = _SETTINGS.alsi10mg.safety_factors.ultimate_factor
        allowable_ultimate = uts / fs_ult  # 340.0 / 1.40 = 242.86 MPa
        ms_ultimate_samples = (allowable_ultimate / stress_samples) - 1.0

        # 5. Vectorized Steinberg 3-band cumulative fatigue damage
        m = _SETTINGS.alsi10mg.fatigue_properties.basquin_exponent_m
        c = _SETTINGS.alsi10mg.fatigue_properties.basquin_constant_c
        duration = _SETTINGS.gevs.general.duration_per_axis_seconds
        k_steinberg = 0.6831 * (1.0 / 3.0) ** m + 0.2710 * (2.0 / 3.0) ** m + 0.0433 * (1.0) ** m
        fatigue_samples = (duration / c) * k_steinberg * f1_samples * (stress_samples**m)

        # 6. Flight qualification compliance probabilities
        prob_f1 = float(
            np.mean(
                f1_samples >= _SETTINGS.gevs.stiffness_requirements.minimum_fundamental_frequency_hz
            )
        )
        prob_ms_yield = float(np.mean(ms_yield_samples > 0.0))
        prob_ms_ultimate = float(np.mean(ms_ultimate_samples > 0.0))
        prob_fatigue = float(np.mean(fatigue_samples <= 0.25))

        elapsed = time.perf_counter() - start_time
        logger.info(
            "Monte Carlo UQ finished in %.3f s (N=%d). P(f1>=100)=%.4f, P(MS_ult>0)=%.4f, P(D<=0.25)=%.4f",
            elapsed,
            num_samples,
            prob_f1,
            prob_ms_ultimate,
            prob_fatigue,
        )

        return UncertaintyResult(
            nominal_inputs={
                "theta_deg": theta_deg,
                "thickness_t": thickness_t,
                "length_l": length_l,
                "height_h": height_h,
            },
            tolerances={
                "sigma_thickness_mm": tol.sigma_thickness_mm,
                "sigma_theta_deg": tol.sigma_theta_deg,
                "sigma_length_mm": tol.sigma_length_mm,
                "sigma_height_mm": tol.sigma_height_mm,
            },
            num_samples=num_samples,
            f1_hz=self._compute_stats(f1_samples),
            peak_stress_mpa=self._compute_stats(stress_samples),
            payload_grms=self._compute_stats(grms_samples),
            transmissibility=self._compute_stats(trans_samples),
            margin_of_safety_yield=self._compute_stats(ms_yield_samples),
            margin_of_safety_ultimate=self._compute_stats(ms_ultimate_samples),
            fatigue_damage=self._compute_stats(fatigue_samples),
            prob_f1_compliant=prob_f1,
            prob_ms_yield_positive=prob_ms_yield,
            prob_ms_ultimate_positive=prob_ms_ultimate,
            prob_fatigue_qualified=prob_fatigue,
            execution_time_sec=elapsed,
        )
