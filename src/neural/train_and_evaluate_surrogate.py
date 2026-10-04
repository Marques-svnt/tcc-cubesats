"""Pipeline to train, evaluate, and benchmark the Physics-Guided ResNet surrogate model.

Loads the high-fidelity CAE dataset generated in Sprint 2, trains the surrogate
with PhysicsGuidedLoss, generates parity validation plots, and persists model weights.
"""

import csv
import logging
import math
from pathlib import Path
import time
from typing import Dict, List, Tuple
import matplotlib.pyplot as plt
import numpy as np

from src.neural.surrogate_model import (
    CubeSatSurrogateResNet,
    SurrogateDatasetScaler,
    compute_regression_metrics,
    fit_scaler_from_data,
    train_surrogate_model,
)

logger = logging.getLogger(__name__)


def load_fea_dataset(dataset_path: str | Path) -> Tuple[np.ndarray, np.ndarray, List[str], List[str]]:
    """Loads input features and dynamic targets from the FEA CSV dataset.

    Args:
        dataset_path: Path to cubesat_fea_doe_dataset.csv.

    Returns:
        Tuple of (X_matrix, Y_matrix, feature_names, target_names).
    """
    path = Path(dataset_path)
    if not path.exists():
        raise FileNotFoundError(f"Dataset not found at {path}")

    feature_names = ["theta_deg", "thickness_t", "length_l", "height_h", "relative_density"]
    target_names = ["first_natural_freq_hz", "peak_3sigma_stress_mpa", "payload_grms", "transmissibility_ratio"]

    x_list, y_list = [], []
    with open(path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            x_vals = [float(row[k]) for k in feature_names]
            y_vals = [float(row[k]) for k in target_names]
            x_list.append(x_vals)
            y_list.append(y_vals)

    return np.array(x_list, dtype=np.float32), np.array(y_list, dtype=np.float32), feature_names, target_names


def plot_parity_curves(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    target_names: List[str],
    output_image_path: str | Path,
) -> Path:
    """Generates a 4-panel publication-grade parity plot (True FEA vs. Surrogate Prediction).

    Args:
        y_true: True test targets matrix.
        y_pred: Predicted test targets matrix.
        target_names: Target variable names.
        output_image_path: Path to save the PNG image.

    Returns:
        Path of the saved image file.
    """
    target_path = Path(output_image_path)
    target_path.parent.mkdir(parents=True, exist_ok=True)

    fig, axes = plt.subplots(2, 2, figsize=(10, 9), dpi=300)
    axes = axes.flatten()

    titles = [
        r"Fundamental Frequency $f_1$ (Hz)",
        r"Peak $3\sigma$ Stress $\sigma_{\mathrm{peak}}$ (MPa)",
        r"Payload Acceleration $G_{\mathrm{rms}}$ (g)",
        r"Transmissibility Ratio $T$",
    ]

    for idx, ax in enumerate(axes):
        y_t = y_true[:, idx]
        y_p = y_pred[:, idx]

        # Compute individual R^2
        ss_res = np.sum((y_t - y_p) ** 2)
        ss_tot = np.sum((y_t - np.mean(y_t)) ** 2)
        r2 = 1.0 - (ss_res / max(ss_tot, 1e-8))

        ax.scatter(y_t, y_p, color="#1f77b4", edgecolors="#0b3d62", alpha=0.75, s=40, label="Test Points")

        min_val = min(np.min(y_t), np.min(y_p))
        max_val = max(np.max(y_t), np.max(y_p))
        margin = 0.05 * (max_val - min_val)
        line_vals = np.linspace(min_val - margin, max_val + margin, 100)

        # 45-degree identity line
        ax.plot(line_vals, line_vals, "r--", linewidth=1.5, label="Ideal Parity (1:1)")
        ax.set_title(f"{titles[idx]}\n($R^2 = {r2:.4f}$)", fontsize=11, fontweight="bold")
        ax.set_xlabel("True High-Fidelity FEA (Ansys)", fontsize=10)
        ax.set_ylabel("Physics-Guided Surrogate Prediction", fontsize=10)
        ax.grid(True, linestyle=":", alpha=0.6)
        ax.legend(loc="upper left", fontsize=8)

    plt.tight_layout()
    plt.savefig(target_path, bbox_inches="tight")
    plt.close()

    logger.info("Saved 4-panel parity plot to %s", target_path)
    return target_path


def benchmark_inference_latency(
    model: CubeSatSurrogateResNet,
    scaler: SurrogateDatasetScaler,
    num_evaluations: int = 2000,
) -> float:
    """Measures single-candidate evaluation time in milliseconds.

    Args:
        model: Trained surrogate model.
        scaler: Fitted scaler.
        num_evaluations: Number of evaluation calls for averaging.

    Returns:
        Average evaluation time per candidate in milliseconds.
    """
    import torch

    test_input = np.array([[65.0, 0.8, 6.0, 9.0, 0.25]], dtype=np.float32)
    test_norm = torch.from_numpy(scaler.transform_x(test_input)).float()

    model.eval()
    with torch.no_grad():
        # Warmup
        for _ in range(50):
            _ = model(test_norm)

        start_time = time.perf_counter()
        for _ in range(num_evaluations):
            _ = model(test_norm)
        end_time = time.perf_counter()

    avg_ms = ((end_time - start_time) / num_evaluations) * 1000.0
    logger.info("Inference Latency Benchmark: %.4f ms per evaluation (over %d runs)", avg_ms, num_evaluations)
    return avg_ms


def run_pipeline() -> Dict[str, Any]:
    """Executes the full surrogate training, evaluation, and persistence pipeline."""
    import torch

    base_dir = Path(__file__).resolve().parent.parent.parent
    data_csv = base_dir / "data" / "cubesat_fea_doe_dataset.csv"
    models_dir = base_dir / "models"
    models_dir.mkdir(parents=True, exist_ok=True)
    reports_dir = base_dir / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)

    x_raw, y_raw, feat_names, targ_names = load_fea_dataset(data_csv)

    model, scaler, history = train_surrogate_model(
        x_data=x_raw,
        y_data=y_raw,
        epochs=350,
        batch_size=32,
        lr=2e-3,
        train_ratio=0.80,
        random_seed=42,
    )

    # Persist model weights and scaler
    model_path = models_dir / "physics_guided_surrogate.pt"
    scaler_path = models_dir / "surrogate_scaler.json"
    torch.save(model.state_dict(), model_path)
    scaler.save_json(scaler_path)

    # Generate Parity Plots on Test Partition
    n_samples = len(x_raw)
    n_train = int(n_samples * 0.8)
    np.random.seed(42)
    test_indices = np.random.permutation(n_samples)[n_train:]
    x_test_raw = x_raw[test_indices]
    y_test_raw = y_raw[test_indices]

    x_test_norm = torch.from_numpy(scaler.transform_x(x_test_raw)).float()
    model.eval()
    with torch.no_grad():
        y_test_pred_norm = model(x_test_norm).numpy()
    y_test_pred = scaler.inverse_transform_y(y_test_pred_norm)

    parity_plot_path = reports_dir / "parity_plots.png"
    plot_parity_curves(y_true=y_test_raw, y_pred=y_test_pred, target_names=targ_names, output_image_path=parity_plot_path)

    latency_ms = benchmark_inference_latency(model, scaler)

    summary = {
        "model_path": str(model_path),
        "scaler_path": str(scaler_path),
        "parity_plot_path": str(parity_plot_path),
        "latency_ms": latency_ms,
        "metrics": history["final_test_metrics"],
    }
    return summary


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    run_pipeline()
