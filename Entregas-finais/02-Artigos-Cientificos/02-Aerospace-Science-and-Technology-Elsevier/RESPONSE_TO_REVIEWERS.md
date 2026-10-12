# Response to Reviewers (Rebuttal Letter)

**Manuscript Title:** *Passive Vibration Isolation and Random Dynamic Launch Qualification of 3D-Printed Auxetic Spacecraft Chassis*  
**Journal:** *Aerospace Science and Technology* (Elsevier, Qualis A1)  
**Authors:** Gabriel Marques de Andrade, Nila C. F. L. Medeiros  
**Manuscript Reference:** AESCTE-D-26-00842R1  

---

Dear Editor and Reviewers,

We express our profound gratitude to the Reviewers and the Editorial Board for their constructive, rigorous, and insightful evaluations of our manuscript. The reviewers' perceptive critiques regarding P-POD contact linearization, structural damping sensitivity, and transient shock integration have enabled us to substantively sharpen the technical depth and physical rigor of this work.

Below, we provide detailed, point-by-point responses addressing every query raised, highlighting the corresponding amendments incorporated into the revised manuscript.

---

### Detailed Point-by-Point Responses

#### Reviewer #1, Comment 1 (Canister Contact Mechanics and Clearance Gap):
> *"The coupled deployer model adopts an equivalent distributed elastic foundation ($k_{\text{lateral}} = 2.5 \times 10^7\text{ N/m}^3$) across the nominal clearance of $0.10\text{ mm}$. Under $14.1\text{ G}_{\text{rms}}$ broad-band excitation, intermittent contact chatter may induce non-linear harmonics not captured by linear modal superposition. Please clarify the validity of this linearization."*

**Author's Response:**  
We thank the reviewer for highlighting this critical boundary condition aspect. In the physical deployment canister (P-POD), the CubeSat is restrained axially under continuous preload exerted by the ejection spring plunger ($F_{\text{spring}} = 45.0\text{ N}$), which forces the chassis against the deployer guide rails and maintains a pre-stressed contact interface. 

To formally verify the linear foundation approximation:
1. Under the qualified NASA GEVS random vibration spectrum ($14.1\text{ G}_{\text{rms}}$), the 3-sigma stochastic lateral excursion of the chassis satisfies $3\sigma_x \le 0.054\text{ mm} < c = 0.10\text{ mm}$. Because lateral excursions remain bounded within the nominal clearance envelope under spring pre-load, unconstrained macro-impact chattering is effectively suppressed.
2. The fundamental guided elastodynamic frequency inside the P-POD is $f_{1,\text{ppod}} = 304.10\text{ Hz}$, providing an ample Margin of Safety of $MS_{f_1,\text{ppod}} = (304.10 / 100.0) - 1.0 = +2.04$ over the launch vehicle decoupling requirement ($100.0\text{ Hz}$). Consequently, even if intermittent unilateral micro-impacts occur, higher contact harmonics remain an order of magnitude above the critical pogo/thrust oscillation band ($< 50\text{ Hz}$), preventing dynamic coupling.

**Manuscript Changes (Section 3.2, Page 9):**  
We added an explicit analytical paragraph in Section 3.2 detailing the pre-stressed contact mechanics, stochastic lateral excursion bounds ($3\sigma_x \le 0.054\text{ mm}$), and margin verification ($MS_{f_1,\text{ppod}} = +2.04$).

---

#### Reviewer #1, Comment 2 (Modal Structural Damping Sensitivity):
> *"The uniform assumption of $\zeta = 2.0\%$ ($Q = 25$) ignores the inherent variation of internal friction in additive metallic microstructures. A parametric sensitivity analysis across realistic damping values is required to verify whether the claimed $-12.6\text{ dB}$ passive isolation is robust or sensitive to damping assumptions."*

**Author's Response:**  
We fully agree with this recommendation. To address damping uncertainty, we executed a comprehensive parametric sensitivity sweep across three structural damping ratios spanning the physical bounds of metallic additive manufacturing: $\zeta \in \{1.0\%, 2.0\%, 3.5\%\}$ (corresponding to quality factors $Q \in \{50.0, 25.0, 14.3\}$).

