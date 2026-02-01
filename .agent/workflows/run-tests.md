---
description: How to run unit tests reliably
agent: QA Engineer
skills: [qa-docker]
validation: |
  - Verificar que todos los tests pasen (361 tests OK)
  - Confirmar que no hay errores de mocking
1. **Run Unit Tests (Fast)**:
   ```bash
   PYTHONPATH=.. uv run python3 -m unittest discover tests/core
   ```

2. **Run Integration Tests (Real QGIS)**:
   ```bash
   FORCE_MOCKS=0 PYTHONPATH=.. uv run python3 -m unittest discover tests/integration
   ```

3. **Recommended Method (Docker - Complete)**:
   The definitive health check is running all tests in Docker:
   // turbo
   ```bash
   make docker-test
   ```

**Key Notes:**
- Do not use `pytest`. The project has migrated to strict `unittest`.
- Always set `PYTHONPATH=..` when running unit tests from the project root.
- **Process Isolation**: Do NOT run `tests/core` and `tests/integration` in the same process to avoid Mock pollution.

🤖 **Agent Action**: Usar skill **qa-docker** para interpretar fallos y validar la estrategia de mocking.

## Resultado Esperado
- Informe claro del estado de estabilidad del proyecto.
- Identificación de regresiones o fallos democks.
- Confirmación de si el código es seguro para ser integrado.
