"""Design of Experiments (DoE) sampler module using Latin Hypercube Sampling (LHS).

Generates statistically well-distributed geometric parameter points
across the 3D re-entrant auxetic design space for surrogate model training.
"""

import logging
from typing import Dict, List, Tuple
import numpy as np

from src.core.geometry import calculate_relative_density, validate_dfam_constraints

logger = logging.getLogger(__name__)


def generate_latin_hypercube_samples(
    num_samples: int = 250,
    random_seed: int = 42,
    bounds: Dict[str, Tuple[float, float]] = None,
) -> List[Dict[str, float]]:
    """Generates Latin Hypercube samples within the geometric design space.

    Args:
        num_samples: Number of sample configurations to generate.
        random_seed: Random state seed for reproducibility.
        bounds: Dictionary mapping variable names to (min, max) bounds.

    Returns:
        List of dictionaries with valid geometric parameter sets and relative density.
    """
    if bounds is None:
        bounds = {
            "theta_deg": (55.0, 80.0),
            "thickness_t": (0.50, 1.80),
            "length_l": (4.0, 10.0),
            "height_h": (6.0, 15.0),
        }

    rng = np.random.default_rng(random_seed)
    dim = len(bounds)
    var_names = list(bounds.keys())

    # Generate standard Latin Hypercube intervals
    intervals = np.zeros((num_samples, dim))
    for j in range(dim):
        perm = rng.permutation(num_samples)
        offset = rng.uniform(0.0, 1.0, size=num_samples)
        intervals[:, j] = (perm + offset) / num_samples

    samples: List[Dict[str, float]] = []
    for i in range(num_samples):
        sample_dict: Dict[str, float] = {}
        for j, name in enumerate(var_names):
            v_min, v_max = bounds[name]
            sample_dict[name] = float(v_min + intervals[i, j] * (v_max - v_min))

        # Check DfAM compliance and compute analytical relative density
        is_dfam, _ = validate_dfam_constraints(
            theta_deg=sample_dict["theta_deg"],
            thickness_t=sample_dict["thickness_t"],
            length_l=sample_dict["length_l"],
            height_h=sample_dict["height_h"],
        )

        rel_density = calculate_relative_density(
            theta_deg=sample_dict["theta_deg"],
            thickness_t=sample_dict["thickness_t"],
            length_l=sample_dict["length_l"],
            height_h=sample_dict["height_h"],
        )
        sample_dict["relative_density"] = rel_density
        sample_dict["is_dfam_valid"] = 1.0 if is_dfam else 0.0

        samples.append(sample_dict)

    logger.info(
        "Generated %d Latin Hypercube samples across %d dimensions (seed=%d)",
        num_samples,
        dim,
        random_seed,
    )
    return samples
