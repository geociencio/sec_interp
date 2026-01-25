---
name: qgis-core
description: Knowledge about QGIS API, plugin structure, and asynchronous processing with QgsTask.
trigger: when working with PyQGIS, layers, CRS or QgsTask.
scope: root
---

# QGIS Core Development Skill

## Context
This project is a QGIS plugin named `sec_interp`. It uses the QGIS Python API (PyQGIS).

## Mandatory Guidelines
- **QgsTask**: Use `QgsTask` for any operation that takes more than 0.5s to prevent UI freezing.
- **Layers Handling**: Always check if a layer is valid (`isValid()`) before operating on it.
- **CRS Management**: Explicitly handle Coordinate Reference Systems. Use `QgsProject.instance().crs()` if no specific CRS is provided.
- **Project Structure**: Follow the established structure: `core/` for business logic (Agnostic/WKT), `gui/` for widgets (PyQGIS dependent), `exporters/` for output.
- **Boundary Rules**: Use `asWkt()` and `fromWkt()` to communicate between CLI/Core and the QGIS UI.

## Code Style
- Use `iface` only when necessary; prefer passing required objects in constructors for better testability.
- Follow the PEP8 standard and the project's `.pre-commit-config.yaml`.
