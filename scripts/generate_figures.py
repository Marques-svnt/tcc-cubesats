"""Generates publication-quality technical schematic diagrams for monographs and scientific articles.

Outputs:
- auxetic_cell_geometry.png: Geometric schematic of the 2D re-entrant auxetic unit cell.
- multi_agent_workflow.png: Deterministic multi-agent state machine flowchart (LangGraph).
"""

import logging
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Enable publication fonts
plt.rcParams["font.sans-serif"] = "DejaVu Sans"
plt.rcParams["font.family"] = "sans-serif"


def generate_auxetic_cell_figure(output_path: Path, lang: str = "pt") -> None:
    """Plots a 2D geometric schematic of the canonical re-entrant auxetic unit cell.

    Args:
        output_path: Destination file path for the generated PNG.
        lang: Language for titles and dimension callouts ('pt' for Portuguese, 'en' for English).
    """
    fig, ax = plt.subplots(figsize=(8.4, 6.6), dpi=300)

    # Premium color palette (Elsevier / ASME standard)
    strut_color = "#1B365D"    # Deep navy for structural ribs
    dim_color_h = "#C0392B"    # Ruby red for vertical height h
    dim_color_l = "#27AE60"    # Emerald green for inclined length l
    dim_color_th = "#8E44AD"   # Royal purple for re-entrant angle theta
    dim_color_t = "#D35400"    # Amber orange for rib wall thickness t
    dim_color_gap = "#2980B9"  # Cerulean blue for central clearance gap
    ref_color = "#7F8C8D"      # Slate gray for reference lines

    # Geometric parameters of canonical re-entrant honeycomb
    h_val = 2.1          # vertical strut height
    l_val = 1.7          # inclined strut length
    theta_deg = 25.0     # re-entrant angle magnitude from horizontal
    theta_rad = np.radians(theta_deg)

    # Coordinate projections
    dx = l_val * np.cos(theta_rad)
    dy = l_val * np.sin(theta_rad)

    x_outer = 2.45
    x_inner = x_outer - dx   # re-entrant waist position (~ 0.91)
    y_mid = dy               # vertical half-spread of re-entrant vertex (~ 0.72)

    # Strut centerline segments
    struts = [
        # Left side
        ((-x_outer, y_mid + h_val), (-x_outer, y_mid)),
        ((-x_outer, y_mid), (-x_inner, 0)),
        ((-x_inner, 0), (-x_outer, -y_mid)),
        ((-x_outer, -y_mid), (-x_outer, -y_mid - h_val)),
        # Right side
        ((x_outer, y_mid + h_val), (x_outer, y_mid)),
        ((x_outer, y_mid), (x_inner, 0)),
        ((x_inner, 0), (x_outer, -y_mid)),
        ((x_outer, -y_mid), (x_outer, -y_mid - h_val)),
    ]

    # Plot struts as thick solid lines with rounded caps
    for p1, p2 in struts:
        ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color=strut_color, lw=7.0, solid_capstyle="round", zorder=3)

    # Highlight re-entrant hinge nodes
    hinge_nodes = [
        (-x_outer, y_mid), (-x_inner, 0), (-x_outer, -y_mid),
        (x_outer, y_mid), (x_inner, 0), (x_outer, -y_mid),
    ]
    for hx, hy in hinge_nodes:
        ax.plot(hx, hy, marker="o", markersize=5.5, color="#34495E", zorder=4)

    # Reference dashed horizontal lines at y = y_mid
    ax.plot([-x_outer, -x_outer + 1.4], [y_mid, y_mid], color=ref_color, ls="--", lw=1.3, zorder=2)
    ax.plot([x_outer - 1.4, x_outer], [y_mid, y_mid], color=ref_color, ls="--", lw=1.3, zorder=2)

    # Centerline across waist (symmetry axis)
    ax.plot([-x_outer - 0.4, x_outer + 0.4], [0, 0], color="#BDC3C7", ls=":", lw=1.1, zorder=1)

    # 1. Height h (Right side upper vertical strut)
    h_x_dim = x_outer + 0.45
    ax.annotate("", xy=(h_x_dim, y_mid), xytext=(h_x_dim, y_mid + h_val),
                arrowprops=dict(arrowstyle="<->", color=dim_color_h, lw=1.8, mutation_scale=14))
    # Extension ticks for h
    ax.plot([x_outer + 0.10, h_x_dim + 0.15], [y_mid, y_mid], color=dim_color_h, lw=1.2)
    ax.plot([x_outer + 0.10, h_x_dim + 0.15], [y_mid + h_val, y_mid + h_val], color=dim_color_h, lw=1.2)

    # 2. Wall Thickness t (Left side upper vertical strut)
    t_x = -x_outer
    t_y = y_mid + h_val * 0.60

    # 3. Angle theta (Left side inclined strut)
    arc_r = 1.05
    arc_angles = np.linspace(0, -theta_rad, 40)
    arc_x = -x_outer + arc_r * np.cos(arc_angles)
    arc_y = y_mid + arc_r * np.sin(arc_angles)
    ax.plot(arc_x, arc_y, color=dim_color_th, lw=2.0, zorder=4)
    # Arrow head for theta arc pointing down
    ax.annotate("", xy=(-x_outer + arc_r * np.cos(-theta_rad), y_mid + arc_r * np.sin(-theta_rad)),
                xytext=(-x_outer + (arc_r * 0.97) * np.cos(-theta_rad * 0.80), y_mid + (arc_r * 0.97) * np.sin(-theta_rad * 0.80)),
                arrowprops=dict(arrowstyle="-|>", color=dim_color_th, lw=2.0, mutation_scale=14))

    # 4. Length l (Right side lower inclined strut)
    perp = np.array([-dy, -dx]) / l_val
    offset_l = 0.45
    p1_dim = np.array([x_inner, 0]) + offset_l * perp
    p2_dim = np.array([x_outer, -y_mid]) + offset_l * perp

    ax.annotate("", xy=(p1_dim[0], p1_dim[1]), xytext=(p2_dim[0], p2_dim[1]),
                arrowprops=dict(arrowstyle="<->", color=dim_color_l, lw=1.8, mutation_scale=14))
    # Extension ticks
    t_len = 0.16
    ax.plot([p1_dim[0] - t_len * perp[0], p1_dim[0] + t_len * perp[0]],
            [p1_dim[1] - t_len * perp[1], p1_dim[1] + t_len * perp[1]], color=dim_color_l, lw=1.2)
    ax.plot([p2_dim[0] - t_len * perp[0], p2_dim[0] + t_len * perp[0]],
            [p2_dim[1] - t_len * perp[1], p2_dim[1] + t_len * perp[1]], color=dim_color_l, lw=1.2)

    # 5. Clearance gap across the central waist
    ax.annotate("", xy=(-x_inner + 0.05, 0), xytext=(x_inner - 0.05, 0),
                arrowprops=dict(arrowstyle="<->", color=dim_color_gap, lw=1.8, mutation_scale=13))

    # Text Labels
    if lang == "en":
        title = r"$\bf{2D\ Re\text{-}entrant\ Auxetic\ Unit\ Cell\ (\nu_{eff} < 0)}$"
        lbl_h = r"$\bf{h}$ (Vertical strut height)"
        lbl_l = r"$\bf{l}$ (Inclined strut length)"
        lbl_th = r"$\bf{\theta}$ (Re-entrant angle, $\theta < 0^\circ$)"
        lbl_t = r"Wall thickness $\bf{t}$"
        lbl_gap = r"Clearance $\bf{gap}$"
    else:
        title = r"$\bf{Célula\ Auxética\ Reentrante\ 2D\ (\nu_{eff} < 0)}$"
        lbl_h = r"$\bf{h}$ (Altura da costela vertical)"
        lbl_l = r"$\bf{l}$ (Comprimento da costela oblíqua)"
        lbl_th = r"$\bf{\theta}$ (Ângulo de reentrância, $\theta < 0^\circ$)"
        lbl_t = r"Espessura de costela $\bf{t}$"
        lbl_gap = r"Folga $\bf{gap}$"

    # Annotations with rounded publication callout boxes
    # Height h (Right Upper)
    ax.text(h_x_dim + 0.22, y_mid + h_val / 2, lbl_h, color=dim_color_h, fontsize=10.5,
            va="center", ha="left", fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.35", facecolor="#FDEDEC", edgecolor=dim_color_h, lw=1.0, alpha=0.96))

    # Wall thickness t (Left Upper)
    ax.annotate(lbl_t, xy=(t_x, t_y), xytext=(t_x - 0.65, t_y),
                arrowprops=dict(arrowstyle="->", color=dim_color_t, lw=1.8),
                fontsize=10.5, color=dim_color_t, fontweight="bold", va="center", ha="right",
                bbox=dict(boxstyle="round,pad=0.35", facecolor="#FEF9E7", edgecolor=dim_color_t, lw=1.0, alpha=0.96))

    # Theta (Left Mid / Re-entrant)
    ax.annotate(lbl_th, xy=(-x_outer + arc_r * 0.70, y_mid - arc_r * 0.30),
                xytext=(-x_outer - 0.65, y_mid - 0.50),
                arrowprops=dict(arrowstyle="->", color=dim_color_th, lw=1.6, connectionstyle="arc3,rad=0.15"),
                fontsize=10.5, color=dim_color_th, fontweight="bold", va="center", ha="right",
                bbox=dict(boxstyle="round,pad=0.35", facecolor="#F4ECF7", edgecolor=dim_color_th, lw=1.0, alpha=0.96))

    # Length l (Right Lower)
    mid_dim = (p1_dim + p2_dim) / 2.0
    ax.text(mid_dim[0] - 0.10, mid_dim[1] - 0.20, lbl_l, color=dim_color_l, fontsize=10.5,
            va="top", ha="right", fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.35", facecolor="#EAFAF1", edgecolor=dim_color_l, lw=1.0, alpha=0.96))

    # Clearance gap: placed cleanly in upper waist notch
    ax.text(0, 0.40, lbl_gap, color=dim_color_gap, fontsize=10.5,
            va="bottom", ha="center", fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.30", facecolor="#EBF5FB", edgecolor=dim_color_gap, lw=1.0, alpha=0.96))

    ax.set_title(title, fontsize=13.5, pad=18, color="#1B365D", fontweight="bold")

    ax.set_xlim(-x_outer - 2.8, x_outer + 3.2)
    ax.set_ylim(-y_mid - h_val - 0.6, y_mid + h_val + 0.8)
    ax.set_aspect("equal")
    ax.axis("off")

    fig.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    fig.savefig(output_path.with_suffix(".pdf"), bbox_inches="tight")
    plt.close(fig)
    logger.info("Generated %s (lang=%s)", output_path, lang)


def generate_multi_agent_workflow_figure(output_path: Path, lang: str = "pt") -> None:
    """Plots a clean, professional flowchart of the deterministic LangGraph multi-agent workflow.

    Args:
        output_path: Destination file path for the generated PNG.
        lang: Language for nodes and transitions ('pt' for Portuguese, 'en' for English).
    """
    fig, ax = plt.subplots(figsize=(10.5, 6.2), dpi=300)

    # Vertical levels
    y_main = 0.50
    y_reject = 0.14
    y_top = 0.84

    if lang == "en":
        title_text = "Deterministic Multi-Agent State Machine (LangGraph) for Aerospace Qualification"
        nodes = [
            ("Exploration & Optimization\nNSGA-II / LHS Sampling\n[θ, t, l, h]", 0.12, y_main, "#2C3E50", 0.18, 0.16),
            ("CadDfamAgent\nB-Rep Synthesis (build123d)\nLPBF DfAM AlSi10Mg Gates", 0.36, y_main, "#1B365D", 0.20, 0.16),
            ("NeuralSurrogateAgent\nPhysics-Guided ResNet\nGibson-Ashby / < 1 ms", 0.61, y_main, "#5B2C6F", 0.20, 0.16),
            ("GevsQualifierAgent\nNASA GSFC-7000A Standard\nf1, MS_yield, D_Steinberg", 0.86, y_main, "#117A65", 0.20, 0.16),
        ]
        transitions = [
            (0.12, 0.36, "DoE Sample\n[STEP / B-Rep]"),
            (0.36, 0.61, "DfAM Approved\n[Valid Geometry]"),
            (0.61, 0.86, "Dynamic Prediction\n[fn, σ_3σ, Grms]"),
        ]
        rej_dfam = ("REJECTED_DFAM\nImmediate Discard (Fail-Fast)\nAngle / Wall Violation", "DfAM Violation")
        rej_gevs = ("REJECTED_GEVS\nNASA Non-Compliant\nf1 < 100 Hz | MS < 0 | D > 0.25", "Normative Failure")
        qual_top = ("OpenFeaKernel (Ground Truth)\nCode_Aster / CalculiX Tet10 (Gmsh)\nOpenRadioss P-POD Shock / SRS", "NASA Qualified\n(TOPSIS #28)")
    else:
        title_text = "Máquina de Estados Multi-Agente Determinística (LangGraph) para Qualificação Aeroespacial"
        nodes = [
            ("Exploração & Otimização\nNSGA-II / Amostragem LHS\n[θ, t, l, h]", 0.12, y_main, "#2C3E50", 0.18, 0.16),
            ("CadDfamAgent\nSíntese B-Rep (build123d)\nPortões LPBF DfAM AlSi10Mg", 0.36, y_main, "#1B365D", 0.20, 0.16),
            ("NeuralSurrogateAgent\nPhysics-Guided ResNet\nGibson-Ashby / < 1 ms", 0.61, y_main, "#5B2C6F", 0.20, 0.16),
            ("GevsQualifierAgent\nNorma NASA GSFC-7000A\nf1, MS_yield, D_Steinberg", 0.86, y_main, "#117A65", 0.20, 0.16),
        ]
        transitions = [
            (0.12, 0.36, "Amostra DoE\n[STEP / B-Rep]"),
            (0.36, 0.61, "Aprovado DfAM\n[Geometria Válida]"),
            (0.61, 0.86, "Predição Dinâmica\n[fn, σ_3σ, Grms]"),
        ]
        rej_dfam = ("REJECTED_DFAM\nDescarte Imediato (Fail-Fast)\nViolação de Ângulo / Parede", "Violação DfAM")
        rej_gevs = ("REJECTED_GEVS\nNão-Conforme NASA\nf1 < 100 Hz | MS < 0 | D > 0.25", "Falha Normativa")
        qual_top = ("OpenFeaKernel (Ground Truth)\nCode_Aster / CalculiX Tet10 (Gmsh)\nOpenRadioss Choque P-POD / SRS", "Qualificado NASA\n(TOPSIS #28)")

    # 1. Main Pipeline Nodes
    for title, x, y, color, _, _ in nodes:
        ax.text(x, y, title, ha="center", va="center", fontsize=8.8, fontweight="bold", color="white",
                bbox=dict(boxstyle="round,pad=0.7", facecolor=color, edgecolor="#BDC3C7", lw=1.2, alpha=0.96))

    # Forward arrows
    for x_start, x_end, label in transitions:
        x1 = x_start + 0.095
        x2 = x_end - 0.095
        ax.annotate("", xy=(x2, y_main), xytext=(x1, y_main),
                    arrowprops=dict(arrowstyle="-|>", color="#1B365D", lw=2.0, mutation_scale=15))
        ax.text((x1 + x2) / 2.0, y_main + 0.11, label, ha="center", va="center", fontsize=7.6,
                color="#1B365D", fontweight="bold",
                bbox=dict(boxstyle="round,pad=0.25", facecolor="#EBF5FB", edgecolor="#AED6F1", lw=0.8))

    # 2. Rejection Gates (Bottom)
    ax.text(0.36, y_reject, rej_dfam[0], ha="center", va="center", fontsize=8.2, color="white", fontweight="bold",
            bbox=dict(boxstyle="square,pad=0.6", facecolor="#C0392B", edgecolor="#922B21", lw=1.2, alpha=0.95))
    ax.annotate("", xy=(0.36, y_reject + 0.065), xytext=(0.36, y_main - 0.085),
                arrowprops=dict(arrowstyle="-|>", color="#C0392B", lw=1.8, ls="--", mutation_scale=14))
    ax.text(0.36, (y_main + y_reject) / 2.0, rej_dfam[1], ha="center", va="center", fontsize=7.5,
            color="#C0392B", fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.2", facecolor="#FDEDEC", edgecolor="#F5B7B1", lw=0.8))

    ax.text(0.86, y_reject, rej_gevs[0], ha="center", va="center", fontsize=8.2, color="white", fontweight="bold",
            bbox=dict(boxstyle="square,pad=0.6", facecolor="#C0392B", edgecolor="#922B21", lw=1.2, alpha=0.95))
    ax.annotate("", xy=(0.86, y_reject + 0.065), xytext=(0.86, y_main - 0.085),
                arrowprops=dict(arrowstyle="-|>", color="#C0392B", lw=1.8, ls="--", mutation_scale=14))
    ax.text(0.86, (y_main + y_reject) / 2.0, rej_gevs[1], ha="center", va="center", fontsize=7.5,
            color="#C0392B", fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.2", facecolor="#FDEDEC", edgecolor="#F5B7B1", lw=0.8))

    # 3. High-Order Validation & Qualified Flight Model (Top)
    ax.text(0.86, y_top, qual_top[0], ha="center", va="center", fontsize=8.4, color="white", fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.65", facecolor="#196F3D", edgecolor="#145A32", lw=1.3, alpha=0.96))
    ax.annotate("", xy=(0.86, y_top - 0.075), xytext=(0.86, y_main + 0.085),
                arrowprops=dict(arrowstyle="-|>", color="#196F3D", lw=2.0, mutation_scale=15))
    ax.text(0.86, (y_main + y_top) / 2.0, qual_top[1], ha="center", va="center", fontsize=7.5,
            color="#196F3D", fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.25", facecolor="#EAFAF1", edgecolor="#A9DFBF", lw=0.8))

    ax.set_title(title_text, fontsize=12, fontweight="bold", color="#1B365D", pad=18)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    fig.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=300)
    fig.savefig(output_path.with_suffix(".pdf"))
    plt.close(fig)
    logger.info("Generated %s (lang=%s)", output_path, lang)


def update_all_figures() -> None:
    """Updates all schematic figures across monographs, theses, and international articles."""
    root_dir = Path(__file__).resolve().parent.parent

    # Portuguese destination directories (monographs, theses, graduation reports)
    pt_dirs = [
        root_dir / "figures",
        root_dir / "monografia" / "04-figuras",
        root_dir / "monografia" / "figuras",
        root_dir / "Entregas-finais" / "01-Tese-Exaustiva" / "04-figuras",
        root_dir / "Entregas-finais" / "01-Tese-Exaustiva" / "figuras",
        root_dir / "Entregas-finais" / "03-TCC-Graduacao-UESC" / "04-figuras",
        root_dir / "Entregas-finais" / "03-TCC-Graduacao-UESC" / "figuras",
    ]

    # English destination directories (Elsevier scientific articles)
    en_dirs = [
        root_dir / "Entregas-finais" / "02-Artigos-Cientificos" / "01-Materials-and-Design-Elsevier" / "figures",
        root_dir / "Entregas-finais" / "02-Artigos-Cientificos" / "02-Aerospace-Science-and-Technology-Elsevier" / "figures",
        root_dir / "Entregas-finais" / "02-Artigos-Cientificos" / "03-Engineering-Applications-of-AI-Elsevier" / "figures",
    ]

    logger.info("Generating Portuguese figures in %d directories...", len(pt_dirs))
    for d in pt_dirs:
        d.mkdir(parents=True, exist_ok=True)
        generate_auxetic_cell_figure(d / "auxetic_cell_geometry.png", lang="pt")
        generate_multi_agent_workflow_figure(d / "multi_agent_workflow.png", lang="pt")

    logger.info("Generating English figures in %d directories...", len(en_dirs))
    for d in en_dirs:
        d.mkdir(parents=True, exist_ok=True)
        generate_auxetic_cell_figure(d / "auxetic_cell_geometry.png", lang="en")
        generate_multi_agent_workflow_figure(d / "multi_agent_workflow.png", lang="en")

    logger.info("All figures updated successfully.")


if __name__ == "__main__":
    update_all_figures()
