# 01: Centralized Settings and Sealed Dependency Infrastructure

**What to build:** Immutable, typed configuration management via Pydantic v2 and sealed dependency resolution with `uv.lock` ensuring 100% reproducible execution across all environments.

**Blocked by:** None (can start immediately)

**Status:** ready-for-agent

- [x] Integrate `src/core/settings.py` loading NASA GEVS, AlSi10Mg LPBF, and optimization bounds from `configs/`
- [x] Configure `pyproject.toml` with `pythonpath = ["."]` for direct pytest invocation
- [x] Generate deterministic `uv.lock` with cryptographic hashes
- [x] Ensure 100% test pass rate on `tests/test_settings.py`
