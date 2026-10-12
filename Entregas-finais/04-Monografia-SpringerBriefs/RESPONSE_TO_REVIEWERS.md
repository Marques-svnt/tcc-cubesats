# Response to Reviewers (Editorial Review Report)

**Monograph Title:** *Structural Optimization of a 1U CubeSat Chassis with Auxetic Metamaterials in AlSi10Mg under Dynamic Launch Loads: Design for Additive Manufacturing, Spectral Vibration, and Physics-Guided AI*  
**Series:** *SpringerBriefs in Applied Sciences and Technology* (Aerospace Technology, Springer Nature)  
**Author:** Gabriel Marques de Andrade  
**Institutional Affiliation:** State University of Santa Cruz (UESC), Brazil  
**Supervisor:** Prof. Dr. Nila C. F. L. Medeiros  

---

Dear Editorial Board and Reviewers,

We express our profound gratitude for the comprehensive, meticulous, and constructive review of our monograph. The reviewers' feedback regarding structural mass progression transparency, additive manufacturing process parameter harmonization, and typographical hygiene has guided valuable refinements across the manuscript chapters.

Below is our point-by-point response detailing how each comment was addressed in the revised monograph.

---

### Detailed Point-by-Point Responses

#### Reviewer #1, Comment 1 (Mass Consistency across Chapters 4, 5, and 6):
> *"Table 4.1 reports a structural chassis mass of $0.2830\text{ kg}$ ($\SI{31.5}{\percent}$ reduction), whereas Chapters 5 and 6 report an optimal flight mass of $0.1155\text{ kg} \approx 0.116\text{ kg}$ ($\SI{62.49}{\percent}$ reduction). The transition between these two geometric models should be explicitly explained to prevent reader confusion."*

**Author's Response:**  
We thank the reviewer for this perceptive observation. We have clarified the structural mass progression:
- **Preliminary CAE Mesh Calibration Baseline (Chapter 4, Table 4.1, $M = 0.2830\text{ kg}$):** Represents a preliminary parametric geometry with conservative, uniform rib thickness ($t = 1.20\text{ mm}$). This model was utilized exclusively in Chapter 4 to establish spatial Grid Convergence Index (GCI) independence and calibrate eigenvalue extractions across dual solvers (Code\_Aster and CalculiX).
- **Optimal Multiobjective Flight Candidate #28 (Chapters 5 and 6, $M = 0.1155\text{ kg}$):** Result of coupling the Physics-Guided ResNet with multiobjective NSGA-II search and TOPSIS decision-making, refining the cell wall thickness to $t^* = 0.613\text{ mm}$ and re-entrant angle to $\theta^* = 65.75^\circ$, achieving the final $62.49\%$ mass savings ($0.1155\text{ kg}$ vs. $0.308\text{ kg}$).

**Manuscript Changes (Chapter 4, Section 4.2, Page 57):**  
We inserted an explicit Springer `svgraybox` environment (*Methodological Note on Chassis Mass Progression Across Chapters*) directly preceding Table 4.1, and updated the caption of Table 4.1 to designate it as the *preliminary CAE mesh calibration baseline chassis ($t = 1.20\text{ mm}$)*.

---

#### Reviewer #1, Comment 2 (Substrate Preheating Temperature Standardization):
> *"There is a minor discrepancy regarding substrate plate temperature: some sections and tables state $200^\circ\text{C}$, while process flow diagrams indicate $150^\circ\text{C}$."*

**Author's Response:**  
We have standardized the thermal process parameters throughout Chapter 3 (`chapters/03_dfam_alsi10mg.tex`):
- The substrate preheating temperature is standardized to **$T_{\text{bed}} = 150.0^\circ\text{C}$ (Nominal flight qualification baseline)**.
- The certified process window is explicitly documented as $150.0^\circ\text{C}\text{--}200.0^\circ\text{C}$ across Table 3.1 and the caption of Fig. 3.1.

**Manuscript Changes (Chapter 3, Section 3.1, Table 3.1, Fig. 3.1, Pages 38–39):**  
All references to substrate preheating have been harmonized to $T_{\text{bed}} = 150.0^\circ\text{C}$ nominal within the certified $150^\circ\text{C}\text{--}200^\circ\text{C}$ operating window.

---

#### Reviewer #2, Comment 1 (Figure Language Standardization):
> *"Ensure all figure labels, axis titles, and callouts are 100% in professional English, eliminating any residual Portuguese terms."*

**Author's Response:**  
All figure vector sources and caption references across the entire monograph have been thoroughly inspected. All graphic callouts, legend keys, and technical terms are verified to adhere strictly to publication-grade English terminology (IEEE/Elsevier/Springer Nature standards).

---

We believe these systematic enhancements provide complete clarity and transparency for the monograph readership.

Sincerely,  
**Gabriel Marques de Andrade**  
State University of Santa Cruz (UESC), Brazil  
Author
