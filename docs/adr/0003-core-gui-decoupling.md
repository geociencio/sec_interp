# 3. Core-GUI Decoupling

Date: 2024-08 (v1.1)

## Status

Accepted

## Context

Early versions of QGIS plugins often mix business logic (calculations, data processing) with UI logic (widgets, slots), creating a "Big Ball of Mud". This makes the code:
- Hard to test (requires a running QGIS GUI).
- Hard to maintain (changes in UI break logic and vice versa).
- Hard to extend (logic cannot be reused in other contexts, e.g., headless scripts).

## Decision

We enforces a strict **Architectural Boundary** between the `core` package and the `gui` package.

### 1. Dependency Rule
- **`gui` depends on `core`**: The UI layer imports services and types from the core to display data.
- **`core` MUST NOT depend on `gui`**: The core package must never import anything from the `gui` package or use `PyQt5.QtWidgets`. It should rely only on `qgis.core` and standard Python types.

### 2. Service Layer
- All business logic (e.g., `GeologyService`, `DrillholeService`) resides in `core/services`.
- Services are stateless where possible.
- Services implement Interfaces (`core/interfaces`) to allow mocking in tests.

### 3. Data Transfer
- Communication between layers happens via **Data Transfer Objects (DTOs)** defined in `core/types.py`.
- We avoid passing raw QGIS UI widgets (like `QgsMapCanvas`) into Core services. Instead, we extract necessary data (e.g., `QgsGeometry`, `currentScale`) and pass that.

## Consequences

### Positive
- **Testability**: We can write unit tests for `core` logic without initializing the full QGIS GUI application (using `qgis.core` headless).
- **Flexibility**: We can swap the UI completely (e.g., from a Dialog to a DockWidget) without rewriting business logic.
- **Stability**: Reduces the risk of "spaghetti code" entanglements.

### Negative
- **Boilerplate**: Requires creating DTOs and wrapper methods to pass data across the boundary.
- **Indirection**: Developers must jump between file definitions to trace execution flow.

## Compliance
- CI/CD hooks (or `pylint`/`import-linter`) should verify that no file in `core/` imports from `gui/` or `PyQt5.QtWidgets`.
