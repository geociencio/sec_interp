---
description: How to run unit tests reliably
agent: QA Engineer
skills: [qa-docker]
validation: |
  - Verify that all tests pass (535 tests OK)
  - Confirm that there are no mocking errors
---

# Workflow: Run Tests

This workflow ensures that the plugin's stability is verified through unit and integration tests.

### 1. Run Unit Tests (Fast)
```bash
PYTHONPATH=.. uv run python3 -m unittest discover tests/core
```

### 2. Run Integration Tests (Real QGIS)
```bash
FORCE_MOCKS=0 PYTHONPATH=.. uv run python3 -m unittest discover tests/integration
```

### 3. Recommended Method (Docker - Complete)
The definitive health check is running all tests in Docker:
// turbo
```bash
make docker-test
```

**Key Notes:**
- Do not use `pytest`. The project has migrated to strict `unittest`.
- Always set `PYTHONPATH=..` when running unit tests from the project root.
- **Process Isolation**: Do NOT run `tests/core` and `tests/integration` in the same process to avoid Mock pollution.

🤖 **Agent Action**: Use **qa-docker** skill to interpret failures and validate the mocking strategy.

## Expected Result
- Clear report of the project's stability status.
- Identification of regressions or mock failures.
- Confirmation of whether the code is safe to be integrated.

## Structured Result Summary
🤖 **Agent Action**: Conclude with a YAML block summarizing the test run:
```yaml
test_run: complete
total_tests: 535
passed: X
failed: Y
errors: Z
stability_score: 0-100
```
