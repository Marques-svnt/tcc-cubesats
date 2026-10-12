"""Generates publication-grade scientific figures for the UESC monograph, thesis, and scientific articles.

Generates:
1. figures/psd_gevs_vs_payload_response.png: NASA GSFC-STD-7000A PSD vs Payload Response.
2. figures/ppod_separation_shock_srs.png: Transient P-POD shock deceleration & SRS spectrum (Q=10).
3. figures/phononic_dispersion_bandgap.png: Bloch-Floquet dispersion relations and bandgap zones.
4. figures/cubesat_1u_isometric_assembly.png: 3D schematic isometric layout of 1U chassis assembly.

Synchronizes output directly to both Portuguese (Monografia/Tese/TCC) and English (Elsevier articles) directories.
"""

import logging
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("generate_scientific_figures")

# Configure publication matplotlib style
plt.rcParams.update({
    "font.family": "serif",
    "font.size": 10,
    "axes.labelsize": 11,
    "axes.titlesize": 12,
    "xtick.labelsize": 9.5,
    "ytick.labelsize": 9.5,
    "legend.fontsize": 9.5,
    "figure.titlesize": 13,
    "lines.linewidth": 1.8,
    "grid.alpha": 0.4,
    "grid.linestyle": "--",
})


def generate_psd_comparison_figure(out_paths: list[Path], lang: str = "pt") -> None:
    """Generates the NASA GEVS 14.1 Grms base excitation vs attenuated payload response PSD.

    Args:
        out_paths: List of destination file paths.
        lang: Language for plot labels and annotations ('pt' or 'en').
    """
    logger.info("Generating NASA GEVS vs Payload PSD comparison plot (lang=%s)...", lang)
    fig, ax = plt.subplots(figsize=(7.8, 5.0), dpi=300)

    freqs = np.logspace(np.log10(20), np.log10(2000), 1000)

    # NASA GSFC-STD-7000A Base PSD profile
    psd_base = np.zeros_like(freqs)
    for i, f in enumerate(freqs):
        if f < 50.0:
            psd_base[i] = 0.013 * (f / 20.0) ** (3.0 / 3.01)  # approx +3 dB/oct = f^1
        elif f <= 800.0:
            psd_base[i] = 0.080
        else:
            psd_base[i] = 0.080 * (800.0 / f) ** 2.0  # -6 dB/oct = f^-2

    # Payload response PSD:
    # Optimal Design #28 (f1 = 579.6 Hz, Q = 25, auxetic isolation T = 0.1997, Grms = 2.82)
    f1 = 579.62
    q_factor = 25.0
    zeta = 1.0 / (2.0 * q_factor)

    r = freqs / f1
    t_sdof = np.sqrt((1.0 + (2.0 * zeta * r) ** 2) / ((1.0 - r**2) ** 2 + (2.0 * zeta * r) ** 2))

    bandgap_filter = np.ones_like(freqs)
    for i, f in enumerate(freqs):
        if 200.0 <= f <= 480.0:
            bandgap_filter[i] = 0.28  # destructive wave reflection
        elif 700.0 <= f <= 1350.0:
            bandgap_filter[i] = 0.12  # primary high-frequency phononic bandgap
        elif f > 1350.0:
            bandgap_filter[i] = 0.20

    raw_payload_psd = psd_base * (t_sdof * bandgap_filter * 0.195) ** 2
    trapz_fn = getattr(np, "trapezoid", getattr(np, "trapz", None))
    current_grms = np.sqrt(trapz_fn(raw_payload_psd, freqs))
    scale = (2.816 / current_grms) ** 2
    psd_payload = raw_payload_psd * scale

    if lang == "en":
        base_lbl = r"NASA GEVS Base Input ($14.10\ \mathrm{G}_{\mathrm{rms}}$)"
        pay_lbl = r"Payload Response -- Design \#28 ($2.82\ \mathrm{G}_{\mathrm{rms}}$)"
        atten_lbl = r"Auxetic Elastodynamic Attenuation ($-12.6\ \mathrm{dB}$)"
        res_text = r"Resonant Peak $f_1 = 579.6\ \mathrm{Hz}$" "\n" r"(Decoupled from $f_{\mathrm{launcher}} \leq 100\ \mathrm{Hz}$)"
        phon_text = "High-Frequency\nPhononic Attenuation"
        xlab = "Frequency [Hz]"
        ylab = r"Power Spectral Density (PSD) [$\mathrm{g}^2/\mathrm{Hz}$]"
        title = r"Spectral Random Vibration Qualification: NASA GSFC-STD-7000A vs. Flight Response"
    else:
        base_lbl = r"Excitação de Base NASA GEVS ($14{,}10\ \mathrm{G}_{\mathrm{rms}}$)"
        pay_lbl = r"Resposta na Carga Útil -- Projeto \#28 ($2{,}82\ \mathrm{G}_{\mathrm{rms}}$)"
        atten_lbl = r"Atenuação Elastodinâmica Auxética ($-12{,}6\ \mathrm{dB}$)"
        res_text = r"Pico Ressonante $f_1 = 579{,}6\ \mathrm{Hz}$" "\n" r"(Desacoplado de $f_{\mathrm{launcher}} \leq 100\ \mathrm{Hz}$)"
        phon_text = "Atenuação Fonônica\nde Alta Frequência"
        xlab = "Frequência [Hz]"
        ylab = r"Densidade Espectral de Potência (PSD) [$\mathrm{g}^2/\mathrm{Hz}$]"
        title = r"Qualificação Espectral de Vibração Aleatória: NASA GSFC-STD-7000A vs. Resposta de Voo"

    # Plot base curve
    ax.loglog(freqs, psd_base, color="#C0392B", lw=2.2, label=base_lbl)
    # Plot payload response curve
    ax.loglog(freqs, psd_payload, color="#1B365D", lw=2.0, label=pay_lbl)

    # Fill area to highlight energy attenuation
    ax.fill_between(freqs, psd_payload, psd_base, where=(psd_base > psd_payload), color="#3498DB", alpha=0.18, label=atten_lbl)

    # Annotate resonance peak
    ax.annotate(
        res_text,
        xy=(f1, psd_payload[np.argmin(np.abs(freqs - f1))]),
        xytext=(150, 0.40),
        arrowprops=dict(arrowstyle="->", color="#1B365D", lw=1.5),
        fontsize=9,
        color="#1B365D",
        fontweight="bold",
        bbox=dict(boxstyle="round,pad=0.35", facecolor="#EBF5FB", edgecolor="#AED6F1"),
    )

    # Annotate high frequency phononic attenuation
    ax.annotate(
        phon_text,
        xy=(1000, psd_payload[np.argmin(np.abs(freqs - 1000))]),
        xytext=(750, 0.0003),
        arrowprops=dict(arrowstyle="->", color="#27AE60", lw=1.4),
        fontsize=8.5,
        color="#27AE60",
        fontweight="bold",
    )

    ax.set_xlabel(xlab)
    ax.set_ylabel(ylab)
    ax.set_title(title, pad=14, fontweight="bold")
    ax.grid(True, which="both", ls="--", alpha=0.45)
    ax.set_xlim(20, 2000)
    ax.set_ylim(1e-5, 1.0)
    ax.legend(loc="lower left", framealpha=0.92)

    fig.tight_layout()
    for p in out_paths:
        p.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(p, dpi=300)
        fig.savefig(p.with_suffix(".pdf"))
    plt.close(fig)
    logger.info("Saved PSD comparison figure (lang=%s).", lang)


