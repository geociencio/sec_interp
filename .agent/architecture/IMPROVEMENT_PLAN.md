# Agentic System Improvement Plan — SecInterp

> **Created**: 2026-05-24 | **Updated**: 2026-09-12 (Phase 1-3 complete, Phase 4 partial)
> **Based on**: Full audit of `.agent/` system (Gen 6) + live qgis-analyzer + check_cc.py + verify_i18n_hygiene.py
> **Scope**: .agent/ system integrity, metric coherence, and runtime adaptation
> **Status**: 🟢 Phases 1-3 shipped. Remaining: Phase 4 quick wins (4.1.1, 4.1.2, 4.1.4).

---

## Executive Summary

The `.agent/` system is architecturally mature (Gen 6, 18 sessions, 100% task completion, 100+ session logs in `docs/maintenance/`). Phase 0 ground-truth audit revealed **two tooling scope mismatches** (not system failures) and one real metric gap:

- **CC gate**: ✅ CONFIRMED — `check_cc.py` verifies all functions CC ≤ 10. `AI_CONTEXT.md` avg 13.6 is from a different analyzer (ai-ctx) with different measurement.
- **i18n**: ⚠️ SCOPE MISMATCH — `verify_i18n_hygiene.py` checks `self.tr()` wrapping (0 violations). `qgis-analyzer` finds 254 MISSING_I18N (broader detection). Neither is wrong — they measure different things.
- **Quality score**: ✅ CORRECTED — was stale 40.8. Real score is 52.3 (Module Stability) / 90.7 (Maintainability) from qgis-analyzer.
- **Sessions**: ✅ CONFIRMED — 100+ session logs in `docs/maintenance/`, not `.agent/history/sessions/`. Memory policy reference needs update.

---

## Phase 0: Ground-Truth Synchronization ✅ COMPLETE

**Executed**: 2026-05-24

### 0.1 Actual Findings (correcting initial assumptions)

| Metric | Previous `.agent/` claim | Ground truth (2026-05-24) | Verdict |
|--------|-------------------------|--------------------------|---------|
| CC gate | CC ≤ 10 enforced | ✅ `check_cc.py`: all functions comply | CLAIM VALID |
| Quality score | 40.8 | **52.3** (Stability) / **90.7** (Maintainability) | WAS STALE |
| Security score | Not tracked | **100.0/100** (Bandit) | EXCELLENT |
| Docstrings | 100% claimed | **100%** confirmed by qgis-analyzer | CLAIM VALID |
| Return types | 100% claimed | **100%** confirmed by qgis-analyzer | CLAIM VALID |
| Param types | Not tracked | **94.2%** | GOOD |
| i18n (AST) | Goal 1 complete | ✅ `verify_i18n_hygiene.py`: 0 violations | CLAIM VALID |
| i18n (analyzer) | Not tracked separately | ⚠️ **254 MISSING_I18N** from qgis-analyzer | SCOPE GAP |
| Total issues | Not tracked | **257** (254 i18n + 2 loop + 1 spatial) | NEW |
| Test count | 572/620 conflicting | **620 verified** via Docker (2026-05-24) | RESOLVED |
| Sessions dir | Assumed `.agent/history/sessions/` | Actually `docs/maintenance/` (100+ files) | DOC FIX NEEDED |

### 0.2 Actions Completed

- [x] **0.2.1** Test discovery: 92 ran locally, 84 errors (QGIS env required). Full count needs Docker.
- [x] **0.2.2** `qgis-analyzer analyze .` executed — ground-truth captured in `analysis_results/`
- [x] **0.2.3** `check_cc.py` executed — PASS, all functions CC ≤ 10
- [x] **0.2.4** `verify_i18n_hygiene.py` executed — PASS, 53 files, 0 violations
- [x] **0.2.5** `agent_metrics.json` updated with verified scores, ground_truth_sources section added

### 0.3 Root Cause of Discrepancies

1. **Quality score 40.8 → 52.3**: The old number was from a prior qgis-analyzer version or before docstring/CC campaigns completed. The system never re-ran the analyzer after fixes.
2. **CC 13.6 vs CC ≤ 10**: `AI_CONTEXT.md` uses `ai-ctx` which measures *average* CC including legacy code. `check_cc.py` enforces *maximum* CC ≤ 10 per function. Both are correct within their own scope.
3. **i18n 0 vs 254**: `verify_i18n_hygiene.py` uses AST parsing for `self.tr()` wrapping (narrow scope). `qgis-analyzer` uses broader heuristics detecting *any* user-facing string without translation context. The AST checker was designed to eliminate false positives, not catch all analyzer-flagged strings.

---

## Phase 1: Metric Integrity & Automation 🔴 HIGH

**Problem**: Metrics are updated manually and inconsistently. The system declared 40.8 quality score for weeks after the real score improved to 52.3.

### 1.1 Centralize Metric Extraction

- [x] **1.1.1** Create `scripts/sync_metrics.py` that:
  1. Runs `qgis-analyzer analyze .`
  2. Runs `check_cc.py`
  3. Runs `verify_i18n_hygiene.py`
  4. Writes unified metrics to `agent_metrics.json` summary
  5. Flags any score that changed by >5 points since last run
- [x] **1.1.2** Add metric sync as step in `/close-session` workflow
- [x] **1.1.3** Document the difference between `verify_i18n_hygiene.py` (AST, `self.tr()` wrapping) and `qgis-analyzer i18n` (heuristic, broader) in `.agent/skills/i18n-standards/SKILL.md`

### 1.2 Documentation Fixes

