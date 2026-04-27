# Next Steps — 2026-04-27 (agentic_standards_upgrade)

## Session Summary
All Gen 5 agentic system targets have been completed. The system is now aligned with
2025/2026 industry standards as documented in `OPTIMIZATION_PLAN.md`.

## Immediate Next Steps (Gen 6 — Pick up here)

### High Priority
1. **`scripts/memory_prune.py`** — Auto-prune consolidated lessons on `/close-session`
   - Read `AGENT_LESSONS.md`, find entries with `consolidated_in:` older than 90 days
   - Move them to the `[PRUNED]` index automatically
   - Integrate into `/close-session` Step 3

2. **`pre-push` CC gate** — Block pushes introducing CC regressions
   - Hook: `qgis-analyzer analyze . --output json` → check no new CC > 10 hotspots
   - File: `.git/hooks/pre-push` (or a `Makefile` target)

### Medium Priority
3. **Docstring coverage campaign** — Target `core/services/` and `core/utils/`
   - Current score: 41.7/100 (penalized by missing docstrings, NOT bugs)
   - Expected score after campaign: ~60/100
   - Command: `uv run ruff check --select D .` to identify gaps

4. **`scripts/context_selector.py`** — Semantic skill injection for `/start-session`
   - Reduce context tokens ~40% by loading only 2–3 relevant skills per task

5. **`SPATIAL_INDEX` warning** — `gui/dialog_interpretation_manager.py:123`
   - Low risk but should be addressed before next release

### Open Items (Non-blocking)
- Monitor Auditor critique effectiveness in real feature development
- Decide if a "Mobile" or "Web" blueprint is needed for the framework

## Resume Command
```bash
cd /home/jmbernales/qgispluginsdev/sec_interp
/start-session
```

## Current State (Verified — 2026-04-27 fresh analysis)
- **Tests**: 571 ✅
- **CC hotspots**: 0 ✅ (confirmed — no `HIGH_COMPLEXITY` in `qgis-analyzer analyze .` output)
- **skill_sync**: 13 skills / 15 workflows / 0 warnings
- **agent_metrics schema**: v2.0
- **AGENTS.md hierarchy**: root + core/ + gui/
- **Quality Scores**: Module Stability: 53.1/100 | Maintainability: 93.2/100 | Security: 100/100
- **Signal leaks detected**: 13 (all in export/settings page signals — see High Priority #2 below)

## Updated Priorities

### High Priority (newly confirmed)
- **13 signal leaks** in `settings_page.py` or related export widgets:
  `btn_reset_export.clicked`, `chk_3d_*`, `chk_exp_*`, `combo_format`, `txt_naming`
  → These need explicit `disconnect_signals()` implementation before next release.
