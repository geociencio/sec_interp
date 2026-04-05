---
description: Procedimiento para finalizar una sesión de trabajo, actualizar logs y archivar resultados
agent: QA Engineer
skills: [qa-standards, commit-standards]
validation: |
  - Verificar que todos los logs están actualizados
  - Confirmar que tests pasan antes de cerrar
  - Validar que .agent/next_steps.md existe y tiene contenido claro
---

Este workflow cierra el ciclo de desarrollo, convirtiendo el trabajo técnico en memoria histórica para la próxima sesión.

1.  **Actualización de Memoria (Logs & Roadmap)**:

    🤖 **Agent Action**: Validar que todos los archivos críticos de documentación están actualizados según los estándares del proyecto.

    *   **Identificación del Tema**: Define un nombre corto para la sesión (ej: `stabilization_mocks`).
    *   **Roadmap/Plan (`docs/ROADMAP.md` etc)**: **[CRÍTICO]** Actualiza el estado de las tareas (marcar con `[x]` las completadas).
    *   **`.agent/next_steps.md`**: **[CRÍTICO]** Crea o actualiza este archivo con el "paso de testigo": qué falta, qué errores hay pendientes y cuál es el comando para retomar.
    *   **Archivado de Next Steps**: **[NUEVO]** Si corresponde, copia `.agent/next_steps.md` al historial para mantener el registro.
    *   **Log de Sesión (`docs/DEVELOPMENT_LOG.md`)**: **[OBLIGATORIO]** Añade una entrada `## [YYYY-MM-DD] Resumen` documentando los cambios mayores.
    *   **Changelog (`CHANGELOG.md`)**: Registra cambios visibles para el usuario en `[Unreleased]`.

2.  **Verificación Final (Safety Net)**:

    🤖 **Agent Action**: Usar skill **qa-standards** para validar estabilidad antes de cerrar.

    Ejecuta el formateador y los tests base (Sanity Check).

    ```bash
    # EJEMPLO: npm run lint:fix o ruff check .
    {{LINTER_FIX_COMMAND}}
    ```

    // turbo
    ```bash
    # Control de salud definitivo
    {{MASTER_TEST_COMMAND}}
    ```

    🤖 **Agent Action**: Verificar que la suite de tests pasa. Alertar al usuario si hay fallos no resueltos.

3.  **Sincronización de Memoria Final**:

    🤖 **Agent Action**: Actualizar el `project-context` si hubo cambios arquitectónicos y validar que `next_steps.md` sea claro para la próxima sesión.

4.  **Commit Local**:

    🤖 **Agent Action**: Usar skill **commit-standards** para generar mensaje apropiado.

    Guarda tu progreso (opcional, si no se han hecho commits regulares).
    ```bash
    git add .
    git commit -m "chore(docs): close session [TEMA]"
    ```

    **Formato recomendado**: `chore(docs): close session [tema_descriptivo]`

5.  **Resumen para el Usuario**:

    🤖 **Agent Action**: Generar resumen estructurado e informar al desarrollador.

    Genera un mensaje final listando:
    *   Archivos de log actualizados.
    *   Estado de los tests.
    *   Contenido de `.agent/next_steps.md`.
    *   Sugerencia para la próxima sesión (comando `/inicia-sesion`).

## Resultado Esperado
- Memoria de la sesión persistida en Logs y `next_steps.md`.
- Repositorio limpio y validado técnicamente.
- Instrucciones claras para que el asistente retome la tarea sin pérdida de contexto.

**Filosofía**: Una sesión no termina cuando el código funciona, sino cuando la historia está contada.