- [x] **1.2.1** Update `QUICK_REFERENCE.md` quality score from 40.8 → 52.3, add maintainability 90.7
- [x] **1.2.2** Update `README.md` quality badge to reflect 52.3
- [x] **1.2.3** Fix `memory_policy.md` — session directory is `docs/maintenance/`, not `.agent/history/sessions/`
- [x] **1.2.4** Resolve test count discrepancy: run `make docker-test` and record definitive number (620)

### 1.3 i18n Strategy Clarification

- [x] **1.3.1** Decide: is target 0 violations on `verify_i18n_hygiene.py` (achieved) or 0 on `qgis-analyzer i18n` (254 remaining)? → Dual-scope: AST gate blocking, analyzer triaged.
- [x] **1.3.2** If targeting analyzer: triage 254 MISSING_I18N into false positives vs real gaps → 72 false positives, 0 genuine remaining.
- [x] **1.3.3** Update `.agent/next_steps.md` Goal 1 status accordingly

---

## Phase 2: Runtime Adaptation 🟡 MEDIUM

**Problem**: The `.agent/` system is designed for Antigravity/Gemini runtime. Current runtime is CodeWhale/DeepSeek V4.

### 2.1 CodeWhale Integration

- [x] **2.1.1** Create `.codewhale/instructions.md` with:
  - Skill load mappings (`.agent/skills/` ↔ CodeWhale skills)
  - Workflow translations (what to read/run for each `.agent/workflows/` doc)
  - Tool availability matrix
- [x] **2.1.2** Test all Gen 6 scripts via `exec_shell`:
  - `scripts/check_cc.py` ✅ tested, works
  - `scripts/verify_i18n_hygiene.py` ✅ tested, works
  - `scripts/context_selector.py` ✅ tested, works
  - `scripts/memory_prune.py` ✅ tested, works
  - `scripts/metrics_report.py` ✅ tested, works
  - `scripts/skill_sync.py` ✅ tested, works

---

## Phase 3: Memory System Hardening 🟡 MEDIUM

### 3.1 Session History

- [x] **3.1.1** Update `memory_policy.md` Tier 2 reference: `docs/maintenance/` (confirmed, 100+ files)
- [x] **3.1.2** Update `/close-session` workflow to reflect actual path (`docs/maintenance/session_YYYY-MM-DD_[topic].md`)
- [x] **3.1.3** Add cross-reference index in `.agent/README.md` to `docs/maintenance/`

### 3.2 Lessons Coverage

- [x] **3.2.1** Add lesson to `AGENT_LESSONS.md` about this ground-truth audit (metric staleness risk)
- [x] **3.2.2** Add lesson about `verify_i18n_hygiene.py` vs `qgis-analyzer i18n` scope difference

---

## Phase 4: Quality Score Elevation 🟢 LOW

**Current**: Module Stability 54.0/100, Maintainability 99.9/100, Security 100/100

### 4.1 Quick Wins

- [x] **4.1.1** Fix 2 NON_PYTHONIC_LOOP issues → `enumerate` over a generator.
- [x] **4.1.2** Fix 1 SPATIAL_INDEX warning → `QgsFeatureRequest().setFilterRect()`.
- [x] **4.1.3** Triage 254 MISSING_I18N — how many are real user-facing strings? → 72 false positives, 0 real gaps.
- [x] **4.1.5** Resolve `module_size_gate` (7 modules > 400 lines → all < 300) — 52.4 → 54.0.
- [ ] **4.1.4** Target: push Stability from 54.0 → 60+ by resolving top penalty factors

---

## Phase 5: Gen 6 → Gen 7 Evolution 🟢 LOW (Future)

### 5.1 Gen 6 Completion Audit

- [x] `scripts/memory_prune.py` — exists (runtime tested)
- [x] `scripts/context_selector.py` — exists (runtime tested)
- [x] `scripts/metrics_report.py` — exists (runtime tested)
- [x] `check_cc.py` CC gate — confirmed working
- [x] Pre-push hook effectiveness — verified (CC gate blocks push)

### 5.2 Gen 7 Proposals

| Proposal | Rationale | Status |
|----------|-----------|--------|
| Runtime-agnostic workflow descriptions | Decouple from Antigravity-specific commands | ✅ `workflow_executor.py` + `.codewhale/instructions.md` |
| Cross-skill conflict detection | When two skills give contradictory guidance | ⏳ Not started |
| Automated lesson extraction | LLM proposes AGENT_LESSONS.md entries from session summaries | ✅ `lesson_extractor.py` |
| Metric trend dashboard | Visualize quality score / CC / i18n over time | ✅ `metrics_report.py` (sparklines, session delta) |

---

## Updated Success Criteria

| Criterion | Before Phase 0 | After Phase 0 | Target |
|-----------|---------------|---------------|--------|
| Metric coherence | ❌ Conflicting | ✅ Single source with provenance | ✅ Maintained |
| CC gate effectiveness | ❓ Unknown | ✅ Confirmed working (CC ≤ 10) | ✅ Maintained |
| Quality score accuracy | ❌ Stale 40.8 | ✅ Live 54.0 / 99.9 | → 60+ |
| i18n status clarity | ❌ "100% complete" ambiguous | ✅ Two metrics documented | ✅ Clarified |
| Session history | ❓ Assumed missing | ✅ Confirmed in docs/maintenance/ | ✅ Docs updated |
| Runtime operability | ❌ Antigravity-only | ⏳ Phase 2 pending | ✅ CodeWhale-compatible |
| Security posture | ❓ Unknown | ✅ 100/100 Bandit | ✅ Maintained |

---

*Phases 0-3 complete (2026-09-12). Remaining: Phase 4 quick wins (4.1.1, 4.1.2, 4.1.4) and Phase 5 cross-skill conflict detection.*
*Sessions directory confirmed: `docs/maintenance/` (not `.agent/history/sessions/`)*
