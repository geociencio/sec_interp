# Next Steps - Phase v3.7.0 (Updated 2026-05-27)

## 🔍 Ground-Truth Audit (2026-05-24)

A full metric re-scan was performed. Key findings:
- **CC gate**: ✅ Confirmed — all functions CC ≤ 10 (`check_cc.py`)
- **i18n (AST)**: ✅ Confirmed — 0 violations (`verify_i18n_hygiene.py`)
- **i18n (analyzer)**: ⚠️ 254 MISSING_I18N flagged by `qgis-analyzer` (broader heuristic scope than AST checker)
- **Quality score**: 52.3 Stability / 90.7 Maintainability / 100 Security
- **Sessions**: 100+ logs in `docs/maintenance/`
- **Tests**: 620 passing (confirmed via `make docker-test`)

## 🎯 Phase v3.7.0 Goals

### Goal 1: i18n — Dual-Scope Completion
- **AST gate**: ✅ `verify_i18n_hygiene.py` — 0 violations (blocking)
- **qgis-analyzer**: ⚠️ 79 MISSING_I18N remaining
  - [ ] Triage 79 analyzer flags: how many are false positives vs genuine gaps? <!-- id: 1.4 -->
  - [ ] Reduce genuine user-facing untranslated strings to < 20 <!-- id: 1.5 -->
  - [x] ~~Document dual-scope i18n in i18n-standards SKILL.md~~ <!-- id: 1.6 -->

### Goal 2: 3D Interpretation & Symbology Enhancements
- **Objective**: Extend custom rendering and styling features.
- **Tasks**:
  - [ ] Implement a live symbology/legend styling preview under the Settings sidebar. <!-- id: 2.1 -->
  - [ ] Investigate adaptive vertical exaggeration settings for complex structural projections. <!-- id: 2.2 -->
  - [ ] Expand Cartesian vertical projection integration tests for highly deviated drillhole surveys. <!-- id: 2.3 -->

### Goal 3: Agentic System Integrity (Phase 2 — COMPLETE)
- **Objective**: Gen 7 automation scripts, metric coherence, runtime adaptation.
- **Tasks**:
  - [x] Create `scripts/sync_metrics.py` — unified metric extraction <!-- id: 3.1 -->
  - [x] Update `QUICK_REFERENCE.md` with verified scores <!-- id: 3.2 -->
  - [x] Fix `memory_policy.md` session directory reference <!-- id: 3.3 -->
  - [x] Document dual-scope i18n in `i18n-standards/SKILL.md` <!-- id: 3.4 -->
  - [x] Create `.codewhale/instructions.md` for runtime adaptation <!-- id: 3.5 -->
  - [x] ~~Resolve test count discrepancy (572 vs 620) via Docker run~~ → **620 confirmed** <!-- id: 3.6 -->
  - [x] Create `scripts/validate_agent_metrics.py` — cross-file metric validator <!-- id: 3.7 -->
  - [x] Create `scripts/workflow_graph.py` — workflow→script→skill dependency graph <!-- id: 3.8 -->
  - [x] Create `scripts/workflow_executor.py` — runtime-agnostic workflow translator <!-- id: 3.9 -->
  - [x] Create `scripts/lesson_extractor.py` — auto-propose AGENT_LESSONS candidates <!-- id: 3.10 -->
  - [x] Create `scripts/validate_agent_system.py` — .agent/ structure validator <!-- id: 3.11 -->
  - [x] Create `scripts/session_index.py` — chronological index of maintenance logs <!-- id: 3.12 -->
  - [x] Enhanced `scripts/metrics_report.py` with sparklines, bar charts, session delta <!-- id: 3.13 -->
  - [x] Added trigger fields to changelog-generator, i18n-standards, qgis-migration-4x skills <!-- id: 3.14 -->
  - [x] Added metric coherence validation to /start-session and /close-session <!-- id: 3.15 -->
  - [x] Fixed stale test counts (535/572 → 620) and quality scores (40.8 → 52.3) in 12 files <!-- id: 3.16 -->
  - [x] Fixed CC threshold 15 → 10, Gen 5 → 6, python3 → uv run python <!-- id: 3.17 -->
  - [x] Updated memory_policy.md: pruning quarterly → monthly <!-- id: 3.18 -->

## 🛠️ Prioritized Technical Debt
- [ ] Add a strict check in pre-commit hooks to validate `qt6_compat` import hygiene across all GUI pages. <!-- id: 4.1 -->
- [ ] Fix 2 NON_PYTHONIC_LOOP issues flagged by qgis-analyzer <!-- id: 4.2 -->
- [ ] Investigate 1 SPATIAL_INDEX warning in `dialog_interpretation_manager.py` <!-- id: 4.3 -->

## 📋 Sessions Closed 2026-05-26/27 — Agentic System Gen 7 Completion

The `.agent/` system reached operational maturity with 12 new automation scripts and 4 enhanced workflows:

**Gen 7 Scripts (12 total):**
- `sync_metrics.py` — unified ground-truth extraction
- `validate_agent_metrics.py` — cross-file consistency checker
- `workflow_graph.py` — dependency graph & broken ref detector
- `workflow_executor.py` — runtime-agnostic translator
- `lesson_extractor.py` — auto-propose AGENT_LESSONS candidates
- `session_index.py` — chronological maintenance log index
- `validate_agent_system.py` — .agent/ structure integrity validator
- `metrics_report.py` — enhanced with sparklines, bar charts, delta
- `memory_prune.py` — monthly lesson pruning (cadence shortened)
- `context_selector.py` — semantic skill injection
- `check_cc.py` — CC ≤ 10 gate
- `verify_i18n_hygiene.py` — AST-based i18n gate

**Session metrics:**
- 2 commits: `e8f3dbc`, `f796f0e`
- 12 new/8 modified files in `.agent/` + 6 new scripts
- Tests: 620 passing (Docker confirmed)
- All quality gates PASS

## 🚀 How to Resume
1. Run `/start-session` — now includes automatic metric validation and delta check
2. Continue with Goal 1.4 (i18n triage of 79 analyzer flags) or Goal 2.1 (symbology preview)
