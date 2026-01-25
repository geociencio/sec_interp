# Core Components Distinction Guide

This document aims to clarify the distinction between the different "Core" components within the **SecInterp** project to avoid confusion for both human developers and AI agents.

## ⚠️ The Fundamental Distinction

Two "Core" entities coexist in this development environment:

1.  **SecInterp Core** (The Project's Kernel):
    *   **Location**: `/core` directory within the project root.
    *   **Purpose**: Contains pure business logic, geological algorithms, processing services, and domain models (DTOs) specific to SecInterp.
    *   **Current State**: **Decoupled**. As of version 2.8.0, this module has been sanitized to have no direct dependencies on QGIS live classes during heavy processing (Thread-Safe).

2.  **QGIS Core** (The QGIS API):
    *   **Reference**: `qgis.core` Python package.
    *   **Purpose**: Provides the underlying geospatial infrastructure (geometries, layers, projects, CRS).
    *   **Interaction**: SecInterp uses `qgis.core` to extract data in the main thread, but the **SecInterp Core** processes this data using agnostic types (WKT, dictionaries, primitives).

---

## 🧭 Guidelines for Developers and AI

To maintain architectural integrity, follow these directives:

### 1. Do not assume "Core" always means QGIS
If asked to "review the core", it almost exclusively refers to the `/core` directory of this plugin. Do not attempt to search for or modify internal files of the QGIS engine.

### 2. Data Boundaries (Decoupling)
*   **Inside `/core`**: Agnostic domain types must be used. Avoid instantiating `QgsVectorLayer` or accessing `QgsProject.instance()` within kernel services. Use `DomainGeometry` (WKT) and attribute dictionaries.
*   **Inside `/gui`**: This is where the translation between the real QGIS API (`qgis.core`) and the **SecInterp Core** takes place. Geometries are extracted and DTOs are prepared here.

### 3. File Naming and Imports
*   **Local Files**: Files in `core/` (e.g., `core/services/geology_service.py`) are the **SecInterp Brain**.
*   **External API**: Imports starting with `qgis.core`, `qgis.gui`, or `qgis.utils` are **External Dependencies**.
*   **Naming Rule**: In discussions or code comments, use "Internal Core" to refer to `/core` and "PyQGIS API" for the software's API.

### 4. The "Extract-then-Compute" Pattern
To avoid future complications, the data flow **MUST** follow this pattern:
1.  **GUI/Task Interface Layer**: Receives QGIS objects (`QgsVectorLayer`, `QgsFeature`). Extracts what is necessary (WKT geometry, attribute dictionaries).
2.  **Core Layer**: Receives only the extracted data (strings, dicts, floats). Performs heavy geometric calculations.
3.  **Result**: The Core returns DTOs (Data Transfer Objects) defined in `core/types.py`. The GUI layer is responsible for converting these back to QGIS layers if necessary.

### 5. Golden Rules for Thread-Safety
*   **Prohibited**: Importing `qgis.gui` inside `core/`. Background threads will crash if they attempt to touch any widget or window.
*   **Restriction**: Minimize the use of `qgis.core` inside `core/`. While some classes like `QgsGeometry` are thread-safe, it is preferable to operate on WKT to guarantee total independence.
*   **Application Context**: Never use `iface` or `QgsProject.instance()` inside `core/`. If project data is needed, pass it as pre-extracted arguments.

---

## 🧪 Differentiated Testing Strategy

*   **Core Tests (`tests/core/`)**: Must be able to run without a full QGIS installation. They use lightweight mocks. They are the thermometer of geological logic.
*   **Integration Tests (`tests/integration/`)**: Require real QGIS. They test that our "Core" correctly communicates with the "QGIS API".

---

## 🛠️ Decoupling Summary (January 2026)

A major effort has been completed to ensure:
*   `GeologyService` does not use live QGIS layers in its processing method.
*   `DrillholeService` uses dictionaries instead of `QgsFeature` objects during trace calculation.
*   3D projection logic accepts tuples and primitive types.

**In summary: Keep our Core "pure". Treat QGIS as an external service provider. Do not let the roots of one enter the logic of the other.**
