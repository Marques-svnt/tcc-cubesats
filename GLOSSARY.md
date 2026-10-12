# CubeSat 1U Auxetic Chassis Domain Model

Canonical domain vocabulary and technical terminology for the geometric optimization, additive manufacturing (DfAM), dynamic FEA qualification, and neural surrogate modeling of a 1U CubeSat nanosatellite chassis.

---

## 1. Structural Architecture & Mission Envelope

**Chassis**:
The primary load-bearing structural frame of the 1U CubeSat enclosing avionics and mission payloads while guaranteeing mechanical integrity under launch loads.
_Avoid_: Frame, housing, box, skeleton

**Deployer Rails**:
Four continuous solid longitudinal corner rails of $8.5 \times 8.5\text{ mm}$ cross-section conforming to Cal Poly CubeSat specifications and sliding directly inside the dispenser.
_Avoid_: Sliders, guide bars, skids

**P-POD**:
The standard Poly-Picosatellite Orbital Deployer providing tubular mechanical containment and spring-loaded rail ejection for CubeSat secondary payloads.
_Avoid_: Launcher tube, dispenser canister

**Mass Budget**:
The allocated maximum allowable mass for the structural subsystem ($0.116\text{ kg}$ for the optimized chassis versus $0.308\text{ kg}$ conventional baseline).
_Avoid_: Weight limit, structural allowance

---

## 2. Cellular Metamaterials & Auxetic Mechanics

**Auxetic Lattice**:
A mechanical metamaterial structure exhibiting a negative Poisson ratio ($\nu_{\text{eff}} < 0$) that laterally expands under axial tension and contracts under compression to maximize energy dissipation.
_Avoid_: Cellular foam, honeycomb grid

**Re-entrant Unit Cell**:
A 2D/3D auxetic unit cell parameterized by $[\theta, t, l, h]^\top$ whose inward-pointing re-entrant struts buckle or flex to produce negative transverse strain.
_Avoid_: Bowtie cell, inward diamond

**Relative Density ($\rho^* / \rho_s$)**:
The ratio of the effective volume occupied by the cellular struts to the total bounding volume of the unit cell envelope.
_Avoid_: Fill factor, solidity ratio

**Gibson-Ashby Scaling**:
Analytical power-law constitutive relationships linking cellular relative density to effective macroscopic elastic modulus ($E^* \propto (\rho^*/\rho_s)^2$) and yield strength ($\sigma_y^* \propto (\rho^*/\rho_s)^{1.5}$) in bending-dominated topologies.
_Avoid_: Scaling rule, foam empirical fit

**Effective Poisson's Ratio ($\nu_{\text{eff}}$)**:
The negative ratio of transverse normal strain to longitudinal axial strain under uniaxial loading, measuring auxetic lateral contraction capability ($\nu_{\text{eff}} = -13.81$ at Pareto optimum).
_Avoid_: Transverse factor, contraction index

---

## 3. Design for Additive Manufacturing (DfAM)

**LPBF**:
Laser Powder Bed Fusion, a metallic additive manufacturing process consolidating pre-alloyed AlSi10Mg powder layer-by-layer via a focused ytterbium fiber laser.
_Avoid_: SLM, 3D printing, metal sintering

**Overhang Angle ($\theta_{\text{overhang}}$)**:
The angle between a downward-facing lattice strut surface and the horizontal build plate, strictly constrained to $\theta_{\text{overhang}} \ge 35.0^\circ$ (recommended $\ge 45.0^\circ$) to eliminate sacrificial internal supports.
_Avoid_: Cantilever angle, tilt limit

**Strut Thickness ($t$)**:
The nominal cross-sectional thickness of the re-entrant cellular rib, constrained to $t \ge 0.50\text{ mm}$ to ensure complete melt-pool coalescence without lack-of-fusion voids.
_Avoid_: Wall thickness, rib width

**Powder Drainage Port**:
An unblocked opening of minimum diameter $d \ge 2.0\text{ mm}$ integrated into closed cell faces to evacuate non-sintered residual metal powder post-build.
_Avoid_: Cleaning hole, bleed vent

**Stress Relief Treatment**:
The mandatory post-build annealing thermal cycle ($300^\circ\text{C}$ for 2 hours followed by slow furnace cooling) applied to eliminate residual tensile stresses and homogenize the microstructure.
_Avoid_: Tempering, heat baking

---

## 4. Environmental Dynamics & Flight Qualification

**Fundamental Frequency ($f_1$)**:
The first natural structural eigenfrequency under clamped deployer boundary conditions, strictly constrained to $f_1 \ge 100.0\text{ Hz}$ to avoid dynamic resonance with launch vehicle low-frequency pogo modes.
_Avoid_: First resonance, lowest natural mode

**NASA GEVS Profile**:
The qualification random vibration Power Spectral Density profile ($14.1\text{ G}_{\text{rms}}$, $20-2000\text{ Hz}$, $120\text{ s}$ per orthogonal axis) mandated by NASA GSFC-STD-7000A for secondary payloads.
_Avoid_: Launch noise, shake table spec

**Dynamic Transmissibility ($T$)**:
The ratio of payload interface stochastic acceleration response to shaker base input acceleration ($T = 0.39$ for the optimal auxetic core, providing $-12.6\text{ dB}$ attenuation).
_Avoid_: Vibration transfer, amplification factor

**Steinberg 3-Band Technique**:
The Gaussian statistical random fatigue method partitioning response cycles into $1\sigma$ ($68.3\%$), $2\sigma$ ($27.1\%$), and $3\sigma$ ($4.33\%$) bands to compute Miner's cumulative damage.
_Avoid_: Cycle counting, random SN sum

**Cumulative Damage Index ($D$)**:
The Miner linear damage summation across all three Steinberg stress bands, subjected to the strict NASA astronautics qualification gate $D \le 0.25$ (providing a $4\times$ fatigue life safety factor).
_Avoid_: Miner sum, failure index

**Margin of Safety ($MS$)**:
The non-dimensional safety factor metric defined as $(\sigma_{\text{adm}} / \sigma_{3\sigma}) - 1.0$, required to be strictly positive ($MS > 0$) against the $1.25\times$ factored yield limit.
_Avoid_: Safety margin, safety coefficient

---

## 5. Machine Learning & Optimization Pipeline

**Physics-Guided ResNet**:
The deep residual surrogate neural network mapping design vector $\mathbf{x} = [\theta, t, l, h]^\top$ to structural responses, constrained by an explicit Gibson-Ashby physics regularization loss.
_Avoid_: Surrogate black-box, ML regressor

**LHS (Latin Hypercube Sampling)**:
The space-filling quasi-random sampling technique ensuring orthogonal and uniform coverage across the 4-dimensional hypercube of auxetic design variables.
_Avoid_: Grid search, random sweep

**NSGA-II**:
The Non-dominated Sorting Genetic Algorithm II used for multi-objective optimization (minimizing mass while maximizing fundamental frequency and acoustic vibration attenuation).
_Avoid_: Genetic solver, GA loop

**TOPSIS**:
Technique for Order of Preference by Similarity to Ideal Solution, the multi-criteria decision algorithm selecting the best single flight candidate along the non-dominated Pareto front.
_Avoid_: Pareto picker, tradeoff ranker
