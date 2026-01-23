---
description: Procedimiento estándar y robusto para iniciar una sesión de desarrollo "Local First"
agent: Senior Architect
skills: [qgis-core, qa-docker]
validation: |
  - Verificar que 361 tests pasen en Docker
  - Confirmar que project_brain.md está actualizado con métricas recientes
  - Validar que no hay regresiones en complejidad ciclomática
---

Este workflow optimiza el inicio del desarrollo asegurando un entorno sincronizado, **contextualizado** y validado.

1.  **Sintonización de Contexto (CRÍTICO)**:
    Actualiza y lee el contexto para entender "dónde nos quedamos".
    // turbo
    ```bash
    uv run ai-ctx analyze --path . && cat .agent/next_steps.md
    ```

    🤖 **Agent Action**: Revisar `project_brain.md` usando skill **qgis-core** para identificar:
    - Deuda técnica crítica relacionada con QGIS API
    - Métodos con alta complejidad ciclomática (CC > 15)
    - Violaciones de arquitectura (UI en Core)

    Revisa los siguientes archivos en este orden:
    *   `docs/plans/implementation_plan_v2.8.0.md`: **Mapa de Ruta Maestro**. Fuente de verdad sobre tareas completadas.
    *   `.agent/next_steps.md`: **El Testigo**. Punto exacto donde se detuvo la sesión anterior.
    *   `.ai-context/project_brain.md`: Memoria de largo plazo y métricas.
    *   `docs/DEVELOPMENT_LOG.md`: Ver resumen de la última sesión (orden cronológico inverso).
    *   `docs/LOGGING_GUIDELINES.md`: Seguir estrictamente para registrar nuevas actividades.
    *   `AI_CONTEXT.md`: Ver directrices de alto nivel y roadmap general.

2.  **Sincronización de Entorno (Local)**:
    Asegura dependencias actualizadas.
    ```bash
    uv sync
    ```

    🤖 **Agent Action**: Verificar que no hay conflictos de dependencias relacionadas con PyQGIS.

3.  **Verificación de Estado (Sanity Check)**:
    Confirma que el sistema está estable ("en verde"). Todos los tests (361) deben pasar.

    *Opción A (Docker - Recomendado):*
    ```bash
    make docker-test
    ```

    *Opción B (Local):*
    ```bash
    env PYTHONPATH=.. uv run python3 -m unittest discover tests
    ```

    🤖 **Agent Action**: Usar skill **qa-docker** para interpretar fallos de tests:
    - Identificar si son fallos de mocks o de lógica real
    - Sugerir correcciones basadas en estándares del skill
    - Verificar que tests de integración 3D están cubiertos

**Objetivo**: Empezar a codificar sabiendo *exactamente* qué pasó ayer y con el contexto especializado cargado.