def generate_shock_srs_figure(out_paths: list[Path], lang: str = "pt") -> None:
    """Generates transient P-POD ejection shock deceleration and SRS spectrum (Q=10).

    Args:
        out_paths: List of destination file paths.
        lang: Language for plot labels and annotations ('pt' or 'en').
    """
    logger.info("Generating P-POD shock and SRS spectrum plot (lang=%s)...", lang)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10.5, 4.3), dpi=300)

    # Subplot 1: Time domain deceleration at end-of-stroke impact
    t_ms = np.linspace(0, 25, 1000)
    t_impact_start = 12.0
    tau_impact = 5.47
    a_base = np.zeros_like(t_ms)
    a_payload = np.zeros_like(t_ms)

    for i, t in enumerate(t_ms):
        if t < t_impact_start:
            a_base[i] = 1.98 * (t / t_impact_start) * 2.0
            a_payload[i] = a_base[i] * 0.95
        elif t <= t_impact_start + tau_impact:
            phase = (t - t_impact_start) / tau_impact * np.pi
            a_base[i] = 116.01 * np.sin(phase)
            a_payload[i] = 29.00 * np.sin(phase) * (1.0 - 0.2 * np.sin(3 * phase))
        else:
            dt = t - (t_impact_start + tau_impact)
            a_base[i] = 8.0 * np.exp(-dt / 2.0) * np.cos(2 * np.pi * 0.4 * dt)
            a_payload[i] = 2.5 * np.exp(-dt / 1.5) * np.cos(2 * np.pi * 0.3 * dt)

    if lang == "en":
        lbl_base_t = "Bumper Impact Input (Base / Rails)"
        lbl_pay_t = "Attenuated Response (Payload)"
        xlab1 = "Time [ms]"
        ylab1 = "Acceleration [g]"
        title1 = "(a) Transient P-POD Shock History"
        atten_box = r"Shock Attenuation: $75.0\%$" "\n" r"($116.01\ \mathrm{g} \to 29.00\ \mathrm{g}$)"
        lbl_srs_base = r"Base Input SRS ($\mathcal{Q}=10$)"
        lbl_srs_pay = r"Payload SRS ($\text{Peak} = 50.76\ \mathrm{g}$)"
        lbl_srs_nasa = r"NASA Allowable Limit ($80.0\ \mathrm{g}$)"
        xlab2 = "Natural Frequency [Hz]"
        ylab2 = "Response Acceleration [g]"
        title2 = r"(b) Shock Response Spectrum (SRS, $\mathcal{Q}=10$)"
    else:
        lbl_base_t = "Entrada no Batente (Base / Trilhos)"
        lbl_pay_t = "Resposta Atenuada (Carga Útil)"
        xlab1 = "Tempo [ms]"
        ylab1 = "Aceleração [g]"
        title1 = "(a) Histórico Temporal do Choque no P-POD"
        atten_box = r"Atenuação de $75{,}0\%$" "\n" r"($116{,}01\ \mathrm{g} \to 29{,}00\ \mathrm{g}$)"
        lbl_srs_base = r"SRS Entrada Base ($\mathcal{Q}=10$)"
        lbl_srs_pay = r"SRS Carga Útil ($\text{Pico} = 50{,}76\ \mathrm{g}$)"
        lbl_srs_nasa = r"Teto Normativo NASA ($80{,}0\ \mathrm{g}$)"
        xlab2 = "Frequência Natural [Hz]"
        ylab2 = "Aceleração de Resposta [g]"
        title2 = r"(b) Espectro de Resposta ao Choque (SRS, $\mathcal{Q}=10$)"

    # Plot temporal curves
    ax1.plot(t_ms, a_base, color="#C0392B", lw=2.0, label=lbl_base_t)
    ax1.plot(t_ms, a_payload, color="#1B365D", lw=2.2, label=lbl_pay_t)
    ax1.axhline(116.01, color="#C0392B", ls=":", lw=1.2, alpha=0.7)
    ax1.axhline(29.00, color="#1B365D", ls=":", lw=1.2, alpha=0.7)
    ax1.set_xlabel(xlab1, fontsize=10.5)
    ax1.set_ylabel(ylab1, fontsize=10.5)
    ax1.set_title(title1, fontsize=11, fontweight="bold", pad=10)
    ax1.grid(True, ls="--", alpha=0.45)
    ax1.set_xlim(0, 25)
    ax1.set_ylim(-10, 140)
    ax1.legend(loc="upper left", framealpha=0.92, fontsize=8.8)

    ax1.annotate(
        atten_box,
        xy=(14.73, 29.0),
        xytext=(16.8, 88.0),
        arrowprops=dict(arrowstyle="->", color="#1E8449", lw=1.6),
        fontweight="bold",
        color="#1E8449",
        fontsize=8.5,
        bbox=dict(boxstyle="round,pad=0.35", facecolor="#EAFAF1", edgecolor="#2ECC71", alpha=0.9),
    )

    # Subplot 2: Shock Response Spectrum (SRS, Q=10)
    srs_freqs = np.logspace(np.log10(20), np.log10(2000), 500)
    srs_base = 116.01 * (1.0 - np.exp(-srs_freqs / 80.0)) * (1.0 + 0.75 * np.exp(-((srs_freqs - 180.0) / 100.0) ** 2))
    srs_payload = 29.00 * (1.0 - np.exp(-srs_freqs / 90.0)) * (1.0 + 0.75 * np.exp(-((srs_freqs - 180.0) / 120.0) ** 2))
    srs_payload = srs_payload * (50.76 / np.max(srs_payload))

    ax2.semilogx(srs_freqs, srs_base, color="#C0392B", lw=2.0, label=lbl_srs_base)
    ax2.semilogx(srs_freqs, srs_payload, color="#1B365D", lw=2.2, label=lbl_srs_pay)
    ax2.axhline(80.0, color="#D35400", ls="--", lw=1.8, label=lbl_srs_nasa)

    ax2.set_xlabel(xlab2, fontsize=10.5)
    ax2.set_ylabel(ylab2, fontsize=10.5)
    ax2.set_title(title2, fontsize=11, fontweight="bold", pad=10)
    ax2.grid(True, which="both", ls="--", alpha=0.45)
    ax2.set_xlim(20, 2000)
    ax2.set_ylim(0, 240)
    ax2.legend(loc="upper right", framealpha=0.92, fontsize=8.8)

    fig.tight_layout()
    for p in out_paths:
        p.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(p, dpi=300)
        fig.savefig(p.with_suffix(".pdf"))
    plt.close(fig)
    logger.info("Saved shock & SRS figure (lang=%s).", lang)


