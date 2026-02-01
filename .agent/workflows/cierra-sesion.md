---
description: Procedimiento para finalizar una sesión de trabajo, actualizar logs y archivar resultados
agent: QA Engineer
skills: [qa-docker, commit-standards]
validation: |
  - Verificar que todos los logs están actualizados
  - Confirmar que tests pasan antes de cerrar
  - Validar que .agent/next_steps.md existe y tiene contenido claro
---

Este workflow cierra el ciclo de desarrollo, convirtiendo el trabajo técnico en memoria histórica para la próxima sesión.

1.  **Actualización de Memoria (Logs & Roadmap)**:

    🤖 **Agent Action**: Validar que todos los archivos críticos están actualizados.

    *   **Identificación del Tema**: Define un nombre corto para la sesión (ej: `stabilization_mocks`).
    *   **`docs/plans/implementation_plan_vX.Y.Z.md`**: **[CRÍTICO]** Actualiza el estado de las tareas (marcar con `[x]` las completadas).
    *   **`.agent/next_steps.md`**: **[CRÍTICO]** Crea o actualiza este archivo con el "paso de testigo": qué falta, qué errores hay pendientes y cuál es el comando para retomar.
    *   **Archivado de Next Steps**: **[NUEVO]** Copia `.agent/next_steps.md` a `.agent/history/next_steps/next_steps_YYYY-MM-DD.md` para mantener el registro histórico.
    *   **`docs/maintenance/sesion_YYYY-MM-DD_[TEMA].md`**: **[OBLIGATORIO]** Crea este archivo con el resumen técnico de la sesión.
    *   **`docs/DEVELOPMENT_LOG.md`**: **[CRÍTICO]** Añade una entrada `## [YYYY-MM-DD] Resumen` en la parte superior.
    *   **`docs/source/MAINTENANCE_LOG.md`**: Actualiza si hubo cambios de infraestructura.
    *   **`docs/CHANGELOG.md`**: Registra cambios visibles para el usuario en `[Unreleased]`.

2.  **Verificación Final (Safety Net)**:

    🤖 **Agent Action**: Usar skill **qa-docker** para validar estabilidad antes de cerrar.

    Ejecuta el formateador y los tests para no dejar la casa en llamas.

    ```bash
    uv run black .
    ```

    *Opción A (Docker - Recomendado):*
    ```bash
    make docker-test
    ```

    🤖 **Agent Action**: Verificar que 361 tests pasan. Alertar si hay fallos.

    *Opción B (Local):*
    ```bash
    PYTHONPATH=.. uv run python3 -m unittest discover tests
    ```

3.  **Sincronización de Memoria Final (IA)**:

    🤖 **Agent Action**: Actualizar AI_CONTEXT.md y validar que next_steps.md es claro.


    Asegura que el "Cerebro" de la IA esté al día con los cambios finales.
    // turbo
    ```bash
    ai-ctx analyze --path . && cat .agent/next_steps.md
    ```

4.  **Commit Local**:

    🤖 **Agent Action**: Usar skill **commit-standards** para generar mensaje apropiado.

    Guarda tu progreso.
    ```bash
    git add .
    git commit -m "chore(docs): close session [TEMA]"
    ```

    **Formato recomendado**: `chore(docs): close session [tema_descriptivo]`

    *Si el pre-commit hook persiste en fallar:*
    1. Revisa los mensajes de error detectados.
    2. Ejecuta `git add` de nuevo si hubo cambios automáticos.
    3. Repite el commit.

5.  **Resumen para el Usuario**:

    🤖 **Agent Action**: Generar resumen estructurado de la sesión.

    Genera un mensaje final listando:
    *   Archivos de log actualizados.
    *   Estado de los tests (361 tests OK).
    *   Contenido de `.agent/next_steps.md`.
    *   Sugerencia para la próxima sesión (comando `/inicia-sesion`).

## Resultado Esperado
- Memoria de la sesión persistida en Logs y `next_steps.md`.
- Repositorio limpio y validado técnicamente.
- Instrucciones claras para que el asistente retome la tarea sin pérdida de contexto.

**Filosofía**: Una sesión no termina cuando el código funciona, sino cuando la historia está contada.
