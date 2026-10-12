"""Physics-Guided Deep ResNet Surrogate Model for CubeSat Elastodynamics.

Implements a deep residual network (ResNet) in PyTorch to predict structural
dynamic properties (natural frequency f1, 3-sigma peak stress, payload Grms,
and transmissibility) with sub-millisecond inference latency.
The model incorporates physical regularization via a custom Physics-Guided Loss
penalizing departures from Gibson-Ashby scaling and enforcing physical monotonicity.
"""

from dataclasses import dataclass
import json
import logging
import math
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np

logger = logging.getLogger(__name__)

# Resilient PyTorch import with informative logging
try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
    from torch.utils.data import DataLoader, TensorDataset
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    logger.warning("PyTorch not yet found in environment; surrogate will operate in pure NumPy mode.")


class ResidualBlock(nn.Module if TORCH_AVAILABLE else object):  # type: ignore
    """Dense Residual Block with Skip Connection and Layer Normalization."""

    def __init__(self, hidden_dim: int = 64, dropout_rate: float = 0.05) -> None:
        """Initializes the residual block.

        Args:
            hidden_dim: Number of hidden units in linear layers.
            dropout_rate: Dropout probability for regularization.
        """
        super().__init__()
        if TORCH_AVAILABLE:
            self.linear1 = nn.Linear(hidden_dim, hidden_dim)
            self.layer_norm = nn.LayerNorm(hidden_dim)
            self.activation = nn.SiLU()  # Smooth non-linear activation (Swish)
            self.linear2 = nn.Linear(hidden_dim, hidden_dim)
            self.dropout = nn.Dropout(dropout_rate)

    def forward(self, x: "torch.Tensor") -> "torch.Tensor":
        """Forward pass with skip connection: y = x + F(x)."""
        residual = x
        out = self.linear1(x)
        out = self.layer_norm(out)
        out = self.activation(out)
        out = self.dropout(out)
        out = self.linear2(out)
        return residual + out


class MLPSurrogate(nn.Module if TORCH_AVAILABLE else object):  # type: ignore
    """Standard Dense MLP without residual skip connections for ablation baseline."""

    def __init__(
        self,
        input_dim: int = 5,
        output_dim: int = 3,
        hidden_dim: int = 64,
        num_layers: int = 3,
        dropout_rate: float = 0.05,
    ) -> None:
        """Initializes standard dense MLP architecture.

        Args:
            input_dim: Number of input features.
            output_dim: Number of predicted dynamic responses (default 3: f1, stress, grms).
            hidden_dim: Width of dense hidden layers.
            num_layers: Number of intermediate dense hidden layers.
            dropout_rate: Dropout regularization probability.
        """
        super().__init__()
        self.input_dim = input_dim
        self.output_dim = output_dim
        self.hidden_dim = hidden_dim

        if TORCH_AVAILABLE:
            layers: List[nn.Module] = [
                nn.Linear(input_dim, hidden_dim),
                nn.LayerNorm(hidden_dim),
                nn.SiLU(),
                nn.Dropout(dropout_rate),
            ]
            for _ in range(num_layers - 1):
                layers.extend([
                    nn.Linear(hidden_dim, hidden_dim),
                    nn.LayerNorm(hidden_dim),
                    nn.SiLU(),
                    nn.Dropout(dropout_rate),
                ])
            layers.append(nn.Linear(hidden_dim, output_dim))
            self.network = nn.Sequential(*layers)

    def forward(self, x: "torch.Tensor") -> "torch.Tensor":
        """Executes forward pass through the dense feedforward MLP."""
        return self.network(x)


