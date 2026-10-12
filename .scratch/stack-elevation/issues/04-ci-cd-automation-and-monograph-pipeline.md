# 04: CI/CD Pipeline Automation and Monograph Verification

**What to build:** GitHub Actions continuous integration workflow running hermetic tests, ruff linting, and compiling the LaTeX monograph upon every commit.

**Blocked by:** 02: Property-Based Invariant Testing Suite, 03: Monte Carlo Uncertainty Quantification on Neural Surrogate

**Status:** completed

- [x] Create `.github/workflows/ci.yml` with `uv` caching and matrix testing
- [x] Add step to verify Ruff linting and formatting compliance
- [x] Add step to run full pytest suite with coverage reporting (83 tests)
- [x] Add TeX Live step compiling `monografia/Main.tex` to ensure zero compilation drift
- [x] Ensure pipeline artifact upload for `monografia_tcc_final.pdf`
