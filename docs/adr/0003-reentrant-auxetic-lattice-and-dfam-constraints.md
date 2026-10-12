# 0003. Re-entrant Auxetic Unit Cell Parameterization and LPBF DfAM Geometric Constraints

Parameterize the auxetic cellular lattice using a 4-parameter re-entrant geometry $[\theta, t, l, h]^\top$ designed to achieve negative Poisson's ratio ($\nu_{\text{eff}} < 0$) and broadband vibration attenuation, while embedding strict Design for Additive Manufacturing (DfAM) constraints directly into the optimization search space to ensure support-free Laser Powder Bed Fusion (LPBF) printability.

## Status
Accepted

## Context & Problem Statement
Conventional CubeSat chassis rely on monolithic machined aluminum panels (Al 6061-T6), which are rigid and simple to machine but exhibit poor acoustic damping, transferring high dynamic shock and random vibration directly to internal electronics. 

Auxetic metamaterials (negative Poisson's ratio) expand laterally under tension and contract under compression, creating superior strain energy dissipation, shear resistance, and dynamic acoustic attenuation. However, complex cellular metamaterials often violate additive manufacturing physics when fabricated via metal powder bed fusion:
1. Downward-facing struts with overhang angles below $35^\circ$ cause dross formation, melt-pool sagging, and recoater blade crashes unless internal sacrificial support structures are added (which cannot be physically removed from inside a closed micro-lattice).
2. Struts thinner than $0.50\text{ mm}$ suffer from lack-of-fusion voids and incomplete laser track consolidation.
3. Unmelted metal powder trapped inside internal voids increases dead weight and risks floating in microgravity as conductive contamination.

## Decision
1. **Re-entrant Unit Cell Parameterization**:
   - Vector of continuous design variables: $\mathbf{x} = [\theta, t, l, h]^\top$
     - Re-entrant angle: $50.0^\circ \le \theta \le 85.0^\circ$
     - Strut thickness: $0.50\text{ mm} \le t \le 1.80\text{ mm}$
     - Inclined rib length: $6.00\text{ mm} \le l \le 15.00\text{ mm}$
     - Vertical rib height: $8.00\text{ mm} \le h \le 20.00\text{ mm}$
   - Theoretical relative density formulation:
     $$\frac{\rho^*}{\rho_s} = \frac{t}{l} \cdot \frac{h/l + 2}{2 \cos\theta \cdot (h/l + \sin\theta)}$$
   - Poisson's ratio formulation:
     $$\nu_{\text{eff}} = \frac{\sin\theta \cdot (h/l + \sin\theta)}{\cos^2\theta}$$

2. **Embedded DfAM Constraints**:
   - **Self-Supporting Overhang Angle**: $\theta_{\text{overhang}} \ge 35.0^\circ$ (conservative operational target $\ge 45.0^\circ$), strictly preventing internal support requirements within the core lattice.
   - **Minimum Melt Pool Coalescence**: Rib thickness $t \ge 0.50\text{ mm}$ (accounting for an effective laser beam spot diameter $d_{\text{spot}} \approx 100\ \mu\text{m}$).
   - **Powder Evacuation Clearance**: Minimum inter-strut free aperture $\ge 1.50\text{ mm}$ and powder evacuation drain ports with diameter $d_{\text{drain}} \ge 2.0\text{ mm}$ in closed faces.

3. **Optimum Solution**:
   - At the NSGA-II Pareto frontier selected via TOPSIS:
     - $\theta^* = 65.75^\circ$
     - $t^* = 0.613\text{ mm}$
     - $l^* = 10.42\text{ mm}$
     - $h^* = 14.85\text{ mm}$
     - Effective Poisson's ratio: $\nu_{\text{eff}} = -13.81$
     - Mass reduction: $62.49\%$ ($116\text{ g}$ vs. $308\text{ g}$)
     - Transmissibility: $T = 0.39$ ($-12.6\text{ dB}$ vibration reduction)

## Consequences
- **Positive**: The optimized chassis is $100\%$ printable in a single LPBF build job on standard industrial metal printers (EOS M 290, SLM 280) with zero internal support structures and completely evacuable powder.
- **Negative / Trade-off**: Re-entrant geometry introduces localized stress concentrations at cell re-entrant vertices, requiring verification via $3\sigma$ stochastic stress evaluations and Paris-Erdogan linear elastic fracture mechanics.
- **Obsidian Linkage**: Referenced in [[Capítulo 3 - Metodologia e Formulação Estrutural]], [[Capítulo 5 - Resultados e Otimização]], and [[PARAMETROS_CANONICOS]].
