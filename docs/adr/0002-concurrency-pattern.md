# 2. Concurrency Pattern: Queued Tasks and DTOs

Date: 2026-01-15

## Status

Accepted

## Context

The plugin performs significant geoprocessing tasks, such as:
- Generating topographic profiles from DEM.
- Projecting geological structures.
- Projecting drillhole traces and interpolating intervals.

Initially, these operations were synchronous or used basic `QThread` implementations which were prone to UI freezing (blocking the main thread) or random crashes (segmentation faults) when accessing QGIS API objects (like `QgsVectorLayer` or `QgsGeometry`) from background threads without proper thread affinity management.

## Decision

We have decided to adopt a strict **Queued Task Pattern** using `QgsTask` and **Data Transfer Objects (DTOs)** for all heavy processing operations (>100ms).

### 1. QgsTask
We use `QgsTask` (specifically subclassing it) instead of raw `QThread` or `QThreadPool` because:
- It integrates natively with the QGIS Task Manager UI, providing progress bars and cancellation support out-of-the-box.
- It simplifies cleaning up resources upon completion or cancellation.

### 2. Data Transfer Objects (DTOs)
To solve the thread-safety issues inherent in the QGIS C++ API, we enforce a strict separation of data:

- **Main Thread (Preparation)**: Before starting a task, all necessary data is extracted from QGIS objects (`QgsVectorLayer`, `QgsFeature`, etc.) and packed into a pure Python dataclass (DTO) or a detached `QgsGeometry` copy.
- **Background Thread (Processing)**: The service layer receives *only* the DTO. It performs calculations using these detached objects. It absolutely **must not** access the original layer or feature objects.
- **Main Thread (Completion)**: The task returns the results (also as DTOs or simple types) to the main thread via a callback, where they can be safely used to update the UI or QGIS layers.

## Consequences

### Positive
- **Responsiveness**: The plugin UI remains responsive even during heavy processing.
- **Stability**: Eliminates "QObject::startTimer: Timers cannot be started from another thread" warnings and potential segfaults.
- **Testability**: Service logic becomes pure (stateless) and easier to test since it relies on simple input data structures rather than complex mocked QGIS environment states.

### Negative
- **Complexity**: Requires defining dedicated DTO classes (e.g., `DrillholeTaskInput`, `GeologyTaskInput`).
- **Memory Overhead**: Data is duplicated (detached) for the background task, which might increase memory usage for very large datasets, though this is usually negligible compared to the stability benefits.

## Compliance
New features involving data processing must verify:
1. Is a `QgsTask` used?
2. Is a DTO defined in `core/types.py`?
3. Does the service processing method take only the DTO as input?
