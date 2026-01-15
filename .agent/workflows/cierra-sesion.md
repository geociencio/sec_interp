---
description: Procedimiento para finalizar una sesión de trabajo, actualizar logs y archivar resultados
---

Este workflow cierra el ciclo de desarrollo, convirtiendo el trabajo técnico en memoria histórica para la próxima sesión.

1.  **Actualización de Memoria (Logs & Roadmap)**:
    *   **Identificación del Tema**: Define un nombre corto para la sesión (ej: `stabilization_mocks`).
    *   **`docs/plans/implementation_plan_v2.7.0.md`**: **[CRÍTICO]** Actualiza el estado de las tareas (marcar con `[x]` las completadas).
    *   **`.agent/next_steps.md`**: **[CRÍTICO]** Crea o actualiza este archivo con el "paso de testigo": qué falta, qué errores hay pendientes y cuál es el comando para retomar.
    *   **`docs/maintenance/sesion_YYYY-MM-DD_[TEMA].md`**: **[OBLIGATORIO]** Crea este archivo con el resumen técnico de la sesión.
    *   **`docs/DEVELOPMENT_LOG.md`**: **[CRÍTICO]** Añade una entrada `## [YYYY-MM-DD] Resumen` en la parte superior.
    *   **`docs/source/MAINTENANCE_LOG.md`**: Actualiza si hubo cambios de infraestructura.
    *   **`docs/CHANGELOG.md`**: Registra cambios visibles para el usuario en `[Unreleased]`.

2.  **Verificación Final (Safety Net)**:
    Ejecuta el formateador y los tests para no dejar la casa en llamas.
    ```bash
    uv run black .
    PYTHONPATH=.. uv run python3 -m unittest discover tests
    ```

3.  **Sincronización de Memoria Final (IA)**:
    Asegura que el "Cerebro" de la IA esté al día con los cambios finales.
    // turbo
    ```bash
    uv run ai-ctx analyze --path . && cat .agent/next_steps.md
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
