# Canonical Engineering Parameters Matrix (1U CubeSat Chassis)

**Project:** Structural Optimization of a 1U CubeSat Chassis with Auxetic Metamaterials in AlSi10Mg under Dynamic Launch Loads  
**Author:** Gabriel Marques de Andrade | **Advisor:** Prof. Dr. Nila Cecília de Faria Lopes Medeiros  
**Institution:** State University of Santa Cruz (UESC) — Mechanical Engineering Division  
**Revision:** Version 2.0 (Post-Jury Examination / Q1 Peer Review Canonical Reconciliation)

---

## 1. Geometric Envelope and Deployer Interface
- **Standard:** CalPoly CubeSat Design Specification (Rev. 14 / P-POD).
- **Form Factor:** 1U CubeSat.
- **Nominal External Dimensions:** $100.0 \times 100.0 \times 113.5\text{ mm}$ ($\pm 0.1\text{ mm}$ tolerance).
- **Deployer Contact Rails:** $8.5 \times 8.5\text{ mm}$ solid monolithic continuous rails on all 4 longitudinal edges.
  - Edge fillets: $R \ge 1.0\text{ mm}$.
  - Surface roughness: $Ra \le 1.6\ \mu\text{m}$ (cold welding and sliding wear mitigation against P-POD anodized guides).
  - Hard surface finish: Type III hard anodizing (PTFE-impregnated).
- **Internal Payload Cavity:** Standard PC/104 stack mountings ($90.0 \times 96.0\text{ mm}$ board clearance).

---

## 2. Flight Mass Budget and Comparative Structural Performance
| Parameter | Conventional Monolithic Chassis (Al 6061-T6) | Proposed Auxetic Lattice Chassis (AlSi10Mg) | Performance Delta |
| :--- | :---: | :---: | :---: |
| **Structural Mass** | $0.308\text{ kg}$ ($308\text{ g}$) | $0.116\text{ kg}$ ($116\text{ g}$) | **$-62.49\%$** |
| **Fundamental Frequency ($f_1$, Free-Free)** | $412.10\text{ Hz}$ | $579.62\text{ Hz}$ | **$+40.65\%$** (NASA GEVS $\ge 100\text{ Hz}$) |
| **P-POD Guided Fundamental ($f_{1,\text{ppod}}$)** | $245.30\text{ Hz}$ | $304.10\text{ Hz}$ | **$+23.97\%$** ($MS_{f_1} = +2.04$) |
| **Dynamic Transmissibility ($T$)** | $1.66$ | $0.39$ | **$-76.50\%$** ($-12.6\text{ dB}$) |
| **Payload RMS Acceleration ($G_{\text{rms,pay}}$)** | $23.4\text{ G}_{\text{rms}}$ | $5.5\text{ G}_{\text{rms}}$ | **$-76.50\%$** ($2.82\text{ G}_{\text{rms}}$ at sensor mount) |
| **Nominal Stress ($3\sigma$)** | $112.4\text{ MPa}$ | $68.8\text{ MPa}$ | **$-38.79\%$** |
| **Critical Notch Peak Stress ($\sigma_{3\sigma,\text{notch}}$)** | -- | $166.91\text{ MPa}$ | Elastic notch factor $K_t \approx 1.26$ |
| **Yield Margin of Safety ($MS_{\text{yield}}$)** | $+0.56$ | $+0.102$ (notch) / $+1.56$ (nominal) | Pass ($MS > 0$, limit $184.0\text{ MPa}$) |
| **Steinberg Cumulative Fatigue Damage ($D$)** | $0.182$ | $0.0458$ | Pass at critical notch ($D \ll 0.25$, $5.46\times$ margin) |

---

## 3. Material Properties (AlSi10Mg — Laser Powder Bed Fusion)
- **Base Material:** Additively manufactured AlSi10Mg alloy (L-PBF).
- **Post-Process Thermal Route:** Stress-relief heat treatment at $300^\circ\text{C}$ for 2 hours (dual mitigation route: $250^\circ\text{C}$ for 2h preserves $\sigma_{\text{yield}} \ge 245\text{ MPa}$).
- **Solid Density ($\rho_s$):** $2670\text{ kg/m}^3$ ($2.67\text{ g/cm}^3$).
- **Solid Young's Modulus ($E_s$):** $68.0\text{ GPa}$.
- **Poisson's Ratio ($\nu_s$):** $0.33$.
- **Yield Strength ($0.2\%$ offset, $\sigma_{\text{yield}}$):** $230.0\text{ MPa}$.
- **Allowable Design Stress ($\sigma_{\text{adm}} = \sigma_{\text{yield}} / 1.25$):** $184.0\text{ MPa}$.
- **Ultimate Tensile Strength ($\sigma_{\text{ult}}$):** $340.0\text{ MPa}$ (Allowable ultimate $\sigma_{\text{adm,ult}} = \sigma_{\text{ult}} / 1.40 = 242.86\text{ MPa}$).
- **Threshold Stress Intensity Factor Range ($\Delta K_{\text{th}}$):** $2.50\text{ MPa}\sqrt{\text{m}}$.
- **Plane-Strain Fracture Toughness ($K_{\text{Ic}}$):** $34.0\text{ MPa}\sqrt{\text{m}}$.
- **Basquin S-N Parameters:** Coefficient $C = 1.2 \times 10^{20}$, exponent $m = 6.8$.

