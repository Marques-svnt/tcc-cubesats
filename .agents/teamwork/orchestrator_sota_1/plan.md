# Plan: SOTA Benchmarking & Global Scientific Positioning

## Architecture & Work Breakdown
The objective is to produce two high-impact, publication-grade academic reports benchmarking our 1U CubeSat AlSi10Mg re-entrant auxetic chassis against global state-of-the-art literature:
1. `sota_mapping_report.md`
2. `novelty_assessment_report.md`

### Milestone 1: Multi-Base Systematic Literature Discovery & Exploration
- Dispatch 3 parallel Explorers:
  - **Explorer 1 (Metamaterials & DfAM)**: Search Crossref, OpenAlex, Semantic Scholar, arXiv, Google Scholar for metallic LPBF auxetic structures, vibroacoustic isolation, satellite brackets/chassis.
  - **Explorer 2 (CubeSat Launch Qualification)**: Search for CubeSat primary structure qualification under NASA GSFC-STD-7000A GEVS, deployer (P-POD) dynamics, random vibration PSD, and fatigue damage (Steinberg).
  - **Explorer 3 (Physics-Guided AI & Multi-objective Optimization)**: Search for Physics-Guided ResNets, PINNs for lattice structures, NSGA-II multiobjective optimization, speedup factors, and constitutive loss formulations.

### Milestone 2: Taxonomic SOTA Matrix & Snowballing
- Map 4 to 6 competitive international Q1 baselines from peer-reviewed literature (2022–2026):
  - Author, Year, Title, Journal (Q1/A1), DOI.
  - Performance vectors: Mass reduction %, $f_1$ (clamped & deployer), Attenuation dB (RMS reduction %), DfAM compliance, Steinberg damage $D$, Surrogate acceleration.
  - Rigorous comparison against Candidate #28 from `PARAMETROS_CANONICOS.md`.

### Milestone 3: Novelty Delta, Nickerson Taxonomy & TRL Assessment
- Rigorous formalization of:
  - $\Delta_{\text{nov}} = \{\Delta_{\text{metodológico}}, \Delta_{\text{teórico}}, \Delta_{\text{empírico}}\}$.
  - Innovation regime classification (Architectural/Systemic vs Incremental/Modular).
  - TRL assessment (NASA/ESA scale TRL 1 to 9) anchored in `Entregas-finais` evidence base, with detailed maturation roadmap towards TRL 7–8.

### Milestone 4: Deliverable Authoring & Vault Sync
- Worker drafts both exhaustive reports in `/home/marques/Área de trabalho/2026.2/TCC/benchmarks/sota_assessment/`.
- Synchronizes artifacts to `/home/marques/vault/svnt/04-Projetos/TCC-CubeSat/SOTA/`.

### Milestone 5: Dual Review & Forensic Audit Gate
- Reviewer 1 (Aerospace & Metamaterials focus).
- Reviewer 2 (Surrogate AI & Optimization focus).
- Forensic Auditor (teamwork_preview_auditor) verifying metric fidelity against PARAMETROS_CANONICOS.md, non-hallucination of DOIs/papers, and adherence to integrity guidelines.
