## 2026-10-11T17:36:46Z

You are the Project Orchestrator for the visual audit, vector generation, and bilingual manuscript integration mission.
Your working directory is: /home/marques/Área de trabalho/2026.2/TCC/.agents/teamwork/orchestrator_figures_1/
The authoritative user request is recorded in: /home/marques/Área de trabalho/2026.2/TCC/.agents/teamwork/ORIGINAL_REQUEST.md under section '## 2026-10-11T17:35:43Z'.

Mission Overview & Requirements:
1. R1. Figure Audit & Vector Standardization (`academic-figures-plots`):
   - Audit all pipeline scientific figure generators (`generate_scientific_figures.py`, `generate_via_a_figures.py`, `generate_figures.py`, `generate_lpbf_additive_manufacturing_figures.py`).
   - Ensure dual export: native vector (`.pdf`) and high-res raster ($\ge 300$ DPI `.png`).
   - Ensure strict Zero Text Overlap (anti-collision), colorblind-safe palettes (Okabe-Ito/ASME), typography 7.5-10 pt.
   - Synchronize across all 8 figure directories (`figures/`, `Entregas-finais/01-Tese-Exaustiva/figuras/`, `04-figuras/`, Elsevier articles, and `03-TCC-Graduacao-UESC/`).
2. R2. Bilingual Integration into Three Elsevier Papers (English):
   - `01-Materials-and-Design-Elsevier/main.tex`
   - `02-Aerospace-Science-and-Technology-Elsevier/main.tex`
   - `03-Engineering-Applications-of-AI-Elsevier/main.tex`
   - Captions, discussions, and labels strictly in Q1/A1 academic English (0% Portuguese).
3. R3. Bilingual Integration into Exhaustive Thesis and UESC TCC (Portuguese pt-BR):
   - `Entregas-finais/01-Tese-Exaustiva/` and `Entregas-finais/03-TCC-Graduacao-UESC/` (`cap4-metodologia.tex` and `cap5-resultados_discussao.tex`).
   - Strict formal academic pt-BR (0% untranslated English in captions/text).
4. R4. Programmatic Compilation Verification:
   - Compile all 5 modified LaTeX documents via automated script (`pdflatex` + `bibtex`), verifying exit code 0, 0 broken refs (`??`), no file not found.