---

## 4. Launch Dynamics and NASA GEVS Qualification Envelope
- **Governing Standard:** NASA GSFC-STD-7000A (*General Environmental Verification Standard - GEVS*).
- **Minimum Fundamental Frequency:** $f_1 \ge 100.0\text{ Hz}$ (avoids pogo and quasi-static launch resonance).
- **Overall Base Input Vibration:** $G_{\text{rms,base}} = 14.1\text{ G}_{\text{rms}}$ applied sequentially along 3 orthogonal axes ($X, Y, Z$).
- **Test Duration:** $120.0\text{ seconds}$ per axis.
- **NASA GEVS Random Vibration PSD Profile:**
  - $20\text{ Hz}$: $0.013\text{ g}^2/\text{Hz}$ ($+3\text{ dB/octave}$ slope)
  - $50 - 800\text{ Hz}$: $0.080\text{ g}^2/\text{Hz}$ (energy plateau)
  - $2000\text{ Hz}$: $0.0053\text{ g}^2/\text{Hz}$ ($-6\text{ dB/octave}$ roll-off)
- **Modal Damping:** Nominal $\zeta = 2.0\%$ ($Q = 25$); sensitivity verified over $\zeta \in \{1.0\%, 2.0\%, 3.5\%\}$ proving acoustic attenuation invariance at $-12.6\text{ dB}$.
- **Steinberg 3-Band Random Fatigue Damage Criterion:**
  $$D = \sum_{i=1}^{3} \frac{n_i}{N_i} = \frac{0.683 \cdot f_0 \cdot t}{N_{1\sigma}} + \frac{0.271 \cdot f_0 \cdot t}{N_{2\sigma}} + \frac{0.043 \cdot f_0 \cdot t}{N_{3\sigma}} \le 0.25$$
  - Flight Qualification Requirement (NASA-HDBK-7005): $D \le 0.25$ ($4.0\times$ life safety factor).
  - Calculated at maximum elastic notch stress concentration ($\sigma_{3\sigma,\text{notch}} = 166.91\text{ MPa}$): $D = 0.0458 \ll 0.25$ ($5.46\times$ margin).

---

## 5. DfAM Constraints (Laser Powder Bed Fusion)
- **Minimum Overhang Self-Supporting Angle:** $\theta_{\text{overhang}} \ge 35.0^\circ$ relative to horizontal build plate (eliminates internal lattice support structures).
- **Minimum Cell Strut Thickness:** $t \ge 0.8\text{ mm}$ (ensures full melt-pool coalescence and mitigates lack-of-fusion defects).
- **Residual Powder Evacuation Clearance:** Free internal drain diameter $d_{\text{drain}} \ge 2.0\text{ mm}$ (actual minimum clear passage in optimal lattice is $6.42\text{ mm}$).
- **Volumetric Energy Density:** $E_v = \frac{P}{v \cdot h \cdot t_{\text{layer}}} = 63.49\text{ J/mm}^3$ ($P = 370\text{ W}$, $v = 1300\text{ mm/s}$, $h = 0.13\text{ mm}$, $t_{\text{layer}} = 30\ \mu\text{m}$).

---

## 6. Fracture Mechanics and Murakami Defect Tolerance
- **Defect Size in L-PBF:** Maximum gas/LoF pore diameter observed in micro-CT: $d_{\text{pore}} \le 50\ \mu\text{m}$ ($\sqrt{\text{area}} \approx 44.3\ \mu\text{m}$).
- **Operating Stress Intensity Factor Range:**
  $$\Delta K = Y \cdot \Delta \sigma \cdot \sqrt{\pi a} = 0.65 \cdot (166.91\text{ MPa}) \cdot \sqrt{\pi \cdot 25 \times 10^{-6}\text{ m}} = 1.28\text{ MPa}\sqrt{\text{m}}$$
- **Dormancy Criterion:**
  $$\Delta K = 1.28\text{ MPa}\sqrt{\text{m}} < \Delta K_{\text{th}} = 2.50\text{ MPa}\sqrt{\text{m}}$$
  Threshold crack size for propagation is $a_{\text{th}} = 169\ \mu\text{m} \gg 50\ \mu\text{m}$. Defects remain strictly dormant under qualification loads.
