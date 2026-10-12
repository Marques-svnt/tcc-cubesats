# 03: Monte Carlo Uncertainty Quantification on Neural Surrogate

**What to build:** Stochastic uncertainty quantification module simulating additively manufactured geometric tolerances ($\pm 50\ \mu\text{m}$) and assessing flight margin confidence intervals ($95\%$ and $99.73\%$).

**Blocked by:** 01: Centralized Settings and Sealed Dependency Infrastructure

**Status:** completed

- [x] Implement `src/neural/uncertainty_quantifier.py` with deep module interface `UncertaintyQuantifier.propagate()`
- [x] Sample Gaussian distributions representing LPBF dimensional deviations:
  - Rib thickness variation $\Delta t \sim \mathcal{N}(0, (15\ \mu\text{m})^2)$
  - Overhang angle variation $\Delta \theta \sim \mathcal{N}(0, (0.5^\circ)^2)$
  - Rib length $\Delta l \sim \mathcal{N}(0, (20\ \mu\text{m})^2)$
  - Rib height $\Delta h \sim \mathcal{N}(0, (20\ \mu\text{m})^2)$
- [x] Perform vectorized surrogate batch inference ($N = 10,000$ realizations in $< 0.02\text{ s}$)
- [x] Compute mean, standard deviation, percentile bounds ($2.5\%$, $97.5\%$), and flight Margins of Safety (Yield & Ultimate)
- [x] Create unit and integration test in `tests/test_uncertainty_quantification.py`
