"""Generates publication-grade scientific figures for metallic Laser Powder Bed Fusion (L-PBF).

Redesign (academic-figures-plots skill, double-column 7.2 in width):
    * The former two-panel composite is split into TWO full-width figures so that every
      label can be set at >= 8 pt on the final page width:
        - ``lpbf_am_build_chamber``  : panel (a), L-PBF chamber and 45 deg build orientation.
        - ``lpbf_am_scan_strategy``  : panel (b), laser scan strategy and process window.
    * Anti-collision architecture: all explanatory callouts live in a column OUTSIDE the
      chamber drawing (panel a) or in dedicated free bands (panel b); leader lines only
      touch the geometry they annotate. Every axes uses an equal-aspect data grid
      (1 data unit = 0.05 in) so that the 45 deg chassis is not distorted.
    * Vector-first export (.pdf with embedded TrueType fonts) plus 300 dpi raster (.png).
"""

from __future__ import annotations

import logging
import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.patches import Arc, Ellipse, Polygon, Rectangle  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("generate_lpbf_am_figure")

# --------------------------------------------------------------------------- #
# Global style
# --------------------------------------------------------------------------- #
UNIT_IN = 0.05  # inches per data unit (equal aspect on both axes)
FS_TITLE = 10.0
FS_LABEL = 8.5
FS_SMALL = 8.0

plt.rcParams.update(
    {
        "font.family": "serif",
        "font.serif": ["Latin Modern Roman", "STIXGeneral", "DejaVu Serif"],
        "mathtext.fontset": "cm",
        "font.size": FS_LABEL,
        "axes.linewidth": 0.8,
        "lines.linewidth": 1.2,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "savefig.pad_inches": 0.03,
    }
)

# Palette (Okabe-Ito / slate engineering tones)
C_WALL = "#1E293B"
C_INK = "#0F172A"
C_MUTED = "#475569"
C_POWDER = "#E2E8F0"
C_POWDER_EDGE = "#94A3B8"
C_AUX = "#0072B2"
C_SUPPORT = "#B91C1C"
C_LASER = "#E69F00"
C_HATCH = "#009E73"
C_ORANGE = "#D55E00"
C_BOX_EDGE = "#94A3B8"


def _new_canvas(width_units: float, height_units: float) -> tuple[plt.Figure, plt.Axes]:
    """Creates a figure whose axes fill the canvas with an equal-aspect data grid.

    Args:
        width_units: Canvas width in data units (1 unit = ``UNIT_IN`` inches).
        height_units: Canvas height in data units.

    Returns:
        Tuple of figure and the full-canvas axes (axis lines hidden).
    """
    fig = plt.figure(figsize=(width_units * UNIT_IN, height_units * UNIT_IN), dpi=300)
    ax = fig.add_axes((0.0, 0.0, 1.0, 1.0))
    ax.set_xlim(0, width_units)
    ax.set_ylim(0, height_units)
    ax.set_aspect("equal")
    ax.axis("off")
    return fig, ax


def _callout(
    ax: plt.Axes,
    text: str,
    box_xy: tuple[float, float],
    target_xy: tuple[float, float],
    color: str,
    edge: str = C_BOX_EDGE,
) -> None:
    """Draws a boxed text callout with a leader line to ``target_xy``.

    Args:
        ax: Target axes.
        text: Box content (mathtext allowed).
        box_xy: Left-centre anchor of the text box in data units.
        target_xy: Point on the geometry that the leader line touches.
        color: Text and leader colour.
        edge: Box edge colour.
    """
    ax.annotate(
        text,
        xy=target_xy,
        xytext=box_xy,
        ha="left",
        va="center",
        fontsize=FS_LABEL,
        color=color,
        linespacing=1.45,
        bbox=dict(boxstyle="square,pad=0.45", facecolor="#FFFFFF", edgecolor=edge, lw=0.8),
        arrowprops=dict(
            arrowstyle="-|>",
            color=color,
            lw=0.9,
            shrinkA=0,
            shrinkB=1.5,
            relpos=(0.0, 0.5),
            mutation_scale=7,
        ),
        zorder=12,
    )


