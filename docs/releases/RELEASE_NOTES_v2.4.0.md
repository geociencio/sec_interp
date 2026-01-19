# v2.4.0: Global Interpretation & Core Modernization

**Release Date:** 2025-12-31

### 🚀 Major Features
- **Internationalization (I18n) System**:
  - Full support for **5 languages**: Spanish (ES), French (FR), German (DE), Russian (RU), Portuguese Brazil (PT_BR).
  - Native Qt translation pipeline (`.ts` → `.qm`) with automatic locale detection from QGIS settings.
  - Dedicated translation management scripts (`update-strings.sh`, `compile-strings.sh`).
- **New Interpretation Tool**:
  - Interactive **Polygon Drawing**: digitize geological interpretations directly on the profile view.
  - **Smart Snapping**: `ProfileSnapper` engine snaps to vertices/edges of projected layers (tolerance ~12px).
  - **Auto-Styling**: Generates vivid, distinct colors (HSV) for each new interpretation polygon.
  - **UX Enhancements**: "Undo" (Right-click), Rubber-band real-time preview, and intuitive finalize actions.

### 🏗️ Architecture & Core Refactoring
- **Phase 1: Dependency Injection & Interfaces**:
  - Introduced `core/interfaces/` defining strict contracts for all services (`DrillholeInterface`, `GeologyInterface`, etc.).
  - Decoupled `Manager` classes using DI principles.
- **Phase 2: Robust Error Handling**:
  - Unified exception hierarchy in `core/exceptions.py`.
  - Structured logging across the entire application with traceable error contexts.
- **Phase 3: Performance & Caching**:
  - Advanced `CacheManager` with Time-To-Live (TTL) and Level-of-Detail (LOD) awareness.
  - Vectorized geometry calculations for massive speedups in spatial operations.
- **Phase 4: Asynchronous Processing**:
  - `AsyncGeologyProcessor` with cancellation tokens to prevent UI freezes.
  - Proper resource cleanup using Python Context Managers.
- **Phase 5: Modern Python & Validation**:
  - Adopted `dataclasses` for all data transfer objects (DTOs).
  - Strongly typed codebase with `typing.Protocol` and Python 3.10+ syntax.
  - Centralized validation logic in `core/validation/` (Project, Layer, Field validators).
- **Phase 6: GUI Decomposition**:
  - Split monolithic `main_dialog.py` into specialized handlers:
    - `gui/main_dialog_settings.py`
    - `gui/main_dialog_preview.py`
    - `gui/main_dialog_tools.py`
    - `gui/main_dialog_data.py`

### 🔧 Infrastructure & Tooling
- **Modern Package Management**:
  - Migrated to **`uv`** for 10-100x faster dependency resolution.
  - Added `uv.lock` for deterministic, reproducible builds.
  - Centralized all tool configs (Ruff, Pytest, Pylint) into `pyproject.toml`.
- **Code Quality Pipeline**:
  - **Pre-commit Hooks**: strictly enforcing `ruff`, `trailing-whitespace`, and file validity.
  - **Metrics History**: Tracking code quality evolution in `.ai-context/metrics_history.json`.
  - **Strict Linting**: 9% reduction in issues, 100% QGIS Plugin compliance score.

### 🐛 Critical Bug Fixes
- **Stability**: Fixed `QgsProject` import crash in preview axes manager.
- **Rendering**: Fixed coordinate reference system (CRS) transformations for memory layers.
- **I18n**: Fixed Russian XML corruption and empty translation attributes.
- **Logic**: Resolved `super().__init__()` ordering issues in Page classes and validation false positives.

### 📝 Documentation
- **Google-Style Docstrings**: Standardized across all `core/` modules.
- **Research Archive**: Moved internal technical notes to `research/` directory to clean up `docs/`.
- **New Guides**: Added `research/project_docs/ARCHITECTURE_EN.md` and `DEVELOPMENT_GUIDE.md`.
