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
- **qgis-analyzer**: ✅ 79 MISSING_I18N triaged (2026-07-20 session)
  - [x] Triage 79 analyzer flags: 9 genuine gaps fixed, 70 false positives (dict keys, CSS, logging, HTML markup)
  - [x] Reduce genuine user-facing untranslated strings to 0
  - [x] ~~Document dual-scope i18n in i18n-standards SKILL.md~~
- **Gaps fixed (session 2026-07-20)**:
  - `dialog_export_manager.py`: Export Error, Data Export Error, Unexpected Data Export Error
  - `dialog_preview_manager.py`: Preview Error, Unexpected Preview Error, Critical Error, Geology Error, Drillhole Error
  - `dialog_interpretation_manager.py`: "ID:" label in results HTML

### Goal 2: 3D Interpretation & Symbology Enhancements
- **Objective**: Extend custom rendering and styling features.
- **Tasks**:
  - [ ] Implement a live symbology/legend styling preview under the Settings sidebar. <!-- id: 2.1 -->
  - [x] Implementation plan created (session 2026-07-20): `docs/plans/implementation_plan_adaptive_ve_v3.7.0.md` — 5-fase plan with aspect-ratio algorithm + structural density factor <!-- id: 2.2 -->
  - [ ] Execute Fase 1: Implement `core/services/vertical_exaggeration_service.py` + unit tests <!-- id: 2.2a -->
  - [ ] Execute Fase 2: Add Auto/Manual toggle to `dem_page.py` <!-- id: 2.2b -->
  - [ ] Execute Fase 3: Integrate into `sec_interp_plugin.py` render pipeline <!-- id: 2.2c -->
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
- [x] Migrate to scoped enums for Qt6/QGIS 4 (114 enum errors resolved via pyqt5_to_pyqt6.py). Mocks updated. Gate wired into pre-release + CI. <!-- id: 4.1 -->
- [ ] Retire `core/utils/qt6_compat.py` monkeypatch (harmless fallback, now unused) <!-- id: 4.1b -->
- [ ] Fix 2 NON_PYTHONIC_LOOP issues flagged by qgis-analyzer <!-- id: 4.2 -->
- [ ] Investigate 1 SPATIAL_INDEX warning in `dialog_interpretation_manager.py` <!-- id: 4.3 -->

## 📋 Session Closed 2026-09-06 — Qt6 Scoped Enum Migration + Releases v3.7.0/v3.7.1

Achieved in this session:
- **Releases**: v3.7.0 (i18n gate + collapsible controls) and v3.7.1 (security patch).
- **Security**: fixed silent `try/except/pass` (Bandit B110); wired full Bandit scan into release workflow.
- **Qt6 migration**: resolved all 114 `pyqgis4-checker` enum errors via `pyqt5_to_pyqt6.py` auto-fix; updated test mocks; bumped `qgisMinimumVersion` 3.0 → 3.28.
- **Gate**: added `make qt6-check`/`make qt6-fix` + GitHub Actions `qt6` job + `pre-release` wiring.
- **Packaging**: excluded `.codewhale`/`.continue`/`.deepseek`/`artifacts`/`.doctrees`/fonts from ZIP (25MB → 3.3MB).

## 🚀 How to Resume
1. Run `/start-session`.
2. Continue with Goal 2.1 (symbology preview), Fase 1 adaptive VE, or tech debt 4.1b/4.2/4.3.
