# SecInterp - Development Log

Chronological record of development activities, significant fixes, and technical decisions.

---

## [2026-01-04] - Docker Learning Workshop (00:05)

### Activities
- **Fase 1: Interactive Exploration**: Launched containers, managed volumes (`-v`), and identified system dependencies inside `python:3.10-slim`.
- **Fase 2: Dockerfile Automation**:
    - Implemented a production-ready `Dockerfile` featuring `uv` for dependency management.
    - Integrated `.dockerignore` to optimize build context and ignore `__pycache__`.
    - Resolved critical permission issues caused by `root` user in isolated environments.
- **Fase 3: Containerized Verification**:
    - Automated unit tests execution within the container.
    - Resolved `PYTHONPATH` package discovery issues relative to the `/app` mounting point.

### Verification
- Successfully executed **319 tests** inside the Docker container.
- Proof of work archived in: [docker_workshop_2026-01-04.md](file:///home/jmbernales/qgispluginsdev/sec_interp/docs/maintenance/docker_workshop_2026-01-04.md)

---

## [2026-01-03] - Global Ruff Activation & Cleanup (10:20)

### Activities
- **Ruff Rule Enablement**: Activated `F401` (unused imports), `F841` (unused variables), and `I001` (isort) project-wide.
- **Automated Fixes**: Executed `ruff check --fix` and `ruff format`. 253 fixes applied, 102 files reformatted.
- **Mock System Refactor**: Enhanced `tests/base_test.py` to fix regressions in `MockQWidget`, `MockQgsProject`, and `MockQApplication`.
- **Regression Fixes**:
    - Restored missing `logger` in `gui/main_dialog_settings.py`.
    - Fixed 3D component discovery in `exporters/interpretation_3d_exporter.py`.
    - Modernized `isinstance` checks in `gui/services/parallel_geology_service.py` (Rule `UP038`).

### Verification
- Full test suite passed: **316 tests** (312 passed, 4 skipped).
- Detailed report saved in: [ruff_cleanup_2026-01-03_10-20.md](file:///home/jmbernales/qgispluginsdev/sec_interp/docs/maintenance/ruff_cleanup_2026-01-03_10-20.md)

---

## [2026-01-03] - Bug Fix: Preview Render TypeError (10:45)

### Problem
- **TypeError**: `cannot unpack non-iterable GeologySegment object` in `gui/preview_renderer.py`.
- **Cause**: After refactoring `GeologyData` to use `GeologySegment` objects, a legacy list comprehension in `render()` was still trying to unpack them as 3-tuples.

### Fix
- Updated `gui/preview_renderer.py` to extract points from `GeologySegment.points` when calculating `reference_data`.
- Added a regression test case in `tests/gui/test_preview_components.py`.

### Verification
- Full test suite passed: **316 tests**.
- Regression confirmed manually via test case.

---

## [2026-01-03] - Data Persistence Fix & UI Robustness (12:20)

### Activities
- **Proactive Persistence**: Reorganized `accept_handler` and `preview_profile_handler` in `main_dialog.py` to save settings immediately upon success or dialog acceptance, even if secondary validation fails.
- **Robust Settings Hub**:
    - Enhanced `DialogSettingsManager` with multi-scope support (`SecInterp` and `SecInterpUI`).
    - Implemented layer name fallback for restoration when IDs change.
    - Added type-safe parsing for persistent string values ("True", "None", etc.).
- **Forced Sync**: Added `self.settings.sync()` in `ConfigService` to ensure immediate disk writes.
- **Validation Fix**: Resolved `AttributeError` in `validate_inputs` that caused crashes on validation failure.
- **Workflow Automation**: Followed `/cierra-sesion` workflow to archive results.

### Verification
- Full test suite passed: **110 GUI tests** + all core tests.
- User confirmed automatic loading of previous configurations.
- Verified persistent restoration of layers and spinbox values after QGIS restart.

---

## [2026-01-03] - Official Release Version 2.5.0 (12:35)

### Activities
- **Release Automation**: Executed `make package` to compile translations and help files, creating `sec_interp.2.5.0.zip`.
- **Changelog Consolidation**: Merged multi-day improvements into a unified technical changelog in [`CHANGELOG.md`](file:///home/jmbernales/qgispluginsdev/sec_interp/docs/CHANGELOG.md).
- **Metadata Update**: Synchronized `metadata.txt` and `MAINTENANCE_LOG.md` with version 2.5.0.
- **Git Deployment**: Created and pushed tag `v2.5.0` to GitHub.

### Verification
- GitHub repository synchronized with `main` and `v2.5.0` tag.
- Final test verification passed: **319 tests**.

---

## [2026-01-03] - Release Workflow Standardization (13:15)

### Activities
- **Workflow Adaptation**: Customized [`release_process_ai.md`](file:///home/jmbernales/qgispluginsdev/sec_interp/docs/release_process_ai.md) for SecInterp, including 5 distinct phases (Quality, Versioning, Verification, Git, and Distribution).
- **Agent Integration**: Standardized internal agent workflows (`/release-plugin` and `/release-plugin-en`) to strictly follow the AI-guided 5-phase process.
- **Documentation Cleanup**: Removed legacy/redundant release documentation (`docs/docsec/RELEASE_PROCESS.md`).
- **Template Creation**: Implemented [`.github/release_template.md`](file:///home/jmbernales/qgispluginsdev/sec_interp/.github/release_template.md) with QGIS-specific instructions.

### Verification
- Sync confirmed between guide, template, and agent internal workflows.
- Phase 2 synchronization (metadata.txt vs pyproject.toml) verified as mandatory.

---