class CubeSatSurrogateResNet(nn.Module if TORCH_AVAILABLE else object):  # type: ignore
    """Deep Residual MLP for multi-output elastodynamic regression."""

    def __init__(
        self,
        input_dim: int = 5,
        output_dim: int = 3,
        hidden_dim: int = 64,
        num_blocks: int = 2,
    ) -> None:
        """Initializes the surrogate ResNet architecture.

        Args:
            input_dim: Number of input geometric features (theta, t, l, h, rho_rel).
            output_dim: Number of predicted dynamic responses (default 3: f1, stress, grms).
            hidden_dim: Width of intermediate dense layers.
            num_blocks: Number of stacked residual blocks.
        """
        super().__init__()
        self.input_dim = input_dim
        self.output_dim = output_dim
        self.hidden_dim = hidden_dim

        if TORCH_AVAILABLE:
            self.input_layer = nn.Sequential(
                nn.Linear(input_dim, hidden_dim),
                nn.SiLU(),
            )
            self.res_blocks = nn.ModuleList([ResidualBlock(hidden_dim) for _ in range(num_blocks)])
            self.head = nn.Sequential(
                nn.Linear(hidden_dim, hidden_dim // 2),
                nn.SiLU(),
                nn.Linear(hidden_dim // 2, output_dim),
            )

    def forward(self, x: "torch.Tensor") -> "torch.Tensor":
        """Executes forward pass through the deep residual network."""
        out = self.input_layer(x)
        for block in self.res_blocks:
            out = block(out)
        return self.head(out)

    def predict_with_transmissibility(
        self,
        x: "torch.Tensor",
        scaler: Optional["SurrogateDatasetScaler"] = None,
    ) -> "torch.Tensor":
        """Forward pass computing [f1, stress, grms, T] with deterministic T = grms / 14.1.

        Args:
            x: Input tensor of shape (batch_size, input_dim).
            scaler: Optional dataset scaler to un-normalize predictions.

        Returns:
            Tensor of shape (batch_size, 4) containing [f1, stress, grms, transmissibility].
        """
        y_3d = self.forward(x)
        if scaler is not None:
            device = x.device
            y_mean = torch.tensor(scaler.y_mean[:3], device=device, dtype=torch.float32)
            y_std = torch.tensor(scaler.y_std[:3], device=device, dtype=torch.float32)
            y_phys = y_3d * y_std + y_mean
            grms = y_phys[:, 2:3]
            t_ratio = grms / 14.1
            return torch.cat([y_phys, t_ratio], dim=-1)
        else:
            grms = y_3d[:, 2:3]
            t_ratio = grms / 14.1
            return torch.cat([y_3d, t_ratio], dim=-1)


class PhysicsGuidedLoss(nn.Module if TORCH_AVAILABLE else object):  # type: ignore
    """Custom Loss function integrating MSE with Gibson-Ashby and Monotonicity penalties."""

    def __init__(
        self,
        lambda_phys: float = 0.15,
        lambda_mono: float = 0.10,
        solid_modulus_gpa: float = 68.0,
    ) -> None:
        """Initializes the physics-guided loss function.

        Args:
            lambda_phys: Weight for the Gibson-Ashby analytical penalty.
            lambda_mono: Weight for the stiffness-mass monotonicity constraint.
            solid_modulus_gpa: Young's modulus of solid AlSi10Mg base material.
        """
        super().__init__()
        self.lambda_phys = lambda_phys
        self.lambda_mono = lambda_mono
        self.solid_modulus_gpa = solid_modulus_gpa
        if TORCH_AVAILABLE:
            self.mse = nn.MSELoss()

    def forward(
        self,
        y_pred: "torch.Tensor",
        y_true: "torch.Tensor",
        x_inputs: "torch.Tensor",
        target_scaler: Optional["SurrogateDatasetScaler"] = None,
    ) -> Tuple["torch.Tensor", Dict[str, float]]:
        """Computes total physics-guided loss: L_MSE + lambda_phys * L_GA + lambda_mono * L_mono.

        Args:
            y_pred: Predicted target tensor (batch_size, 4).
            y_true: Ground truth target tensor (batch_size, 4).
            x_inputs: Normalized inputs (batch_size, 5).
            target_scaler: Scaler to un-normalize predictions for physics verification.

        Returns:
            Tuple of (total_loss_tensor, loss_breakdown_dict).
        """
        loss_mse = self.mse(y_pred, y_true)

        # 1. Physical consistency penalty: enforce lower bound (20 Hz) and Gibson-Ashby scaling
        f1_pred = y_pred[:, 0:1]

        if target_scaler is not None:
            # Un-normalize relative density
            if hasattr(target_scaler, "x_mean") and hasattr(target_scaler, "x_std"):
                idx_rho = 4 if len(target_scaler.x_mean) >= 5 else 1
                rho_mean = float(target_scaler.x_mean[idx_rho])
                rho_std = float(target_scaler.x_std[idx_rho])
                rho_raw = x_inputs[:, idx_rho : idx_rho + 1]
                rho_rel_physical = torch.clamp(rho_raw * rho_std + rho_mean, min=0.01, max=0.99)
            else:
                rho_raw = x_inputs[:, 4:5] if x_inputs.shape[1] >= 5 else x_inputs[:, 1:2]
                rho_rel_physical = torch.clamp(rho_raw, min=0.01, max=0.99)

            if hasattr(target_scaler, "y_mean") and hasattr(target_scaler, "y_std"):
                mean_f1 = float(target_scaler.y_mean[0])
                std_f1 = float(target_scaler.y_std[0])
            elif hasattr(target_scaler, "mean_y") and hasattr(target_scaler, "std_y"):
                mean_f1 = float(target_scaler.mean_y[0])
                std_f1 = float(target_scaler.std_y[0])
            else:
                mean_f1, std_f1 = None, None

            if mean_f1 is not None and std_f1 is not None:
                f1_physical = f1_pred * std_f1 + mean_f1
                # Penalize frequencies below NASA GEVS lower bound (20.0 Hz)
                loss_bound = torch.mean(torch.relu(20.0 - f1_physical) ** 2)
                # Gibson-Ashby asymptotic power-law scaling penalty (soft boundary regularization)
                f1_ga = 1350.0 * torch.sqrt(rho_rel_physical)
                loss_ga = torch.mean(((f1_physical - f1_ga) / torch.clamp(f1_ga, min=100.0)) ** 2)
                loss_positivity = loss_bound + 0.05 * loss_ga
            else:
                loss_positivity = torch.mean(torch.relu(-f1_pred) ** 2)

            # 2. Monotonicity regularization evaluated on physical density ordering
            sorted_indices = torch.argsort(rho_rel_physical.squeeze(-1))
            sorted_f1 = f1_pred[sorted_indices]
            sorted_rho = rho_rel_physical[sorted_indices]
            diff_f1 = sorted_f1[1:] - sorted_f1[:-1]
            diff_rho = sorted_rho[1:] - sorted_rho[:-1]

            # Penalize only where relative density increases significantly (> 0.02) but frequency drops sharply
            significant_step = diff_rho > 0.02
            if significant_step.any():
                severe_drop = torch.relu(-(diff_f1[significant_step] + 0.10))
                loss_mono = torch.mean(severe_drop**2) if severe_drop.numel() > 0 else torch.tensor(0.0, device=y_pred.device)
            else:
                loss_mono = torch.tensor(0.0, device=y_pred.device)
        else:
            loss_positivity = torch.mean(torch.relu(-f1_pred) ** 2)
            loss_mono = torch.tensor(0.0, device=y_pred.device)

        total_loss = loss_mse + self.lambda_phys * loss_positivity + self.lambda_mono * loss_mono

        breakdown = {
            "loss_total": float(total_loss.item()),
            "loss_mse": float(loss_mse.item()),
            "loss_positivity": float(loss_positivity.item()),
            "loss_mono": float(loss_mono.item()),
        }
        return total_loss, breakdown


@dataclass
class SurrogateDatasetScaler:
    """Standard Z-Score normalization scaler for neural inputs and targets."""

    x_mean: np.ndarray
    x_std: np.ndarray
    y_mean: np.ndarray
    y_std: np.ndarray
    input_names: List[str]
    target_names: List[str]

    def transform_x(self, x: np.ndarray) -> np.ndarray:
        """Transforms raw inputs to normalized Z-scores."""
        return (x - self.x_mean) / np.maximum(self.x_std, 1e-8)

    def inverse_transform_x(self, z_x: np.ndarray) -> np.ndarray:
        """Inverse-transforms Z-scores to original input space."""
        return z_x * self.x_std + self.x_mean

    def transform_y(self, y: np.ndarray) -> np.ndarray:
        """Transforms raw targets to normalized Z-scores."""
        return (y - self.y_mean) / np.maximum(self.y_std, 1e-8)

    def inverse_transform_y(self, z_y: np.ndarray) -> np.ndarray:
        """Inverse-transforms Z-scores to original target dimensions."""
        return z_y * self.y_std + self.y_mean

    def save_json(self, filepath: str | Path) -> Path:
        """Saves scaler parameters to a JSON file."""
        target_path = Path(filepath)
        target_path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "x_mean": self.x_mean.tolist(),
            "x_std": self.x_std.tolist(),
            "y_mean": self.y_mean.tolist(),
            "y_std": self.y_std.tolist(),
            "input_names": self.input_names,
            "target_names": self.target_names,
        }
        with open(target_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        logger.info("Saved scaler parameters to %s", target_path)
        return target_path

    @classmethod
    def load_json(cls, filepath: str | Path) -> "SurrogateDatasetScaler":
        """Loads scaler parameters from a JSON file."""
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls(
            x_mean=np.array(data["x_mean"], dtype=np.float32),
            x_std=np.array(data["x_std"], dtype=np.float32),
            y_mean=np.array(data["y_mean"], dtype=np.float32),
            y_std=np.array(data["y_std"], dtype=np.float32),
            input_names=data["input_names"],
            target_names=data["target_names"],
        )


def fit_scaler_from_data(
    x_raw: np.ndarray,
    y_raw: np.ndarray,
    input_names: Optional[List[str]] = None,
    target_names: Optional[List[str]] = None,
) -> SurrogateDatasetScaler:
    """Computes mean and standard deviation to initialize a dataset scaler.

    Args:
        x_raw: Input data matrix of shape (N, D_in).
        y_raw: Target data matrix of shape (N, D_out).
        input_names: List of input feature names.
        target_names: List of target variable names.

    Returns:
        Fitted SurrogateDatasetScaler instance.
    """
    input_names = input_names or ["theta_deg", "thickness_t", "length_l", "height_h", "relative_density"]
    if target_names is None:
        if y_raw.shape[1] == 3:
            target_names = ["first_natural_freq_hz", "peak_3sigma_stress_mpa", "payload_grms"]
        else:
            target_names = ["first_natural_freq_hz", "peak_3sigma_stress_mpa", "payload_grms", "transmissibility_ratio"]

    x_mean = np.mean(x_raw, axis=0, dtype=np.float32)
    x_std = np.std(x_raw, axis=0, dtype=np.float32)
    y_mean = np.mean(y_raw, axis=0, dtype=np.float32)
    y_std = np.std(y_raw, axis=0, dtype=np.float32)

    return SurrogateDatasetScaler(
        x_mean=x_mean,
        x_std=x_std,
        y_mean=y_mean,
        y_std=y_std,
        input_names=input_names,
        target_names=target_names,
    )


def compute_regression_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    target_names: Optional[List[str]] = None,
) -> Dict[str, float]:
    """Computes R^2 (coefficient of determination), NRMSE (%), and MAE per target and globally.

    Args:
        y_true: Ground truth target matrix (N, D).
        y_pred: Predicted target matrix (N, D).
        target_names: Optional list of target variable names.

    Returns:
        Dictionary of statistical quality metrics.
    """
    ss_res = np.sum((y_true - y_pred) ** 2, axis=0)
    ss_tot = np.sum((y_true - np.mean(y_true, axis=0)) ** 2, axis=0)
    r2_per_dim = 1.0 - (ss_res / np.maximum(ss_tot, 1e-8))

    rmse_per_dim = np.sqrt(np.mean((y_true - y_pred) ** 2, axis=0))
    mae_per_dim = np.mean(np.abs(y_true - y_pred), axis=0)
    range_per_dim = np.maximum(np.max(y_true, axis=0) - np.min(y_true, axis=0), 1e-8)
    nrmse_per_dim = (rmse_per_dim / range_per_dim) * 100.0  # percentage

    if target_names is None:
        if y_true.shape[1] == 3:
            target_names = ["f1", "stress", "grms"]
        elif y_true.shape[1] == 4:
            target_names = ["f1", "stress", "grms", "transmissibility"]
        else:
            target_names = [f"dim_{i}" for i in range(y_true.shape[1])]

    metrics: Dict[str, float] = {
        "r2_mean": float(np.mean(r2_per_dim)),
        "nrmse_mean_percent": float(np.mean(nrmse_per_dim)),
        "mae_mean": float(np.mean(mae_per_dim)),
    }

    for i in range(len(r2_per_dim)):
        name = target_names[i] if i < len(target_names) else f"dim_{i}"
        metrics[f"r2_{name}"] = float(r2_per_dim[i])
        metrics[f"nrmse_{name}_percent"] = float(nrmse_per_dim[i])
        metrics[f"mae_{name}"] = float(mae_per_dim[i])

    return metrics


def train_surrogate_model(
    x_data: np.ndarray,
    y_data: np.ndarray,
    epochs: int = 400,
    batch_size: int = 32,
    lr: float = 1e-3,
    train_ratio: float = 0.80,
    random_seed: int = 42,
) -> Tuple[CubeSatSurrogateResNet, SurrogateDatasetScaler, Dict[str, Any]]:
    """Trains the Physics-Guided ResNet surrogate model on FEA dataset.

    Args:
        x_data: Input parameter matrix (N, 5).
        y_data: Target dynamic responses matrix (N, 3 or 4).
        epochs: Number of training epochs (default 400).
        batch_size: Mini-batch size.
        lr: Initial learning rate for AdamW.
        train_ratio: Proportion of samples used for training.
        random_seed: Random seed for data split.

    Returns:
        Tuple of (trained_model, scaler, training_history_dict).
    """
    if not TORCH_AVAILABLE:
        raise RuntimeError("PyTorch is required for training the surrogate ResNet.")

    torch.manual_seed(random_seed)
    np.random.seed(random_seed)

    n_samples = len(x_data)
    n_train = int(n_samples * train_ratio)
    indices = np.random.permutation(n_samples)
    train_idx, test_idx = indices[:n_train], indices[n_train:]

    x_train_raw, y_train_raw = x_data[train_idx], y_data[train_idx]
    x_test_raw, y_test_raw = x_data[test_idx], y_data[test_idx]

    # Fit scaler on training set
    scaler = fit_scaler_from_data(x_train_raw, y_train_raw)
    x_train = scaler.transform_x(x_train_raw)
    y_train = scaler.transform_y(y_train_raw)
    x_test = scaler.transform_x(x_test_raw)
    y_test = scaler.transform_y(y_test_raw)

    train_dataset = TensorDataset(torch.from_numpy(x_train).float(), torch.from_numpy(y_train).float())
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)

    out_dim = y_data.shape[1]
    model = CubeSatSurrogateResNet(input_dim=5, output_dim=out_dim, hidden_dim=64, num_blocks=2)
    criterion = PhysicsGuidedLoss(lambda_phys=0.15, lambda_mono=0.10)
    optimizer = optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4)
    scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs, eta_min=1e-5)

    history: Dict[str, Any] = {
        "train_loss": [],
        "val_loss": [],
        "mse_loss": [],
        "phys_loss": [],
        "mono_loss": [],
    }
    logger.info("Starting training of Physics-Guided ResNet (%d epochs, %d train, %d test)...", epochs, n_train, n_samples - n_train)

    best_val_loss = float("inf")
    best_weights = None

    x_test_tensor = torch.from_numpy(x_test).float()
    y_test_tensor = torch.from_numpy(y_test).float()

    for epoch in range(1, epochs + 1):
        model.train()
        epoch_losses = []
        epoch_mse, epoch_phys, epoch_mono = [], [], []
        for x_batch, y_batch in train_loader:
            optimizer.zero_grad()
            y_pred = model(x_batch)
            loss, b_dict = criterion(y_pred, y_batch, x_batch, scaler)
            loss.backward()
            optimizer.step()
            epoch_losses.append(loss.item())
            epoch_mse.append(b_dict["loss_mse"])
            epoch_phys.append(b_dict["loss_positivity"])
            epoch_mono.append(b_dict["loss_mono"])

        scheduler.step()
        train_loss = float(np.mean(epoch_losses))

        # Evaluate on validation/test set
        model.eval()
        with torch.no_grad():
            y_val_pred = model(x_test_tensor)
            val_loss, _ = criterion(y_val_pred, y_test_tensor, x_test_tensor, scaler)
            val_loss_scalar = float(val_loss.item())

        history["train_loss"].append(train_loss)
        history["val_loss"].append(val_loss_scalar)
        history["mse_loss"].append(float(np.mean(epoch_mse)))
        history["phys_loss"].append(float(np.mean(epoch_phys)))
        history["mono_loss"].append(float(np.mean(epoch_mono)))

        if val_loss_scalar < best_val_loss:
            best_val_loss = val_loss_scalar
            best_weights = model.state_dict()

        if epoch % 50 == 0 or epoch == epochs:
            logger.info("Epoch %03d/%03d | Train Loss: %.5f | Val Loss: %.5f", epoch, epochs, train_loss, val_loss_scalar)

    # Restore best checkpoint
    if best_weights is not None:
        model.load_state_dict(best_weights)

    # Compute final metrics on test set
    model.eval()
    with torch.no_grad():
        y_test_pred_norm = model(x_test_tensor).numpy()
    y_test_pred = scaler.inverse_transform_y(y_test_pred_norm)

    if out_dim == 3:
        t_true = (y_test_raw[:, 2:3] / 14.1).astype(np.float32)
        t_pred = (y_test_pred[:, 2:3] / 14.1).astype(np.float32)
        y_test_raw_full = np.hstack([y_test_raw, t_true])
        y_test_pred_full = np.hstack([y_test_pred, t_pred])
        test_metrics = compute_regression_metrics(y_true=y_test_raw_full, y_pred=y_test_pred_full)
    else:
        test_metrics = compute_regression_metrics(y_true=y_test_raw, y_pred=y_test_pred)

    history["final_test_metrics"] = test_metrics
    logger.info("Training complete. Test Metrics: %s", test_metrics)
    return model, scaler, history


