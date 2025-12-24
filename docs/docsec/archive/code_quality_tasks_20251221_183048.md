# Task: Optimize Code Quality

## Refactoring Targets
- [x] Refactor `core/validation.py` to reduce complexity (Complexity: High)
  - [x] Split validation logic into specialized validators (e.g., `LayerValidator`, `FieldValidator`)
  - [x] Create facade for backward compatibility
  - [x] Implement tests without QGIS dependencies (32/36 passing)
  - [ ] Complete mocking for geometry processing tests (4 remaining)
- [ ] Refactor `gui/main_dialog.py` to reduce complexity (Complexity: 95)
  - [ ] Extract additional logic into separate managers or page-specific controllers
- [ ] Address Architectural Violations
  - [ ] Move `core/algorithms.py` (contains UI imports) to plugin root
  - [ ] Ensure `core/` package contains only business logic
- [ ] Improve `gui/preview_renderer.py` (Complexity: 21.8) if necessary
- [ ] Monitor QGIS Compliance Score (Goal: > 80/100)

## Verification
- [ ] Run `analyze_project_optfixed.py` again to verify score improvement
- [ ] Run tests to ensure no regressions
