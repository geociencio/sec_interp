# Active Tasks - SecInterp

## [x] Phase v3.4.1: Export Architecture Refinement [x]
- [x] **Core Enhancement**: Update `io.py` with `symbologyExport` for DXF/CAD colors.
- [x] **Structural Parsing**: Fixed combined strike/dip support by splitting parts.
- [x] **Parsing Tests**: Verified with regression tests in `test_utils_standalone.py`.
- [x] **Naming Refactor**: Rename `*ShpExporter` to `*VectorExporter` across the project.
- [x] **DXF Integration**: Refactor `exporters/dxf_exporter.py` to use unified writer.
- [x] **Orchestration**: Update `ExportService` with new class names.
- [x] **Verification**: Update unit tests and perform manual DXF/GPKG validation.

## [x] Phase v3.4.0: Advanced Export & Complexity Reduction [x]
- [x] **Complexity Reduction**: Refactor `ExportService` to reduce CC (Extract `_resolve_layers`, Declarative Task List).
- [x] **Settings Expansion**: Add `ExportSettings` to `core/models/settings_model.py`.
- [x] **UI Integration**: Update `gui/ui/pages/settings_page.py` with Format and Naming controls.
- [x] **DXF/GPKG Implementation**:
    - [x] Create `exporters/dxf_exporter.py` (Generic Writer).
    - [x] Fix ExportService integration (Fix signature mismatch and DTO conversion).
    - [x] Implement/Update specialized exporters to support DXF/GPKG formats natively.
- [x] **Verification**:
    - [x] Run 600+ tests and ensure no regressions.
    - [x] Perform manual export to DXF and GeoPackage.

## [x] Session Initialization [x]
- [x] Context Tuning (`ai-ctx`, `next_steps.md`, `AGENT_LESSONS.md`)
- [x] Log and Context Review (`AI_CONTEXT.md`, `DEVELOPMENT_LOG.md`)
- [x] Quality Scan (`qgis-analyzer summary`)
- [x] Environment Sync (`uv sync`)
- [x] Stability Verification (`make docker-test`)
- [x] **Goal Refinement**: Identify remaining gaps in v3.4.0.

## [ ] Cleanup & Maintenance [ ]
- [ ] Fix Pyright/Pyre ghost errors in IDE if they persist.
- [ ] Generate changelog for v3.4.0/v3.4.1 progress.
