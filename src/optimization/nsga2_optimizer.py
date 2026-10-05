"""Multi-objective evolutionary optimization module using NSGA-II and TOPSIS decision making.

Implements constrained Pareto optimization for the 1U CubeSat auxetic chassis,
optimizing Total Mass, Dynamic Transmissibility, and Fundamental Natural Frequency.
"""

from dataclasses import dataclass, field
import logging
import math
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import matplotlib.pyplot as plt
import numpy as np
import torch

from src.agents.specialists import get_surrogate_artifacts
from src.analysis.ansys_batch_runner import AnsysBatchRunner
from src.core.geometry import (
    calculate_analytical_poisson_ratio,
    calculate_relative_density,
    validate_dfam_constraints,
)
from src.neural.surrogate_model import CubeSatSurrogateResNet, SurrogateDatasetScaler

logger = logging.getLogger(__name__)


@dataclass
class DesignVariableBounds:
    """Continuous decision variable bounds for the re-entrant unit cell."""

    theta_min_deg: float = 45.0
    theta_max_deg: float = 75.0
    t_min_mm: float = 0.60
    t_max_mm: float = 1.80
    l_min_mm: float = 4.00
    l_max_mm: float = 8.50
    h_min_mm: float = 8.00
    h_max_mm: float = 14.00

    def lower_bounds(self) -> np.ndarray:
        """Returns lower bound array [theta, t, l, h]."""
        return np.array(
            [self.theta_min_deg, self.t_min_mm, self.l_min_mm, self.h_min_mm],
            dtype=np.float32,
        )

    def upper_bounds(self) -> np.ndarray:
        """Returns upper bound array [theta, t, l, h]."""
        return np.array(
            [self.theta_max_deg, self.t_max_mm, self.l_max_mm, self.h_max_mm],
            dtype=np.float32,
        )


@dataclass(eq=False)
class CandidateIndividual:
    """Represents a single candidate chassis design in the NSGA-II population."""

    variables: np.ndarray  # [theta_deg, thickness_t, length_l, height_h]
    objectives: np.ndarray = field(default_factory=lambda: np.zeros(3, dtype=np.float32))
    # obj 0: Total Mass (kg) -> minimize
    # obj 1: Transmissibility T -> minimize
    # obj 2: Negative Natural Frequency (-f1, Hz) -> minimize (maximizes f1)

    constraint_violation: float = 0.0
    is_feasible: bool = True
    relative_density: float = 0.0
    poisson_ratio: float = 0.0
    f1_hz: float = 0.0
    peak_stress_mpa: float = 0.0
    payload_grms: float = 0.0
    transmissibility: float = 0.0
    total_mass_kg: float = 0.0
    margin_of_safety_yield: float = 0.0
    fatigue_damage_steinberg: float = 0.0

    rank: int = 0
    crowding_distance: float = 0.0


