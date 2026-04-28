# Task: Gen 6 Immediate Priorities

- [x] Fix 13 signal leaks in `settings_page.py` and export widgets (`disconnect_signals()`).
- [x] Implement `scripts/memory_prune.py` to auto-prune consolidated lessons.
- [x] Integrate memory prune into `/close-session` Step 3.
- [x] Create `pre-push` CC gate (`qgis-analyzer analyze . --output json` -> block CC > 10).
- [x] **QGIS 4 Readiness**: Achieve compatibility with QGIS 4.x (Qt6).
- [ ] Docstring coverage campaign for `core/services/` and `core/utils/`.
- [ ] Implement `scripts/context_selector.py` for semantic skill injection.
- [ ] Fix `SPATIAL_INDEX` warning in `gui/dialog_interpretation_manager.py:123`.

**Status**: Session Initialized, ready to start Gen 6 tasks.

## QGIS 4 Migration (Completed 2026-04-28)
- [x] Update `metadata.txt` with `qgisMaximumVersion=4.99`.
- [x] Update `docs/source/conf.py` with version 3.4.0 and Qt6 mocks.
- [x] Update `README.md` with QGIS 4.x compatibility.
- [x] Verify API-agnostic compliance with `qgis-analyzer`.

## Refactorización CC (Rama: refactor/cc-compliance)
- [x] **Lote 1**: Gestores de Señales (Riesgo Bajo)
- [x] **Lote 2**: Controladores UI y Persistencia (Riesgo Medio)
- [x] **Lote 3**: Fábricas de UI y Previsualización (Riesgo Medio)
- [x] **Lote 4**: Lógica Core Algorítmica (Riesgo Alto)
