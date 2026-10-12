# 0001. Delimitation between PLA Interface Prototype and AlSi10Mg Flight Structure under Incomplete Similarity

Establish strict technical separation between the 3D printed polymer model (PLA) used exclusively for virtual/physical CAD packaging fit-checks and the metallic flight chassis (AlSi10Mg LPBF) evaluated for dynamic space qualification, explicitly rejecting any cross-material structural extrapolation due to incomplete similitude.

## Status
Accepted

## Context & Problem Statement
During initial CubeSat development, a rapid polymeric prototype was fabricated in Polylactic Acid (PLA) to evaluate volumetric packaging of internal PC/104 electronic boards, antenna release clearance, and sliding tolerance within the P-POD deployer rails. 

However, in aerospace structural engineering, polymers exhibit severe viscoelastic damping, significant strain-rate sensitivity, high thermal expansion coefficients, and brittle notch sensitivity. These phenomena diverge completely from the elastic-plastic, high-temperature, and fatigue mechanisms of additive aerospace aluminum alloys (AlSi10Mg).

Attempting to extrapolate tap-testing, natural frequencies, or vibration attenuation measured on a PLA mock-up to predict the dynamic behavior of an LPBF metallic satellite constitutes a major physical fallacy due to **incomplete similarity** (severe discrepancies in Cauchy and Strouhal numbers, loss factor $\eta$, and modulus-to-density ratio $E/\rho$).

## Decision
1. **Model Scope Delimitation**:
   - The PLA model is classified strictly as a **Non-Structural Form-and-Fit Interface Prototype**. It is restricted to spatial packaging verification, deployer sliding fit-checks, and camera visual inspections.
   - The **Flight Structural Model** is exclusively simulated and designed as an **AlSi10Mg metallic lattice** manufactured via Laser Powder Bed Fusion (LPBF) followed by mandatory stress relief annealing ($300^\circ\text{C}$ for $2\text{ h}$).

2. **Rejection of Empirical Polymeric Dynamic Testing**:
   - No experimental modal testing (tap testing or shaker excitation) performed on polymeric prototypes shall be accepted as numerical validation for the space flight qualification campaign.
   - All modal, harmonic, and random vibration qualifications are derived strictly from high-fidelity finite element formulations (Tet10 formulations in Code_Aster and CalculiX) using canonical additive AlSi10Mg material properties ($E = 68.0\text{ GPa}$, $\rho = 2670\text{ kg/m}^3$, $\nu = 0.33$, $\sigma_y = 220.0\text{ MPa}$).

## Consequences
- **Positive**: Eliminates misleading dynamic predictions and guarantees that flight qualification calculations reflect authentic metallic microstructures governed by Paris-Erdogan crack propagation ($\Delta K_{th} = 2.5\text{ MPa}\sqrt{\text{m}}$) and Gibson-Ashby metallic cellular bending.
- **Negative / Trade-off**: Precludes using cheap desktop 3D printer tests as experimental validation in the monograph, necessitating rigorous verification via open-source high-fidelity numerical solvers (Gmsh, Code_Aster, CalculiX, and OpenRadioss).
- **Obsidian Linkage**: Referenced in [[Capítulo 3 - Metodologia e Formulação Estrutural]] and [[PARAMETROS_CANONICOS]].
