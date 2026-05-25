# Core Component Distinction Guide

This document aims to clarify the distinction between the different components named "Core" within the **SecInterp** project, to avoid confusion for both human developers and AI agents.

## ⚠️ The Fundamental Distinction

Two "Core" entities coexist in this development environment:

1.  **SecInterp Core** (The Project Core):
    *   **Location**: `/core` directory within the project root.
    *   **Purpose**: Contains pure business logic, geological algorithms, processing services, and SecInterp-specific data models (DTOs).
    *   **Current Status**: **Decoupled**. As of version 2.8.0, this module has been sanitized to have no direct dependencies on live QGIS classes during heavy processing (Thread-Safe).

2.  **QGIS Core** (The QGIS API):
    *   **Reference**: `qgis.core` Python package.
    *   **Purpose**: Provides the underlying geospatial infrastructure (geometries, layers, projects, CRS).
    *   **Interaction**: SecInterp uses `qgis.core` to extract data on the main thread, but **SecInterp Core** processes this data using agnostic types (WKT, dicts, primitives).

---

## 🧭 Rules for Developers and AI

To maintain architectural integrity, follow these guidelines:

### 1. Do Not Assume "Core" Always Means QGIS
When asked to "review the core," this almost exclusively refers to the `/core` directory of this plugin. Do not attempt to search for or modify internal QGIS engine files.

### 2. Data Boundaries (Decoupling)
*   **In `/core`**: Use agnostic domain types. Avoid instantiating `QgsVectorLayer` or accessing `QgsProject.instance()` within core services. Use `DomainGeometry` (WKT) and attribute dictionaries.
*   **In `/gui`**: This is where the translation between the real QGIS API (`qgis.core`) and **SecInterp Core** takes place. This is where geometries are extracted and DTOs are prepared.

### 3. File Naming and Imports
*   **Local Files**: Files in `core/` (e.g., `core/services/geology_service.py`) are the **SecInterp Brain**.
*   **External API**: Imports starting with `qgis.core`, `qgis.gui`, or `qgis.utils` are **External Dependencies**.
*   **Naming Rule**: In discussions or code comments, use "Internal Core" to refer to `/core` and "PyQGIS API" for the software's API.

### 4. The "Extract-then-Compute" Pattern
To avoid future complications, the data flow **MUST** follow this pattern:
1.  **GUI/Task Interface Layer**: Receives QGIS objects (`QgsVectorLayer`, `QgsFeature`). Extracts what is needed (geometry in WKT, attribute dictionaries).
2.  **Core Layer**: Receives only the extracted data (strings, dicts, floats). Performs heavy geometric calculations.
3.  **Result**: Core returns DTOs (Data Transfer Objects) defined in `core/types.py`. The GUI layer handles converting these back to QGIS layers if needed.

### 5. Golden Rules of Thread-Safety
*   **Forbidden**: Import `qgis.gui` inside `core/`. Background threads will die if they attempt to touch any widget or window.
*   **Restriction**: Minimize the use of `qgis.core` inside `core/`. Although some classes like `QgsGeometry` are safe, it is preferable to operate on WKT to ensure full independence.
*   **Application Context**: Never use `iface` or `QgsProject.instance()` inside `core/`. If you need project data, pass it as pre-extracted arguments.

---

## 🧪 Differentiated Testing Strategy

*   **Core Tests (`tests/core/`)**: Must be able to run without a full QGIS installation. They use lightweight mocks. They are the thermometer of geological logic.
*   **Integration Tests (`tests/integration/`)**: Require real QGIS. They verify that our "Core" communicates correctly with the "QGIS API".

---

## 🛠️ Decoupling Summary (January 2026)

A major effort has been completed to ensure that:
*   `GeologyService` does not use live QGIS layers in its processing method.
*   `DrillholeService` uses dictionaries instead of `QgsFeature` objects during trace calculation.
*   3D projection logic accepts tuples and primitive types.

**In summary: Keep our Core "pure." Treat QGIS as an external service provider. Do not allow the roots of one to enter the logic of the other.**
