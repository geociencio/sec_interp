# 8. Drillhole Service Decomposition and Types Modularization

Date: 2026-01-25

## Status

Accepted

## Context

The `DrillholeService` class had grown into a monolithic component (approx. 1000 lines, maintainability index < 20, Cyclomatic Complexity > 100) responsible for multiple distinct concerns:
1. Extracting data from QGIS layers (`QgsVectorLayer`).
2. Performing geometric calculations (projections, desurveying).
3. Interpolating geological intervals.
4. Orchestrating the overall process.

Similarly, `core/types.py` was becoming a catch-all file for Data Transfer Objects (DTOs), Domain Entities, and Enums, creating tight coupling and circular dependency risks across the `core` module.

This high coupling made unit testing difficult (requiring complex mocks) and hindered the addition of new features like advanced 3D integration.

## Decision

We decided to apply the **Single Responsibility Principle (SRP)** and **Facade Pattern** to refactor these components.

### 1. DrillholeService Breakdown
We decomposed `DrillholeService` into specialized processors located in a new package `core/services/drillhole/`:

*   **`DrillholeService` (Facade)**: Remains as the main entry point but delegates logic to processors. It orchestrates the flow and manages dependency injection.
*   **`CollarProcessor`**: Handles extraction of collar data from QGIS layers and initial projection onto the section line.
*   **`SurveyProcessor`**: Handles depth calculations and trajectory logic.
*   **`IntervalProcessor`**: Handles the interpolation of geological intervals along the drillhole trace.
*   **`ProjectionEngine`**: Contains pure geometric math functions (e.g., `project_point_to_line`), completely decoupled from QGIS API objects where possible.

### 2. Types Modularization
We split `core/types.py` into a package `core/types/` with specialized modules:

*   **`domain_types.py`**: Core domain entities (`GeologySegment`, `StructureMeasurement`).
*   **`task_inputs.py`**: DTOs specifically designed for decoupling background tasks (`DrillholeTaskInput`).
*   **`dtos.py`**: General data transfer objects like `PreviewParams`.
*   **`enums.py`**: Enumerations like `FieldType`.
*   **`__init__.py`**: Re-exports all types to maintain backward compatibility with existing imports.

## Consequences

### Positive
*   **Testability**: Each processor can be tested in isolation (Unit Tests).
*   **Maintainability**: Codebase is easier to navigate. `DrillholeService` complexity dropped significantly.
*   **Scalability**: New processing logic (e.g., a new desurvey algorithm) can be added as a new processor or method without modifying the orchestration logic.
*   **Decoupling**: `ProjectionEngine` allows for geometric logic reuse without `QgsVectorLayer` overhead.

### Negative
*   **File Count**: increased number of files in the project.
*   **Complexity**: Wiring up the service requires instantiating multiple processors (handled in `__init__`).

## Compliance
This ADR complies with the project's goal of "Quality First" and prepares the architecture for "Objective 1: Advanced 3D Integration".
