"""Unit and integration tests for Monte Carlo Uncertainty Quantification."""

import pytest

from src.neural.uncertainty_quantifier import (
    ToleranceSpec,
    UncertaintyQuantifier,
    UncertaintyResult,
)


@pytest.fixture
def quantifier() -> UncertaintyQuantifier:
    """Fixture providing initialized UncertaintyQuantifier instance."""
    return UncertaintyQuantifier()


def test_uncertainty_quantifier_initialization(quantifier: UncertaintyQuantifier) -> None:
    """Verifies that UncertaintyQuantifier initializes with model and scaler."""
    assert quantifier.model is not None
    assert quantifier.scaler is not None
    assert quantifier.scaler.input_names == [
        "theta_deg",
        "thickness_t",
        "length_l",
        "height_h",
        "relative_density",
    ]


def test_propagate_canonical_flight_candidate(quantifier: UncertaintyQuantifier) -> None:
    """Evaluates the canonical Pareto flight design under 10,000 Monte Carlo realizations.

    Canonical parameters: theta=65.75 deg, t=0.613 mm, l=10.42 mm, h=14.85 mm.
    Verifies that flight qualification requirements (NASA GEVS) hold with >= 99.9% probability.
    """
    res: UncertaintyResult = quantifier.propagate(
        theta_deg=65.75,
        thickness_t=0.613,
        length_l=10.42,
        height_h=14.85,
        num_samples=10_000,
        random_seed=42,
    )

    # 1. Performance check: 10,000 evaluations in under 1 second
    assert res.execution_time_sec < 1.0
    assert res.num_samples == 10_000

    # 2. Stiffness qualification: f1 >= 100 Hz
    assert res.f1_hz.mean > 450.0  # nominal around ~646 Hz
    assert res.f1_hz.p025 > 350.0  # conservative 97.5% lower bound
    assert res.prob_f1_compliant == 1.0

    # 3. Peak stress & Ultimate Margin of Safety
    assert 50.0 < res.peak_stress_mpa.mean < 220.0
    assert res.margin_of_safety_ultimate.mean > 0.15  # positive ultimate margin
    assert res.margin_of_safety_ultimate.p025 > 0.0  # 97.5% lower bound > 0
    assert res.prob_ms_ultimate_positive == 1.0

    # 4. Steinberg fatigue qualification: D <= 0.25
    assert res.fatigue_damage.mean < 0.20
    assert res.prob_fatigue_qualified == 1.0

    # 5. Attenuation check (vibration damping)
    assert res.transmissibility.mean < 0.50
    assert res.payload_grms.mean < 5.0


def test_propagate_tolerance_sensitivity(quantifier: UncertaintyQuantifier) -> None:
    """Verifies that larger tolerances lead to larger dispersion (standard deviation)."""
    tight_tol = ToleranceSpec(
        sigma_thickness_mm=0.005,
        sigma_theta_deg=0.10,
        sigma_length_mm=0.005,
        sigma_height_mm=0.005,
    )
    wide_tol = ToleranceSpec(
        sigma_thickness_mm=0.050,
        sigma_theta_deg=1.50,
        sigma_length_mm=0.050,
        sigma_height_mm=0.050,
    )

    res_tight = quantifier.propagate(
        65.75, 0.613, 10.42, 14.85, num_samples=5_000, tolerances=tight_tol, random_seed=42
    )
    res_wide = quantifier.propagate(
        65.75, 0.613, 10.42, 14.85, num_samples=5_000, tolerances=wide_tol, random_seed=42
    )

    assert res_wide.f1_hz.std > res_tight.f1_hz.std
    assert res_wide.peak_stress_mpa.std > res_tight.peak_stress_mpa.std


def test_propagate_reproducibility(quantifier: UncertaintyQuantifier) -> None:
    """Verifies that identical seeds yield identical distributions."""
    res1 = quantifier.propagate(65.75, 0.613, 10.42, 14.85, num_samples=2_000, random_seed=123)
    res2 = quantifier.propagate(65.75, 0.613, 10.42, 14.85, num_samples=2_000, random_seed=123)

    assert res1.f1_hz.mean == pytest.approx(res2.f1_hz.mean, rel=1e-6)
    assert res1.peak_stress_mpa.mean == pytest.approx(res2.peak_stress_mpa.mean, rel=1e-6)
    assert res1.margin_of_safety_ultimate.mean == pytest.approx(
        res2.margin_of_safety_ultimate.mean, rel=1e-6
    )


def test_uncertainty_result_serialization(quantifier: UncertaintyQuantifier) -> None:
    """Verifies that UncertaintyResult serializes cleanly to dict."""
    res = quantifier.propagate(65.75, 0.613, 10.42, 14.85, num_samples=500, random_seed=42)
    d = res.to_dict()

    assert isinstance(d, dict)
    assert "f1_hz" in d
    assert "prob_f1_compliant" in d
    assert "prob_ms_ultimate_positive" in d
    assert d["num_samples"] == 500
    assert "mean" in d["f1_hz"]


def test_run_full_uncertainty_pipeline_artifacts() -> None:
    """Verifies that run_full_uncertainty_pipeline executes and creates valid files."""
    from pathlib import Path
    from scripts.run_uncertainty_analysis import run_full_uncertainty_pipeline

    result = run_full_uncertainty_pipeline()
    assert result["candidates_evaluated"] == 3

    json_path = Path(result["json_path"])
    md_path = Path(result["markdown_path"])
    tex_path = Path(result["latex_path"])

    assert json_path.exists()
    assert md_path.exists()
    assert tex_path.exists()

    assert json_path.stat().st_size > 500
    assert md_path.stat().st_size > 500
    assert tex_path.stat().st_size > 300

    tex_content = tex_path.read_text(encoding="utf-8")
    assert "\\begin{table}" in tex_content
    assert "\\label{tab:incerteza_monte_carlo_voo}" in tex_content

