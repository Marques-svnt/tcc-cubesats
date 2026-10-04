"""Unit tests for the DoE sampler module (src/neural/doe_sampler.py)."""

import csv
from pathlib import Path
import pytest

from src.neural.doe_sampler import (
    compute_doe_statistics,
    export_doe_dataset,
    generate_latin_hypercube_samples,
)


def test_lhs_sampler_sample_count_and_keys() -> None:
    """Verifies that LHS generates the requested number of points with all keys."""
    n_samples = 30
    samples = generate_latin_hypercube_samples(num_samples=n_samples, random_seed=42)

    assert len(samples) == n_samples
    expected_keys = {
        "theta_deg",
        "thickness_t",
        "length_l",
        "height_h",
        "relative_density",
        "is_dfam_valid",
        "poisson_ratio",
        "e_effective_gpa",
        "sigma_y_effective_mpa",
        "fn_estimated_hz",
        "peak_3sigma_stress_mpa",
        "margin_of_safety",
        "fatigue_damage_steinberg",
        "is_nasa_gevs_compliant",
    }
    for sample in samples:
        assert expected_keys.issubset(sample.keys())
        assert 55.0 <= sample["theta_deg"] <= 80.0
        assert 0.50 <= sample["thickness_t"] <= 1.80
        assert sample["relative_density"] > 0.0
        assert sample["poisson_ratio"] < 0.0  # Must be auxetic


def test_lhs_sampler_reproducibility() -> None:
    """Verifies that identical random seeds produce identical sample points."""
    samples_1 = generate_latin_hypercube_samples(num_samples=10, random_seed=99)
    samples_2 = generate_latin_hypercube_samples(num_samples=10, random_seed=99)

    for s1, s2 in zip(samples_1, samples_2):
        assert s1["theta_deg"] == pytest.approx(s2["theta_deg"])
        assert s1["thickness_t"] == pytest.approx(s2["thickness_t"])
        assert s1["relative_density"] == pytest.approx(s2["relative_density"])
        assert s1["fn_estimated_hz"] == pytest.approx(s2["fn_estimated_hz"])


def test_export_doe_dataset(tmp_path: Path) -> None:
    """Verifies CSV dataset export and file structure."""
    samples = generate_latin_hypercube_samples(num_samples=15, random_seed=42)
    output_file = tmp_path / "test_samples.csv"

    exported_path = export_doe_dataset(samples=samples, output_filepath=output_file)
    assert exported_path.is_file()

    with open(exported_path, mode="r", encoding="utf-8") as f:
        reader = list(csv.DictReader(f))
        assert len(reader) == 15
        assert "theta_deg" in reader[0]
        assert "fn_estimated_hz" in reader[0]


def test_compute_doe_statistics() -> None:
    """Verifies statistical metric aggregation for the DoE dataset."""
    samples = generate_latin_hypercube_samples(num_samples=50, random_seed=42)
    stats = compute_doe_statistics(samples)

    assert stats["num_total_samples"] == 50
    assert 0.0 <= stats["dfam_valid_percentage"] <= 100.0
    assert 0.0 <= stats["gevs_compliant_percentage"] <= 100.0
    assert stats["relative_density_min"] < stats["relative_density_max"]
    assert stats["fn_estimated_min_hz"] > 0.0
