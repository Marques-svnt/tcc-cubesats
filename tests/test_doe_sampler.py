"""Unit tests for the DoE sampler module (src/neural/doe_sampler.py)."""

import pytest
from src.neural.doe_sampler import generate_latin_hypercube_samples


def test_lhs_sampler_sample_count_and_keys() -> None:
    """Verifies that LHS generates the requested number of points with all keys."""
    n_samples = 30
    samples = generate_latin_hypercube_samples(num_samples=n_samples, random_seed=42)

    assert len(samples) == n_samples
    expected_keys = {"theta_deg", "thickness_t", "length_l", "height_h", "relative_density", "is_dfam_valid"}
    for sample in samples:
        assert expected_keys.issubset(sample.keys())
        assert 55.0 <= sample["theta_deg"] <= 80.0
        assert 0.50 <= sample["thickness_t"] <= 1.80
        assert sample["relative_density"] > 0.0


def test_lhs_sampler_reproducibility() -> None:
    """Verifies that identical random seeds produce identical sample points."""
    samples_1 = generate_latin_hypercube_samples(num_samples=10, random_seed=99)
    samples_2 = generate_latin_hypercube_samples(num_samples=10, random_seed=99)

    for s1, s2 in zip(samples_1, samples_2):
        assert s1["theta_deg"] == pytest.approx(s2["theta_deg"])
        assert s1["thickness_t"] == pytest.approx(s2["thickness_t"])
