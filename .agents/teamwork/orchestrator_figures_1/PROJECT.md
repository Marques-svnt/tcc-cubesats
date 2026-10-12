# Project: Visual Audit, Vector Generation, and Bilingual Manuscript Integration

## Architecture
- **Figure Generators**:
  - `generate_scientific_figures.py`
  - `generate_via_a_figures.py`
  - `generate_figures.py`
  - `generate_lpbf_additive_manufacturing_figures.py`
- **Figure Storage Repositories (8 Sync Targets)**:
  1. `figures/`
  2. `04-figuras/`
  3. `Entregas-finais/01-Tese-Exaustiva/figuras/`
  4. `Entregas-finais/02-Artigos-Cientificos/01-Materials-and-Design-Elsevier/figures/` (or local figures dir)
  5. `Entregas-finais/02-Artigos-Cientificos/02-Aerospace-Science-and-Technology-Elsevier/figures/` (or local figures dir)
  6. `Entregas-finais/02-Artigos-Cientificos/03-Engineering-Applications-of-AI-Elsevier/figures/` (or local figures dir)
  7. `Entregas-finais/03-TCC-Graduacao-UESC/figuras/`
  8. Any secondary root/doc figures folder mapped during survey
- **Document Targets**:
  - **Elsevier 1**: `Entregas-finais/02-Artigos-Cientificos/01-Materials-and-Design-Elsevier/main.tex` (English)
  - **Elsevier 2**: `Entregas-finais/02-Artigos-Cientificos/02-Aerospace-Science-and-Technology-Elsevier/main.tex` (English)
  - **Elsevier 3**: `Entregas-finais/02-Artigos-Cientificos/03-Engineering-Applications-of-AI-Elsevier/main.tex` (English)
  - **Thesis**: `Entregas-finais/01-Tese-Exaustiva/02-elementos-textuais/cap4-metodologia.tex` & `cap5-resultados_discussao.tex` (Portuguese pt-BR)
  - **UESC TCC**: `Entregas-finais/03-TCC-Graduacao-UESC/02-elementos-textuais/cap4-metodologia.tex` & `cap5-resultados_discussao.tex` (Portuguese pt-BR)

## Feature Inventory
| # | Feature | Description | Milestone | Source |
|---|---------|-------------|-----------|--------|
| 1 | Audit & Dual Export Pipeline | Update generator scripts for `.pdf` and `.png` (>=300 DPI), zero overlap, Okabe-Ito, typography 7.5-10pt | M1 | ORIGINAL_REQUEST §R1 |
| 2 | Figure Sync Across 8 Dirs | Synchronize all vector and raster figures across the 8 target directories | M1 | ORIGINAL_REQUEST §R1 |
| 3 | Materials & Design Integration | Integrate LPBF, Tet10 mesh zoom, and CAD models with Q1 English captions & discussion | M2 | ORIGINAL_REQUEST §R2 |
| 4 | Aerospace Science & Tech Integration | Integrate modal mode 1, P-POD SRS shock, and LPBF figures with Q1 English captions & discussion | M2 | ORIGINAL_REQUEST §R2 |
| 5 | Engineering Apps of AI Integration | Integrate ResNet telemetry dashboard and 3D neural response surface with Q1 English captions & discussion | M2 | ORIGINAL_REQUEST §R2 |
| 6 | Exhaustive Thesis Integration | Integrate LPBF, Tet10 mesh, CAD, ResNet dashboard, response surface, modal contour with ABNT pt-BR captions & text | M3 | ORIGINAL_REQUEST §R3 |
| 7 | UESC TCC Integration | Integrate LPBF, Tet10 mesh, CAD, ResNet dashboard, response surface, modal contour with ABNT pt-BR captions & text | M3 | ORIGINAL_REQUEST §R3 |
| 8 | Automated LaTeX Compilation & Verification | Scripted compilation of all 5 documents (`pdflatex` + `bibtex`), verifying exit code 0, no `??` or missing files | M4 | ORIGINAL_REQUEST §R4 |

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| 0 | Survey | Map scripts, figures, directory paths, and current LaTeX structure | none | IN_PROGRESS |
| 1 | Figure Generation & Vector Sync | Audit scripts, enforce dual export (.pdf/.png), run generation, sync 8 dirs | M0 | PLANNED |
| 2 | Elsevier Manuscripts Integration | Insert & reference figures in 3 Elsevier papers in English | M1 | PLANNED |
| 3 | Thesis & TCC Integration | Insert & reference figures in Thesis and TCC in pt-BR | M1 | PLANNED |
| 4 | Programmatic Compilation & Audit | Compile all 5 docs, check refs, run Reviewers & Forensic Auditor | M2, M3 | PLANNED |

## Interface Contracts
- **Figures**: Native `.pdf` vector format prioritized in LaTeX `\includegraphics`, fallback to `.png` where appropriate. Both files must exist in target figure folders.
- **Figure Labels**: Unique labels (`\label{fig:...}`) across each document.
- **Citations & Cross-references**: Every figure referenced via `\ref{fig:...}` in adjacent explanatory paragraphs.
- **Language Boundaries**:
  - Elsevier papers: 100% Academic English (0% Portuguese).
  - Thesis & TCC: 100% Formal pt-BR (0% untranslated English captions/text).
