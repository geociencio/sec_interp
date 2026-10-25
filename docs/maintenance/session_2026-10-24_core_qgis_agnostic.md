# Session 2026-10-24 — Core QGIS-Agnostic & Documentation Close

## Objective

Close the remaining QGIS coupling in `core/` and leave the architecture/documentation
consistent, without functional changes.

## Result

`core/` no longer imports `qgis.*` or `qgis.PyQt`; the architecture gate has an
**empty allowlist**:

```python
CORE_VIOLATIONS = {}
```

Verified in a plain development venv without QGIS:

```text
CORE IMPORT OK ProfileController ExportService
```

## Changes

### Translation port

- `core/utils/i18n.py`: injectable translator with identity fallback.
- `ConfigService`, `DataCache`, `ExportService` use the shared `translate()` helper.
- `SecInterp` installs `QCoreApplication.translate` at startup.
- Contexts (`ConfigService`, `DataCache`, `ExportService`, class names) preserved.

### Settings port

- New `core/interfaces/settings_store.py` (`SettingsStore`, `InMemorySettingsStore`).
- New `gui/adapters/qgs_settings_store.py` (`QgsSettingsStore`).
- `ConfigService(store)` and `AccessControlService(store)`.
- `ProfileController`, `SettingsPage`, `ExportService` and the plugin composition root
  receive the Qgs adapter; headless core defaults to in-memory.
- Persistence keys `SecInterp/*` unchanged.

### Export QGIS helpers

- `core/utils/io.py` → `exporters/qgis_io.py`.
- `core/services/export/map_settings_factory.py` → `exporters/map_settings.py`.
- `ExportService` receives `map_settings_factory` from `dialog_export_manager` and the
  plugin; a missing factory raises an explicit error for image/PDF/SVG export.
- `core/utils/__init__.py` and `core/services/export/__init__.py` no longer export QGIS
  helpers.

### Logger

- `logger_config` imports QGIS lazily (`QgsLogHandler.emit`, file-logging fallback), so
  importing `core` does not pull `qgis.core`.

### Documentation and side work

- Interpretation Settings moved into a Settings tab (sidebar 7 → 6), with the
  `page_interpretation` alias preserved.
- Code walkthrough consolidated on v2; v1 archived under `docs/archive/`.
- Public architecture site rebuilt with root redirects to `/en/`.
- v3.11.0 technical analysis published (EN/ES).

## Verification

| Gate | Result |
|---|---|
| Tests | **839 OK / 888 static** |
| `ruff` / format | PASS |
| `mypy` core + exporters | PASS |
| `check_docs` | PASS (37 active docs) |
| `sync_vault_mirrors --check` | PASS |
| `forge validate` | PASS |
| `sync_metrics --validate` | PASS |
| Core without QGIS | PASS (subprocess test) |
| Architecture allowlist | **empty** |

The benchmark `projection_math_performance` failed once at 0.0501 s vs 0.0500 s and
passed alone and in the full rerun; treated as a timing flake.

## Git and deployment

- Translation port: `c7154e42`
- Settings port: `25c74460`
- Export helpers: `e46499a9`
- Logger purity: `4b6024c9`
- Docs/core boundary: `af0bfbbb`
- Merge/docs status: `7fa2db42`
- v3.11 analysis: `79f71c2e`
- API stubs: `ed379236`
- `main` synced with `origin/main` at `ed379236`.
- QGIS 4 deploy: `sec_interp.bak.20261024223312`, version 3.11.0.

## Documentation URLs

- Architecture: `https://geociencio.github.io/sec_interp_docs/en/ARCHITECTURE.html`
- Technical analysis: `https://geociencio.github.io/sec_interp_docs/en/v3.11.0_technical_analysis.html`
- Spanish analysis: `https://geociencio.github.io/sec_interp_docs/es/v3.11.0_technical_analysis.html`

## Pending

1. `uv` 0.12.10 → 0.13.x in Manjaro stable (0.13.5 in unstable/Arch).
2. Interop §9 → **B1**.
3. `ProfileController` `GOD_OBJECT` (21 attributes).
4. `Invert line` future feature.
5. Optional translation review / `help/html` refresh.
6. Analyzer debt: 37 issues (20 `GOD_OBJECT`, 9 missing docstrings, 4 non-pythonic loops,
   2 potential missing slots, 1 spaghetti, 1 unprecise layer).

## Notes

- The `quality_score` **56.6** is the average Maintainability Index per module, not a
  test/coverage score.
- Native Qt translation contexts remain valid after the ports; no catalog migration.
