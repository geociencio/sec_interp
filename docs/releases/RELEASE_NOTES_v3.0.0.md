# Release v3.0.0 - The Internationalization & Modular Architecture Release

Short Summary
-------------
This major release introduces full support for 8 languages and a significant architectural refactoring of core services to improve modularity and maintainability.

Highlights
----------
- **Extended I18n Support**: Now supporting English, Spanish, French, German, Russian, Brazilian Portuguese, Chinese (Simplified), and Japanese.
- **Architectural Evolution**: Decomposition of `DrillholeService` and implementation of `AccessControlService` for better feature management.
- **Advanced Quality Audit**: Migration to `qgis-plugin-analyzer` v1.7.0 for rigorous compliance checking.
- **Improved UI Validation**: Strengthened output path validation and asynchronous task handling.

Notable Changes (Detailed)
----------------------------
- **Internacionalización (I18n)**:
    - Automated translation workflow integrated with `ai-context-core`.
    - 100% translation coverage for UI components.
- **Core Services**:
    - `DrillholeService` refactored into smaller, specialized units.
    - New `AccessControlService` to manage feature access.
- **Bug Fixes**:
    - Fixed `AttributeError` in `DrillholeService` when optional survey/interval layers were missing.
    - Fixed UI crash when closing the dialog while `GeologyGenerationTask` was running.
    - Corrected typo in `DialogStatusManager` affecting "Save" button state.

Security Fixes
-------------------------
- Enhanced path validation logic in `ExportManager` to prevent directory traversal or invalid output locations.
- Security Score: 100/100 (Audit performed by `qgis-analyzer`).

Breaking Changes
----------------------------------------------------
- None. This release maintains backward compatibility with existing project configurations.

Installation / Update Instructions
--------------------------------------------
- Installation from QGIS Repository:
  1. Search for `SecInterp` in Plugins Manager.
  2. Click Install.
- Installation from ZIP:
  1. Download `sec_interp.3.0.0.zip` from GitHub.
  2. In QGIS: Plugins > Manage and Install Plugins > Install from ZIP.

Published Artifacts
---------------------
- Plugin ZIP: `sec_interp.3.0.0.zip`
- Checksum: `sec_interp.3.0.0.zip.sha256`

Verifications Performed (CI)
------------------------------
- [x] All 361+ tests passed in Docker environment.
- [x] Ruff linting and formatting validated.
- [x] Manual verification of UI flows and interpretation persistence.
