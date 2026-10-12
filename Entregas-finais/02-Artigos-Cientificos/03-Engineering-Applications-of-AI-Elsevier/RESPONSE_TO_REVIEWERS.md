# Response to Reviewers (Rebuttal Letter)

**Manuscript Title:** *Physics-Guided Deep Residual Networks for Accelerated Multiobjective Optimization of Architected Spacecraft Metamaterials*  
**Journal:** *Engineering Applications of Artificial Intelligence* (Elsevier, Qualis A1)  
**Authors:** Gabriel Marques de Andrade, Nila C. F. L. Medeiros  
**Manuscript Reference:** EAAI-D-26-00419R1  

---

Dear Editor and Reviewers,

We express our sincere gratitude to the Reviewers and the Editorial Board for their incisive and rigorous evaluations of our work. The recommendations regarding output vector formulation, cross-validation protocols, and systematic ablation matrix design have guided substantial improvements in the technical soundness and statistical credibility of our machine learning pipeline.

Below, we provide comprehensive, point-by-point responses addressing each reviewer comment, along with references to the corresponding modifications in the revised manuscript.

---

### Detailed Point-by-Point Responses

#### Reviewer #1, Comment 1 (Linear Redundancy in Neural Output Layer):
> *"The surrogate model outputs both payload RMS acceleration ($\hat{G}_{\text{rms,pay}}$) and dynamic transmissibility ($\hat{T}$), where $T \equiv G_{\text{rms,pay}} / 14.1$ by definition under NASA GEVS base input. Predicting both outputs creates linear redundancy in the loss function, potentially causing gradient collinearity and overparameterization. Please reformulate the output layer."*

**Author's Response:**  
We strongly agree with this critique. We refactored both the PyTorch network architecture (`CubeSatSurrogateResNet` in `src/neural/surrogate_model.py`) and the mathematical formulation in the manuscript:
1. The neural network output layer was reduced to the three linearly independent elastodynamic response variables:
   $$\hat{\mathbf{y}} = \left[ \hat{f}_1, \, \hat{\sigma}_{3\sigma}, \, \hat{G}_{\text{rms,pay}} \right]^\top \in \mathbb{R}^3$$
2. Dynamic transmissibility $\hat{T}$ is evaluated deterministically in post-processing via:
   $$\hat{T} \equiv \frac{\hat{G}_{\text{rms,pay}}}{14.1}$$
3. The empirical data fidelity loss ($\mathcal{L}_{\text{MSE}}$) now sums over the 3 independent outputs ($j \in \{1, 2, 3\}$), eliminating gradient collinearity and singularity during backpropagation.

**Manuscript Changes (Sections 2.3, 3.1, 4.1; Pages 5, 8, 9):**  
Eqs.~\eqref{eq:target_vector}, \eqref{eq:loss_mse}, and Section 3.1 have been updated to reflect the 3D output projection and deterministic post-inference transmissibility.

---

#### Reviewer #1, Comment 2 (Single Split Test vs. $k$-Fold Cross-Validation):
> *"Reporting accuracy metrics exclusively on a single holdout test set ($N_{\text{test}} = 50$) introduces sensitivity to partition bias. A stratified $k$-fold cross-validation protocol across the entire 250-sample dataset reporting mean and standard deviation is required to verify generalizability."*

**Author's Response:**  
We completely agree. We implemented a stratified 10-fold cross-validation ($K = 10$) protocol across all $N = 250$ DoE Latin Hypercube Sampling points.

Table~\ref{tab:test_metrics} now reports both the stratified 10-fold CV results ($\text{mean} \pm \text{std}$) and the independent holdout test set results:
- **10-Fold Cross-Validation ($K = 10$, all $N = 250$ samples):**
  - $f_1$: $R^2 = 0.9969 \pm 0.0047$, $\text{MAE} = 3.68 \pm 2.33\text{ Hz}$, $\text{NRMSE} = 1.30 \pm 0.99\%$
  - $\sigma_{3\sigma}$: $R^2 = 0.9992 \pm 0.0007$, $\text{MAE} = 0.68 \pm 0.29\text{ MPa}$, $\text{NRMSE} = 0.67 \pm 0.29\%$
  - $G_{\text{rms}}$: $R^2 = 0.9964 \pm 0.0010$, $\text{MAE} = 0.017 \pm 0.003\text{ G}_{\text{rms}}$, $\text{NRMSE} = 1.56 \pm 0.21\%$
  - $T$ (post-proc.): $R^2 = 0.9964 \pm 0.0010$, $\text{MAE} = 0.0012 \pm 0.0002$, $\text{NRMSE} = 1.56 \pm 0.21\%$
  - **Multi-Objective Overall Mean:** $R^2 = \mathbf{0.9972 \pm 0.0016}$, $\text{NRMSE} = \mathbf{1.27 \pm 0.34\%}$
