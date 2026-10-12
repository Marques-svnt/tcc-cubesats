"""NASA GEVS qualification and random vibration verification utilities.

Follows NASA-STD-5020 and NASA-HDBK-7005 guidelines for random vibration (14.1 Grms),
modal frequency requirements (f1 >= 500.0 Hz), Steinberg 3-band fatigue damage,
and Margin of Safety (MS) computation anchored in AlSi10Mg L-PBF material properties.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Dict, Optional, Tuple
import numpy as np

logger = logging.getLogger(__name__)


def compute_gevs_margin_of_safety(
    sigma_3sigma_mpa: float,
    yield_strength_mpa: float = 230.0,
    factor_of_safety: float = 1.25,
) -> float:
    """Calculates structural Margin of Safety (MS) under NASA GEVS random vibration.

    Mathematical formulation:
        allowable_stress = yield_strength / factor_of_safety
        MS = (allowable_stress / sigma_3sigma) - 1.0

    Args:
        sigma_3sigma_mpa: 3-sigma peak Von Mises stress (99.73% confidence limit).
        yield_strength_mpa: Material yield strength (AlSi10Mg = 230.0 MPa).
        factor_of_safety: NASA structural safety factor (NASA-STD-5020 = 1.25).

    Returns:
        Margin of Safety (float). MS >= 0 indicates structural compliance.

    Raises:
        ValueError: If stress or safety factors are non-positive.
    """
    if sigma_3sigma_mpa <= 0.0:
        raise ValueError(f"sigma_3sigma_mpa must be positive, got {sigma_3sigma_mpa}")
    if factor_of_safety <= 0.0 or yield_strength_mpa <= 0.0:
        raise ValueError("Yield strength and safety factor must be positive")

    allowable_mpa = yield_strength_mpa / factor_of_safety
    ms = (allowable_mpa / sigma_3sigma_mpa) - 1.0

    logger.info(
        "NASA GEVS MS verification: sigma_3sigma=%.2f MPa, allowable=%.2f MPa, MS=%.4f",
        sigma_3sigma_mpa,
        allowable_mpa,
        ms,
    )
    return float(ms)


def compute_steinberg_fatigue_damage(
    f_natural_hz: float,
    t_seconds: float = 120.0,
    peak_stress_3sigma_mpa: Optional[float] = None,
    basquin_m: float = 6.8,
    basquin_c: float = 1.2e20,
    n_cycles_fail_1sigma: float = 1.0e7,
    n_cycles_fail_2sigma: float = 1.0e6,
    n_cycles_fail_3sigma: float = 1.0e5,
) -> Dict[str, float]:
    """Calculates cumulative fatigue damage ratio using Steinberg's 3-band technique.

    Under Gaussian random vibration:
    - Band 1: 1-sigma level occurs 68.3% of the time.
    - Band 2: 2-sigma level occurs 27.1% of the time.
    - Band 3: 3-sigma level occurs 4.33% of the time.

    Miner's cumulative damage law:
        D_total = sum(n_i / N_i) for i in {1, 2, 3}.

    Args:
        f_natural_hz: Fundamental resonant frequency in Hz.
        t_seconds: Qualification vibration test duration in seconds (GEVS standard = 120 s).
        peak_stress_3sigma_mpa: Optional 3-sigma peak stress in MPa. If provided, allowable
            cycles N_i are computed via the Basquin relation N_i = C * sigma_i^(-m).
        basquin_m: Basquin exponent (6.8 for AlSi10Mg).
        basquin_c: Basquin coefficient (1.2e20 for AlSi10Mg).
        n_cycles_fail_1sigma: Allowable cycles to failure at 1-sigma amplitude if stress not given.
        n_cycles_fail_2sigma: Allowable cycles to failure at 2-sigma amplitude if stress not given.
        n_cycles_fail_3sigma: Allowable cycles to failure at 3-sigma amplitude if stress not given.

    Returns:
        Dictionary with band-wise and total cumulative damage ratio D_total, plus compliance status.
    """
    total_cycles = f_natural_hz * t_seconds

    n1 = 0.6830 * total_cycles
    n2 = 0.2710 * total_cycles
    n3 = 0.0433 * total_cycles

    if peak_stress_3sigma_mpa is not None and peak_stress_3sigma_mpa > 0.0:
        s1 = peak_stress_3sigma_mpa / 3.0
        s2 = 2.0 * peak_stress_3sigma_mpa / 3.0
        s3 = peak_stress_3sigma_mpa
        n_fail_1 = basquin_c * (s1 ** (-basquin_m))
        n_fail_2 = basquin_c * (s2 ** (-basquin_m))
        n_fail_3 = basquin_c * (s3 ** (-basquin_m))
    else:
        n_fail_1 = n_cycles_fail_1sigma
        n_fail_2 = n_cycles_fail_2sigma
        n_fail_3 = n_cycles_fail_3sigma

    d1 = n1 / n_fail_1
    d2 = n2 / n_fail_2
    d3 = n3 / n_fail_3
    d_total = d1 + d2 + d3

    # NASA space qualification requirement (NASA-HDBK-7005): D <= 0.25 (4x life safety factor)
    is_compliant = bool(d_total <= 0.25)

    logger.info(
        "Steinberg fatigue: f=%.1f Hz, duration=%.1f s, D_total=%.6f (NASA compliant=%s)",
        f_natural_hz,
        t_seconds,
        d_total,
        is_compliant,
    )
    return {
        "d_1sigma": float(d1),
        "d_2sigma": float(d2),
        "d_3sigma": float(d3),
        "d_total": float(d_total),
        "is_compliant": is_compliant,
        "is_theoretical_safe": bool(d_total < 1.0),
    }


def verify_fundamental_frequency(
    f1_hz: float,
    min_required_hz: float = 100.0,
) -> Tuple[bool, float]:
    """Checks whether first natural frequency meets launch vehicle stiff chassis requirements.

    Args:
        f1_hz: First natural frequency identified by Lanczos modal analysis.
        min_required_hz: Minimum frequency threshold (NASA GEVS GSFC-STD-7000A >= 100.0 Hz).

    Returns:
        Tuple of (is_compliant, frequency_margin_hz).
    """
    margin_hz = f1_hz - min_required_hz
    compliant = f1_hz >= min_required_hz
    logger.info("Frequency qualification: f1=%.2f Hz (required >= %.2f Hz), compliant=%s", f1_hz, min_required_hz, compliant)
    return compliant, float(margin_hz)


def evaluate_nasa_gevs_psd(frequencies_hz: float | np.ndarray) -> float | np.ndarray:
    """Evaluates the canonical NASA GSFC-STD-7000A GEVS random vibration PSD envelope.

    Specification (Qualification Level = 14.1 Grms overall):
    - 20 Hz: 0.013 g^2/Hz (ramp up to 50 Hz at +3 dB/octave)
    - 50 to 800 Hz: 0.080 g^2/Hz (maximum energy plateau)
    - 800 to 2000 Hz: roll-off down to 0.0053 g^2/Hz at 2000 Hz (-6 dB/octave)

    Uses standard aerospace log-log breakpoint interpolation.

    Args:
        frequencies_hz: Single frequency (float) or array of frequencies in Hz.

    Returns:
        Power Spectral Density in g^2/Hz.
    """
    is_scalar = np.isscalar(frequencies_hz)
    f = np.atleast_1d(np.asarray(frequencies_hz, dtype=float))
    psd = np.zeros_like(f)

    # Breakpoint log-log slopes
    m_ramp = np.log10(0.080 / 0.013) / np.log10(50.0 / 20.0)
    m_roll = np.log10(0.0053 / 0.080) / np.log10(2000.0 / 800.0)

    # 1. Ramp 20 to 50 Hz
    mask1 = (f >= 20.0) & (f <= 50.0)
    psd[mask1] = 0.013 * (f[mask1] / 20.0) ** m_ramp

    # 2. Plateau 50 to 800 Hz
    mask2 = (f > 50.0) & (f <= 800.0)
    psd[mask2] = 0.080

    # 3. Roll-off 800 to 2000 Hz
    mask3 = (f > 800.0) & (f <= 2000.0)
    psd[mask3] = 0.080 * (f[mask3] / 800.0) ** m_roll

    logger.debug("Evaluated NASA GEVS PSD at %d frequency points", f.size)
    return float(psd[0]) if is_scalar else psd


def compute_miles_acceleration_grms(
    f_natural_hz: float,
    q_factor: float = 25.0,
) -> float:
    """Estimates stochastic resonant response using Miles' Single-DOF equation.

    Miles equation:
        G_rms = sqrt( (pi / 2.0) * f_n * Q * PSD(f_n) )

    Args:
        f_natural_hz: Resonant natural frequency in Hz.
        q_factor: Dynamic amplification factor Q = 1 / (2 * zeta) (standard Q=25 for zeta=2%).

    Returns:
        Stochastic 1-sigma acceleration in Grms.

    Raises:
        ValueError: If resonant frequency or Q factor are non-positive.
    """
    if f_natural_hz <= 0.0 or q_factor <= 0.0:
        raise ValueError("Natural frequency and Q factor must be positive")

    psd_val = float(evaluate_nasa_gevs_psd(f_natural_hz))
    g_rms = np.sqrt(0.5 * np.pi * f_natural_hz * q_factor * psd_val)
    logger.info(
        "Miles equation: fn=%.1f Hz, Q=%.1f, PSD=%.5f g^2/Hz -> G_rms=%.2f G",
        f_natural_hz,
        q_factor,
        psd_val,
        g_rms,
    )
    return float(g_rms)


def export_canonical_nastran_bdf(
    output_bdf_path: Path | str,
    e_modulus_mpa: float = 68000.0,
    nu: float = 0.33,
    rho_ton_mm3: float = 2.68e-9,
) -> Path:
    """Exports a canonical NASA Nastran BDF bulk data deck via pyNastran.

    Contains standard GRID coordinates, quadratic CTETRA solid elements,
    isotropic MAT1 material (AlSi10Mg), PSOLID property, and SPC1 boundary constraints.

    Args:
        output_bdf_path: Target path for the .bdf file.
        e_modulus_mpa: Young's Modulus in MPa (default 68000.0 MPa).
        nu: Poisson's ratio (default 0.33).
        rho_ton_mm3: Mass density in ton/mm^3 (default 2.68e-9).

    Returns:
        Absolute Path to the written Nastran BDF deck.
    """
    # NumPy 2.0+ backward compatibility shim for pyNastran <= 1.4.1
    if not hasattr(np, "in1d"):
        np.in1d = np.isin  # type: ignore[attr-defined]

    from pyNastran.bdf.bdf import BDF  # Lazy import for lightweight usage

    target = Path(output_bdf_path).resolve()
    target.parent.mkdir(parents=True, exist_ok=True)

    model = BDF()

    # Define standard 10-node tetrahedron keypoints (corners + midpoints)
    coords = [
        (1, 0.0, 0.0, 0.0),
        (2, 10.0, 0.0, 0.0),
        (3, 0.0, 10.0, 0.0),
        (4, 0.0, 0.0, 10.0),
        (5, 5.0, 0.0, 0.0),
        (6, 5.0, 5.0, 0.0),
        (7, 0.0, 5.0, 0.0),
        (8, 0.0, 0.0, 5.0),
        (9, 5.0, 0.0, 5.0),
        (10, 0.0, 5.0, 5.0),
    ]
    for nid, x, y, z in coords:
        model.add_grid(nid, [x, y, z])

    # Material & Solid Section Properties
    model.add_mat1(1, E=e_modulus_mpa, G=None, nu=nu, rho=rho_ton_mm3)
    model.add_psolid(1, mid=1)
    model.add_ctetra(1, pid=1, nids=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10])

    # Boundary constraint (Fixed base at node 1)
    model.add_spc1(1, "123456", [1])

    model.write_bdf(str(target))
    logger.info("Successfully exported NASA Nastran BDF deck: %s (%d bytes)", target, target.stat().st_size)
    return target

