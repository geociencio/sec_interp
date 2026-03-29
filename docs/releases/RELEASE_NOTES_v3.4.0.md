# Release 3.4.0 - Integration & Translation Completeness - 2026-03-29

Short Summary
-------------
Official release completing the 100% translation of 13 supported languages, unified GeoPackage exports, robust 3D DXF rendering, and advanced integration tests.

Highlights
----------
- **Global Reach (i18n)**: 100% UI translation coverage across 13 languages with an ElementTree-based XML injector.
- **Advanced Export (GPKG/DXF)**: Unified layer-backed GeoPackage storage and explicit Z-dimensional 3D DXF exports for drillholes.
- **Parsing Reliability**: Restored and improved structural string parsing for multiple combined dip/strike notations.
- **Integration Testing**: Extensive validation pipelines for Vector Drivers and structural parsing without live QGIS dependencies.

Notable Changes (Detailed)
----------------------------
- feat: Implemented unified GeoPackage layer appending under unique section subdirectories (`[SectionName]/`).
- feat: Achieved 100% complete translation for the UI across all 13 supported languages.
- feat: Added full bi-directional "Vector Layer Mode" synchronization between QGIS Vector Layers and internal features.
- fix: Resolved a critical signature mismatch in `ExportService._export_drillholes_3d`.
- fix: Updated `ai-context-core` resolving project report aggregation bugs.
- fix: `KeyError: 0` in `DXFExporter` when processing empty or malformed feature sets.
- docs: Complete documentation standardization to English and integration of `make docker-test` guidelines.

Security Fixes
-------------------------
- None applicable for this minor release.

Breaking Changes
----------------------------------------------------
- None.

Installation / Update Instructions
--------------------------------------------
- Installation from QGIS Repository:
  1. Search for `SecInterp` in Plugins Manager.
  2. Click Install.
- Installation from ZIP:
  1. Download `sec_interp.3.4.0.zip` from GitHub.
  2. In QGIS: Plugins > Manage and Install Plugins > Install from ZIP.

Published Artifacts
---------------------
- Plugin ZIP: `sec_interp.3.4.0.zip` (attached).
- Checksum: `sec_interp.3.4.0.zip.sha256` (attached).

Verifications Performed (CI)
------------------------------
- [x] Tests and Linter passed (455+ Headless Docker tests).
- [x] Security audited via `qgis-analyzer security --deep`.