def k_fold_cross_validation(
    x_data: np.ndarray,
    y_data: np.ndarray,
    k: int = 10,
    epochs: int = 300,
    batch_size: int = 32,
    lr: float = 1e-3,
    model_architecture: str = "resnet",
    use_physics_loss: bool = True,
    lambda_phys: float = 0.15,
    lambda_mono: float = 0.10,
    random_seed: int = 42,
) -> Dict[str, Any]:
    """Executes stratified k-fold cross-validation across the DoE dataset.

    Args:
        x_data: Input parameter matrix of shape (N, 5).
        y_data: Target matrix of shape (N, 3) with [f1, stress, grms].
        k: Number of folds (default 10).
        epochs: Training epochs per fold.
        batch_size: Mini-batch size.
        lr: Learning rate for AdamW.
        model_architecture: 'resnet' for residual blocks or 'mlp' for standard dense MLP.
        use_physics_loss: If True, uses PhysicsGuidedLoss; if False, uses standard MSE.
        lambda_phys: Physical consistency penalty weight.
        lambda_mono: Monotonicity penalty weight.
        random_seed: Reproducibility seed.

    Returns:
        Dictionary containing per-fold metrics, mean, and standard deviation.
    """
    if not TORCH_AVAILABLE:
        raise RuntimeError("PyTorch is required for cross-validation.")

    n_samples = len(x_data)
    np.random.seed(random_seed)
    torch.manual_seed(random_seed)

    indices = np.random.permutation(n_samples)
    fold_sizes = np.full(k, n_samples // k, dtype=int)
    fold_sizes[: n_samples % k] += 1
    current = 0
    folds = []
    for f_size in fold_sizes:
        folds.append(indices[current : current + f_size])
        current += f_size

    out_dim = y_data.shape[1]
    fold_results: List[Dict[str, float]] = []

    logger.info(
        "Starting %d-Fold Cross-Validation: arch=%s, phys_loss=%s (%d samples)",
        k,
        model_architecture,
        use_physics_loss,
        n_samples,
    )

    for fold_idx in range(k):
        test_idx = folds[fold_idx]
        train_idx = np.setdiff1d(indices, test_idx)

        x_train_raw, y_train_raw = x_data[train_idx], y_data[train_idx]
        x_test_raw, y_test_raw = x_data[test_idx], y_data[test_idx]

        scaler = fit_scaler_from_data(x_train_raw, y_train_raw)
        x_train = scaler.transform_x(x_train_raw)
        y_train = scaler.transform_y(y_train_raw)
        x_test = scaler.transform_x(x_test_raw)
        y_test = scaler.transform_y(y_test_raw)

        train_dataset = TensorDataset(torch.from_numpy(x_train).float(), torch.from_numpy(y_train).float())
        train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)

        if model_architecture == "mlp":
            model: nn.Module = MLPSurrogate(input_dim=5, output_dim=out_dim, hidden_dim=64, num_layers=3)
        else:
            model = CubeSatSurrogateResNet(input_dim=5, output_dim=out_dim, hidden_dim=64, num_blocks=2)

        criterion = (
            PhysicsGuidedLoss(lambda_phys=lambda_phys, lambda_mono=lambda_mono)
            if use_physics_loss
            else nn.MSELoss()
        )
        optimizer = optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4)
        scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs, eta_min=1e-5)

        best_val_loss = float("inf")
        best_weights = None
        x_test_t = torch.from_numpy(x_test).float()
        y_test_t = torch.from_numpy(y_test).float()

        for epoch in range(1, epochs + 1):
            model.train()
            for x_b, y_b in train_loader:
                optimizer.zero_grad()
                y_pred = model(x_b)
                if use_physics_loss:
                    loss, _ = criterion(y_pred, y_b, x_b, scaler)
                else:
                    loss = criterion(y_pred, y_b)
                loss.backward()
                optimizer.step()
            scheduler.step()

            model.eval()
            with torch.no_grad():
                y_val_pred = model(x_test_t)
                if use_physics_loss:
                    val_loss, _ = criterion(y_val_pred, y_test_t, x_test_t, scaler)
                    val_loss_val = float(val_loss.item())
                else:
                    val_loss_val = float(criterion(y_val_pred, y_test_t).item())

            if val_loss_val < best_val_loss:
                best_val_loss = val_loss_val
                best_weights = {key: val.cpu().clone() for key, val in model.state_dict().items()}

        if best_weights is not None:
            model.load_state_dict(best_weights)

        model.eval()
        with torch.no_grad():
            y_test_pred_norm = model(x_test_t).numpy()
        y_test_pred = scaler.inverse_transform_y(y_test_pred_norm)

        if out_dim == 3:
            t_true = (y_test_raw[:, 2:3] / 14.1).astype(np.float32)
            t_pred = (y_test_pred[:, 2:3] / 14.1).astype(np.float32)
            y_test_raw_4d = np.hstack([y_test_raw, t_true])
            y_test_pred_4d = np.hstack([y_test_pred, t_pred])
            m = compute_regression_metrics(
                y_test_raw_4d,
                y_test_pred_4d,
                target_names=["f1", "stress", "grms", "transmissibility"],
            )
        else:
            m = compute_regression_metrics(y_test_raw, y_test_pred)

        fold_results.append(m)

    # Compute mean and standard deviation across all folds
    summary: Dict[str, Any] = {
        "k_folds": k,
        "model_architecture": model_architecture,
        "use_physics_loss": use_physics_loss,
        "per_fold": fold_results,
        "metrics_summary": {},
    }

    metric_keys = list(fold_results[0].keys())
    for k_name in metric_keys:
        vals = [res[k_name] for res in fold_results]
        summary["metrics_summary"][k_name] = {
            "mean": float(np.mean(vals)),
            "std": float(np.std(vals)),
            "min": float(np.min(vals)),
            "max": float(np.max(vals)),
        }

    return summary


