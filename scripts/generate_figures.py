"""Generates publication-quality technical schematic diagrams for the LaTeX monograph and presentation.

Outputs:
- figures/auxetic_cell_geometry.png: Geometric schematic of re-entrant auxetic unit cell.
- figures/multi_agent_workflow.png: Deterministic multi-agent state machine flowchart.
"""

from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np


def generate_auxetic_cell_figure(output_path: Path) -> None:
    """Plots a 2D geometric schematic of the re-entrant honeycomb auxetic cell."""
    fig, ax = plt.subplots(figsize=(6, 5), dpi=300)
    
    # Coordinates of re-entrant honeycomb cell
    # Central vertical strut and re-entrant oblique struts
    h = 2.0
    l = 1.4
    theta_deg = 65.0
    theta_rad = np.radians(theta_deg)
    
    dx = l * np.sin(theta_rad)
    dy = l * np.cos(theta_rad)
    
    # Points
    p_center_top = np.array([0, h/2])
    p_center_bot = np.array([0, -h/2])
    
    # Left re-entrant vertices
    p_left_top = np.array([-dx, h/2 + dy])
    p_left_mid = np.array([-dx + 0.3, 0]) # re-entrant
    p_left_bot = np.array([-dx, -h/2 - dy])
    
    # Right re-entrant vertices
    p_right_top = np.array([dx, h/2 + dy])
    p_right_mid = np.array([dx - 0.3, 0])
    p_right_bot = np.array([dx, -h/2 - dy])
    
    # Draw struts
    struts = [
        # Left side
        (np.array([-dx, h]), np.array([-dx, h/2])),
        (np.array([-dx, h/2]), np.array([0, 0])),
        (np.array([0, 0]), np.array([-dx, -h/2])),
        (np.array([-dx, -h/2]), np.array([-dx, -h])),
        # Right side
        (np.array([dx, h]), np.array([dx, h/2])),
        (np.array([dx, h/2]), np.array([0, 0])),
        (np.array([0, 0]), np.array([dx, -h/2])),
        (np.array([dx, -h/2]), np.array([dx, -h])),
    ]
    
    for p1, p2 in struts:
        ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color='#1B365D', lw=4, solid_capstyle='round')
        
    # Annotations
    ax.annotate(r'$h$ (Strut vertical)', xy=(dx + 0.15, 0), xytext=(dx + 0.4, 0),
                arrowprops=dict(arrowstyle='<->', color='#C0392B', lw=1.5),
                fontsize=11, color='#C0392B', va='center')
    ax.annotate(r'$l$ (Strut oblíquo)', xy=(dx/2, h/4), xytext=(dx/2 + 0.3, h/4 + 0.3),
                arrowprops=dict(arrowstyle='->', color='#27AE60', lw=1.5),
                fontsize=11, color='#27AE60')
    ax.annotate(r'$\theta$ (Ângulo de reentrada)', xy=(0.1, 0.1), xytext=(0.4, 0.6),
                arrowprops=dict(arrowstyle='->', color='#8E44AD', lw=1.5),
                fontsize=11, color='#8E44AD')
    ax.annotate(r'Espessura $t$', xy=(-dx, h * 0.75), xytext=(-dx - 0.7, h * 0.75),
                arrowprops=dict(arrowstyle='->', color='#D35400', lw=1.5),
                fontsize=11, color='#D35400')
    
    ax.set_title(r'Célula Auxética Reentrante 2D ($\nu_{\mathrm{eff}} < 0$)', fontsize=13, fontweight='bold', pad=15)
    ax.set_xlim(-2.2, 2.2)
    ax.set_ylim(-2.2, 2.2)
    ax.set_aspect('equal')
    ax.axis('off')
    
    fig.tight_layout()
    fig.savefig(output_path, dpi=300)
    plt.close(fig)


