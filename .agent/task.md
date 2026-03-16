# Active Tasks - SecInterp

## [/] Phase v3.4.0: Advanced Export & Complexity Reduction [/]
- [x] **Complexity Reduction**: Refactor `ExportService` to reduce CC (Extract `_resolve_layers`, Declarative Task List).
- [x] **Settings Expansion**: Add `ExportSettings` to `core/models/settings_model.py`.
- [x] **UI Integration**: Update `gui/ui/pages/settings_page.py` with Format and Naming controls.
- [/] **DXF/GPKG Implementation**:
    - [x] Create `exporters/dxf_exporter.py` (Generic Writer).
    - [/] Fix `ExportService` integration (Fix signature mismatch and DTO conversion).
    - [ ] Implement/Update specialized exporters to support DXF/GPKG formats natively.
- [ ] **Verification**:
    - [ ] Run 600+ tests and ensure no regressions.
    - [ ] Perform manual export to DXF and GeoPackage.

## [ ] Session Initialization [ ]
- [x] Context Tuning (`ai-ctx`, `next_steps.md`, `AGENT_LESSONS.md`)
- [x] Log and Context Review (`AI_CONTEXT.md`, `DEVELOPMENT_LOG.md`)
- [x] Quality Scan (`qgis-analyzer summary`)
- [x] Environment Sync (`uv sync`)
- [x] Stability Verification (`make docker-test`)
- [/] **Goal Refinement**: Identify remaining gaps in v3.4.0 (In Progress).

## [ ] Cleanup & Maintenance [ ]
- [ ] Fix Pyright/Pyre ghost errors in IDE if they persist.
- [ ] Generate changelog for v3.4.0 progress.
