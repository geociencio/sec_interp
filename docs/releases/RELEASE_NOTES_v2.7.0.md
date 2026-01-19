# Release v2.7.0 - Operational Excellence & Documentation

Short Summary
-------------
This release marks a major stabilization milestone alongside enhanced documentation and QA infrastructure. It introduces a modernized sidebar UI, full internationalization (EN/ES), robust 3-level validation architecture, and high-fidelity 3D interpretation export.

Highlights
----------
- **Infra (Dockerized QA)**: Full isolation for testing with 361 tests passing (100% success rate).
- **Docs (Sphinx & Clean HTML)**: Automated API documentation and decoupled HTML build process.
- **UI (Sidebar Navigation)**: Replaced tabs with a native QGIS-style sidebar and icons.
- **Feat (Enhanced 3D Export)**: Native `PolygonZ` export for interpretations and drillhole data.
- **Arch (3-Level Validation)**: Type -> Logic -> Domain validation hierarchy preventing crashes.

Notable Changes (Detailed)
----------------------------
- **feat**: Implemented `MessageManager`, `CacheHandler`, and `SettingsManager` to decouple Main Dialog.
- **refactor**: Centralized logging system (`logger_config`) with hierarchical propagation.
- **fix**: Resolved massive mock infrastructure instability (`ModuleProxy`, `MockSignal`).
- **fix**: Restored 50+ broken links in `README.md` and standardizing terminology.
- **chore**: Updated `MAINTENANCE_LOG` and `DEVELOPMENT_LOG` with standardized entries.

Security Fixes
-------------------------
- N/A

Breaking Changes
----------------------------------------------------
- **Architecture**: `SecInterpDialog` has been decomposed. Callers relying on internal widgets (e.g. `self.dlg.tabs`) must now use the provided public managers or access via `dlg.ui`.
- **API**: Private methods in `GeologyService` have been extracted/renamed for clarity.

Installation / Update Instructions
--------------------------------------------
- Installation from QGIS Repository:
  1. Search for `SecInterp` in Plugins Manager.
  2. Click Install.
- Installation from ZIP:
  1. Download `sec_interp.2.7.0.zip` from GitHub.
  2. In QGIS: Plugins > Manage and Install Plugins > Install from ZIP.

Published Artifacts
---------------------
- Plugin ZIP: `sec_interp.2.7.0.zip` (attached).
- Checksum: `sec_interp.2.7.0.zip.sha256` (attached).

Verifications Performed (CI)
------------------------------
- [x] Tests and Linter passed.
- [x] Manual verification in QGIS.

Suggested Commands
------------------
```bash
# Build artifacts (SecInterp ZIP)
make package VERSION=main

# Create release using GitHub CLI
gh release create v2.7.0 --title "v2.7.0 - Operational Excellence & Documentation" --notes-file /tmp/release_notes.md dist/*.zip dist/*.sha256 --draft
```
