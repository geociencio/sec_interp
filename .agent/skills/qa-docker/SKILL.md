---
name: qa-docker
description: Standards for testing within the Dockerized QA environment and using Mocks for QGIS.
trigger: when writing or running tests, using mocks or dealing with Docker infrastructure.
scope: root
---

# QA & Docker Automation Skill

## Environment
- **Docker**: The primary testing environment uses the `qgis/qgis:latest` image.
- **Commands**: Use `make docker-test` to run the full suite.

## Testing Rules
- **Mock-First**: Follow [ADR-0004](file:///home/jmbernales/qgispluginsdev/sec_interp/docs/adr/ADR-0004-Mock-First-Testing-Strategy.md). Use `unittest.mock` to simulate QGIS components when running outside a full QGIS instance.
- **Coverage**: Every new service must have at least 80% unit test coverage.
- **Integration**: 1 integration test per major feature is required.

## Environment Isolation
- **Process Splitting**: To avoid contamination between Mocks and the real QGIS API, execute tests in separate processes (core/exporters/gui vs integration).
- **FORCE_MOCKS**: Use environment variable `FORCE_MOCKS=0` to force load the real QGIS API in integration tests.
- **Cleanup**: Always call `remove_mock_patches()` from `tests.base_test` before initializing `QgsApplication` in integration tests.

## Tools
- `unittest` for running tests. Direct reference via module path is preferred.
- `make docker-test` as the definitive health check (runs all suites in isolated processes).
- `ruff` and `black` for linting and formatting.
