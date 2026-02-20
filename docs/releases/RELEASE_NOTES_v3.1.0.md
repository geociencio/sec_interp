# Release 3.1.0 - Global i18n Expansion & Architecture Pipeline - 2026-02-19

Short Summary
-------------
Global i18n Expansion & Architecture Pipeline with mass automatic translation for 14 languages and architectural modularization of the ProjectValidator.

Highlights
----------
- Mass automatic translation of missing strings in all 14 Supported languages.
- Modularized ProjectValidator using Pipeline pattern and decomposed StateManager into specialized components.
- Added debug logging and i18n support to exporters, plus a 'Reset to defaults' button for export options.

Notable Changes (Detailed)
----------------------------
- feat(i18n): mass automatic translation of missing strings and UI formatting fixes
- feat(gui): add translatable validation messages
- feat(settings): add 'Reset to defaults' button for export options
- fix(export): add debug logging and i18n to exporters
- fix(core): correct QCoreApplication imports and stabilize tests
- refactor(core): modularize ProjectValidator using Pipeline pattern
- refactor(gui): decompose StateManager into specialized components
- refactor(validation): eliminate circular imports and fix minor issues

Security Fixes
-------------------------
- No new vulnerabilities detected.

Breaking Changes
----------------------------------------------------
- None.

Installation / Update Instructions
--------------------------------------------
- Installation from QGIS Repository:
  1. Search for `SecInterp` in Plugins Manager.
  2. Click Install.
- Installation from ZIP:
  1. Download `sec_interp.3.1.0.zip` from GitHub.
  2. In QGIS: Plugins > Manage and Install Plugins > Install from ZIP.

Published Artifacts
---------------------
- Plugin ZIP: `sec_interp.3.1.0.zip`
- Checksum: `sec_interp.3.1.0.zip.sha256`

Verifications Performed (CI)
------------------------------
- [x] Tests and Linter passed.
- [ ] Manual verification in QGIS.