# --------------------------------------------------------------------------- #
# Figure (a): build chamber
# --------------------------------------------------------------------------- #
def draw_build_chamber(ax: plt.Axes) -> None:
    """Draws the L-PBF chamber (EOS M 290 layout) with the 45 deg chassis orientation.

    Args:
        ax: Full-canvas axes of size 144 x 108 data units.
    """
    # Chamber geometry (data units)
    x0, x1, y0, y1 = 2.0, 92.0, 2.0, 100.0
    div_l, div_r = 22.0, 76.0
    surface_y = 60.0
    plate_y0, plate_y1 = 10.0, 16.0
    cx0, cz0 = 49.0, 26.0

    # Enclosure and roof banner
    ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, facecolor="#F8FAFC", edgecolor=C_WALL, lw=1.8, zorder=1))
    ax.add_patch(Rectangle((x0, 93.0), x1 - x0, y1 - 93.0, facecolor=C_POWDER, edgecolor=C_WALL, lw=0.9, zorder=2))
    ax.text(
        (x0 + x1) / 2, 96.5, r"Argon Inert Atmosphere ($\mathrm{O}_2 < 100\ \mathrm{ppm}$)",
        ha="center", va="center", fontsize=FS_LABEL, color=C_INK, fontweight="bold", zorder=4,
    )

    # Dividers and powder fields
    for xd in (div_l, div_r):
        ax.plot([xd, xd], [y0, surface_y], color=C_WALL, lw=1.4, zorder=3)
    ax.add_patch(Rectangle((x0 + 0.5, plate_y0), div_l - x0 - 1.0, surface_y - plate_y0, facecolor=C_POWDER, alpha=0.9, zorder=2))
    ax.add_patch(Rectangle((div_l + 0.5, plate_y1), div_r - div_l - 1.0, surface_y - plate_y1, facecolor=C_POWDER, alpha=0.55, zorder=2))
    ax.add_patch(Rectangle((div_r + 0.5, y0 + 0.5), x1 - div_r - 1.0, 30.0 - y0, facecolor=C_POWDER, alpha=0.55, zorder=2))

    # A. Powder supply well: feed piston head, rod and +Z arrow
    ax.add_patch(Rectangle((x0 + 1.0, 27.0), div_l - x0 - 2.0, 4.0, facecolor="#64748B", edgecolor=C_WALL, lw=0.9, zorder=4))
    ax.plot([12.0, 12.0], [y0 + 1.0, 27.0], color=C_WALL, lw=2.6, zorder=3)
    ax.annotate("", xy=(6.5, 23.0), xytext=(6.5, 8.0),
                arrowprops=dict(arrowstyle="-|>", color=C_INK, lw=1.2, mutation_scale=8), zorder=5)
    ax.text(6.5, 24.8, r"$+Z$", fontsize=FS_LABEL, color=C_INK, va="center", ha="center", fontweight="bold", zorder=5)
    ax.text(12.0, 38.0, "Feed\nPiston", ha="center", va="center", fontsize=FS_SMALL, color=C_MUTED, linespacing=1.3, zorder=5)

    # B. Build well: platform, rod and -Z arrow
    ax.add_patch(Rectangle((div_l + 1.5, plate_y0 + 0.0), div_r - div_l - 3.0, plate_y1 - plate_y0,
                           facecolor="#475569", edgecolor=C_WALL, lw=1.1, zorder=4))
    ax.text((div_l + div_r) / 2, (plate_y0 + plate_y1) / 2,
            r"Heated Substrate Platform ($T = 150^\circ\mathrm{C}$)",
            ha="center", va="center", fontsize=FS_SMALL, color="#FFFFFF", fontweight="bold", zorder=5)
    ax.plot([cx0, cx0], [y0 + 1.0, plate_y0], color=C_WALL, lw=3.0, zorder=3)
    ax.annotate("", xy=(cx0 + 4.0, 4.5), xytext=(cx0 + 4.0, 9.0),
                arrowprops=dict(arrowstyle="-|>", color=C_SUPPORT, lw=1.2, mutation_scale=8), zorder=5)
    ax.text(cx0 + 6.0, 6.5, r"$-Z\ (\Delta z = 30\ \mu\mathrm{m})$", fontsize=FS_SMALL, color=C_SUPPORT,
            va="center", ha="left", zorder=5)

    # C. Overflow well
    ax.text((div_r + x1) / 2, 9.0, "Overflow", ha="center", va="center", fontsize=FS_SMALL,
            color=C_MUTED, rotation=90, zorder=4)

    # Recoater blade moving left over the powder surface
    rx = 66.0
    blade = [(rx, surface_y + 9.0), (rx + 3.5, surface_y + 9.0), (rx + 3.5, surface_y + 2.0),
             (rx + 1.8, surface_y), (rx, surface_y)]
    ax.add_patch(Polygon(blade, facecolor="#334155", edgecolor=C_INK, lw=0.9, zorder=8))
    ax.add_patch(Polygon([(rx - 5.0, surface_y), (rx - 1.2, surface_y + 2.8), (rx, surface_y + 0.8), (rx, surface_y)],
                         facecolor="#CBD5E1", edgecolor=C_POWDER_EDGE, lw=0.7, zorder=7))
    ax.annotate("", xy=(rx - 9.0, surface_y + 5.0), xytext=(rx - 1.0, surface_y + 5.0),
                arrowprops=dict(arrowstyle="-|>", color=C_INK, lw=1.2, mutation_scale=8), zorder=9)
    ax.text(rx + 1.8, surface_y + 10.0, r"Blade ($100\ \mathrm{mm/s}$)", ha="center", va="bottom",
            fontsize=FS_SMALL, color=C_INK, fontweight="bold", zorder=9)

    # Laminar argon flow
    for gy in (74.5, 77.5):
        ax.annotate("", xy=(x1 - 3.0, gy), xytext=(x0 + 6.0, gy),
                    arrowprops=dict(arrowstyle="-|>", color=C_AUX, lw=0.8, ls="--", alpha=0.65, mutation_scale=7), zorder=4)
    ax.text(x0 + 6.0, 80.8, r"Laminar Argon Flow ($v \approx 2.5\ \mathrm{m/s}$)", ha="left", va="center",
            fontsize=FS_SMALL, color=C_AUX, fontstyle="italic", zorder=5)

    # Galvo scanner
    gx_c = 56.0
    ax.add_patch(Rectangle((gx_c - 22.0, 83.0), 44.0, 7.0, facecolor=C_WALL, edgecolor=C_INK, lw=1.0, zorder=8))
    ax.text(gx_c, 86.5, r"Galvo Scanner & $f$-$\theta$ Lens", ha="center", va="center",
            fontsize=FS_LABEL, color="#FFFFFF", fontweight="bold", zorder=9)

    # 45 deg rotated chassis
    phi = math.radians(45.0)
    cos_p, sin_p = math.cos(phi), math.sin(phi)
    w_ch, h_ch, rail_t = 22.0, 26.0, 2.4

    def to_rot(lx: float, lz: float) -> tuple[float, float]:
        return cx0 + lx * cos_p - lz * sin_p, cz0 + lx * sin_p + lz * cos_p

    # Sacrificial support under the lowest rail corner + wire-EDM cut line
    b0, b1 = to_rot(0, 0), to_rot(rail_t, 0)
    sup = [(b0[0] - 1.2, plate_y1), (b1[0] + 1.2, plate_y1), (b1[0] + 1.2, b1[1]), (b0[0] - 1.2, b0[1])]
    ax.add_patch(Polygon(sup, facecolor="#FEE2E2", edgecolor=C_SUPPORT, lw=1.0, ls="--", zorder=4))
    for sx in np.linspace(b0[0] - 0.8, b1[0] + 0.8, 4):
        ax.plot([sx, sx + 1.0], [plate_y1, b0[1]], color=C_SUPPORT, lw=0.6, zorder=5)
    cut_y = 19.5
    ax.plot([b0[0] - 5.0, b1[0] + 5.0], [cut_y, cut_y], color="#991B1B", lw=1.0, ls="-.", zorder=6)
    ax.text(b0[0] - 6.5, cut_y, "Wire-EDM\nCut Line", fontsize=FS_SMALL, color="#991B1B", va="center",
            ha="right", fontweight="bold", linespacing=1.3, zorder=7)

    # Rails (solid) + inner cavity
    cavity = [to_rot(rail_t, rail_t), to_rot(w_ch - rail_t, rail_t),
              to_rot(w_ch - rail_t, h_ch - rail_t), to_rot(rail_t, h_ch - rail_t)]
    ax.add_patch(Polygon(cavity, facecolor="#F0F9FF", edgecolor="none", zorder=4))
    rails = [
        [to_rot(0, 0), to_rot(w_ch, 0), to_rot(w_ch, rail_t), to_rot(0, rail_t)],
        [to_rot(0, h_ch - rail_t), to_rot(w_ch, h_ch - rail_t), to_rot(w_ch, h_ch), to_rot(0, h_ch)],
        [to_rot(0, rail_t), to_rot(rail_t, rail_t), to_rot(rail_t, h_ch - rail_t), to_rot(0, h_ch - rail_t)],
        [to_rot(w_ch - rail_t, rail_t), to_rot(w_ch, rail_t), to_rot(w_ch, h_ch - rail_t), to_rot(w_ch - rail_t, h_ch - rail_t)],
    ]
    for poly in rails:
        ax.add_patch(Polygon(poly, facecolor="#CBD5E1", edgecolor=C_INK, lw=1.1, zorder=6))

    # Re-entrant auxetic cells
    dx_w, dz_h, dz_in = 2.2, 1.9, 0.7
    for gx in np.linspace(rail_t + 3.4, w_ch - rail_t - 3.4, 3):
        for gz in np.linspace(rail_t + 3.4, h_ch - rail_t - 3.4, 4):
            cell = [to_rot(gx - dx_w, gz - dz_h), to_rot(gx, gz - dz_in), to_rot(gx + dx_w, gz - dz_h),
                    to_rot(gx + dx_w, gz + dz_h), to_rot(gx, gz + dz_in), to_rot(gx - dx_w, gz + dz_h)]
            ax.add_patch(Polygon(cell, facecolor="none", edgecolor=C_AUX, lw=1.0, zorder=6))

    # Laser beam and melt pool on top edge
    hit = to_rot(w_ch * 0.80, h_ch)
    ax.plot([gx_c, hit[0]], [83.0, hit[1]], color=C_LASER, lw=1.7, zorder=7)
    ax.plot(hit[0], hit[1], marker="o", markersize=5.0, color="#D62828", zorder=9)
    ax.plot(hit[0], hit[1], marker="*", markersize=6.5, color="#FEF08A", zorder=10)

    # Build angle indicator
    ax.plot([cx0, cx0 + 14.0], [cz0, cz0], color="#64748B", ls=":", lw=1.1, zorder=5)
    ax.add_patch(Arc((cx0, cz0), 20.0, 20.0, theta1=0, theta2=45, color=C_SUPPORT, lw=1.3, zorder=7))

    # Right-hand callout column (outside the chamber)
    bx = 98.0
    _callout(
        ax,
        "Laser Exposure:\n" + r"$\bullet\ P = 200\ \mathrm{W}\ (\lambda = 1070\ \mathrm{nm})$" + "\n"
        + r"$\bullet\ d_{\mathrm{spot}} = 70\ \mu\mathrm{m}$",
        (bx, 86.0), (gx_c + 22.0, 86.5), "#92400E",
    )
    core_pt = to_rot(w_ch * 0.5, h_ch * 0.5)
    _callout(
        ax,
        "Self-Supporting Core:\n" + r"$\bullet\ \theta_{\mathrm{overhang}} \geq 35^\circ\ (\mathrm{min.}\ 45^\circ)$" + "\n"
        + r"$\bullet\ \mathrm{Zero\ internal\ supports}$" + "\n"
        + r"$\bullet\ d_{\mathrm{drain}} \geq 2.0\ \mathrm{mm}\ (\mathrm{drain})$",
        (bx, 54.0), core_pt, "#005A8C",
    )
    arc_mid = (cx0 + 10.0 * math.cos(math.radians(22.5)), cz0 + 10.0 * math.sin(math.radians(22.5)))
    _callout(
        ax,
        "Build orientation:\n" + r"$\theta_{\mathrm{build}} = 45.0^\circ$" + " (vs. build plate)",
        (bx, 28.0), arc_mid, "#B91C1C",
    )
    _callout(
        ax,
        "Sacrificial support:\nlowest rail corner only,\nremoved by wire-EDM",
        (bx, 14.0), (b1[0] + 1.2, 22.0), "#991B1B",
    )

    ax.text(72.0, 105.0, r"(a) L-PBF Build Chamber & $45^\circ$ Orientation", ha="center", va="center",
            fontsize=FS_TITLE, fontweight="bold", color=C_INK)


