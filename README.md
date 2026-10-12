# 1U Auxetic CubeSat Spacecraft Chassis: Multi-Objective Structural Optimization & NASA GEVS Random Vibration Launch Qualification

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Standard: NASA GEVS](https://img.shields.io/badge/Standard-NASA%20GSFC--STD--7000A-red.svg)](https://standards.nasa.gov/)
[![Tests: 101 Passing](https://img.shields.io/badge/Tests-101%20Passing-brightgreen.svg)]()
[![Code Style: Ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![Type Checked: Mypy](https://img.shields.io/badge/type_checker-mypy-blue.svg)](https://mypy-lang.org/)
[![Physics: Code_Aster / Gmsh](https://img.shields.io/badge/FEA-Code__Aster%20%7C%20Gmsh-orange.svg)](https://code-aster.org)

An open-source, publication-grade aerospace computational framework for the design, multiphysics finite element simulation, physics-guided deep learning surrogacy, and evolutionary multi-objective optimization of an architected **1U CubeSat spacecraft chassis**.

The chassis replaces conventional solid bulkheads with 3D re-entrant auxetic metamaterials ($\nu_{\text{eff}} < 0$) in additive **AlSi10Mg** alloy (Laser Powder Bed Fusion - L-PBF), preserving four monolithic deployer guide rails ($8.5 \times 8.5\text{ mm}$) for standard **P-POD** (*Poly-Picosatellite Orbital Deployer*) kinematic deployment. The structural architecture is qualified under dynamic random launch loads according to **NASA GSFC-STD-7000A (GEVS)** ($14.1\text{ G}_{\text{rms}}$, $20-2000\text{ Hz}$).

---

## 🛰️ Executive Summary & Flight Qualification Performance

| Parameter | Conventional Solid Chassis (Al 6061-T6) | Optimized Auxetic Lattice Chassis (AlSi10Mg) | Performance Delta / Metric | Qualification Status |
| :--- | :---: | :---: | :---: | :---: |
| **Structural Mass ($m$)** | $0.308\text{ kg}$ ($308\text{ g}$) | **$0.116\text{ kg}$ ($116\text{ g}$)** | **$-62.49\%$** mass reduction | ✅ Exceeds lightweight goal |
| **Fundamental Frequency ($f_1$, Free)** | $412.10\text{ Hz}$ | **$579.62\text{ Hz}$** | **$+40.65\%$** dynamic stiffness | ✅ NASA GEVS $\ge 100\text{ Hz}$ |
| **P-POD Guided Fundamental ($f_{1,\text{ppod}}$)** | $245.30\text{ Hz}$ | **$304.10\text{ Hz}$** | **$+23.97\%$** | ✅ $MS_{f_1} = +2.04$ |
| **Dynamic Transmissibility ($T$)** | $1.66$ | **$0.39$** | **$-76.50\%$** ($-12.6\text{ dB}$ attenuation) | ✅ Acoustic shock protection |
| **Payload RMS Acceleration ($G_{\text{rms,pay}}$)** | $23.4\text{ G}_{\text{rms}}$ | **$5.5\text{ G}_{\text{rms}}$** | **$-76.50\%$** ($2.82\text{ G}_{\text{rms}}$ at sensor) | ✅ High attenuation gain |
| **Peak $3\sigma$ Notch Stress ($\sigma_{3\sigma,\text{notch}}$)** | -- | **$166.91\text{ MPa}$** | Notch concentration $K_t \approx 1.26$ | ✅ Below allowable limit |
| **Yield Margin of Safety ($MS_{\text{yield}}$)** | $+0.56$ | **$+0.102$ (notch) / $+1.56$ (nominal)** | Allowable: $\sigma_{\text{adm}} = 184.0\text{ MPa}$ | ✅ Positive flight margin |
| **Steinberg Fatigue Damage ($D$)** | $0.182$ | **$0.0458$** | NASA-HDBK-7005 limit $D \le 0.25$ | ✅ $5.46\times$ safety factor |
| **Murakami Fracture Threshold ($\Delta K$)** | -- | **$1.28\text{ MPa}\sqrt{\text{m}}$** | Threshold: $\Delta K_{\text{th}} = 2.50\text{ MPa}\sqrt{\text{m}}$ | ✅ Defects strictly dormant |

---

## 📚 Companion Academic Publications & Manuscripts

The peer-reviewed scientific papers, doctoral-level monographs, rebuttal letters, and defense presentation slides are maintained in dedicated publication branches. To access the complete academic archive:

```bash
git fetch origin feat/scientific-writings-and-monographs
git checkout feat/scientific-writings-and-monographs
```

### Archived Publication Dossier:
1. **Manuscript 1 (Aerospace Engineering / Elsevier Q1):**  
   *Passive Vibration Isolation and Random Dynamic Launch Qualification of 3D-Printed Auxetic Spacecraft Chassis*  
   *Target:* **Aerospace Science and Technology**
2. **Manuscript 2 (Materials Science / Elsevier Q1):**  
   *Additive Manufacturing and Elastodynamic Optimization of Re-entrant Auxetic 1U CubeSat Structures under Dynamic Launch Environments*  
   *Target:* **Materials & Design**
3. **Manuscript 3 (Applied Artificial Intelligence / Elsevier Q1):**  
   *Physics-Guided Deep Residual Networks for Accelerated Multiobjective Optimization of Architected Spacecraft Metamaterials*  
   *Target:* **Engineering Applications of Artificial Intelligence**
4. **Book Monograph (Springer Nature):**  
   *Structural Optimization of a 1U CubeSat Chassis with Auxetic Metamaterials in AlSi10Mg under Dynamic Launch Loads: Design for Additive Manufacturing, Spectral Vibration, and Physics-Guided AI*  
   *Series:* **SpringerBriefs in Applied Sciences and Technology**
5. **Bachelor's Thesis Monograph (State University of Santa Cruz - UESC):**  
   *Otimização Estrutural de Chassi CubeSat 1U com Metamateriais Auxéticos em AlSi10Mg sob Cargas Dinâmicas de Lançamento* (Concise 66 pp. Defense Version & Comprehensive 110 pp. Exhaustive Version in Brazilian Portuguese).

---

## 🏛️ Codebase Architecture & Deep Modules

The repository follows deep-module software engineering principles, isolating geometry generation, meshing, finite element multiphysics, neural surrogate inference, evolutionary optimization, and autonomous multi-agent orchestration behind strict, typed interfaces:

```text
.
├── src/
│   ├── cad/             # Parametric B-Rep CAD and DfAM validation (build123d / CadQuery)
│   ├── mesh/            # Quadratic tetrahedral (Tet10) meshing & adaptive refinement (Gmsh)
│   ├── analysis/        # Open-source CAE solvers (Code_Aster, CalculiX, OpenRadioss)
│   ├── neural/          # Physics-Guided ResNet (PG-ResNet), 10-fold CV, and MC Dropout UQ
│   ├── optimization/    # Multiobjective NSGA-II genetic algorithm & TOPSIS selection
│   ├── agents/          # LangGraph autonomous multi-agent engineering workflows
│   ├── core/            # Continuum mechanics, Gibson-Ashby scaling, and Pydantic v2 settings
│   ├── dfam/            # LPBF additive manufacturing rules & TPMS gyroid lattices
│   └── pipeline/        # Unified qualification pipeline runner
├── tests/               # 101 automated unit, integration, and property-based tests (Hypothesis)
├── configs/             # NASA GEVS specifications and material property configuration YAMLs
├── data/                # Latin Hypercube Sampling DoE datasets and Pareto frontier CSVs
├── docs/                # Architecture Decision Records (ADRs) and Canonical Parameters Matrix
├── models/              # Pretrained neural checkpoints (.pt), scalers (.json), and CAD (.step, .stl)
├── reports/             # Flight synthesis reports, uncertainty quantification logs, and Pareto curves
├── scripts/             # CLI utilities for CAD export, figure generation, and preflight checks
├── pyproject.toml       # Python project configuration, dependencies, and pytest settings
└── README.md            # This documentation
```

### Module Breakdown:
- **`src.cad` (`build123d_engine.py`, `cadquery_engine.py`):**  
  Constructs full-scale 1U CubeSat chassis assemblies ($100 \times 100 \times 113.5\text{ mm}$), unit cells, and $2\times 2$ lattice panels. Enforces strict DfAM rules: self-supporting overhang angle $\theta_{\text{overhang}} \ge 35^\circ$, strut thickness $t \ge 0.8\text{ mm}$, and powder evacuation clearance $d_{\text{drain}} \ge 2.0\text{ mm}$.
- **`src.mesh` (`gmsh_engine.py`):**  
  Generates quadratic 10-node tetrahedral meshes (`Tet10`) with local adaptive curvature refinement at re-entrant cellular re-entrant notches ($h_{\text{notch}} \le 0.15\text{ mm}$) to resolve elastic stress concentration ($K_t \approx 1.26$).
- **`src.analysis` (`code_aster_runner.py`, `calculix_runner.py`, `openradioss_shock.py`, `rebuttal_verification_engine.py`):**  
  - **Code_Aster:** Extracts pre-stressed modal eigenvalues (`CALC_MODES` via Sorensen/Lanczos) and stochastic frequency response spectra (`DYNA_ALEA_MODAL`) under NASA GEVS $14.1\text{ G}_{\text{rms}}$ PSD.
  - **CalculiX:** Provides independent eigenvalue cross-verification (`.inp`).
  - **OpenRadioss:** Simulates explicit non-linear dynamic transient shock from P-POD separation spring ($116\text{ g}$, $5.5\text{ ms}$, Courant time step $\Delta t \approx 10\text{ ns}$, SRS synthesis with $Q = 10$).
  - **Rebuttal Verification Engine:** Evaluates modal damping sensitivity ($\zeta \in \{1.0\%, 2.0\%, 3.5\%\}$), thin-strut scale knockdowns ($-15\%$ $E$, $-10\%$ $\sigma_y$), and Murakami defect dormancy ($\Delta K < \Delta K_{\text{th}}$).
- **`src.neural` (`surrogate_model.py`, `uncertainty_quantifier.py`):**  
  Deep Residual Network (`CubeSatSurrogateResNet`) mapping design vector $\mathbf{x} = [h, l, t, \theta, \rho^*]^T \in \mathbb{R}^5$ to structural responses $\hat{\mathbf{y}} = [\hat{f}_1, \hat{\sigma}_{3\sigma}, \hat{G}_{\text{rms,pay}}]^T \in \mathbb{R}^3$, with deterministic transmissibility $T \equiv \hat{G}_{\text{rms,pay}} / 14.1$. Trained with a `PhysicsGuidedLoss` penalizing Gibson-Ashby scaling violations. Evaluated via Stratified 10-Fold Cross-Validation ($R^2 = 0.9972 \pm 0.0016$, $\text{NRMSE} = 1.27 \pm 0.34\%$) and Monte Carlo Dropout uncertainty quantification ($\pm 2.3\text{ Hz}$ epistemic, $\pm 8.4\text{ Hz}$ aleatoric).
- **`src.optimization` (`nsga2_optimizer.py`):**  
  Elitist multi-objective evolutionary optimization (NSGA-II) minimizing mass ($m$) and transmissibility ($T$) subject to non-linear flight constraints: $f_1 \ge 100\text{ Hz}$, $MS_{\text{yield}} > 0$, $D_{\text{Miner}} \le 0.25$. TOPSIS multi-criteria decision making selects the balanced flight design from the 100-point Pareto frontier.
- **`src.agents` (`specialists.py`, `multi_agent_graph.py`):**  
  LangGraph state machine coordinating autonomous engineering agents: `CadAgent` (DfAM check), `FeaAgent` (spectral solver), `MaterialsReliabilityAgent` (fatigue and fracture), and `OrchestratorAgent` (automated lifecycle routing).

---

## ⚙️ Installation & Environment Setup

### 1. Prerequisites (Linux / Ubuntu 22.04 / 24.04 LTS or WSL2)
Install the open-source engineering dependencies and CAE solvers:

```bash
# Update system and install CAD / Meshing utilities
sudo apt-get update && sudo apt-get install -y \
    build-essential \
    cmake \
    git \
    gmsh \
    libglu1-mesa \
    libgl1-mesa-glx \
    calculix-ccx
```

*Note:* For Code_Aster and OpenRadioss execution, pre-built binary containers or Singularity/Apptainer images are supported. The framework automatically falls back to analytical high-fidelity surrogate formulations when running in headless CI environments without local CAE daemon licenses.

### 2. Python Environment Setup
We recommend using [`uv`](https://github.com/astral-sh/uv) for fast, reproducible dependency resolution:

```bash
# Clone the repository
git clone https://github.com/Marques-svnt/tcc-cubesats.git
cd tcc-cubesats

# Create virtual environment and install all dependencies
uv venv .venv --python 3.12
source .venv/bin/activate
uv pip install -e .

# Alternatively, using standard pip:
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

## 🧪 Verification & Test Suite

The codebase features comprehensive unit, integration, and property-based test suites using `pytest` and `hypothesis`:

```bash
# Run the complete test suite (101 automated tests)
pytest tests/ -v

# Run with property-based testing and coverage report
pytest tests/ --hypothesis-show-details=normal --cov=src --cov-report=term-missing
```

### Property-Based Invariant Verification:
- **`test_property_poisson_ratio_is_strictly_negative`:** Mathematically guarantees negative Poisson's ratio ($\nu_{\text{eff}} < 0$) across the full re-entrant geometric domain ($\theta \in [-35^\circ, -10^\circ]$).
- **`test_property_gibson_ashby_modulus_is_strictly_monotonic`:** Proves strict monotonicity of effective elastic modulus with respect to relative density ($\partial E^* / \partial \rho^* > 0$).
- **`test_property_steinberg_damage_is_non_negative_and_monotonic`:** Verifies non-negativity and positive monotonicity of Palmgren-Miner cumulative fatigue damage ($D \ge 0$).
- **`test_hypothesis_damping_attenuation_invariance`:** Proves $-12.6\text{ dB}$ passive isolation stability across damping variations ($\zeta \in [1.0\%, 3.5\%]$).

---

## 🚀 Quickstart & Operational Workflows

### 1. Generate 3D Parametric CAD and Printable Panels
Generate full 1U flight chassis geometries and auxetic lattice panels in STEP AP214 and STL formats:

```bash
python scripts/generate_cad_unit_cell_and_panels.py
```
Outputs are saved to `models/cad/`:
- `cubesat_1u_flight_chassis.step`
- `cubesat_1u_flight_chassis.stl`
- `cubesat_auxetic_lattice_panel_2x2.step`

### 2. Train and Evaluate Physics-Guided ResNet (PG-ResNet)
Train the neural surrogate model on the 250-point Latin Hypercube Sampling DoE dataset with Stratified 10-Fold Cross-Validation:

```bash
python -m src.neural.train_and_evaluate_surrogate
```
Generates cross-validation performance telemetry, parity plots, and serialized model checkpoints in `models/`.

### 3. Run Monte Carlo Dropout Uncertainty Quantification
Propagate geometric manufacturing tolerances ($\pm 50\ \mu\text{m}$) and epistemic weight uncertainties:

```bash
python scripts/run_uncertainty_analysis.py
```
Outputs comprehensive flight qualification uncertainty reports in `reports/uncertainty_quantification_flight_report.md`.

### 4. Run Multi-Objective NSGA-II Optimization
Execute evolutionary optimization to discover the 100-point Pareto frontier balancing mass and vibration transmissibility:

```bash
python -m src.optimization.nsga2_optimizer
```

### 5. Execute Autonomous Multi-Agent Qualification Pipeline
Run the complete end-to-end qualification pipeline across all agents:

```bash
python run_pipeline.py
```

---

## 🔬 Mathematical Formulations

### 1. Cellular Scaling Laws (Gibson-Ashby)
For bending-dominated open-cell cellular solids:
$$E^* = E_s \cdot C_1 \cdot \left(\frac{\rho^*}{\rho_s}\right)^2, \quad \sigma_y^* = \sigma_{ys} \cdot C_2 \cdot \left(\frac{\rho^*}{\rho_s}\right)^{1.5}$$
where $C_1 \approx 1.0$, $C_2 \approx 0.3$, $E_s = 68.0\text{ GPa}$, and $\sigma_{ys} = 230.0\text{ MPa}$.

### 2. Random Dynamic Launch Qualification (NASA GEVS)
Input base acceleration spectrum $G_{\text{rms,base}} = 14.1\text{ G}_{\text{rms}}$ applied sequentially along orthogonal axes ($20 - 2000\text{ Hz}$, $120\text{ s}$ per axis). Miles' single-degree-of-freedom equivalent response:
$$G_{\text{rms}} = \sqrt{\frac{\pi}{2} \cdot f_n \cdot Q \cdot \text{PSD}(f_n)}$$
where $Q = 1 / (2\zeta) = 25$ for $\zeta = 2.0\%$ nominal modal damping.

### 3. Steinberg 3-Band Cumulative Fatigue Damage
Under zero-mean Gaussian random excitation, instantaneous stresses follow a Rayleigh distribution partitioned into three standard deviation bands:
$$D = \sum_{i=1}^{3} \frac{n_i}{N_i} = \frac{0.683 \cdot f_0 \cdot t}{N_{1\sigma}} + \frac{0.271 \cdot f_0 \cdot t}{N_{2\sigma}} + \frac{0.043 \cdot f_0 \cdot t}{N_{3\sigma}} \le 0.25$$
evaluated conservatively at the critical notch stress concentration ($\sigma_{3\sigma,\text{notch}} = 166.91\text{ MPa}$), ensuring $D = 0.0458 \ll 0.25$.

### 4. Defect Tolerance & Fracture Mechanics (Murakami Model)
Using the $\sqrt{\text{area}}$ parameter for sub-surface pores in additive AlSi10Mg:
$$\Delta K = Y \cdot \Delta \sigma \cdot \sqrt{\pi a} = 0.65 \cdot (166.91\text{ MPa}) \cdot \sqrt{\pi \cdot 25 \times 10^{-6}\text{ m}} = 1.28\text{ MPa}\sqrt{\text{m}} < \Delta K_{\text{th}} = 2.50\text{ MPa}\sqrt{\text{m}}$$
guaranteeing complete crack propagation dormancy during dynamic launch environments.

---

## 📖 Architecture Decision Records (ADRs)

Formal design and architecture trade-offs are documented under [`docs/adr/`](docs/adr/):
- **`0001`**: [Material Scope & Incomplete Similarity: PLA Prototyping vs. AlSi10Mg Flight Hardware](docs/adr/0001-material-scope-and-incomplete-similarity.md)
- **`0002`**: [NASA GEVS Spectral Qualification & Steinberg 3-Band Random Fatigue Damage](docs/adr/0002-nasa-gevs-qualification-and-steinberg-fatigue.md)
- **`0003`**: [Re-entrant Auxetic Core Parametrization & Laser Powder Bed Fusion (DfAM) Constraints](docs/adr/0003-reentrant-auxetic-lattice-and-dfam-constraints.md)
- **`0004`**: [Physics-Guided Deep Residual Networks vs. Open HPC Numerical Solvers](docs/adr/0004-physics-guided-surrogate-vs-open-hpc-solvers.md)
- **`0005`**: [Open B-Rep CAD, Gmsh Tet10 Meshing, and NASA GEVS Spectral Pipeline](docs/adr/0005-open-brep-cad-gmsh-and-nasa-gevs-spectral-pipeline.md)
- **`0006`**: [Jury Defense Amendments and Canonical Engineering Reconciliation](docs/adr/0006-jury-defense-amendments-and-canonical-reconciliation.md)

---

## 📝 Citation

If you use this framework, computational models, or optimization pipeline in your academic research, please cite:

```bibtex
@thesis{andrade2026cubesat,
  author    = {Gabriel Marques de Andrade},
  title     = {Otimiza{\c{c}}{\~a}o Estrutural de Chassi CubeSat 1U com Metamateriais Aux{\'e}ticos em AlSi10Mg sob Cargas Din{\^a}micas de Lan{\c{c}}amento},
  school    = {Universidade Estadual de Santa Cruz (UESC)},
  year      = {2026},
  address   = {Ilh{\'e}us, BA, Brazil},
  type      = {Trabalho de Conclus{\~a}o de Curso (Engenharia Mec{\^a}nica)},
  note      = {Orientadora: Prof.ª Dr.ª Nila Cecília de Faria Lopes Medeiros}
}
```

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.
