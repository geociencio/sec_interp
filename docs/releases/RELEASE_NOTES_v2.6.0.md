# Release 2.6.0 - 2026-01-09

Short Summary
-------------
Official 2.6.0 release focused on infrastructure stabilization, quality assurance, and internationalization. This version introduces native integration tests and performance benchmarks.

Highlights
----------
- **Native Integration Tests**: Verified core workflows (interpretation, measurement, export) directly in QGIS headless.
- **Dockerized CI/CD**: Optimized pipeline using official QGIS images for 100% development/CI parity.
- **Performance Benchmarks**: Established metrics for geometry processing and spatial data export.
- **Refactoring & Quality**: Reduced cyclomatic complexity in 3D exporters and achieved 100% type safety in GUI validation.
- **Internationalization**: Full English translation for the measurement tool and UI defaults.

Notable Changes (Detailed)
----------------------------
- **feat**: Migrated to native `QgsTask` for long-running geology generation to prevent threading crashes.
- **feat**: Added customizable export controls in Settings.
- **fix**: Resolved mock pollution and StopIteration errors in the GUI test suite.
- **fix**: Standardized project-wide code formatting using `black`.
- **docs**: Integrated visual workflow guides and images into user documentation.

Installation / Update Instructions
--------------------------------------------
- Installation from QGIS Repository:
  1. Search for `SecInterp` in Plugins Manager.
  2. Click Install (Version 2.6.0).
- Installation from ZIP:
  1. Download `sec_interp.2.6.0.zip` from GitHub.
  2. In QGIS: Plugins > Manage and Install Plugins > Install from ZIP.

Published Artifacts
---------------------
- Plugin ZIP: `sec_interp.2.6.0.zip` (attached).
- Checksum: `sec_interp.2.6.0.zip.sha256` (attached).

Verifications Performed (CI)
------------------------------
- [x] 312 tests (Unit + Integration) passing.
- [x] Linter and Formatter (Ruff/Black) compliant.
- [x] Manual verification in QGIS 3.44.
