# 06: Static Type Safety and Pre-commit Hooks

**What to build:** Mypy static type checking configuration in `pyproject.toml` and Git pre-commit hooks (`.pre-commit-config.yaml`) ensuring strict type annotations, Ruff formatting, and prevention of oversized commits.

**Blocked by:** 05: Uncertainty Quantification Synthesis and Monograph Reporting

**Status:** completed

- [x] Configure `[tool.mypy]` in `pyproject.toml` targeting Python 3.12 with strict mode options
- [x] Add `.pre-commit-config.yaml` hooking Ruff lint, format, and check-yaml
- [x] Verify `mypy` runs cleanly on `src/core` and `src/neural/uncertainty_quantifier.py`
