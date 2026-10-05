"""Unit tests for the multi-objective optimization module (src/optimization/nsga2_optimizer.py).

Tests NSGA-II genetic operators, constrained dominance, fast non-dominated sorting,
TOPSIS multi-criteria decision making, and short evolutionary convergence.
"""

from pathlib import Path
import numpy as np
import pytest

from src.optimization.nsga2_optimizer import (
    CandidateIndividual,
    DesignVariableBounds,
    NSGA2Optimizer,
    export_pareto_designs_csv,
    select_best_flight_design_topsis,
)


def test_bounds_and_individual_initialization() -> None:
    """Verifies variable boundary definitions and individual structure."""
    bounds = DesignVariableBounds()
    lb = bounds.lower_bounds()
    ub = bounds.upper_bounds()

    assert len(lb) == 4
    assert len(ub) == 4
    assert np.all(lb < ub)
    assert lb[0] == 45.0  # Self-supporting overhang minimum
    assert lb[1] == 0.60  # Minimum strut thickness

    vars_sample = np.array([60.0, 1.0, 6.0, 10.0], dtype=np.float32)
    ind = CandidateIndividual(variables=vars_sample)
    assert ind.is_feasible is True
    assert ind.constraint_violation == 0.0


def test_genetic_operators_preserve_bounds() -> None:
    """Verifies that SBX crossover and polynomial mutation strictly respect bounds."""
    optimizer = NSGA2Optimizer(population_size=10, num_generations=2, random_seed=42)
    p1 = np.array([50.0, 0.8, 5.0, 9.0], dtype=np.float32)
    p2 = np.array([70.0, 1.5, 7.5, 12.0], dtype=np.float32)

    # Test SBX
    c1, c2 = optimizer.simulated_binary_crossover(p1, p2)
    assert np.all(c1 >= optimizer.lower_b) and np.all(c1 <= optimizer.upper_b)
    assert np.all(c2 >= optimizer.lower_b) and np.all(c2 <= optimizer.upper_b)

    # Test Mutation
    mutated = optimizer.polynomial_mutation(p1)
    assert np.all(mutated >= optimizer.lower_b) and np.all(mutated <= optimizer.upper_b)


def test_constrained_domination_rules() -> None:
    """Verifies Deb's constrained domination criteria."""
    # ind1 feasible, ind2 infeasible -> ind1 dominates
    ind1 = CandidateIndividual(
        variables=np.zeros(4, dtype=np.float32),
        objectives=np.array([0.15, 0.25, -700.0], dtype=np.float32),
        is_feasible=True,
        constraint_violation=0.0,
    )
    ind2 = CandidateIndividual(
        variables=np.zeros(4, dtype=np.float32),
        objectives=np.array([0.10, 0.20, -800.0], dtype=np.float32),
        is_feasible=False,
        constraint_violation=0.5,
    )
    assert NSGA2Optimizer.constrained_dominates(ind1, ind2) is True
    assert NSGA2Optimizer.constrained_dominates(ind2, ind1) is False

    # Both infeasible -> lower violation dominates
    ind3 = CandidateIndividual(
        variables=np.zeros(4, dtype=np.float32),
        is_feasible=False,
        constraint_violation=0.2,
    )
    assert NSGA2Optimizer.constrained_dominates(ind3, ind2) is True

    # Both feasible -> Pareto dominance
    ind4 = CandidateIndividual(
        variables=np.zeros(4, dtype=np.float32),
        objectives=np.array([0.14, 0.24, -720.0], dtype=np.float32),
        is_feasible=True,
    )
    # ind4 is strictly better than ind1 in all objectives
    assert NSGA2Optimizer.constrained_dominates(ind4, ind1) is True


def test_fast_non_dominated_sorting_and_crowding() -> None:
    """Verifies Pareto front partitioning and crowding distance assignment."""
    optimizer = NSGA2Optimizer(population_size=10, num_generations=2, random_seed=42)
    # Construct 3 individuals with clear non-dominated trade-off
    ind_a = CandidateIndividual(
        variables=np.zeros(4, dtype=np.float32),
        objectives=np.array([0.12, 0.30, -600.0], dtype=np.float32),
        is_feasible=True,
    )
    ind_b = CandidateIndividual(
        variables=np.zeros(4, dtype=np.float32),
        objectives=np.array([0.18, 0.18, -800.0], dtype=np.float32),
        is_feasible=True,
    )
    ind_c = CandidateIndividual(
        variables=np.zeros(4, dtype=np.float32),
        objectives=np.array([0.25, 0.40, -500.0], dtype=np.float32),
        is_feasible=True,
    )  # Dominated by both A and B

    fronts = optimizer.fast_non_dominated_sort([ind_a, ind_b, ind_c])
    assert len(fronts) >= 2
    assert ind_a in fronts[0]
    assert ind_b in fronts[0]
    assert ind_c not in fronts[0]

    optimizer.calculate_crowding_distance(fronts[0])
    # Boundary points have infinite crowding distance
    assert np.isinf(fronts[0][0].crowding_distance) or np.isinf(fronts[0][-1].crowding_distance)


def test_topsis_selection() -> None:
    """Verifies TOPSIS decision making selects an effective trade-off candidate."""
    # Design 1: Light but higher transmissibility
    d1 = CandidateIndividual(variables=np.zeros(4, dtype=np.float32))
    d1.total_mass_kg = 0.120
    d1.transmissibility = 0.350
    d1.f1_hz = 600.0

    # Design 2: Moderate mass, very low transmissibility, high stiffness (Ideal compromise)
    d2 = CandidateIndividual(variables=np.zeros(4, dtype=np.float32))
    d2.total_mass_kg = 0.145
    d2.transmissibility = 0.180
    d2.f1_hz = 780.0

    # Design 3: Heavy with average attenuation
    d3 = CandidateIndividual(variables=np.zeros(4, dtype=np.float32))
    d3.total_mass_kg = 0.220
    d3.transmissibility = 0.250
    d3.f1_hz = 720.0

    best = select_best_flight_design_topsis([d1, d2, d3], weights=(0.35, 0.45, 0.20))
    assert best == d2


def test_short_evolutionary_optimization_run(tmp_path: Path) -> None:
    """Verifies a short NSGA-II optimization loop and CSV export."""
    optimizer = NSGA2Optimizer(population_size=16, num_generations=5, random_seed=42)
    pareto_front, history = optimizer.run_optimization()

    assert len(history) == 5
    assert len(pareto_front) > 0
    for ind in pareto_front:
        assert ind.is_feasible is True
        assert ind.f1_hz >= 100.0

    # Test export
    csv_out = tmp_path / "test_pareto.csv"
    export_pareto_designs_csv(pareto_front, csv_out)
    assert csv_out.exists()
    assert csv_out.stat().st_size > 0
