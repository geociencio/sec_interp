# Next Steps - Phase v3.7.0 (Updated 2026-05-24)

## 🔍 Ground-Truth Audit (2026-05-24)

A full metric re-scan was performed. Key findings:
- **CC gate**: ✅ Confirmed — all functions CC ≤ 10 (`check_cc.py`)
- **i18n (AST)**: ✅ Confirmed — 0 violations (`verify_i18n_hygiene.py`)
- **i18n (analyzer)**: ⚠️ 254 MISSING_I18N flagged by `qgis-analyzer` (broader heuristic scope than AST checker)
- **Quality score**: 52.3 Stability / 90.7 Maintainability / 100 Security
- **Sessions**: 100+ logs in `docs/maintenance/`

The i18n Goal 1 is **partially complete**: the AST gate passes, but `qgis-analyzer` detects 254 strings its heuristic considers untranslated. These need triage into false positives vs genuine gaps.

## 🎯 Phase v3.7.0 Goals

### Goal 1: i18n — Dual-Scope Completion
- **AST gate**: ✅ `verify_i18n_hygiene.py` — 0 violations (blocking)
- **qgis-analyzer**: ⚠️ 254 MISSING_I18N remaining
  - [ ] Triage 254 analyzer flags: how many are false positives vs genuine gaps? <!-- id: 1.4 -->
  - [ ] Reduce genuine user-facing untranslated strings to < 20 <!-- id: 1.5 -->
  - [x] ~~Document dual-scope i18n in i18n-standards SKILL.md~~ <!-- id: 1.6 -->

### Goal 2: 3D Interpretation & Symbology Enhancements
- **Objective**: Extend custom rendering and styling features.
- **Tasks**:
  - [ ] Implement a live symbology/legend styling preview under the Settings sidebar. <!-- id: 2.1 -->
  - [ ] Investigate adaptive vertical exaggeration settings for complex structural projections. <!-- id: 2.2 -->
  - [ ] Expand Cartesian vertical projection integration tests for highly deviated drillhole surveys. <!-- id: 2.3 -->

### Goal 3: Agentic System Integrity (Phase 1)
- **Objective**: Metric coherence, documentation fixes, runtime adaptation.
- **Tasks**:
  - [x] Create `scripts/sync_metrics.py` — unified metric extraction <!-- id: 3.1 -->
  - [x] Update `QUICK_REFERENCE.md` with verified scores <!-- id: 3.2 -->
  - [x] Fix `memory_policy.md` session directory reference <!-- id: 3.3 -->
  - [x] Document dual-scope i18n in `i18n-standards/SKILL.md` <!-- id: 3.4 -->
  - [ ] Create `.codewhale/instructions.md` for runtime adaptation <!-- id: 3.5 -->
  - [x] ~~Resolve test count discrepancy (572 vs 620) via Docker run~~ → **620 confirmed** <!-- id: 3.6 -->

## 🛠️ Prioritized Technical Debt
- [ ] Add a strict check in pre-commit hooks to validate `qt6_compat` import hygiene across all GUI pages. <!-- id: 4.1 -->
- [ ] Fix 2 NON_PYTHONIC_LOOP issues flagged by qgis-analyzer <!-- id: 4.2 -->
- [ ] Investigate 1 SPATIAL_INDEX warning in `dialog_interpretation_manager.py` <!-- id: 4.3 -->

## 📋 Session Closed 2026-05-24 — Agentic System Audit Complete

All 5 phases of the Gen 6→7 improvement plan executed:
- Phase 0-5: ground-truth sync, metric integrity, runtime bridge, memory hardening, quality elevation, Gen 7 features
- 3 Gen 7 capabilities added: lesson extraction, metric trends, module size gate
- 7 scripts verified operational in CodeWhale runtime
- Commit: 2d2e0123

## 🚀 How to Resume
1. Run `uv run python scripts/sync_metrics.py` to refresh ground-truth metrics
2. Run `make docker-test` to get definitive test count
3. Continue with Goal 1.4 (i18n triage) or Goal 2.1 (symbology preview)
