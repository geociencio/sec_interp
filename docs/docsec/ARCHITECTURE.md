# SecInterp Architecture

This document describes the technical architecture of the SecInterp QGIS plugin, focusing on its decoupled, service-oriented, and asynchronous design.

## 🏗️ Overview
SecInterp follows a design pattern that strictly separates business logic (Core) from the user interface (GUI), and uses QGIS-safe concurrency patterns.

```mermaid
graph TD
    UI[GUI Layer: Main Dialog] --> PM[PreviewManager]
    PM --> TS[Task System (QgsTask)]
    TS --> DTO[DTOs: Task Inputs]
    DTO --> GS[GeologyService (Stateless)]
    PM --> PS[PreviewService]
    PS --> DS[DrillholeService]
    PS --> SS[StructureService]
```

## 📂 Layer Structure

### 🎨 UI Layer (gui/)
Responsible for user interaction and orchestration.
- **`main_dialog.py`**: Main window controller.
- **`main_dialog_preview.py` (PreviewManager)**: Manages preview state, hash-based caching, and task launching.
- **`tasks/`**: Contains `QgsTask` implementations (e.g., `GeologyGenerationTask`) for background processing.

### ⚙️ Business Layer (core/)
Pure logic, decoupled from the GUI and thread-safe.

#### Services (`core/services/`)
- **`geology_service.py`**: Implements pure geometric intersection logic. Designed to be invoked both synchronously and from secondary threads.
- **`drillhole_service.py`**: Drillhole processing and 3D desurvey.
- **`structure_service.py`**: Structural measurement projection.

#### Types and DTOs (`core/types.py`)
Data exchange between the UI and background threads is performed exclusively through **Data Transfer Objects (DTOs)**.
- **`GeologyTaskInput`**: Encapsulates copied geometries and simple parameters. Prevents passing live `QgsVectorLayer` objects to secondary threads, avoiding C++ API crashes.
- **`PreviewParams`**: Validated object containing all configuration needed to generate a section.

### 🛠️ Interfaces and Decoupling
- **`core/interfaces/`**: Defines abstract contracts (`IGeologyService`, `IPreviewService`) that enable Dependency Injection and facilitate Mocking in tests.

## 🚀 Concurrency Patterns
To ensure the QGIS interface does not freeze during complex calculations, SecInterp uses the **QgsTask + DTO** pattern:

1.  **Prepare (Main Thread)**: The UI collects data and creates a DTO (e.g., `GeologyTaskInput`) by copying the necessary geometries.
2.  **Process (Background Thread)**: A `QgsTask` is launched that invokes a pure service using *only* the DTO. There is no access to `QgsProject` or layers.
3.  **Finish (Main Thread)**: The result (another DTO or list of primitives) is returned to the main thread to update the UI.

## 🛡️ Standards & Quality
- **Type Safety**: Extensive use of Type Hints and validation with `mypy`.
- **Linting**: Strict Ruff rules (including cyclomatic complexity).
- **ADR**: Important architectural decisions are recorded in `docs/adr/`.

---
**Version**: 2.9.1 | **Updated**: 2026-02-07
