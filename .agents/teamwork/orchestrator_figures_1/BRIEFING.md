# BRIEFING — 2026-10-11T17:37:00Z

## Mission
Orchestrate the visual audit, vector generation (.pdf/.png dual export), and bilingual manuscript integration across 3 Elsevier papers (English) and 2 academic theses (pt-BR) with programmatic compilation verification.

## 🔒 My Identity
- Archetype: orchestrator
- Roles: orchestrator, user_liaison, human_reporter, successor
- Working directory: /home/marques/Área de trabalho/2026.2/TCC/.agents/teamwork/orchestrator_figures_1
- Original parent: Sentinel
- Original parent conversation ID: 3053e456-f4e3-4b9b-82e9-f350ec8ddcb2

## 🔒 My Workflow
- **Pattern**: Project Pattern (Survey -> Decompose & Delegate / Iteration Loop)
- **Scope document**: /home/marques/Área de trabalho/2026.2/TCC/.agents/teamwork/orchestrator_figures_1/PROJECT.md
1. **Decompose**: Decompose the project into 4 milestones:
   - M1: Figures generation, audit, vectorization (.pdf + .png >=300 DPI), and directory synchronization
   - M2: Bilingual integration into 3 Elsevier manuscripts (English)
   - M3: Bilingual integration into Thesis and UESC TCC (pt-BR)
   - M4: Programmatic LaTeX compilation and reference integrity verification
2. **Dispatch & Execute**:
   - Survey via Explorers
   - Dispatch specialized workers, reviewers, challengers, and forensic auditor
3. **On failure**:
   - Retry -> Replace -> Skip -> Redistribute -> Redesign
4. **Succession**:
   - Self-succeed at 16 spawns
- **Work items**:
  1. Survey and environment mapping [in-progress]
  2. M1: Figure audit & vector standardization [pending]
  3. M2: Elsevier manuscripts integration [pending]
  4. M3: Thesis & TCC integration [pending]
  5. M4: Compilation & verification gate [pending]
- **Current phase**: 0 (Survey)
- **Current focus**: Surveying figure generators, directories, and LaTeX documents

## 🔒 Key Constraints
- NEVER write, modify, or create source code/LaTeX files directly.
- NEVER run build/test commands directly — require workers to do so.
- NEVER investigate at code level directly — dispatch Explorers.
- Only write/edit metadata .md files in .agents/teamwork/.
- Zero Text Overlap (anti-collision) in figures.
- Dual vector/raster export (.pdf and >=300 DPI .png).
- Strict language separation: 0% Portuguese in Elsevier papers, 0% English in Thesis/TCC captions.
- Automated compilation must exit with code 0 and zero broken references (??).
- Never reuse a subagent after handoff.

## Current Parent
- Conversation ID: 3053e456-f4e3-4b9b-82e9-f350ec8ddcb2
- Updated: 2026-10-11T17:36:46Z

## Key Decisions Made
- Decomposing into 4 distinct modular milestones.
- Surveying existing generator scripts and target directories first via parallel Explorers.

## Team Roster
| Agent | Type | Work Item | Status | Conv ID |
|-------|------|-----------|--------|---------|
| Explorer 1 | teamwork_preview_explorer | Figure-Script-Surveyor | in-progress | f2e139a8-bdd9-4238-bc06-450626e8061f |
| Explorer 2 | teamwork_preview_explorer | Figure-Directory-Surveyor | in-progress | 9b1e417e-25a1-4d2f-a22b-d0baba43182c |
| Explorer 3 | teamwork_preview_explorer | Manuscript-Pipeline-Surveyor | in-progress | 54bd7f7e-94f5-4994-bcfd-ad14da0510eb |

## Succession Status
- Succession required: no
- Spawn count: 3 / 16
- Pending subagents: f2e139a8-bdd9-4238-bc06-450626e8061f, 9b1e417e-25a1-4d2f-a22b-d0baba43182c, 54bd7f7e-94f5-4994-bcfd-ad14da0510eb
- Predecessor: none
- Successor: not yet spawned

## Active Timers
- Heartbeat cron: 70785b8c-5b5a-43a9-8941-5c6a85f747b7/task-12
- Safety timer: none

## Artifact Index
- /home/marques/Área de trabalho/2026.2/TCC/.agents/teamwork/ORIGINAL_REQUEST.md — Authoritative user request
- /home/marques/Área de trabalho/2026.2/TCC/.agents/teamwork/orchestrator_figures_1/DISPATCH.md — Initial dispatch message
- /home/marques/Área de trabalho/2026.2/TCC/.agents/teamwork/orchestrator_figures_1/PROJECT.md — Global plan and milestone definitions
- /home/marques/Área de trabalho/2026.2/TCC/.agents/teamwork/orchestrator_figures_1/progress.md — Execution heartbeat and progress
