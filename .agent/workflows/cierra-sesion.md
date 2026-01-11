---
description: Procedimiento para finalizar una sesión de trabajo, actualizar logs y archivar resultados
---

Este workflow cierra el ciclo de desarrollo, convirtiendo el trabajo técnico en memoria histórica para la próxima sesión.

1.  **Actualización de Memoria (Logs)**:
    *   **Identificación del Tema**: Define un nombre corto para la sesión (ej: `planning_v2.7.0`).
    *   **`docs/maintenance/sesion_YYYY-MM-DD_[TEMA].md`**: **[OBLIGATORIO]** Crea este archivo con el resumen técnico de la sesión, logros, cambios en archivos y estado de la fase.
    *   **`docs/DEVELOPMENT_LOG.md`**: Añade una entrada `## [YYYY-MM-DD] Resumen` con puntos clave y link al informe de sesión.
    *   **`docs/source/MAINTENANCE_LOG.md`**: Actualiza siempre que haya planificación de fases, cambios en CI/CD, pre-commit o infraestructura.
    *   **`docs/CHANGELOG.md`**: Si completaste una feature visible para el usuario, añádela a `[Unreleased]`.

2.  **Verificación Final (Safety Net)**:
    Ejecuta los tests una última vez para no dejar la casa en llamas.
    ```bash
    PYTHONPATH=.. uv run python3 -m unittest discover tests
    ```

3.  **Sincronización de Memoria Final (IA)**:
    Asegura que el "Cerebro" de la IA esté al día con los cambios finales.
    // turbo
    ```bash
    python3 .ai-context/analyze_project_optfixed.py
    ```

4.  **Commit Local**:
    Guarda tu progreso.
    ```bash
    git add .
    git commit -m "chore: cerrar sesion [TEMA]"
    ```
    *Nota: Si pre-commit falla, corrige y repite.*

5.  **Resumen para el Usuario**:
    Genera un mensaje final listando:
    *   Archivos de log actualizados.
    *   Estado de los tests.
    *   Sugerencia para la próxima sesión.

**Filosofía**: Una sesión no termina cuando el código funciona, sino cuando la historia está contada.
