# Next Steps: SecInterp v3.4.0 Transition

## Current Status
- **Export System**: Unified support for SHP, GPKG, and DXF is implemented and verified.
- **Data Integrity**: Drillhole interval robustness and duplication issues are resolved.
- **Persistence**: Export format and settings now persist correctly in QGIS settings.

## Handover Details
- **Known Issues**: DXF files do not contain attribute fields (by design, due to OGR limitations).
- **Pending Tasks**:
    1. **Naming Patterns**: Implement configurable naming patterns in `ExportService` (e.g., `{section}_{type}`).
    2. **Audit i18n**: The new export options in `SettingsPage` might need translation updates.
    3. **Docker Integration**: Verify that all 600+ tests pass in a clean Docker environment (current session used local verification).

## Resume Command
```bash
/[start-session] unified_export_audit
```
