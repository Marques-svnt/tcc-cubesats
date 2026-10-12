# 02: Property-Based Invariant Testing Suite

**What to build:** Property-based testing infrastructure using `hypothesis` fuzzing continuous mechanical and geometric parameters across edge cases to verify constitutive invariants.

**Blocked by:** 01: Centralized Settings and Sealed Dependency Infrastructure

**Status:** completed

- [x] Add `hypothesis` to test dependencies in `pyproject.toml`
- [x] Create `tests/test_properties.py` testing re-entrant cell invariants:
  - Relative density strictly in $(0.0, 1.0)$
  - Poisson's ratio strictly negative ($\nu_{\text{eff}} < 0$) for all valid geometric ranges
  - Monotonic increase of Gibson-Ashby effective modulus with increasing relative density
  - Non-negative Steinberg cumulative fatigue damage ($D \ge 0$)
- [x] Verify test suite executes cleanly and catches out-of-bound degenerate inputs
