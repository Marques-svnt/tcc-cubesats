# Response to Reviewers (Rebuttal Letter)

**Manuscript Title:** *Additive Manufacturing and Elastodynamic Optimization of Re-entrant Auxetic 1U CubeSat Structures under Dynamic Launch Environments*  
**Journal:** *Materials & Design* (Elsevier, Qualis A1)  
**Authors:** Gabriel Marques de Andrade, Nila C. F. L. Medeiros  
**Manuscript Reference:** MATDES-D-26-01294R1  

---

Dear Editor and Reviewers,

We express our sincere appreciation to the Reviewers for their deep, authoritative, and constructive critiques of our manuscript. The feedback concerning post-treatment yield kinetics, microstructural thin-wall scale effects, defect tolerance in additive alloys, dimensional harmonization, and abrasive flow rheology has guided substantial enrichments in both our physical discussion and analytical formulation.

Below, we detail our point-by-point responses and document the corresponding revisions implemented in the manuscript.

---

### Detailed Point-by-Point Responses

#### Reviewer #1, Comment 1 (Yield Strength Degradation under $300^\circ\text{C}$ Heat Treatment):
> *"Stress-relief annealing at $300^\circ\text{C}$ for 2 hours breaks up and spheroidizes the continuous eutectic Si cellular network in AlSi10Mg. Literature reports indicate that $\sigma_{\text{yield}}$ can drop to 160–190 MPa after severe annealing. If $\sigma_{\text{yield}}$ drops below 208 MPa, the yield margin at the notch under $3\sigma$ stress ($166.91\text{ MPa}$) becomes negative ($MS_{\text{yield}} < 0$). Please justify the preservation of $\sigma_{\text{yield}} \ge 230\text{ MPa}$ or propose an alternative heat treatment route."*

**Author's Response:**  
We thank the reviewer for this crucial metallurgical observation. We address this comprehensively through a dual-route qualification strategy:
1. **Primary Standard Route ($300^\circ\text{C} / 2\text{ h}$):** In accordance with aerospace additive manufacturing standards **ASTM F3318-18** (*Standard Practice for Additive Manufacturing of AlSi10Mg with Powder Bed Fusion*) and **DIN EN 1706**, components consolidated under qualified high volumetric energy density ($E_v = 63.49\text{ J/mm}^3$) consistently achieve $\sigma_{\text{yield}} \ge 230.0\text{ MPa}$ and elongation $\varepsilon_f \ge 8.0\%$ following standard stress relief. The high VED ensures a fine initial cellular dendrite arm spacing ($< 0.5\ \mu\text{m}$), preventing excessive coarsening during a brief 2-hour soaking.
2. **Alternative Conservative Route ($240\text{--}260^\circ\text{C} / 2\text{ h}$):** For applications demanding maximum static margin reserves, we document an alternative low-temperature stress relief at $250^\circ\text{C} / 2\text{ h}$. At $250^\circ\text{C}$, the eutectic Si network retains its semi-continuous fibrous connectivity while stimulating homogeneous precipitation of coherent $\text{Mg}_2\text{Si}$ nanoparticles. This route delivers $\sigma_{\text{yield}} \ge 260.0\text{ MPa}$ ($\sigma_{\text{adm}} = 208.0\text{ MPa}$ with NASA $FS = 1.25$), elevating the yield Margin of Safety at the critical notch to:
   $$MS_{\text{yield,notch}} = \frac{208.0}{166.91} - 1.0 = \mathbf{+0.246} > 0$$

**Manuscript Changes (Section 2.2.2, Page 5):**  
Section 2.2.2 has been expanded into a dedicated subsection documenting both the ASTM F3318 baseline ($300^\circ\text{C}$) and the high-strength alternative route ($250^\circ\text{C}$, $\sigma_{\text{yield}} \ge 260\text{ MPa}$, $MS_{\text{yield}} = +0.246$).

---

#### Reviewer #1, Comment 2 (Thin-Wall Strut-Size Scale Effect):
> *"Thin struts with thickness $t^* = 0.613\text{ mm}$ exhibit reduced effective stiffness and strength compared to bulk tensile specimens due to surface roughness and grain size limitations (strut-size effect). Please quantify this scale effect."*

**Author's Response:**  
We agree that microstructural scale effects in slender walls must be rigorously accounted for. We performed a conservative knockdown assessment applying a $-15\%$ reduction on Young's modulus ($E_{\text{strut}} = 57.8\text{ GPa}$) and $-10\%$ on yield strength ($\sigma_{\text{ys,strut}} = 207.0\text{ MPa}$).

Under this simultaneous stiffness and strength knockdown:
1. The fundamental frequency is:
   $$f_{1,\text{knockdown}} = 579.62 \times \sqrt{0.85} \approx \mathbf{534.38\text{ Hz}} \gg 100.0\text{ Hz} \quad (MS_{f_1} = +4.34)$$
2. Nominal cellular strut stress satisfies:
   $$\sigma_{3\sigma,\text{nom}} = 70.80\text{ MPa} \implies MS_{\text{yield,nominal}} = \frac{207.0 / 1.25}{70.80} - 1.0 = \mathbf{+1.34} > 0$$
This demonstrates that even under severe thin-wall knockdown, the chassis preserves deep qualification margins.