# --------------------------------------------------------------------------- #
# Figure (b): scan strategy + process window
# --------------------------------------------------------------------------- #
def draw_scan_strategy(ax: plt.Axes) -> None:
    """Draws the layer scan strategy schematic and the certified process-parameter card.

    Args:
        ax: Full-canvas axes of size 144 x 124 data units.
    """
    # ---- Solidified prior layer (N-1)
    ax.add_patch(Rectangle((4.0, 52.0), 136.0, 8.0, facecolor="#F1F5F9", edgecolor="none", zorder=1))
    for hx in np.linspace(5.0, 138.0, 52):
        ax.plot([hx, hx + 2.2], [52.0, 60.0], color=C_POWDER_EDGE, lw=0.5, alpha=0.7, zorder=2)
    ax.plot([4.0, 140.0], [60.0, 60.0], color=C_INK, ls="--", lw=0.9, zorder=3)
    ax.text(72.0, 56.0, r"Solidified Prior Layer $(N-1)$ [$\Delta z = 30\ \mu\mathrm{m}$, Fully Dense]",
            ha="center", va="center", fontsize=FS_LABEL, color="#334155", fontweight="bold", zorder=4,
            bbox=dict(boxstyle="square,pad=0.25", facecolor="#F1F5F9", edgecolor="none"))

    # ---- Powder layer N with spherical particles
    rng = np.random.default_rng(101)
    for px, py, pr in zip(rng.uniform(5.0, 139.0, 90), rng.uniform(62.5, 72.0, 90), rng.uniform(0.6, 1.4, 90)):
        if 26.0 <= px <= 118.0 and 63.2 <= py <= 70.8:
            continue  # keep the label zone free of particles
        ax.add_patch(plt.Circle((px, py), pr, facecolor="#CBD5E1", edgecolor="#64748B", lw=0.4, zorder=3))
    ax.text(72.0, 67.0, r"AlSi10Mg Powder Layer $N$ ($\Delta z = 30\ \mu\mathrm{m}$, PSD $20\text{--}63\ \mu\mathrm{m}$)",
            ha="center", va="center", fontsize=FS_LABEL, color="#1E293B", fontweight="bold", zorder=5,
            bbox=dict(boxstyle="square,pad=0.3", facecolor="#FFFFFF", edgecolor=C_BOX_EDGE, lw=0.7))

    # ---- Scan-speed note
    ax.text(72.0, 77.0,
            r"Double Contour ($800\ \mathrm{mm/s}$)  $\mid$  Stripe Hatching ($1000\ \mathrm{mm/s}$)",
            ha="center", va="center", fontsize=FS_LABEL, color="#1E293B", zorder=6,
            bbox=dict(boxstyle="square,pad=0.3", facecolor="#F8FAFC", edgecolor=C_BOX_EDGE, lw=0.7))

    # ---- Strut section under exposure
    s_x0, s_x1, s_y0, s_y1 = 42.0, 118.0, 83.0, 107.0
    off = 2.0
    ax.add_patch(Rectangle((s_x0, s_y0), s_x1 - s_x0, s_y1 - s_y0, facecolor="#F0F9FF", edgecolor="none", zorder=2))
    ax.plot([s_x0, s_x1, s_x1, s_x0, s_x0], [s_y0, s_y0, s_y1, s_y1, s_y0], color=C_INK, lw=2.0, zorder=6)
    ax.plot([s_x0 + off, s_x1 - off, s_x1 - off, s_x0 + off, s_x0 + off],
            [s_y0 + off, s_y0 + off, s_y1 - off, s_y1 - off, s_y0 + off],
            color=C_AUX, lw=1.2, ls="--", zorder=6)

    levels = np.linspace(s_y0 + off + 2.4, s_y1 - off - 2.4, 4)
    xa, xb = s_x0 + off + 3.0, s_x1 - off - 3.0
    for i, hy in enumerate(levels):
        start, end = (xa, xb) if i % 2 == 0 else (xb, xa)
        ax.annotate("", xy=(end, hy), xytext=(start, hy),
                    arrowprops=dict(arrowstyle="-|>", color=C_HATCH, lw=1.5, mutation_scale=8), zorder=7)

    # Hatch spacing dimension (right of strut)
    ax.annotate("", xy=(s_x1 + 3.0, levels[2]), xytext=(s_x1 + 3.0, levels[1]),
                arrowprops=dict(arrowstyle="<|-|>", color=C_ORANGE, lw=1.1, mutation_scale=7), zorder=8)
    ax.text(s_x1 + 5.0, (levels[1] + levels[2]) / 2, r"$h_s = 105\ \mu\mathrm{m}$", fontsize=FS_LABEL,
            color=C_ORANGE, va="center", ha="left", fontweight="bold", zorder=8)

    # Laser beam + melt pool (last, leftward-travelling hatch level)
    lx, ly = xb - 1.0, levels[-1]
    for sgn in (-1.0, 1.0):
        ax.plot([lx + sgn * 3.0, lx], [ly + 10.0, ly], color=C_LASER, lw=1.6, zorder=8)
    ax.text(lx, ly + 11.2, r"Laser ($70\ \mu\mathrm{m}$)", ha="center", va="bottom", fontsize=FS_LABEL,
            color="#92400E", fontweight="bold", zorder=9)
    ax.add_patch(Ellipse((lx, ly), 5.6, 3.0, facecolor="#D62828", edgecolor="#991B1B", lw=0.9, zorder=9))
    ax.add_patch(Ellipse((lx, ly), 2.6, 1.4, facecolor="#FDE047", edgecolor="none", zorder=10))
    ax.annotate(r"Melt Pool Penetration ($\approx 1.5\,\Delta z$)", xy=(lx - 2.8, ly + 0.5), xytext=(s_x0 + 2.0, s_y1 + 4.5),
                ha="left", va="center", fontsize=FS_LABEL, color="#991B1B", fontweight="bold",
                arrowprops=dict(arrowstyle="-|>", color="#991B1B", lw=0.9, shrinkA=2, shrinkB=1, mutation_scale=7,
                                connectionstyle="arc3,rad=-0.15"), zorder=11)

    # Strut-thickness dimension on the left (outside the strut)
    dim_x = s_x0 - 3.0
    ax.annotate("", xy=(dim_x, s_y1), xytext=(dim_x, s_y0),
                arrowprops=dict(arrowstyle="<|-|>", color=C_INK, lw=1.0, mutation_scale=7), zorder=8)
    ax.text(dim_x - 2.5, (s_y0 + s_y1) / 2,
            "Strut thickness\n" + r"$t = 0.613\ \mathrm{mm}$" + "\n" + r"($\geq 0.50\ \mathrm{mm}$ DfAM limit)",
            ha="right", va="center", fontsize=FS_LABEL, color=C_INK, linespacing=1.4, zorder=9)

    # Interlayer rotation compass (top-left)
    cxy = (8.0, 106.0)
    ax.annotate("", xy=(cxy[0] + 13.0, cxy[1]), xytext=cxy,
                arrowprops=dict(arrowstyle="-|>", color="#64748B", lw=1.2, mutation_scale=8), zorder=8)
    ax.text(cxy[0] + 6.5, cxy[1] - 2.4, r"Layer $N-1$", ha="center", va="top", fontsize=FS_SMALL, color="#475569")
    rad = math.radians(67.0)
    tip = (cxy[0] + 13.0 * math.cos(rad), cxy[1] + 13.0 * math.sin(rad))
    ax.annotate("", xy=tip, xytext=cxy, arrowprops=dict(arrowstyle="-|>", color="#B91C1C", lw=1.3, mutation_scale=8), zorder=8)
    ax.text(tip[0] + 1.0, tip[1] + 0.3, r"Layer $N$", ha="left", va="center", fontsize=FS_SMALL, color="#B91C1C", fontweight="bold")
    ax.add_patch(Arc(cxy, 9.0, 9.0, theta1=0, theta2=67, color="#B91C1C", lw=1.1, zorder=8))
    ax.text(cxy[0] + 6.0, cxy[1] + 3.6, r"$67^\circ$", fontsize=FS_SMALL, color="#B91C1C", fontweight="bold", ha="left", va="center")

    # ---- Certified process-window card
    ax.add_patch(Rectangle((2.0, 2.0), 140.0, 46.0, facecolor="#F8FAFC", edgecolor=C_WALL, lw=1.1, zorder=1))
    ax.text(72.0, 44.5, "L-PBF CERTIFIED PROCESS PARAMETERS (EOS M 290 / AlSi10Mg)", ha="center", va="center",
            fontsize=FS_LABEL + 0.5, color=C_INK, fontweight="bold", zorder=3)
    ax.plot([5.0, 139.0], [41.8, 41.8], color=C_WALL, lw=0.9, zorder=3)
    ax.text(37.0, 39.3, "Laser Exposure & Energy", ha="center", va="center", fontsize=FS_LABEL, color="#005A8C",
            fontweight="bold")
    ax.text(107.0, 39.3, "Hatching & Densification", ha="center", va="center", fontsize=FS_LABEL, color="#005A8C",
            fontweight="bold")
    ax.plot([5.0, 139.0], [36.8, 36.8], color=C_POWDER_EDGE, lw=0.6, ls="--", zorder=3)
    ax.plot([72.0, 72.0], [5.0, 40.5], color=C_POWDER_EDGE, lw=0.6, zorder=3)

    col1 = [
        r"$\bullet$ Laser Power: $P = 200\ \mathrm{W}$ (Yb-fiber)",
        r"$\bullet$ Hatch Velocity: $v = 1000\ \mathrm{mm/s}$",
        r"$\bullet$ Contour Velocity: $v_c = 800\ \mathrm{mm/s}$",
        r"$\bullet$ Spot Diameter: $d_{\mathrm{spot}} = 70\ \mu\mathrm{m}$",
        r"$\bullet$ Layer Height: $\Delta z = 30\ \mu\mathrm{m}$",
    ]
    col2 = [
        r"$\bullet$ Hatch Spacing: $h_s = 105\ \mu\mathrm{m}$",
        r"$\bullet$ Interlayer Rotation: $\Delta\alpha = 67.0^\circ$",
        r"$\bullet$ Volumetric Energy: $\mathbf{E_v = 63.49\ J/mm^3}$",
        r"$\bullet$ Relative Density: $\mathbf{> 99.8\%}$ (Dense)",
        r"$\bullet$ Platform Preheat: $T_p = 150^\circ\mathrm{C}$",
    ]
    for yp, a, b in zip(np.linspace(32.5, 8.5, 5), col1, col2):
        ax.text(6.0, yp, a, fontsize=FS_LABEL, color="#1E293B", va="center", ha="left", zorder=4)
        ax.text(76.0, yp, b, fontsize=FS_LABEL, color="#1E293B", va="center", ha="left", zorder=4)

    ax.text(72.0, 119.5, r"(b) Laser Scan Strategy & Process Window", ha="center", va="center",
            fontsize=FS_TITLE, fontweight="bold", color=C_INK)


