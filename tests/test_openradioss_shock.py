"""Unit tests for OpenRadioss Explicit Dynamics Deck Generation and SRS Calculation.

Verifies 0000.rad and 0001.rad deck formatting, ejection separation velocity,
mechanical stop impact acceleration, and NASA GSFC-STD-7000A SRS (Q=10).
"""

from pathlib import Path
import pytest

from src.analysis.openradioss_shock_runner import OpenRadiossShockRunner


def test_openradioss_deck_generation(tmp_path: Path) -> None:
    """Verifies generation of starter and engine OpenRadioss decks."""
    runner = OpenRadiossShockRunner(output_dir=tmp_path)
    starter, engine = runner.generate_radioss_decks(
        output_prefix="TEST_EJECTION",
        stroke_length_m=0.100,
        spring_k_n_m=556.0,
    )

    assert starter.exists()
    assert engine.exists()

    starter_txt = starter.read_text(encoding="utf-8")
    assert "/BEGIN" in starter_txt
    assert "/MAT/LAW2" in starter_txt
    assert "/PROP/TYPE4" in starter_txt
    assert "/INTER/TYPE7" in starter_txt

    engine_txt = engine.read_text(encoding="utf-8")
    assert "/RUN/TEST_EJECTION/1" in engine_txt
    assert "/DT/NODA/CST" in engine_txt
    assert "/ANIM/DT" in engine_txt


def test_p_pod_separation_shock_and_srs() -> None:
    """Verifies transient shock and SRS response spectrum calculation."""
    runner = OpenRadiossShockRunner(output_dir="data/test_radioss")

    res = runner.solve_separation_shock(
        cubesat_mass_kg=1.330,
        spring_preload_n=55.60,
        spring_k_n_m=556.0,
        stroke_length_m=0.100,
        srs_limit_g=80.0,
    )

    # Separation velocity ~ 1.5 - 2.5 m/s typical for P-POD
    assert 1.0 <= res.ejection_velocity_m_s <= 3.0
    assert res.peak_shock_acceleration_g > 10.0
    assert res.shock_duration_ms > 0.1
    assert len(res.srs_frequencies_hz) > 30
    assert len(res.srs_peak_accelerations_g) == len(res.srs_frequencies_hz)
    assert res.payload_max_srs_g < res.srs_limit_threshold_g
    assert res.is_shock_qualified is True