def generate_multi_agent_workflow_figure(output_path: Path) -> None:
    """Plots a flowchart of the deterministic LangGraph multi-agent workflow."""
    fig, ax = plt.subplots(figsize=(8, 4.5), dpi=300)
    
    nodes = [
        ("Candidato DoE / NSGA-II\n[θ, t, l, h]", 0.12, 0.5, '#2C3E50'),
        ("CadDfamAgent\n[Portões DfAM L-PBF]", 0.37, 0.5, '#2980B9'),
        ("NeuralSurrogateAgent\n[Physics ResNet]", 0.62, 0.5, '#8E44AD'),
        ("GevsQualifierAgent\n[NASA GEVS Criteria]", 0.87, 0.5, '#27AE60'),
    ]
    
    # Draw boxes
    for title, x, y, color in nodes:
        ax.text(x, y, title, ha='center', va='center', fontsize=9.5, fontweight='bold', color='white',
                bbox=dict(boxstyle='round,pad=0.6', facecolor=color, edgecolor='none', alpha=0.95))
        
    # Draw forward arrows
    for i in range(len(nodes) - 1):
        x1 = nodes[i][1] + 0.08
        x2 = nodes[i+1][1] - 0.08
        ax.annotate("", xy=(x2, 0.5), xytext=(x1, 0.5),
                    arrowprops=dict(arrowstyle="->", color="#1B365D", lw=2.2))
        ax.text((x1 + x2)/2, 0.54, "Aprovado", ha='center', va='bottom', fontsize=8, color='#1B365D', fontweight='bold')
        
    # Rejection boxes below
    ax.text(0.37, 0.15, "REJECTED_DFAM\n(Descarte Imediato)", ha='center', va='center', fontsize=8.5,
            color='white', fontweight='bold', bbox=dict(boxstyle='square,pad=0.5', facecolor='#C0392B', alpha=0.9))
    ax.annotate("", xy=(0.37, 0.23), xytext=(0.37, 0.42),
                arrowprops=dict(arrowstyle="->", color="#C0392B", lw=1.8, ls='--'))
    ax.text(0.39, 0.32, "Violação", ha='left', va='center', fontsize=7.5, color='#C0392B')
    
    ax.text(0.87, 0.15, "REJECTED_GEVS\n(Não-Conforme NASA)", ha='center', va='center', fontsize=8.5,
            color='white', fontweight='bold', bbox=dict(boxstyle='square,pad=0.5', facecolor='#C0392B', alpha=0.9))
    ax.annotate("", xy=(0.87, 0.23), xytext=(0.87, 0.42),
                arrowprops=dict(arrowstyle="->", color="#C0392B", lw=1.8, ls='--'))
    ax.text(0.89, 0.32, "Falha", ha='left', va='center', fontsize=7.5, color='#C0392B')
    
    # Final qualification
    ax.text(0.87, 0.85, "GroundTruthFeaAgent\n[Ansys SOLID187 / Voo]", ha='center', va='center', fontsize=8.5,
            color='white', fontweight='bold', bbox=dict(boxstyle='round,pad=0.5', facecolor='#16A085', alpha=0.95))
    ax.annotate("", xy=(0.87, 0.77), xytext=(0.87, 0.58),
                arrowprops=dict(arrowstyle="->", color="#16A085", lw=2.0))
    ax.text(0.89, 0.67, "Qualificado", ha='left', va='center', fontsize=7.5, color='#16A085', fontweight='bold')

    ax.set_title("Máquina de Estados Multi-Agente Determinística (LangGraph)", fontsize=12, fontweight='bold', pad=15)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    
    fig.tight_layout()
    fig.savefig(output_path, dpi=300)
    plt.close(fig)


if __name__ == "__main__":
    figures_dir = Path(__file__).resolve().parent.parent / "figures"
    figures_dir.mkdir(parents=True, exist_ok=True)
    generate_auxetic_cell_figure(figures_dir / "auxetic_cell_geometry.png")
    generate_multi_agent_workflow_figure(figures_dir / "multi_agent_workflow.png")
    print(f"Figures generated in {figures_dir}")