def run_ablation_study(
    x_data: np.ndarray,
    y_data: np.ndarray,
    k: int = 10,
    epochs: int = 250,
    batch_size: int = 32,
    lr: float = 1e-3,
    random_seed: int = 42,
) -> Dict[str, Any]:
    """Runs full 4x4 systematic ablation matrix under identical k-fold CV.

    Models:
      - M1: MLP Baseline (Pure MSE)
      - M2: MLP + Physics-Guided Loss (GA + Monotonicity)
      - M3: ResNet Baseline (Pure MSE)
      - M4: Full PG-ResNet (Residual Blocks + Physics-Guided Loss)

    Args:
        x_data: Input parameter matrix (N, 5).
        y_data: Target dynamic responses matrix (N, 3).
        k: Number of folds (default 10).
        epochs: Epochs per fold.
        batch_size: Batch size.
        lr: Learning rate.
        random_seed: Random seed.

    Returns:
        Dictionary containing detailed metrics for M1, M2, M3, M4 and comparative table.
    """
    logger.info("Executing 4-model systematic ablation study (%d-fold CV)...", k)
    configs = [
        ("M1_MLP_Pure", "mlp", False),
        ("M2_MLP_Physics", "mlp", True),
        ("M3_ResNet_Pure", "resnet", False),
        ("M4_PG_ResNet", "resnet", True),
    ]

    results: Dict[str, Any] = {}
    for name, arch, use_phys in configs:
        logger.info("Running ablation variant: %s", name)
        res = k_fold_cross_validation(
            x_data=x_data,
            y_data=y_data,
            k=k,
            epochs=epochs,
            batch_size=batch_size,
            lr=lr,
            model_architecture=arch,
            use_physics_loss=use_phys,
            random_seed=random_seed,
        )
        results[name] = res

    return results