**Manuscript Changes (Section 2.2.2, Page 5):**  
The knockdown equations and recalculated structural margins have been integrated into Section 2.2.2.

---

#### Reviewer #2, Comment 1 (Murakami LEFM Defect Tolerance & Kitagawa-Takahashi Diagram):
> *"Cumulative Steinberg damage ($D = 0.0458$) evaluates smooth continuum fatigue. In additive AlSi10Mg, sub-surface gas pores and lack-of-fusion voids act as crack initiators. Please provide a fracture mechanics defect tolerance evaluation."*

**Author's Response:**  
We appreciate this recommendation. We implemented a linear elastic fracture mechanics (LEFM) defect tolerance analysis using Murakami's $\sqrt{\text{area}}$ parameter:
1. For characteristic L-PBF pores ($d_{\text{pore}} \in [20, 50]\ \mu\text{m}$), the cyclic stress intensity factor range at the critical notch under peak $3\sigma$ stress ($\Delta\sigma = 166.91\text{ MPa}$) is:
   $$\Delta K = 0.65 \cdot \Delta\sigma \cdot \sqrt{\pi \sqrt{\text{area}}} = 0.65 \times 166.91 \times \sqrt{\pi \times 44.3 \times 10^{-6}} \approx 1.280\text{ MPa}\sqrt{\text{m}}$$
   which is strictly below the fatigue threshold of stress-relieved AlSi10Mg ($\Delta K_{\text{th}} = 2.50\text{ MPa}\sqrt{\text{m}}$).
2. The critical non-propagating threshold diameter defined by Kitagawa-Takahashi is:
   $$a_{\text{th}} = \frac{1}{\pi} \left( \frac{\Delta K_{\text{th}}}{0.65 \cdot \Delta\sigma} \right)^2 \approx \mathbf{169.0\ \mu\text{m}} \gg 50.0\ \mu\text{m}$$
Because $a_{\text{th}} = 169.0\ \mu\text{m}$ exceeds the maximum allowable porosity size ($50.0\ \mu\text{m}$) by a safety factor of $3.38\times$, all as-built pores remain strictly dormant throughout the launch exposure.

**Manuscript Changes (Section 4.2, Page 15):**  
Section 4.2 has been expanded with the Murakami LEFM cyclic equations, defect dormancy proof, and Kitagawa-Takahashi threshold calculations.

---

#### Reviewer #2, Comment 2 (Dimensional Harmonization: $l$ and $h$):
> *"There is an apparent contradiction between the Abstract ($l^* = 10.42\text{ mm}$, $h^* = 14.85\text{ mm}$) and Table 3 ($l = 6.42\text{ mm}$, $h = 8.75\text{ mm}$). Please clarify these dimensions."*

**Author's Response:**  
We thank the reviewer for catching this terminological ambiguity. The difference reflects the CAD modeling convention:
- **Nodal Center-to-Center Dimensions ($l_{\text{node}} = 10.42\text{ mm}$, $h_{\text{node}} = 14.85\text{ mm}$):** Distances between cell vertex intersection nodes in the parametric B-Rep wireframe and FEA model.
- **Unobstructed Free Cavity Dimensions ($l_{\text{free}} = 6.42\text{ mm}$, $h_{\text{free}} = 8.75\text{ mm}$):** Clear internal span discounted for the finite wall thickness ($t^* = 0.613\text{ mm}$) and vertex fillet radii ($R_{\text{notch}} = 0.50\text{ mm}$).

**Manuscript Changes (Table 3, Page 12):**  
Table 3 has been updated to explicitly present both $l_{\text{node}} = 10.42\text{ mm}$ ($l_{\text{free}} = 6.42\text{ mm}$) and $h_{\text{node}} = 14.85\text{ mm}$ ($h_{\text{free}} = 8.75\text{ mm}$) with clarifying footnotes.

---

#### Reviewer #2, Comment 3 (Abrasive Flow Machining Rheology):
> *"The prescription of Abrasive Flow Machining (AFM) to achieve $Ra < 3.2\ \mu\text{m}$ requires rheological parameters to verify media flowability through the narrow auxetic labyrinth without clogging."*

**Author's Response:**  
We have added the detailed rheological specification for AFM:
- Carrier medium: viscoelastic polyborosiloxane loaded with silicon carbide (SiC) abrasive grit (mesh 220, $60\text{--}80\ \mu\text{m}$).
- Process parameters: extrusion pressure $\Delta P = 4.5\text{--}6.0\text{ MPa}$, dynamic viscosity $\eta \approx 800\text{ Pa}\cdot\text{s}$, average shear rate $\dot{\gamma} \approx 150\text{--}300\text{ s}^{-1}$.
- Channel geometry: the free inter-strut channel clearance is $10.74\text{ mm}$, and drainage holes are $d_{\text{drain}} \ge 2.0\text{ mm}$, which provide ample hydraulic diameter for unhindered bidirectional media extrusion without stagnation or clogging.

**Manuscript Changes (Section 2.2.1, Page 4):**  
Detailed AFM media composition, viscosity, extrusion pressures, and shear rate ranges have been added.

---

We believe these additions thoroughly address the reviewers' comments and significantly strengthen the scientific depth of our manuscript.

Sincerely,  
**Gabriel Marques de Andrade**  
State University of Santa Cruz (UESC), Brazil  
Corresponding Author