class NSGA2Optimizer:
    """Non-dominated Sorting Genetic Algorithm II optimizer for CubeSat structural synthesis."""

    def __init__(
        self,
        population_size: int = 100,
        num_generations: int = 100,
        crossover_prob: float = 0.90,
        mutation_prob: Optional[float] = None,
        eta_crossover: float = 15.0,
        eta_mutation: float = 20.0,
        bounds: Optional[DesignVariableBounds] = None,
        random_seed: int = 42,
    ) -> None:
        """Initializes the NSGA-II evolutionary optimizer.

        Args:
            population_size: Number of candidate designs per generation.
            num_generations: Total number of evolutionary iterations.
            crossover_prob: Probability of Simulated Binary Crossover (SBX).
            mutation_prob: Probability of Polynomial Mutation (default 1 / num_vars).
            eta_crossover: SBX distribution index.
            eta_mutation: Polynomial mutation distribution index.
            bounds: Continuous parameter bounds.
            random_seed: Seed for stochastic reproducibility.
        """
        self.pop_size = population_size
        self.num_generations = num_generations
        self.p_c = crossover_prob
        self.bounds = bounds or DesignVariableBounds()
        self.num_vars = 4
        self.p_m = mutation_prob if mutation_prob is not None else (1.0 / self.num_vars)
        self.eta_c = eta_crossover
        self.eta_m = eta_mutation
        self.random_seed = random_seed

        np.random.seed(random_seed)
        torch.manual_seed(random_seed)

        self.lower_b = self.bounds.lower_bounds()
        self.upper_b = self.bounds.upper_bounds()

        # Load trained neural surrogate model and scaler
        self.surrogate_model, self.surrogate_scaler = get_surrogate_artifacts()
        logger.info(
            "Initialized NSGA-II Optimizer (PopSize=%d, Gens=%d, Seed=%d)",
            population_size,
            num_generations,
            random_seed,
        )

    def evaluate_population(self, population: List[CandidateIndividual]) -> None:
        """Evaluates constraints and multi-objective functions using Physics-Guided ResNet.

        Args:
            population: List of candidate individuals to evaluate in batch.
        """
        n_ind = len(population)
        if n_ind == 0:
            return

        # 1. Compute analytical properties and construct surrogate input batch
        x_surrogate_raw = np.zeros((n_ind, 5), dtype=np.float32)

        for i, ind in enumerate(population):
            theta = float(ind.variables[0])
            t = float(ind.variables[1])
            l = float(ind.variables[2])
            h = float(ind.variables[3])

            rho_rel = calculate_relative_density(
                theta_deg=theta,
                thickness_t=t,
                length_l=l,
                height_h=h,
            )
            nu_eff = calculate_analytical_poisson_ratio(
                theta_deg=theta,
                height_h=h,
                length_l=l,
            )

            ind.relative_density = float(rho_rel)
            ind.poisson_ratio = float(nu_eff)

            # Mass formulation: monolithic rails (0.088 kg) + auxetic panels (0.220 * rho_rel kg)
            ind.total_mass_kg = float(0.088 + 0.220 * rho_rel)

            x_surrogate_raw[i, :] = [theta, t, l, h, rho_rel]

        # 2. Vectorized forward pass through Physics-Guided ResNet (< 2 ms for 100 individuals)
        x_scaled = self.surrogate_scaler.transform_x(x_surrogate_raw)
        with torch.no_grad():
            x_tensor = torch.from_numpy(x_scaled).float()
            y_scaled = self.surrogate_model(x_tensor).numpy()

        y_raw = self.surrogate_scaler.inverse_transform_y(y_scaled)

        # 3. Populate dynamic responses and evaluate constraints
        allowable_yield_mpa = 184.0  # AlSi10Mg yield (230 MPa) / FS (1.25)
        m_basquin = 6.8
        c_basquin = 1.2e20
        duration_s = 120.0

        for i, ind in enumerate(population):
            f1 = float(max(y_raw[i, 0], 10.0))
            stress_3sigma = float(max(y_raw[i, 1], 1.0))
            grms_payload = float(max(y_raw[i, 2], 0.1))
            transmissibility = float(max(y_raw[i, 3], 0.01))

            ind.f1_hz = f1
            ind.peak_stress_mpa = stress_3sigma
            ind.payload_grms = grms_payload
            ind.transmissibility = transmissibility

            # Margin of safety
            ms_yield = (allowable_yield_mpa / stress_3sigma) - 1.0
            ind.margin_of_safety_yield = float(ms_yield)

            # Steinberg 3-band cumulative fatigue damage
            tot_cycles = duration_s * f1
            s1 = 0.333 * stress_3sigma
            s2 = 0.667 * stress_3sigma
            s3 = 1.000 * stress_3sigma

            n1 = 0.683 * tot_cycles
            n2 = 0.271 * tot_cycles
            n3 = 0.0433 * tot_cycles

            cap1 = c_basquin * (max(s1, 1.0) ** (-m_basquin))
            cap2 = c_basquin * (max(s2, 1.0) ** (-m_basquin))
            cap3 = c_basquin * (max(s3, 1.0) ** (-m_basquin))

            d_steinberg = float((n1 / cap1) + (n2 / cap2) + (n3 / cap3))
            ind.fatigue_damage_steinberg = d_steinberg

            # Evaluate constraint violations (g_j(x) >= 0)
            theta = float(ind.variables[0])
            t = float(ind.variables[1])
            l = float(ind.variables[2])
            h = float(ind.variables[3])

            # DfAM constraints
            is_dfam, dfam_msgs = validate_dfam_constraints(
                theta_deg=theta,
                thickness_t=t,
                length_l=l,
                height_h=h,
            )

            theta_rad = math.radians(theta)
            powder_gap = 2.0 * l * math.cos(theta_rad) - 2.0 * t

            cv = 0.0
            # g1: Overhang angle >= 45 deg
            if theta < 45.0:
                cv += (45.0 - theta) / 45.0
            # g2: Thickness >= 0.5 mm
            if t < 0.50:
                cv += (0.50 - t) / 0.50
            # g3: Powder clearance gap >= 1.50 mm
            if powder_gap < 1.50:
                cv += (1.50 - powder_gap) / 1.50
            # g4: Launcher fundamental frequency decoupling f1 >= 100.0 Hz
            if f1 < 100.0:
                cv += (100.0 - f1) / 100.0
            # g5: Margin of safety MS_yield > 0
            if ms_yield < 0.0:
                cv += abs(ms_yield)
            # g6: Steinberg fatigue damage D <= 0.25
            if d_steinberg > 0.25:
                cv += (d_steinberg - 0.25) / 0.25

            ind.constraint_violation = float(cv)
            ind.is_feasible = bool(cv < 1e-5)

            # Define objectives (all to be minimized)
            # Obj 1: Total Mass (kg)
            # Obj 2: Transmissibility T (ratio)
            # Obj 3: -f1 (Hz) -> minimizing -f1 maximizes f1
            ind.objectives = np.array(
                [ind.total_mass_kg, ind.transmissibility, -ind.f1_hz],
                dtype=np.float32,
            )

    @staticmethod
    def constrained_dominates(ind1: CandidateIndividual, ind2: CandidateIndividual) -> bool:
        """Deb's constrained-domination comparison operator.

        Returns True if ind1 dominates ind2 under feasibility criteria.
        """
        # Case 1: ind1 feasible, ind2 infeasible -> ind1 dominates
        if ind1.is_feasible and not ind2.is_feasible:
            return True
        # Case 2: ind1 infeasible, ind2 feasible -> ind2 dominates
        if not ind1.is_feasible and ind2.is_feasible:
            return False
        # Case 3: Both infeasible -> lower constraint violation dominates
        if not ind1.is_feasible and not ind2.is_feasible:
            return ind1.constraint_violation < ind2.constraint_violation

        # Case 4: Both feasible -> standard Pareto dominance
        better_in_all_or_equal = np.all(ind1.objectives <= ind2.objectives)
        strictly_better_in_at_least_one = np.any(ind1.objectives < ind2.objectives)
        return bool(better_in_all_or_equal and strictly_better_in_at_least_one)

    def fast_non_dominated_sort(
        self, population: List[CandidateIndividual]
    ) -> List[List[CandidateIndividual]]:
        """Executes Deb's Fast Non-Dominated Sorting algorithm.

        Returns:
            List of non-dominated fronts (Front 0 is the Pareto frontier).
        """
        n_pop = len(population)
        if n_pop == 0:
            return []

        front_indices: List[List[int]] = [[]]
        n_p = [0] * n_pop  # Domination counter
        s_p: List[List[int]] = [[] for _ in range(n_pop)]  # Dominated solutions set

        for p_idx in range(n_pop):
            ind_p = population[p_idx]
            for q_idx in range(n_pop):
                if p_idx == q_idx:
                    continue
                ind_q = population[q_idx]
                if self.constrained_dominates(ind_p, ind_q):
                    s_p[p_idx].append(q_idx)
                elif self.constrained_dominates(ind_q, ind_p):
                    n_p[p_idx] += 1

            if n_p[p_idx] == 0:
                ind_p.rank = 0
                front_indices[0].append(p_idx)

        curr_rank = 0
        while curr_rank < len(front_indices) and len(front_indices[curr_rank]) > 0:
            next_front_idx: List[int] = []
            for p_idx in front_indices[curr_rank]:
                for q_idx in s_p[p_idx]:
                    n_p[q_idx] -= 1
                    if n_p[q_idx] == 0:
                        population[q_idx].rank = curr_rank + 1
                        next_front_idx.append(q_idx)
            curr_rank += 1
            if next_front_idx:
                front_indices.append(next_front_idx)

        return [[population[idx] for idx in f_idx] for f_idx in front_indices if len(f_idx) > 0]

    @staticmethod
    def calculate_crowding_distance(front: List[CandidateIndividual]) -> None:
        """Calculates crowding distance for individuals in a given Pareto front."""
        n_ind = len(front)
        if n_ind == 0:
            return
        if n_ind <= 2:
            for ind in front:
                ind.crowding_distance = float("inf")
            return

        for ind in front:
            ind.crowding_distance = 0.0

        num_objs = len(front[0].objectives)
        for m in range(num_objs):
            front.sort(key=lambda x: x.objectives[m])
            front[0].crowding_distance = float("inf")
            front[-1].crowding_distance = float("inf")

            obj_min = front[0].objectives[m]
            obj_max = front[-1].objectives[m]
            obj_range = max(obj_max - obj_min, 1e-8)

            for i in range(1, n_ind - 1):
                if math.isinf(front[i].crowding_distance):
                    continue
                dist = (front[i + 1].objectives[m] - front[i - 1].objectives[m]) / obj_range
                front[i].crowding_distance += float(dist)

    def binary_tournament_selection(
        self, population: List[CandidateIndividual]
    ) -> CandidateIndividual:
        """Performs binary tournament selection using Pareto rank and crowding distance."""
        i1, i2 = np.random.choice(len(population), size=2, replace=False)
        ind1, ind2 = population[i1], population[i2]

        if ind1.rank < ind2.rank:
            return ind1
        if ind2.rank < ind1.rank:
            return ind2
        if ind1.crowding_distance > ind2.crowding_distance:
            return ind1
        return ind2

    def simulated_binary_crossover(
        self, parent1: np.ndarray, parent2: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Simulated Binary Crossover (SBX) producing two child decision vectors."""
        if np.random.rand() > self.p_c:
            return parent1.copy(), parent2.copy()

        child1 = np.empty_like(parent1)
        child2 = np.empty_like(parent2)

        for i in range(self.num_vars):
            if np.random.rand() <= 0.5:
                if abs(parent1[i] - parent2[i]) > 1e-8:
                    y1 = min(parent1[i], parent2[i])
                    y2 = max(parent1[i], parent2[i])
                    yl, yu = self.lower_b[i], self.upper_b[i]

                    rand = np.random.rand()
                    beta = 1.0 + (2.0 * (y1 - yl) / (y2 - y1))
                    alpha = 2.0 - (beta ** (-(self.eta_c + 1.0)))
                    if rand <= (1.0 / alpha):
                        beta_q = (rand * alpha) ** (1.0 / (self.eta_c + 1.0))
                    else:
                        beta_q = (1.0 / (2.0 - rand * alpha)) ** (1.0 / (self.eta_c + 1.0))

                    c1 = 0.5 * ((y1 + y2) - beta_q * (y2 - y1))

                    beta = 1.0 + (2.0 * (yu - y2) / (y2 - y1))
                    alpha = 2.0 - (beta ** (-(self.eta_c + 1.0)))
                    if rand <= (1.0 / alpha):
                        beta_q = (rand * alpha) ** (1.0 / (self.eta_c + 1.0))
                    else:
                        beta_q = (1.0 / (2.0 - rand * alpha)) ** (1.0 / (self.eta_c + 1.0))

                    c2 = 0.5 * ((y1 + y2) + beta_q * (y2 - y1))

                    child1[i] = np.clip(c1, yl, yu)
                    child2[i] = np.clip(c2, yl, yu)
                else:
                    child1[i] = parent1[i]
                    child2[i] = parent2[i]
            else:
                child1[i] = parent1[i]
                child2[i] = parent2[i]

        return child1, child2

    def polynomial_mutation(self, individual: np.ndarray) -> np.ndarray:
        """Applies polynomial mutation within design bounds."""
        mutated = individual.copy()
        for i in range(self.num_vars):
            if np.random.rand() <= self.p_m:
                y = mutated[i]
                yl, yu = self.lower_b[i], self.upper_b[i]
                delta1 = (y - yl) / (yu - yl)
                delta2 = (yu - y) / (yu - yl)
                rand = np.random.rand()
                mut_pow = 1.0 / (self.eta_m + 1.0)

                if rand <= 0.5:
                    xy = 1.0 - delta1
                    val = 2.0 * rand + (1.0 - 2.0 * rand) * (xy ** (self.eta_m + 1.0))
                    delta_q = (val**mut_pow) - 1.0
                else:
                    xy = 1.0 - delta2
                    val = 2.0 * (1.0 - rand) + 2.0 * (rand - 0.5) * (xy ** (self.eta_m + 1.0))
                    delta_q = 1.0 - (val**mut_pow)

                mutated[i] = np.clip(y + delta_q * (yu - yl), yl, yu)
        return mutated

    def run_optimization(self) -> Tuple[List[CandidateIndividual], List[Dict[str, Any]]]:
        """Executes the full NSGA-II evolutionary search loop.

        Returns:
            Tuple of (Pareto_optimal_front_individuals, convergence_history).
        """
        logger.info(
            "Starting NSGA-II Optimization (%d generations, %d population)...",
            self.num_generations,
            self.pop_size,
        )

        # 1. Initialize random population uniformly within bounds
        population: List[CandidateIndividual] = []
        for _ in range(self.pop_size):
            vars_init = self.lower_b + np.random.rand(self.num_vars) * (self.upper_b - self.lower_b)
            population.append(CandidateIndividual(variables=vars_init.astype(np.float32)))

        self.evaluate_population(population)
        fronts = self.fast_non_dominated_sort(population)
        for front in fronts:
            self.calculate_crowding_distance(front)

        history: List[Dict[str, Any]] = []

        # 2. Main generational loop
        for gen in range(1, self.num_generations + 1):
            # Generate offspring population Q_t of size N
            offspring: List[CandidateIndividual] = []
            while len(offspring) < self.pop_size:
                p1 = self.binary_tournament_selection(population)
                p2 = self.binary_tournament_selection(population)

                c1_vars, c2_vars = self.simulated_binary_crossover(p1.variables, p2.variables)
                c1_vars = self.polynomial_mutation(c1_vars)
                c2_vars = self.polynomial_mutation(c2_vars)

                offspring.append(CandidateIndividual(variables=c1_vars))
                if len(offspring) < self.pop_size:
                    offspring.append(CandidateIndividual(variables=c2_vars))

            # Evaluate offspring batch
            self.evaluate_population(offspring)

            # Combine R_t = P_t U Q_t (size 2N)
            combined = population + offspring
            fronts = self.fast_non_dominated_sort(combined)

            new_population: List[CandidateIndividual] = []
            for front in fronts:
                self.calculate_crowding_distance(front)
                if len(new_population) + len(front) <= self.pop_size:
                    new_population.extend(front)
                else:
                    # Sort remaining front by crowding distance in descending order
                    front.sort(key=lambda x: x.crowding_distance, reverse=True)
                    needed = self.pop_size - len(new_population)
                    new_population.extend(front[:needed])
                    break

            population = new_population

            # Track generation metrics
            pareto_front = [ind for ind in fronts[0] if ind.is_feasible]
            n_feasible = sum(1 for ind in population if ind.is_feasible)
            min_mass = min(ind.total_mass_kg for ind in population)
            min_t = min(ind.transmissibility for ind in population)
            max_f1 = max(ind.f1_hz for ind in population)

            if gen % 20 == 0 or gen == self.num_generations:
                logger.info(
                    "Gen %03d/%03d | Feasible: %d/%d | Pareto Size: %d | Mass_min: %.3f kg | T_min: %.3f | f1_max: %.1f Hz",
                    gen,
                    self.num_generations,
                    n_feasible,
                    self.pop_size,
                    len(pareto_front),
                    min_mass,
                    min_t,
                    max_f1,
                )

            history.append(
                {
                    "generation": gen,
                    "num_feasible": n_feasible,
                    "pareto_size": len(pareto_front),
                    "min_mass_kg": float(min_mass),
                    "min_transmissibility": float(min_t),
                    "max_f1_hz": float(max_f1),
                }
            )

        # 3. Extract final non-dominated Pareto front of feasible solutions
        final_fronts = self.fast_non_dominated_sort(population)
        pareto_optimal = [ind for ind in final_fronts[0] if ind.is_feasible]
        logger.info(
            "Optimization complete. Discovered %d feasible Pareto-optimal designs.",
            len(pareto_optimal),
        )
        return pareto_optimal, history


def select_best_flight_design_topsis(
    pareto_designs: List[CandidateIndividual],
    weights: Tuple[float, float, float] = (0.35, 0.45, 0.20),
) -> CandidateIndividual:
    """Selects the best compromise flight design from the Pareto front using TOPSIS.

    Criteria weights:
        w1 (0.35): Total Mass (kg) -> lower is better.
        w2 (0.45): Transmissibility ratio T -> lower is better (vital for payload protection).
        w3 (0.20): Fundamental Natural Frequency f1 (Hz) -> higher is better.

    Args:
        pareto_designs: List of feasible non-dominated designs.
        weights: Tuple of relative criteria weights (w_mass, w_transmissibility, w_f1).

    Returns:
        Best compromise CandidateIndividual maximizing TOPSIS relative closeness.
    """
    if not pareto_designs:
        raise ValueError("Pareto design list cannot be empty for TOPSIS selection.")

    # Matrix of criteria: [Mass, Transmissibility, f1]
    m_crit = np.array(
        [[ind.total_mass_kg, ind.transmissibility, ind.f1_hz] for ind in pareto_designs],
        dtype=np.float64,
    )

    # 1. Vector normalization
    norm_factors = np.sqrt(np.sum(m_crit**2, axis=0))
    norm_matrix = m_crit / np.maximum(norm_factors, 1e-8)

    # 2. Weighted normalized matrix
    w = np.array(weights, dtype=np.float64)
    w = w / np.sum(w)
    weighted_matrix = norm_matrix * w

    # 3. Determine ideal positive (A+) and negative (A-) solutions
    # Mass: min (beneficial is min)
    # Transmissibility: min (beneficial is min)
    # f1: max (beneficial is max)
    a_plus = np.array(
        [
            np.min(weighted_matrix[:, 0]),
            np.min(weighted_matrix[:, 1]),
            np.max(weighted_matrix[:, 2]),
        ]
    )
    a_minus = np.array(
        [
            np.max(weighted_matrix[:, 0]),
            np.max(weighted_matrix[:, 1]),
            np.min(weighted_matrix[:, 2]),
        ]
    )

    # 4. Euclidean distance to ideal solutions
    d_plus = np.sqrt(np.sum((weighted_matrix - a_plus) ** 2, axis=1))
    d_minus = np.sqrt(np.sum((weighted_matrix - a_minus) ** 2, axis=1))

    # 5. Relative closeness to ideal solution
    closeness = d_minus / np.maximum(d_plus + d_minus, 1e-8)
    best_idx = int(np.argmax(closeness))

    best_candidate = pareto_designs[best_idx]
    logger.info(
        "TOPSIS selected Design #%d (Closeness=%.4f): Mass=%.3f kg, T=%.3f, f1=%.1f Hz",
        best_idx,
        closeness[best_idx],
        best_candidate.total_mass_kg,
        best_candidate.transmissibility,
        best_candidate.f1_hz,
    )
    return best_candidate


def plot_pareto_frontier(
    pareto_designs: List[CandidateIndividual],
    topsis_choice: CandidateIndividual,
    output_path: str | Path,
) -> Path:
    """Generates publication-quality 2D and 3D Pareto frontier visualizations.

    Args:
        pareto_designs: Feasible Pareto-optimal solutions.
        topsis_choice: Selected best compromise candidate.
        output_path: Target image file path (.png).

    Returns:
        Path to the saved figure.
    """
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    masses = [ind.total_mass_kg for ind in pareto_designs]
    trans = [ind.transmissibility for ind in pareto_designs]
    freqs = [ind.f1_hz for ind in pareto_designs]

    # Baseline solid chassis benchmark
    # Solid panels (rho_rel = 1.0) -> Mass = 0.308 kg, Transmissibility = 1.0 (no damping), f1 ~ 480 Hz
    solid_mass = 0.308
    solid_t = 0.850
    solid_f1 = 512.0

    fig = plt.figure(figsize=(15, 12), dpi=300)

    # Panel 1: 3D Pareto Projection
    ax1 = fig.add_subplot(2, 2, 1, projection="3d")
    sc1 = ax1.scatter(masses, trans, freqs, c=freqs, cmap="plasma", s=40, alpha=0.8, edgecolors="none")
    ax1.scatter(
        [topsis_choice.total_mass_kg],
        [topsis_choice.transmissibility],
        [topsis_choice.f1_hz],
        color="crimson",
        s=140,
        marker="*",
        label="TOPSIS Optimal Flight Design",
    )
    ax1.scatter([solid_mass], [solid_t], [solid_f1], color="black", s=80, marker="s", label="Conventional Solid Baseline")
    ax1.set_xlabel("Chassis Mass (kg)", fontsize=10, labelpad=8)
    ax1.set_ylabel("Transmissibility T", fontsize=10, labelpad=8)
    ax1.set_zlabel("Fundamental Freq f1 (Hz)", fontsize=10, labelpad=8)
    ax1.set_title("(a) 3D Pareto-Optimal Frontier", fontsize=11, fontweight="bold")
    ax1.legend(loc="upper left", fontsize=8)
    fig.colorbar(sc1, ax=ax1, shrink=0.5, pad=0.1, label="f1 (Hz)")

    # Panel 2: Mass vs Transmissibility (Direct Trade-off)
    ax2 = fig.add_subplot(2, 2, 2)
    sc2 = ax2.scatter(masses, trans, c=freqs, cmap="plasma", s=50, alpha=0.8, edgecolors="grey", linewidth=0.5)
    ax2.scatter(
        topsis_choice.total_mass_kg,
        topsis_choice.transmissibility,
        color="crimson",
        s=160,
        marker="*",
        label=f"Optimal: {topsis_choice.total_mass_kg:.3f} kg, T={topsis_choice.transmissibility:.3f}",
    )
    ax2.scatter(solid_mass, solid_t, color="black", s=90, marker="s", label=f"Solid 1U: {solid_mass:.3f} kg, T={solid_t:.3f}")
    ax2.set_xlabel("Total Chassis Mass (kg)", fontsize=10)
    ax2.set_ylabel("Payload Transmissibility T = Grms / 14.1", fontsize=10)
    ax2.set_title("(b) Mass vs. Dynamic Transmissibility Trade-off", fontsize=11, fontweight="bold")
    ax2.grid(True, linestyle="--", alpha=0.5)
    ax2.legend(fontsize=8)
    fig.colorbar(sc2, ax=ax2, label="f1 (Hz)")

    # Panel 3: Mass vs Fundamental Frequency
    ax3 = fig.add_subplot(2, 2, 3)
    sc3 = ax3.scatter(masses, freqs, c=trans, cmap="viridis_r", s=50, alpha=0.8, edgecolors="grey", linewidth=0.5)
    ax3.axhline(100.0, color="red", linestyle=":", linewidth=1.5, label="NASA GEVS Decoupling Limit (100 Hz)")
    ax3.scatter(
        topsis_choice.total_mass_kg,
        topsis_choice.f1_hz,
        color="crimson",
        s=160,
        marker="*",
        label=f"Optimal: f1={topsis_choice.f1_hz:.1f} Hz",
    )
    ax3.scatter(solid_mass, solid_f1, color="black", s=90, marker="s", label="Solid 1U Baseline")
    ax3.set_xlabel("Total Chassis Mass (kg)", fontsize=10)
    ax3.set_ylabel("Fundamental Frequency f1 (Hz)", fontsize=10)
    ax3.set_title("(c) Structural Rigidity vs. Mass", fontsize=11, fontweight="bold")
    ax3.grid(True, linestyle="--", alpha=0.5)
    ax3.legend(fontsize=8)
    fig.colorbar(sc3, ax=ax3, label="Transmissibility T")

    # Panel 4: Transmissibility vs Fundamental Frequency
    ax4 = fig.add_subplot(2, 2, 4)
    sc4 = ax4.scatter(trans, freqs, c=masses, cmap="coolwarm", s=50, alpha=0.8, edgecolors="grey", linewidth=0.5)
    ax4.scatter(
        topsis_choice.transmissibility,
        topsis_choice.f1_hz,
        color="crimson",
        s=160,
        marker="*",
        label="TOPSIS Selected Design",
    )
    ax4.scatter(solid_t, solid_f1, color="black", s=90, marker="s", label="Solid Baseline")
    ax4.set_xlabel("Payload Transmissibility T", fontsize=10)
    ax4.set_ylabel("Fundamental Frequency f1 (Hz)", fontsize=10)
    ax4.set_title("(d) Dynamic Attenuation vs. Rigidity", fontsize=11, fontweight="bold")
    ax4.grid(True, linestyle="--", alpha=0.5)
    ax4.legend(fontsize=8)
    fig.colorbar(sc4, ax=ax4, label="Mass (kg)")

    plt.tight_layout()
    plt.savefig(path, dpi=300)
    plt.close()
    logger.info("Saved Pareto frontier visualization to %s", path)
    return path


def export_pareto_designs_csv(
    pareto_designs: List[CandidateIndividual],
    output_csv_path: str | Path,
) -> Path:
    """Exports Pareto-optimal front candidate data to CSV."""
    import csv

    path = Path(output_csv_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    headers = [
        "design_id",
        "theta_deg",
        "thickness_t_mm",
        "length_l_mm",
        "height_h_mm",
        "relative_density",
        "poisson_ratio",
        "total_mass_kg",
        "f1_hz",
        "peak_stress_3sigma_mpa",
        "payload_grms",
        "transmissibility_ratio",
        "margin_of_safety_yield",
        "fatigue_damage_steinberg",
    ]

    with open(path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        for idx, ind in enumerate(pareto_designs):
            writer.writerow(
                [
                    f"pareto_{idx:03d}",
                    f"{ind.variables[0]:.2f}",
                    f"{ind.variables[1]:.3f}",
                    f"{ind.variables[2]:.2f}",
                    f"{ind.variables[3]:.2f}",
                    f"{ind.relative_density:.4f}",
                    f"{ind.poisson_ratio:.4f}",
                    f"{ind.total_mass_kg:.4f}",
                    f"{ind.f1_hz:.1f}",
                    f"{ind.peak_stress_mpa:.2f}",
                    f"{ind.payload_grms:.2f}",
                    f"{ind.transmissibility:.4f}",
                    f"{ind.margin_of_safety_yield:.2f}",
                    f"{ind.fatigue_damage_steinberg:.6f}",
                ]
            )

    logger.info("Exported %d Pareto-optimal designs to %s", len(pareto_designs), path)
    return path