def _save(fig: plt.Figure, png_paths: list[Path]) -> None:
    """Saves ``fig`` as PNG (300 dpi) and vector PDF next to each requested path.

    Args:
        fig: Figure to export.
        png_paths: Destination PNG paths; a sibling ``.pdf`` is also written.
    """
    for p in png_paths:
        p.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(p, dpi=300)
        fig.savefig(p.with_suffix(".pdf"))
        logger.info("Saved %s (+ .pdf)", p)


def generate_lpbf_am_figures(target_dirs: list[Path]) -> list[str]:
    """Generates the two L-PBF figures and writes them into every target directory.

    Args:
        target_dirs: Directories receiving both figures (PNG + PDF).

    Returns:
        Base names of the generated figures.
    """
    logger.info("Synthesizing L-PBF figure (a): build chamber ...")
    fig_a, ax_a = _new_canvas(144.0, 108.0)
    draw_build_chamber(ax_a)
    _save(fig_a, [d / "lpbf_am_build_chamber.png" for d in target_dirs])
    plt.close(fig_a)

    logger.info("Synthesizing L-PBF figure (b): scan strategy & process window ...")
    fig_b, ax_b = _new_canvas(144.0, 124.0)
    draw_scan_strategy(ax_b)
    _save(fig_b, [d / "lpbf_am_scan_strategy.png" for d in target_dirs])
    plt.close(fig_b)
    return ["lpbf_am_build_chamber", "lpbf_am_scan_strategy"]


def main() -> None:
    """Entry point: synchronizes figures across all article and thesis directories."""
    root = Path(__file__).resolve().parent.parent
    ef = root / "Entregas-finais"
    target_dirs = [
        root / "figures",
        ef / "01-Tese-Exaustiva" / "figuras",
        ef / "01-Tese-Exaustiva" / "04-figuras",
        ef / "02-Artigos-Cientificos" / "01-Materials-and-Design-Elsevier" / "figures",
        ef / "02-Artigos-Cientificos" / "02-Aerospace-Science-and-Technology-Elsevier" / "figures",
        ef / "02-Artigos-Cientificos" / "03-Engineering-Applications-of-AI-Elsevier" / "figures",
        ef / "03-TCC-Graduacao-UESC" / "figuras",
        ef / "03-TCC-Graduacao-UESC" / "04-figuras",
        ef / "04-Monografia-SpringerBriefs" / "figures",
        root / "monografia" / "figuras",
        root / "monografia" / "04-figuras",
    ]
    generate_lpbf_am_figures([d for d in target_dirs if d.exists()])
    logger.info("Successfully produced and synchronized all L-PBF additive manufacturing figures!")


if __name__ == "__main__":
    main()
