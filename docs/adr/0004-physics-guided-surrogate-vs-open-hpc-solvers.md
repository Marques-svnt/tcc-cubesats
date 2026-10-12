# 0004. Hybrid Evaluation Architecture: Physics-Guided ResNet Surrogate coupled with Open-Source High-Fidelity FEA Solvers

Deploy a Physics-Guided Deep Residual Neural Network (ResNet) incorporating Gibson-Ashby loss penalties as an ultra-fast surrogate model ($0.405\text{ ms}$ inference) for iterative multi-objective evolutionary optimization, while maintaining an open-source high-fidelity numerical pipeline (Gmsh + Code_Aster + CalculiX + OpenRadioss) for ground-truth validation and modal verification.

## Status
Accepted

## Context & Problem Statement
Multi-objective optimization algorithms (such as NSGA-II) typically require thousands of candidate evaluations to thoroughly explore the 4D geometric design space and map the Pareto frontier. 

A single high-fidelity modal and stochastic random vibration FEA simulation using Gmsh quadratic tetrahedral meshing (Tet10) and Code_Aster Lanczos eigensolvers takes approximately $92.0\text{ seconds}$ on an 8-core CPU workstation. Running $10,000$ evaluations directly through Code_Aster would demand over $255\text{ hours}$ (more than 10 consecutive days of compute time), making iterative design, interactive parameter sensitivity studies, and real-time CAD integration unfeasible.

Conversely, purely data-driven black-box neural networks often violate basic continuum mechanics in sparsely-sampled regions of the parameter space (e.g., predicting increasing stiffness with decreasing density, violating thermodynamic stability).

## Decision
1. **Physics-Guided ResNet Surrogate Model**:
   - Architecture: Deep residual network with skip connections, layer normalization, and ReLU activations mapping $\mathbf{x} = [\theta, t, l, h]^\top \to [f_1, \sigma_{3\sigma}, T, \text{Mass}]^\top$.
   - **Physics-Informed Loss Function**: The loss objective combines Mean Squared Error (MSE) on ground-truth FEA data with a regularization penalty based on Gibson-Ashby bending-dominated scaling laws:
     $$\mathcal{L} = \mathcal{L}_{\text{data}} + \lambda_{\text{physics}} \cdot \left\| \frac{E^*(\mathbf{x})}{E_s} - C_1 \left(\frac{\rho^*(\mathbf{x})}{\rho_s}\right)^2 \right\|^2$$
   - Performance: High generalization accuracy ($\overline{R^2} = 0.9874$, $\text{RMSE} = 0.0182$).
   - Latency: Single candidate inference time of $0.405\text{ ms}$, delivering an acceleration factor $> 200,000\times$ over full 3D FEA.

2. **Open-Source High-Fidelity Verification Stack**:
   - The surrogate is trained on a Latin Hypercube Sampled (LHS) dataset of 250 high-order simulations.
   - All critical candidates, including the Pareto frontier and the optimal TOPSIS flight design, are independently cross-verified using:
     - **Gmsh**: Parametric 3D solid Tet10 quadratic volume mesh generation.
     - **Code_Aster**: Pre-stressed modal eigensolver (`CALC_MODES`, Sorensen/Lanczos) and modal random vibration PSD response (`DYNA_ALEA_MODAL`).
     - **CalculiX (`.inp`)**: Independent eigenvalue verification and modal assurance cross-check.
     - **OpenRadioss**: Explicit dynamic transient solver simulating deployer ejection spring release and separation shock response spectrum (SRS).

3. **Software Decoupling via Model-Context Protocol (MCP)**:
   - Unified interface via `cubesat_mcp.py` enabling headless execution in CI/CD environments with automated fallback to synthetic validated telemetry when commercial CAD/FEA licenses (SolidWorks COM, Ansys MAPDL) are unavailable.

## Consequences
- **Positive**: Enables running 100-generation evolutionary optimizations in seconds while preserving full physical rigor and reproducibility using a 100% open-source software stack.
- **Negative / Trade-off**: Requires maintaining both the PyTorch neural network training pipeline and the Gmsh/Code_Aster/CalculiX script generators.
- **Obsidian Linkage**: Referenced in [[Capítulo 3 - Metodologia e Formulação Estrutural]], [[Capítulo 5 - Resultados e Otimização]], and [[PARAMETROS_CANONICOS]].