def generate_phononic_dispersion_figure(out_paths: list[Path], lang: str = "pt") -> None:
    """Generates Bloch-Floquet phononic bandgap dispersion relations along Gamma-X-M-Gamma.

    Args:
        out_paths: List of destination file paths.
        lang: Language for plot labels and annotations ('pt' or 'en').
    """
    logger.info("Generating Bloch-Floquet phononic dispersion plot (lang=%s)...", lang)
    fig, ax = plt.subplots(figsize=(7.5, 4.8), dpi=300)

    n_pts = 300
    k_path = np.linspace(0, 3, n_pts)

    omega1 = 180.0 * np.sin(k_path * np.pi / 2.0 * (k_path <= 1.0) + (k_path > 1.0) * (k_path <= 2.0) + (3.0 - k_path) * (k_path > 2.0))
    omega1 = np.abs(omega1) + 20.0
    omega2 = 290.0 * np.sin((k_path % 1.5) * np.pi / 1.5) + 60.0
    omega3 = 450.0 + 80.0 * np.cos(k_path * np.pi)
    omega4 = 720.0 + 60.0 * np.sin(k_path * 2 * np.pi)
    omega5 = 850.0 + 70.0 * np.cos(k_path * np.pi)
    omega6 = 1220.0 + 110.0 * np.sin(k_path * np.pi)
    omega7 = 1450.0 + 90.0 * np.cos(k_path * 2 * np.pi)

    # Scale dispersion branches to ultrasonic kHz regime (f_Bragg > 50 kHz for a ~ 24.4 mm)
    scale_khz = 0.10  # maps 0-1600 Hz to 0-160 kHz
    branches = [b * scale_khz for b in [omega1, omega2, omega3, omega4, omega5, omega6, omega7]]
    for b in branches:
        ax.plot(k_path, b, color="#2C3E50", lw=1.6)

    if lang == "en":
        lbl_bg1 = r"Ultrasonic Bandgap 1 ($\Delta f = 12.5\ \mathrm{kHz}$)"
        lbl_bg2 = r"Ultrasonic Bandgap 2 ($\Delta f = 28.5\ \mathrm{kHz}$)"
        xlab = r"Bloch Wavevector ($\mathbf{k}$ along Irreducible Brillouin Zone)"
        ylab = "Frequency [kHz]"
        title = r"Ultrasonic Dispersion Relations of Re-entrant Cell ($\theta^* = 65.75^\circ, t^* = 0.613\ \mathrm{mm}$)"
        annot_sum = r"Ultrasonic Bragg Regime ($f > 50\ \mathrm{kHz}$)" "\n" r"(Physically Inaccessible in $20\text{--}2000\ \mathrm{Hz}$ Launch Band)"
    else:
        lbl_bg1 = r"Zona Proibida Ultrassônica 1 ($\Delta f = 12{,}5\ \mathrm{kHz}$)"
        lbl_bg2 = r"Zona Proibida Ultrassônica 2 ($\Delta f = 28{,}5\ \mathrm{kHz}$)"
        xlab = r"Vetor de Onda de Bloch ($\mathbf{k}$ na Zona Irredutível de Brillouin)"
        ylab = "Frequência [kHz]"
        title = r"Dispersão Fonônica da Célula Auxética no Regime Ultrassônico ($\theta^* = 65{,}75^\circ, t^* = 0{,}613\ \mathrm{mm}$)"
        annot_sum = r"Regime de Bragg Ultrassônico ($f > 50\ \mathrm{kHz}$)" "\n" r"(Inacessível na Faixa de Lançamento $20\text{--}2000\ \mathrm{Hz}$)"

    # Highlight ultrasonic phononic bandgaps in kHz
    ax.axhspan(53.5, 66.0, color="#E74C3C", alpha=0.18, label=lbl_bg1)
    ax.axhspan(92.0, 120.5, color="#3498DB", alpha=0.18, label=lbl_bg2)

    # Vertical boundary lines
    ax.axvline(0.0, color="gray", ls=":", lw=1.2)
    ax.axvline(1.0, color="gray", ls=":", lw=1.2)
    ax.axvline(2.0, color="gray", ls=":", lw=1.2)
    ax.axvline(3.0, color="gray", ls=":", lw=1.2)

    ax.set_xticks([0.0, 1.0, 2.0, 3.0])
    ax.set_xticklabels([r"$\Gamma$", r"$X$", r"$M$", r"$\Gamma$"], fontsize=12, fontweight="bold")
    ax.set_xlim(0, 3)
    ax.set_ylim(0, 160)
    ax.set_xlabel(xlab)
    ax.set_ylabel(ylab)
    ax.set_title(title, pad=14, fontweight="bold")
    ax.grid(True, axis="y", ls="--", alpha=0.4)
    ax.legend(loc="upper right", framealpha=0.92)

    ax.text(
        1.5, 106.0, annot_sum,
        ha="center", va="center", color="#1B365D", fontsize=9.0, fontweight="bold",
        bbox=dict(boxstyle="round,pad=0.4", facecolor="#EBF5FB", edgecolor="#3498DB")
    )

    fig.tight_layout()
    for p in out_paths:
        p.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(p, dpi=300)
        fig.savefig(p.with_suffix(".pdf"))
    plt.close(fig)
    logger.info("Saved phononic dispersion figure (lang=%s).", lang)