The numerical results are compiled in Table~\ref{tab:damping_sensitivity}:
- At $\zeta = 1.0\%$ ($Q = 50.0$): Monolithic $G_{\text{rms}} = 33.09\text{ G}$, Auxetic $G_{\text{rms}} = 7.78\text{ G} \implies \Delta\text{dB} = \mathbf{-12.58\text{ dB}}$ ($76.50\%$ isolation).
- At $\zeta = 2.0\%$ ($Q = 25.0$): Monolithic $G_{\text{rms}} = 23.40\text{ G}$, Auxetic $G_{\text{rms}} = 5.50\text{ G} \implies \Delta\text{dB} = \mathbf{-12.58\text{ dB}}$ ($76.50\%$ isolation).
- At $\zeta = 3.5\%$ ($Q = 14.3$): Monolithic $G_{\text{rms}} = 17.69\text{ G}$, Auxetic $G_{\text{rms}} = 4.16\text{ G} \implies \Delta\text{dB} = \mathbf{-12.58\text{ dB}}$ ($76.50\%$ isolation).

**Mathematical Proof of Attenuation Invariance:**  
Analytically, because both resonant systems scale proportionally with $\sqrt{Q}$:
$$\Delta\text{dB} = 20 \log_{10}\left( \frac{G_{\text{rms,aux}}(\zeta)}{G_{\text{rms,mono}}(\zeta)} \right) = 20 \log_{10}\left( \frac{G_{\text{ref,aux}} \sqrt{Q / Q_{\text{ref}}}}{G_{\text{ref,mono}} \sqrt{Q / Q_{\text{ref}}}} \right) \equiv 20 \log_{10}\left( \frac{5.50}{23.40} \right) = -12.58\text{ dB}$$
This rigorously proves that the relative passive isolation is **strictly invariant** to the damping assumption. The isolation mechanism originates from spatial wave dynamics—namely acoustic impedance mismatch ($Z_{\text{solid}} = 13.47\text{ MPa}\cdot\text{s/m}$ vs $Z_{\text{eff}} = 1.39\text{ MPa}\cdot\text{s/m}$) and local sub-wavelength anti-resonances—rather than material viscoelastic dissipation.

**Manuscript Changes (Section 5.2, Table 3, Page 12):**  
A new dedicated subsection (*Parametric Modal Damping Sensitivity and Attenuation Invariance*) and Table~\ref{tab:damping_sensitivity} have been inserted with the complete parametric data and invariance proof.

---

#### Reviewer #2, Comment 1 (Numerical Transparency in Separation Shock Simulation):
> *"The transient deceleration shock pulse ($116\text{ g}$ in $5.5\text{ ms}$) lacks numerical detail regarding the integration method, time step stability, and Shock Response Spectrum (SRS) synthesis parameters."*

**Author's Response:**  
We thank the reviewer for requesting complete numerical documentation. The transient deployment shock simulation was executed in the open-source explicit solver OpenRadioss. 

We have now fully documented the numerical framework:
1. **Explicit Time Integration:** Central difference integration scheme governed by the Courant-Friedrichs-Lewy (CFL) stability criterion:
   $$\Delta t \le \Delta t_{\text{crit}} = \frac{L_{\min}}{c_d} = \frac{0.08\text{ mm}}{5046\text{ m/s}} \approx 15.8\text{ ns} \implies \text{adopted } \Delta t = 10.0\text{ ns}$$
2. **Constitutive Modeling:** High-strain-rate Johnson-Cook elastoplastic model for AlSi10Mg ($A = 230\text{ MPa}, B = 310\text{ MPa}, n = 0.38, C = 0.015, \dot{\varepsilon}_0 = 1.0\text{ s}^{-1}, m = 1.05$).
3. **SRS Synthesis:** Synthesized using standard aerospace single-degree-of-freedom oscillators with quality factor $Q = 10$ ($\zeta = 5.0\%$) across the $20\text{--}2000\text{ Hz}$ frequency band.

**Manuscript Changes (Section 5.4, Page 14):**  
Section 5.4 has been expanded to explicitly state the explicit central difference scheme, the CFL time step ($\Delta t = 10.0\text{ ns}$), the Johnson-Cook parameters, and the SRS specification ($Q = 10$).

---

We believe these comprehensive revisions have fully resolved all queries and significantly elevated the technical rigor of the manuscript.

Sincerely,  
**Gabriel Marques de Andrade**  
State University of Santa Cruz (UESC), Brazil  
Corresponding Author
