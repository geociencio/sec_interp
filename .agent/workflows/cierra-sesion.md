---
description: Procedimiento para finalizar una sesión de trabajo, actualizar logs y archivar resultados
---

Este workflow cierra el ciclo de desarrollo, convirtiendo el trabajo técnico en memoria histórica para la próxima sesión.

1.  **Actualización de Memoria (Logs)**:
    *   **`docs/DEVELOPMENT_LOG.md`**: Añade una entrada `## [YYYY-MM-DD] Resumen` con puntos clave (Features, Fixes, Docs).
    *   **`docs/source/MAINTENANCE_LOG.md`**: Si tocaste infraestructura, pre-commit, versiones o CI/CD, regístralo aquí.
    *   **`docs/CHANGELOG.md`**: Si completaste una feature visible para el usuario, añádela a `[Unreleased]`.

2.  **Verificación Final (Safety Net)**:
    Ejecuta los tests una última vez para no dejar la casa en llamas.
    ```bash
    PYTHONPATH=.. uv run python3 -m unittest discover tests
    ```

3.  **Commit Local**:
    Guarda tu progreso.
    ```bash
    git add .
    git commit -m "chore: cerrar sesion [TEMA]"
    ```
    *Nota: Si pre-commit falla, corrige y repite.*

4.  **Resumen para el Usuario**:
    Genera un mensaje final listando:
    *   Archivos de log actualizados.
    *   Estado de los tests.
    *   Sugerencia para la próxima sesión.

**Filosofía**: Una sesión no termina cuando el código funciona, sino cuando la historia está contada.
