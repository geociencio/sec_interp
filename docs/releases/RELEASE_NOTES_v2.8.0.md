# Release 2.8.0 - Debt Reduction & UI Improvements - 2026-01-25

Short Summary
-------------
This release transforms the SecInterp core into a thread-safe, agnostic architecture while introducing high-precision geometric mocks and user-requested UI visibility controls.

Highlights
----------
- **Core-QGIS Architectural Decoupling**: Heavy geometric calculations now operate on detached DTOs (WKT strings and dictionaries), preventing crashes in background tasks.
- **Legend Toggle**: Added a persistent UI control to show or hide the legend on the preview widget and exports.
- **Enhanced Test Suite**: Implemented native geometric calculations in the QGIS mock system to stabilize continuous integration.

Notable Changes (Detailed)
----------------------------
- **Refactoring** — [Core] Fragmented `GeologyService` and `DrillholeService` to reduce cyclomatic complexity and improve modularity.
- **UI** — [Preview] Simplified `PreviewManager` by delegating data preparation logic to services.
- **Testing** — [Mocks] Added `azimuth` support to `MockQgsPointXY` for section orientation validation.
- **Docs** — [Sphinx] Restored and fixed the automated API documentation build infrastructure.

Security Fixes
-------------------------
- No known security vulnerabilities were addressed in this release.

Breaking Changes
----------------------------------------------------
- **Internal API**: The `prepare_task_input` and `process_task_data` signatures in services have changed to support detached data. External scripts using these internal methods must update to pass raw geometry layers or WKT strings.

Installation / Update Instructions
--------------------------------------------
- Installation from QGIS Repository:
  1. Search for `SecInterp` in Plugins Manager.
  2. Click Install.
- Installation from ZIP:
  1. Download `sec_interp.2.8.0.zip` from GitHub.
  2. In QGIS: Plugins > Manage and Install Plugins > Install from ZIP.

Published Artifacts
---------------------
- Plugin ZIP: `sec_interp.2.8.0.zip` (attached).
- Checksum: `sec_interp.2.8.0.zip.sha256` (attached).

Verifications Performed (CI)
------------------------------
- [x] Full suite of 359 tests passed in Docker (Ubuntu/QGIS 3.44 Headless).
- [x] Manual verification of Legend Toggle and Section Rotation persistence.
- [x] Documentation build verified with Sphinx.

Suggested Commands
------------------
```bash
# Verify package integrity
sha256sum -c sec_interp.2.8.0.zip.sha256
```
