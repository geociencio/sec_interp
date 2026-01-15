# 4. Mock-First Testing Strategy

Date: 2025-12 (v2.6.0)

## Status

Accepted

## Context

Testing QGIS plugins typically requires a running QGIS application instance (`QgsApplication`). Initializing this instance for every test run is slow and resource-intensive, making "Test Driven Development" (TDD) painful and CI/CD pipelines slow.
Furthermore, `qgis.testing` utilities often require a display server (X11/xvfb) which complicates headless environments.

## Decision

We have adopted a **Mock-First Testing Strategy** for the majority of our Unit Tests.

### 1. Custom Mock Infrastructure (`tests/base_test.py`)
We implemented a comprehensive set of mock classes mimicking QGIS core objects:
- `MockQgsBase`
- `MockQgsMapLayer`, `MockQgsVectorLayer`, `MockQgsRasterLayer`
- `MockQgsGeometry`, `MockQgsPointXY`
- `MockQgsFeature`, `MockQgsFields`

### 2. Testing Layers
- **Unit Tests (Fast)**: Use `unittest` + `tests.base_test.BaseTestCase`. These tests mock almost all QGIS interactions. They run in milliseconds and require no QGIS installation (pure Python).
- **Integration Tests (Slow)**: Tests that require real QGIS algorithms or rendering engines must be marked separately and run in a specific environment (e.g., Docker container with QGIS installed).

## Consequences

### Positive
- **Speed**: Test suite runs in <1 second vs >10 seconds.
- **Isolation**: Tests focus on our logic, not QGIS internal behaviors.
- **Portability**: Tests can run in any Python environment (e.g., standard GitHub Actions runners) without installing QGIS.

### Negative
- **Mock Maintenance**: We must maintain the mock classes. If QGIS API changes, our mocks might drift from reality.
- **False Positives**: A test might pass against a mock but fail against real QGIS if the mock implementation is too simplistic (e.g., `intersects` always returning True).

## Compliance
- All business logic in `core/` should be testable using `MockQgs*` objects.
- New developers should prefer `unittest.mock` over `qgis.testing` for logic tests.