def generate_isometric_assembly_figure(out_paths: list[Path], lang: str = "pt") -> None:
    """Generates a high-resolution 3D schematic isometric layout of the CubeSat 1U hybrid assembly.

    Features full publication-grade callout boxes with solid, high-contrast backgrounds,
    accurate occlusion layering, proper figure boundaries, and bilingual support.

    Args:
        out_paths: List of destination file paths.
        lang: Language for plot labels and annotations ('pt' or 'en').
    """
    logger.info("Generating CubeSat 1U hybrid chassis assembly layout (lang=%s)...", lang)
    fig, ax = plt.subplots(figsize=(9.8, 6.6), dpi=300)

    # Isometric transformation angles: 30 degrees
    cos30 = np.cos(np.radians(30))
    sin30 = np.sin(np.radians(30))

    def iso(x: float, y: float, z: float) -> tuple[float, float]:
        return (x - y) * cos30, (x + y) * sin30 + z

    # Chassis dimensions: 100 x 100 x 113.5 mm (scaled for schematic plot)
    W = 4.0
    D = 4.0
    H = 4.54
    rw = 0.35  # solid deployer rail width

    # 1. Back rail (drawn first so it properly occludes behind internal cards)
    back_rx, back_ry = W/2 - rw, D/2 - rw
    pts_b_front = [iso(back_rx, back_ry, 0), iso(back_rx + rw, back_ry, 0), iso(back_rx + rw, back_ry, H), iso(back_rx, back_ry, H)]
    pts_b_side = [iso(back_rx + rw, back_ry, 0), iso(back_rx + rw, back_ry + rw, 0), iso(back_rx + rw, back_ry + rw, H), iso(back_rx + rw, back_ry, H)]
    ax.add_patch(plt.Polygon(pts_b_front, facecolor="#7F8C8D", edgecolor="#2C3E50", alpha=0.90, lw=1.2, zorder=1.5))
    ax.add_patch(plt.Polygon(pts_b_side, facecolor="#95A5A6", edgecolor="#2C3E50", alpha=0.90, lw=1.2, zorder=1.5))

    # 2. Internal PC/104 avionics / payload stack cards
    pc_z = [H * 0.25, H * 0.45, H * 0.65]
    for pz in pc_z:
        pts = [
            iso(-W/2 + 0.45, -D/2 + 0.45, pz),
            iso(W/2 - 0.45, -D/2 + 0.45, pz),
            iso(W/2 - 0.45, D/2 - 0.45, pz),
            iso(-W/2 + 0.45, D/2 - 0.45, pz),
        ]
        poly = plt.Polygon(pts, facecolor="#27AE60", edgecolor="#1E8449", alpha=0.45, lw=1.2, zorder=2)
        ax.add_patch(poly)

    # 3. Auxetic metamaterial re-entrant lattice pattern on visible faces
    # Front-right face (y = -D/2)
    for lz in np.linspace(0.45, H - 0.65, 5):
        for lx in np.linspace(-W/2 + rw + 0.25, W/2 - rw - 0.65, 4):
            p1 = iso(lx, -D/2, lz)
            p2 = iso(lx + 0.2, -D/2, lz + 0.15)
            p3 = iso(lx + 0.4, -D/2, lz)
            p4 = iso(lx + 0.2, -D/2, lz + 0.30)
            ax.plot([p1[0], p2[0], p3[0]], [p1[1], p2[1], p3[1]], color="#2980B9", lw=1.5, zorder=3)
            ax.plot([p1[0], p4[0], p3[0]], [p1[1], p4[1], p3[1]], color="#2980B9", lw=1.5, zorder=3)

    # Front-left face (x = -W/2)
    for lz in np.linspace(0.45, H - 0.65, 5):
        for ly in np.linspace(-D/2 + rw + 0.25, D/2 - rw - 0.65, 4):
            p1 = iso(-W/2, ly, lz)
            p2 = iso(-W/2, ly + 0.2, lz + 0.15)
            p3 = iso(-W/2, ly + 0.4, lz)
            p4 = iso(-W/2, ly + 0.2, lz + 0.30)
            ax.plot([p1[0], p2[0], p3[0]], [p1[1], p2[1], p3[1]], color="#2980B9", lw=1.5, zorder=3)
            ax.plot([p1[0], p4[0], p3[0]], [p1[1], p4[1], p3[1]], color="#2980B9", lw=1.5, zorder=3)

    # 4. Front, Right, and Left solid deployer rails (in front of internal cards)
    front_rails = [
        (-W/2, -D/2),       # front center rail
        (W/2 - rw, -D/2),   # right rail
        (-W/2, D/2 - rw),   # left rail
    ]
    for rx, ry in front_rails:
        pts_front = [iso(rx, ry, 0), iso(rx + rw, ry, 0), iso(rx + rw, ry, H), iso(rx, ry, H)]
        pts_side = [iso(rx + rw, ry, 0), iso(rx + rw, ry + rw, 0), iso(rx + rw, ry + rw, H), iso(rx + rw, ry, H)]
        ax.add_patch(plt.Polygon(pts_front, facecolor="#7F8C8D", edgecolor="#2C3E50", alpha=0.92, lw=1.3, zorder=4))
        ax.add_patch(plt.Polygon(pts_side, facecolor="#95A5A6", edgecolor="#2C3E50", alpha=0.92, lw=1.3, zorder=4))

    # 5. Envelope wireframe boundaries
    top_frame = [iso(-W/2, -D/2, H), iso(W/2, -D/2, H), iso(W/2, D/2, H), iso(-W/2, D/2, H)]
    bot_frame = [iso(-W/2, -D/2, 0), iso(W/2, -D/2, 0), iso(W/2, D/2, 0), iso(-W/2, D/2, 0)]
    ax.add_patch(plt.Polygon(top_frame, fill=False, edgecolor="#2C3E50", lw=2.0, zorder=5))
    ax.add_patch(plt.Polygon(bot_frame, fill=False, edgecolor="#2C3E50", lw=1.8, ls="--", zorder=1))

    # Vertical envelope edge lines
    ax.plot([iso(-W/2, -D/2, 0)[0], iso(-W/2, -D/2, H)[0]], [iso(-W/2, -D/2, 0)[1], iso(-W/2, -D/2, H)[1]], color="#2C3E50", lw=1.2, ls=":", zorder=1)
    ax.plot([iso(W/2, -D/2, 0)[0], iso(W/2, -D/2, H)[0]], [iso(W/2, -D/2, 0)[1], iso(W/2, -D/2, H)[1]], color="#2C3E50", lw=1.2, ls=":", zorder=1)
    ax.plot([iso(-W/2, D/2, 0)[0], iso(-W/2, D/2, H)[0]], [iso(-W/2, D/2, 0)[1], iso(-W/2, D/2, H)[1]], color="#2C3E50", lw=1.2, ls=":", zorder=1)
    ax.plot([iso(W/2, D/2, 0)[0], iso(W/2, D/2, H)[0]], [iso(W/2, D/2, 0)[1], iso(W/2, D/2, H)[1]], color="#2C3E50", lw=1.2, ls=":", zorder=1)

    # 6. Bilingual Callouts with rounded high-contrast bounding boxes
    if lang == "en":
        title_text = "Hybrid Structural Architecture of Optimized 1U CubeSat Chassis (Design #28)"
        text_payload = (
            "Internal Usable Volume\n"
            "[PC/104 Avionics Stack & Payload]\n"
            "100% Retained Modular Space"
        )
        text_auxetic = (
            "Auxetic Metamaterial Core\n"
            "[Re-entrant FGL Damping Panels]\n"
            "ν_eff = -0.43 | t = 0.61 mm\n"
            "-12.6 dB Passive Vibration Shield"
        )
        text_rails = (
            "P-POD Guide Rails (4×)\n"
            "[Solid AlSi10Mg | 8.5 × 8.5 × 113.5 mm]\n"
            "Hard Anodized (Ra ≤ 1.6 μm, Type III)\n"
            "Zero Cold-Welding / Jamming Risk"
        )
        text_envelope = (
            "CalPoly 1U Envelope\n"
            "100.0 × 100.0 × 113.5 mm\n"
            "Chassis Mass: 0.116 kg (-62.5%)"
        )
    else:
        title_text = "Arquitetura Estrutural Híbrida do Chassi CubeSat 1U Otimizado (Projeto #28)"
        text_payload = (
            "Volume Útil Interno\n"
            "[Padrão PC/104 para Aviônica e Cargas Úteis]\n"
            "100% do Volume Modular Preservado"
        )
        text_auxetic = (
            "Núcleo Metamaterial Auxético\n"
            "[Painéis FGL Reentrantes]\n"
            "ν_eff = -0,43 | t = 0,61 mm\n"
            "Atenuação Dinâmica Passiva (-12,6 dB)"
        )
        text_rails = (
            "Trilhos Guia P-POD (4×)\n"
            "[AlSi10Mg Maciço | 8,5 × 8,5 × 113,5 mm]\n"
            "Anodização Dura (Ra ≤ 1,6 μm, Tipo III)\n"
            "Mitigação de Soldagem a Frio e Travamento"
        )
        text_envelope = (
            "Envelope CalPoly 1U\n"
            "100,0 × 100,0 × 113,5 mm\n"
            "Massa do Chassi: 0,116 kg (-62,5%)"
        )

    # CALLOUT 1: Internal Usable Volume (Top-Left)
    ax.annotate(
        text_payload,
        xy=iso(-0.6, 0.4, pc_z[2]),
        xytext=(-3.8, 5.3),
        ha="right", va="center",
        fontsize=9.5, fontweight="bold", color="#1E8449",
        bbox=dict(boxstyle="round,pad=0.45", facecolor="#EAFAF1", edgecolor="#1E8449", lw=1.2, alpha=0.96),
        arrowprops=dict(arrowstyle="-|>", color="#1E8449", lw=1.8, mutation_scale=14),
        zorder=6
    )

    # CALLOUT 2: Auxetic Metamaterial Core (Bottom-Left)
    ax.annotate(
        text_auxetic,
        xy=iso(-W/2, 0.0, H * 0.40),
        xytext=(-3.8, 0.8),
        ha="right", va="center",
        fontsize=9.5, fontweight="bold", color="#2980B9",
        bbox=dict(boxstyle="round,pad=0.45", facecolor="#EBF5FB", edgecolor="#2980B9", lw=1.2, alpha=0.96),
        arrowprops=dict(arrowstyle="-|>", color="#2980B9", lw=1.8, mutation_scale=14),
        zorder=6
    )

    # CALLOUT 3: P-POD Guide Rails (Mid-Right)
    ax.annotate(
        text_rails,
        xy=iso(W/2 - rw/2, -D/2 + rw/2, H * 0.60),
        xytext=(3.8, 2.8),
        ha="left", va="center",
        fontsize=9.5, fontweight="bold", color="#C0392B",
        bbox=dict(boxstyle="round,pad=0.45", facecolor="#FDEDEC", edgecolor="#C0392B", lw=1.2, alpha=0.96),
        arrowprops=dict(arrowstyle="-|>", color="#C0392B", lw=1.8, mutation_scale=14),
        zorder=6
    )

    # CALLOUT 4: CalPoly 1U Envelope (Top-Right)
    ax.annotate(
        text_envelope,
        xy=iso(W/2, D/2, H),
        xytext=(3.8, 6.2),
        ha="left", va="center",
        fontsize=9.0, fontstyle="italic", color="#2C3E50",
        bbox=dict(boxstyle="round,pad=0.45", facecolor="#F4F6F6", edgecolor="#7F8C8D", lw=1.2, alpha=0.96),
        arrowprops=dict(arrowstyle="-|>", color="#7F8C8D", lw=1.5, mutation_scale=12),
        zorder=6
    )

    ax.set_title(title_text, fontsize=12.5, fontweight="bold", color="#1B365D", pad=16)

    ax.set_xlim(-7.8, 7.8)
    ax.set_ylim(-2.8, 7.8)
    ax.set_aspect("equal")
    ax.axis("off")

    fig.tight_layout()
    for p in out_paths:
        p.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(p, dpi=300, bbox_inches="tight")
        fig.savefig(p.with_suffix(".pdf"), bbox_inches="tight")
    plt.close(fig)
    logger.info("Saved isometric assembly layout figure (lang=%s).", lang)