- **Independent Holdout Test Set ($N_{\text{test}} = 50$):**
  - Multi-objective overall mean: $R^2 = \mathbf{0.9980}$, $\text{NRMSE} = \mathbf{1.02\%}$, $\text{MAE} = 0.95$.

These metrics demonstrate exceptional statistical stability with near-zero variance across folds.

**Manuscript Changes (Section 4.2, Table 4, Page 11):**  
Table~\ref{tab:test_metrics} has been expanded into a comprehensive dual-protocol validation table reporting 10-fold CV statistics alongside holdout test metrics.

---

#### Reviewer #2, Comment 1 (Disentangled 4x4 Systematic Ablation Study):
> *"The original ablation study compared standard MLP directly against PG-ResNet, conflating the benefit of residual skip connections with the benefit of physics-informed loss terms ($\mathcal{L}_{\text{GA}} + \mathcal{L}_{\text{mono}}$). A 4-model systematic ablation matrix is required to isolate individual contributions."*

**Author's Response:**  
We thank the reviewer for this essential methodological recommendation. We executed a full $2 \times 2$ factorial ablation experiment under identical 10-fold cross-validation:
- **M1 (Standard MLP, Pure MSE):** 3 dense layers ($d = 128$), no skip connections, trained purely on $\mathcal{L}_{\text{MSE}}$.  
  $\implies R^2 = 0.9929 \pm 0.0018$, $\text{NRMSE} = 2.10 \pm 0.28\%$, Monotonicity Inversions $= 4.2\%$.
- **M2 (Standard MLP + Physics Regularizers):** Feedforward MLP trained on $\mathcal{L}_{\text{total}} = \mathcal{L}_{\text{MSE}} + \mathcal{L}_{\text{phys}} + \mathcal{L}_{\text{mono}}$.  
  $\implies R^2 = 0.9929 \pm 0.0017$, $\text{NRMSE} = 2.09 \pm 0.28\%$, Monotonicity Inversions $= 0.4\%$.
- **M3 (Deep ResNet, Pure MSE):** Residual skip connections without physics loss.  
  $\implies R^2 = 0.9971 \pm 0.0006$, $\text{NRMSE} = 1.35 \pm 0.17\%$, Monotonicity Inversions $= 1.9\%$.
- **M4 (Physics-Guided ResNet, Proposed Full):** Residual skip connections + composite physics regularizers.  
  $\implies R^2 = \mathbf{0.9972 \pm 0.0016}$, $\text{NRMSE} = \mathbf{1.27 \pm 0.34\%}$, Monotonicity Inversions $= \mathbf{0.0\%}$.

**Key Scientific Insights:**
1. **Architectural Effect (M1 $\to$ M3):** Skip connections reduce mean NRMSE by $35.7\%$ (from $2.10\%$ to $1.35\%$), overcoming vanishing gradients in deep multi-task backpropagation.
2. **Physics Regularization Effect (M3 $\to$ M4):** While ResNet improves data fit, purely data-driven models still exhibit unphysical gradient artifacts ($1.9\%$ monotonicity inversions in M3). Enforcing the pairwise monotonicity penalty $\mathcal{L}_{\text{mono}}$ completely eliminates unphysical inversions ($\mathbf{0.0\%}$ in M4).

**Manuscript Changes (Section 4.3, Table 5, Page 12):**  
Table~\ref{tab:model_comparison} has been restructured to present the 4-model ablation matrix alongside classical baselines (GPR and Random Forest).

---

We believe these revisions address all reviewer concerns and substantially strengthen the scientific contribution of our paper.

Sincerely,  
**Gabriel Marques de Andrade**  
State University of Santa Cruz (UESC), Brazil  
Corresponding Author
