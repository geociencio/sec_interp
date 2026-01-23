---
description: How to run unit tests reliably
agent: QA Engineer
skills: [qa-docker]
validation: |
  - Verificar que todos los tests pasen (361 tests OK)
  - Confirmar que no hay errores de mocking
---
This workflow describes how to run unit tests for the SecInterp project using `unittest`, ensuring that the Python path and QGIS environment are correctly configured.

1. Ensure you are in the project root directory (`qgispluginsdev/sec_interp`).

2. Run the tests using `uv` to handle dependencies and set `PYTHONPATH` to include the parent directory so that `sec_interp` package resolution works.

```bash
PYTHONPATH=.. uv run python3 -m unittest discover sec_interp/tests
```

Or to run a specific test file, reference it as a module relative to the parent directory:

```bash
PYTHONPATH=.. uv run python3 -m unittest sec_interp.tests.core.test_drillhole_service
```

**Key Notes:**
- Do not use `pytest`. The project has migrated to strict `unittest`.
- Always set `PYTHONPATH=..` when running from the project root to ensure `import sec_interp` works correctly.

🤖 **Agent Action**: Usar skill **qa-docker** para:
- Interpretar fallos de tests (mocks vs lógica real)
- Sugerir correcciones basadas en estándares de mocking del skill
- Verificar que los mocks de QGIS están correctamente configurados según `tests/base_test.py`
