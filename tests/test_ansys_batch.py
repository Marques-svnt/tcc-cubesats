"""Unit tests for the Ansys batch runner module (src/analysis/ansys_batch_runner.py)."""

import csv
from pathlib import Path
import pytest

from src.analysis.ansys_batch_runner import (
    AnsysBatchRunner,
    FEASimulationResult,
    generate_apdl_modal_script,
    generate_apdl_psd_script,
)


def test_generate_apdl_modal_script(tmp_path: Path) -> None:
    """Verifies synthesis and syntax of the APDL modal analysis script."""
    sample = {
        "theta_deg": 65.0,
        "thickness_t": 0.8,
        "length_l": 6.0,
        "height_h": 9.0,
    }
    script_path = tmp_path / "modal_analysis.mac"
    out_path = generate_apdl_modal_script(sample=sample, output_script_path=script_path, num_modes=10)

    assert out_path.is_file()
    content = out_path.read_text(encoding="utf-8")
    assert "SOLID187" in content
    assert "LANB,10" in content
    assert "68.0E9" in content
    assert "2680.0" in content
    assert "THETA = 65.0000" in content


def test_generate_apdl_psd_script(tmp_path: Path) -> None:
    """Verifies synthesis of the APDL random vibration PSD script."""
    modal_db = tmp_path / "cubesat_modal.rst"
    modal_db.touch()
    script_path = tmp_path / "random_psd.mac"
    out_path = generate_apdl_psd_script(modal_db_path=modal_db, output_script_path=script_path, damping_ratio=0.02)

    assert out_path.is_file()
    content = out_path.read_text(encoding="utf-8")
    assert "ANTYPE,SPECTR" in content
    assert "SPOPT,PSD" in content
    assert "0.080" in content
    assert "14.1" in content or "0.013" in content
    assert "DMPRAT, 0.0200" in content


def test_ansys_batch_runner_single_simulation() -> None:
    """Verifies that a candidate is evaluated with physical modal ordering and margins."""
    runner = AnsysBatchRunner(allow_fallback=True)
    sample = {
        "theta_deg": 62.0,
        "thickness_t": 0.8,
        "length_l": 6.0,
        "height_h": 9.0,
    }
    res: FEASimulationResult = runner.simulate_candidate(sample=sample, sample_id=1)

    assert res.sample_id == 1
    assert res.first_natural_freq_hz >= 100.0
    assert res.second_natural_freq_hz > res.first_natural_freq_hz
    assert res.third_natural_freq_hz > res.second_natural_freq_hz
    assert len(res.modal_frequencies_hz) == 10
    assert res.peak_3sigma_stress_mpa > 0.0
    assert res.payload_grms > 0.0
    assert res.transmissibility_ratio > 0.0
    assert res.margin_of_safety_yield > 0.0
    assert res.fatigue_damage_steinberg >= 0.0

    # Serialization check
    res_dict = res.to_dict()
    assert "modal_frequencies_str" in res_dict
    assert "modal_frequencies_hz" not in res_dict


def test_ansys_batch_runner_small_csv_batch(tmp_path: Path) -> None:
    """Verifies batch execution from CSV input to output dataset."""
    in_csv = tmp_path / "input_test.csv"
    out_csv = tmp_path / "output_test.csv"

    fieldnames = ["theta_deg", "thickness_t", "length_l", "height_h"]
    rows = [
        {"theta_deg": 60.0, "thickness_t": 0.8, "length_l": 6.0, "height_h": 9.0},
        {"theta_deg": 70.0, "thickness_t": 1.0, "length_l": 5.0, "height_h": 8.0},
    ]
    with open(in_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    runner = AnsysBatchRunner(allow_fallback=True)
    results = runner.run_batch_from_csv(input_csv_path=in_csv, output_csv_path=out_csv)

    assert len(results) == 2
    assert out_csv.is_file()

    metrics = runner.compute_dataset_metrics(results)
    assert metrics["num_total_runs"] == 2
    assert metrics["f1_min_hz"] > 0.0