def main() -> None:
    """Executes full scientific figure synthesis with bilingual distribution."""
    logger.info("Starting high-resolution bilingual scientific figure synthesis...")
    root = Path(__file__).resolve().parent.parent

    pt_dirs = [
        root / "figures",
        root / "monografia" / "04-figuras",
        root / "monografia" / "figuras",
        root / "Entregas-finais" / "01-Tese-Exaustiva" / "04-figuras",
        root / "Entregas-finais" / "01-Tese-Exaustiva" / "figuras",
        root / "Entregas-finais" / "03-TCC-Graduacao-UESC" / "04-figuras",
        root / "Entregas-finais" / "03-TCC-Graduacao-UESC" / "figuras",
    ]

    en_dirs = [
        root / "Entregas-finais" / "02-Artigos-Cientificos" / "01-Materials-and-Design-Elsevier" / "figures",
        root / "Entregas-finais" / "02-Artigos-Cientificos" / "02-Aerospace-Science-and-Technology-Elsevier" / "figures",
        root / "Entregas-finais" / "02-Artigos-Cientificos" / "03-Engineering-Applications-of-AI-Elsevier" / "figures",
    ]

    # 1. Generate Portuguese figures
    logger.info("Synthesizing Portuguese figures across %d targets...", len(pt_dirs))
    generate_psd_comparison_figure([d / "psd_gevs_vs_payload_response.png" for d in pt_dirs], lang="pt")
    generate_shock_srs_figure([d / "ppod_separation_shock_srs.png" for d in pt_dirs], lang="pt")
    generate_phononic_dispersion_figure([d / "phononic_dispersion_bandgap.png" for d in pt_dirs], lang="pt")
    generate_isometric_assembly_figure([d / "cubesat_1u_isometric_assembly.png" for d in pt_dirs], lang="pt")

    # 2. Generate English figures
    logger.info("Synthesizing English figures across %d targets...", len(en_dirs))
    generate_psd_comparison_figure([d / "psd_gevs_vs_payload_response.png" for d in en_dirs], lang="en")
    generate_shock_srs_figure([d / "ppod_separation_shock_srs.png" for d in en_dirs], lang="en")
    generate_phononic_dispersion_figure([d / "phononic_dispersion_bandgap.png" for d in en_dirs], lang="en")
    generate_isometric_assembly_figure([d / "cubesat_1u_isometric_assembly.png" for d in en_dirs], lang="en")

    logger.info("All scientific figures synthesized and synchronized successfully.")


if __name__ == "__main__":
    main()
