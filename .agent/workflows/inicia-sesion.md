---
description: Procedimiento estándar y robusto para iniciar una sesión de desarrollo "Local First"
agent: Senior Architect
skills: [qgis-core, qa-docker, agentic-memory]
validation: |
  - Verificar que todos los tests pasen en Docker
  - Confirmar que AI_CONTEXT.md está actualizado con métricas recientes

  - Validar que no hay regresiones en complejidad ciclomática
---

Este workflow optimiza el inicio del desarrollo asegurando un entorno sincronizado, **contextualizado** y validado.

1.  **Sintonización de Contexto (CRÍTICO)**:
    Actualiza y lee el contexto para entender "dónde nos quedamos".
    // turbo
    ```bash
    uv run ai-ctx analyze --path . && cat .agent/next_steps.md && cat .agent/memory/AGENT_LESSONS.md
    ```

    🤖 **Agent Action**: Validar Tareas Activas.

    *   **Gestión de Tareas**:
        *   Verifica si existe `.agent/task.md`.
        *   Si existe: Muestra el contenido ("Estado Actual").
        *   Si NO existe: Créalo basándote en el Plan de Implementación activo o `next_steps.md`.

    🤖 **Agent Action**: Revisar `AI_CONTEXT.md` y `project_context.json` usando skill **qgis-core** para identificar:
    - Deuda técnica crítica relacionada con QGIS API
    - Métodos con alta complejidad ciclomática (CC > 15)
    - Violaciones de arquitectura (UI en Core)


    Revisa los siguientes archivos en este orden:
    *   `.agent/next_steps.md`: **El Testigo (Fuente de Verdad)**. Define el punto de partida exacto y objetivos inmediatos.
    *   `.agent/task.md`: **Tablero Activo**. Si existe, debe alinearse con `next_steps.md`. Si no, créalo basado en `next_steps.md`.
    *   `.agent/memory/AGENT_LESSONS.md`: **El Cerebro**. Patrones de error a evitar y preferencias.
    *   `AI_CONTEXT.md`: Contexto arquitectónico y métricas de largo plazo.
    *   `project_context.json`: Datos estructurados de complejidad y dependencias.
    *   `docs/DEVELOPMENT_LOG.md`: Ver resumen de la última sesión (orden cronológico inverso).

    *   `docs/LOGGING_GUIDELINES.md`: Seguir estrictamente para registrar nuevas actividades.


### 3. Quick Quality Scan (Novedad v1.9.0)
Realiza un escaneo rápido del estado del proyecto para identificar deuda técnica crítica.
```bash
uv run qgis-analyzer summary
```

### 4. Validación de Integridad (Tests)**:
    Asegura dependencias actualizadas.
    // turbo
    ```bash
    uv sync
    ```

    🤖 **Agent Action**: Verificar que no hay conflictos de dependencias relacionadas con PyQGIS.

3.  **Verificación de Estado (Sanity Check)**:
    Confirma que el sistema está estable ("en verde"). Todos los tests deben pasar.

    *Opción A (Docker - Recomendado):*
    // turbo
    ```bash
    make docker-test
    ```

    *Opción B (Local):*
    ```bash
    env PYTHONPATH=.. uv run python3 -m unittest discover tests
    ```

    🤖 **Agent Action**: Usar skill **qa-docker** para interpretar fallos de tests e identificar regresiones.

## Resultado Esperado
- Entorno sincronizado y validado (Todos los tests OK).
- Mapa mental claro de las tareas pendientes en `next_steps.md`.
- Agente operando con los perfiles y skills correctos cargados.

**Filosofía**: Empezar a codificar sabiendo *exactamente* qué pasó ayer y con el contexto especializado cargado.
