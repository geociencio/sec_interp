# Task: Gen 6 Immediate Priorities

- [x] Fix 13 signal leaks in `settings_page.py` and export widgets (`disconnect_signals()`).
- [x] Implement `scripts/memory_prune.py` to auto-prune consolidated lessons.
- [x] Integrate memory prune into `/close-session` Step 3.
- [x] Create `pre-push` CC gate (`qgis-analyzer analyze . --output json` -> block CC > 10).
- [ ] Docstring coverage campaign for `core/services/` and `core/utils/`.
- [ ] Implement `scripts/context_selector.py` for semantic skill injection.
- [ ] Fix `SPATIAL_INDEX` warning in `gui/dialog_interpretation_manager.py:123`.

**Status**: Session Initialized, ready to start Gen 6 tasks.

## Refactorización CC (Rama: refactor/cc-compliance)
- [x] **Lote 1**: Gestores de Señales (Riesgo Bajo)
  - [x] `sec_interp_plugin.py` (`disconnect_signals`)
  - [x] `gui/dialog_signal_manager.py` (`_disconnect_button_signals`, etc.)
  - [x] `gui/ui/pages/settings_page.py` (`_disconnect_default_tab_signals`)
- [x] **Lote 2**: Controladores UI y Persistencia (Riesgo Medio)
- [ ] **Lote 3**: Fábricas de UI y Previsualización (Riesgo Medio)
- [ ] **Lote 4**: Lógica Core Algorítmica (Riesgo Alto)
