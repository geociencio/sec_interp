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

## Tools
- `unittest` for running tests.
- `ruff` for linting.
- `black` for formatting.
