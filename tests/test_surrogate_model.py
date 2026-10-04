"""Unit tests for the Physics-Guided ResNet surrogate model (src/neural/surrogate_model.py)."""

import json
from pathlib import Path
import pytest
import numpy as np

import torch
from src.neural.surrogate_model import (
    CubeSatSurrogateResNet,
    PhysicsGuidedLoss,
    SurrogateDatasetScaler,
    compute_regression_metrics,
    fit_scaler_from_data,
)


def test_surrogate_resnet_architecture_and_forward() -> None:
    """Verifies tensor shapes and forward pass through residual layers."""
    model = CubeSatSurrogateResNet(input_dim=5, output_dim=4, hidden_dim=64, num_blocks=2)
    batch_size = 12
    x = torch.randn(batch_size, 5)

    y = model(x)
    assert y.shape == (batch_size, 4)
    assert not torch.isnan(y).any()
    assert not torch.isinf(y).any()


def test_physics_guided_loss_components() -> None:
    """Verifies that physics-guided loss computes valid gradients and breakdown."""
    criterion = PhysicsGuidedLoss(lambda_phys=0.2, lambda_mono=0.1)

    batch_size = 16
    x_inputs = torch.randn(batch_size, 5)
    y_true = torch.randn(batch_size, 4)
    y_pred = torch.randn(batch_size, 4, requires_grad=True)

    loss, breakdown = criterion(y_pred, y_true, x_inputs)

    assert loss.item() > 0.0
    assert "loss_total" in breakdown
    assert "loss_mse" in breakdown
    assert "loss_positivity" in breakdown
    assert "loss_mono" in breakdown

    # Verify backpropagation
    loss.backward()
    assert y_pred.grad is not None
    assert not torch.isnan(y_pred.grad).any()


def test_surrogate_dataset_scaler_roundtrip(tmp_path: Path) -> None:
    """Verifies Z-score transformation, inverse transformation, and JSON persistence."""
    np.random.seed(42)
    x = np.random.uniform(10.0, 50.0, size=(40, 5)).astype(np.float32)
    y = np.random.uniform(100.0, 1000.0, size=(40, 4)).astype(np.float32)

    scaler = fit_scaler_from_data(x, y)

    # Transform and inverse transform
    x_norm = scaler.transform_x(x)
    x_recovered = scaler.inverse_transform_x(x_norm)
    assert np.allclose(x, x_recovered, atol=1e-5)

    y_norm = scaler.transform_y(y)
    y_recovered = scaler.inverse_transform_y(y_norm)
    assert np.allclose(y, y_recovered, atol=1e-5)

    # Save and load JSON
    json_path = tmp_path / "scaler.json"
    scaler.save_json(json_path)
    loaded_scaler = SurrogateDatasetScaler.load_json(json_path)

    assert np.allclose(scaler.x_mean, loaded_scaler.x_mean)
    assert np.allclose(scaler.y_std, loaded_scaler.y_std)


def test_compute_regression_metrics() -> None:
    """Verifies computation of R^2 and NRMSE metrics."""
    y_true = np.array([[100.0, 50.0], [200.0, 70.0], [300.0, 90.0]], dtype=np.float32)
    # Perfect predictions
    metrics_perfect = compute_regression_metrics(y_true, y_true)
    assert pytest.approx(metrics_perfect["r2_mean"], rel=1e-3) == 1.0
    assert pytest.approx(metrics_perfect["nrmse_mean_percent"], rel=1e-3) == 0.0

    # Perturbed predictions
    y_pred = y_true + np.array([[2.0, -1.0], [-1.0, 2.0], [1.0, -1.0]], dtype=np.float32)
    metrics_perturbed = compute_regression_metrics(y_true, y_pred)
    assert 0.95 <= metrics_perturbed["r2_mean"] < 1.0
    assert metrics_perturbed["nrmse_mean_percent"] < 5.0


def test_surrogate_single_inference_latency() -> None:
    """Verifies that single evaluation runs with low latency (< 5 ms)."""
    import time
    model = CubeSatSurrogateResNet(input_dim=5, output_dim=4, hidden_dim=64, num_blocks=2)
    model.eval()

    sample = torch.randn(1, 5)
    with torch.no_grad():
        # Warmup
        _ = model(sample)

        t0 = time.perf_counter()
        for _ in range(200):
            _ = model(sample)
        t1 = time.perf_counter()

    avg_ms = ((t1 - t0) / 200) * 1000.0
    assert avg_ms < 5.0, f"Inference took {avg_ms:.3f} ms, expected < 5.0 ms"
