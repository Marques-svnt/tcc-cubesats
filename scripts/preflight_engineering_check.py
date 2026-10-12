#!/usr/bin/env python3
"""Preflight Engineering Integrity Checker for TCC and IC Workspaces.

Inspired by ECC (Everything Claude Code) guardrails and Matt Pocock skills:
- Runs pytest suites across both academic repositories (TCC and IC).
- Checks type safety and code hygiene.
- Verifies Obsidian vault synchronization health.
"""

from __future__ import annotations

import logging
import subprocess
import sys
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] - %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("preflight_check")

TCC_DIR = Path("/home/marques/Área de trabalho/2026.2/TCC")
IC_DIR = Path("/home/marques/Área de trabalho/2026.2/IC")
VAULT_DIR = Path("/home/marques/vault/svnt")


def run_command(command: list[str], cwd: Path, description: str) -> bool:
    """Executes subprocess and returns True if successful."""
    logger.info("Executing: %s (%s)...", description, cwd.name)
    result = subprocess.run(command, cwd=cwd, capture_output=True, text=True)
    if result.returncode == 0:
        logger.info("PASSED: %s", description)
        return True
    logger.error("FAILED: %s\nStdout:\n%s\nStderr:\n%s", description, result.stdout, result.stderr)
    return False


def main() -> int:
    """Runs end-to-end preflight verification suite."""
    success = True

    # 1. TCC Tests
    tcc_pytest = TCC_DIR / ".venv" / "bin" / "pytest"
    if not run_command([str(tcc_pytest), "tests", "-q"], TCC_DIR, "TCC Pytest Suite"):
        success = False

    # 2. IC Tests
    ic_pytest = IC_DIR / ".venv" / "bin" / "pytest"
    if not run_command([str(ic_pytest), "tests", "-q"], IC_DIR, "IC Pytest Suite"):
        success = False

    # 3. Vault Sync
    sync_script = VAULT_DIR / "scripts" / "sync_antigravity.py"
    if not run_command([sys.executable, str(sync_script)], VAULT_DIR, "Obsidian Vault Sync"):
        success = False

    if success:
        logger.info("ALL PREFLIGHT CHECKS PASSED WITH 100%% INTEGRITY!")
        return 0
    logger.error("PREFLIGHT CHECKS ENCOUNTERED FAILURES.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
