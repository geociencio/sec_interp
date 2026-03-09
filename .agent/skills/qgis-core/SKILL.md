---
name: qgis-core
description: Knowledge about the QGIS API, plugin structure, and asynchronous processing with QgsTask.
trigger: when working with PyQGIS, layers, CRS, or QgsTask.
---

# QGIS Core Development

Standardizes interaction with the QGIS API, ensuring a responsive and well-structured plugin.

## When to use this skill
- When implementing new tools that interact with the map canvas.
- When handling vector or raster layers.
- When performing heavy operations that require secondary threads.

## Degree of Freedom
- **Strict**: The use of `QgsTask` for long processes and Core/GUI decoupling are mandatory.

## Workflow
1. **Architecture**: Separate logic into `core/` (processing) and `gui/` (visualization).
2. **Validation**: Always verify `isValid()` on layers before operating.
3. **Asynchrony**: Wrap processes > 0.5s in a `QgsTask`.
4. **CRS Management**: Explicitly handle coordinate transformations.

## Instructions and Rules

### Golden Rules
- **QgsTask**: Do not block the UI. Use signals and slots for communication.
- **Network/Threads**: Avoid `threading.Thread` (use `QgsTask`) and synchronous network calls (rules `UNSAFE_THREAD` and `BLOCKING_NETWORK_CALL`).
- **Boundaries**: Use WKT to communicate core logic with the graphical interface.
- **Modernization**: Avoid legacy `QVariant`; the analyzer will detect `OBSOLETE_VARIANT`.
- **Injection**: Avoid global use of `iface`; prefer passing objects in constructors.

### Plugin Structure
- `core/`: Business logic agnostic to the UI.
- `gui/`: Widgets and dialogs dependent on PyQGIS.
- `exporters/`: Data output modules.

## Quality Checklist
- [ ] Is UI blocking avoided through `QgsTask`?
- [ ] Is layer integrity validated in every operation?
- [ ] Are CRS transformations explicitly defined?
- [ ] Is the Core/GUI separation of responsibilities followed?
