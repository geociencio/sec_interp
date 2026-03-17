---
name: qa-docker
description: Standards for testing in a Dockerized environment and use of Mocks for QGIS.
trigger: when writing or executing tests, using mocks, or managing Docker infrastructure.
---

# QA and Docker Automation

Ensures code stability through a controlled execution environment (Docker) and simulation strategies (Mocks) for PyQGIS.

## When to use this skill
- When creating new unit or integration test cases.
- When debugging failures in the CI/CD pipeline.
- When configuring or modifying the Docker development environment.

## Degree of Freedom
- **Guided**: Defined mocking strategies must be followed, but there is freedom in test case design.

## Workflow
1. **Design**: Apply "Mock-First" strategy for UI-independent logic.
2. **Implementation**: Create tests using `unittest` or `pytest`.
3. **Execution**: Validate locally and then in Docker (`make docker-test`).
    - *Lesson*: Run the full core test suite (`make test`) immediately after refactoring internal orchestration methods or changing method signatures to catch regression in mocks.
4. **Coverage**: Verify that a minimum of 80% coverage is achieved in new services.

## Instructions and Rules

### Mocking Strategy
- **Mock-First**: Follow [ADR-0004](file:///home/jmbernales/qgispluginsdev/sec_interp/docs/adr/ADR-0004-Mock-First-Testing-Strategy.md).
- **Isolation**: Run tests in separate processes to prevent Mock contamination.
- **Arithmetic Mocks**: When mocking Qt objects (QRectF, QSizeF) used in layouts, ensure numeric return values for dimensional methods (width, height, x, y) to prevent `TypeErrors` during layout calculations or comparisons like `max()`.
- **FORCE_MOCKS**: Use `FORCE_MOCKS=0` only for real integration tests.

### Docker Environment
- **Image**: Use `qgis/qgis:latest` as base.
- **Master Command**: `make docker-test` is the definitive health check.

## Quality Checklist
- [ ] Is new service coverage > 80%?
- [ ] Are Mock patches cleaned up after each test?
- [ ] Is the integration test executed in an isolated process?
- [ ] Does the Docker report show 0 failures?
