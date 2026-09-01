# Session 2026-07-20c — Collapsible Preview Controls

**Date**: 2026-07-20
**Topic**: `collapsible_preview_controls`
**Phase**: v3.7.0 — Goal 2 (UX enhancement)
**Commit**: `e6c1b1a`

---

## Executive Summary

Separated the preview map canvas from the action buttons, LOD controls, and layer checkboxes by wrapping them in a `QgsCollapsibleGroupBox("Controls")`. The canvas and status bar remain always-visible, while controls and results can be collapsed independently.

---

## Main Achievements

### Layout Refactor
- Added `_setup_controls_group()` to assemble a collapsible "Controls" section
- Refactored `_setup_action_buttons()`, `_setup_lod_controls()`, and `_setup_layer_checkboxes()` to accept a `parent_layout` parameter instead of binding to `self.frame_layout`
- Resulting structure: Canvas (always visible) → Controls (collapsible) → Results (collapsible)

### Quality Gates
- ruff check: PASS
- ruff format: PASS
- CC gate: PASS
- i18n AST gate: PASS (new "Controls" string wrapped in `self.tr()`)
- Docker tests: 620/620 PASS

## Files Modified

| File | Changes |
|---|---|
| `gui/ui/pages/preview_page.py` | 18 insertions, 9 deletions |

## Next Session

Execute `/start-session` and begin Fase 1: implement `core/services/vertical_exaggeration_service.py` with unit tests.
