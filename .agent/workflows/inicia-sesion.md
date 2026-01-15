---
description: Procedimiento estándar y robusto para iniciar una sesión de desarrollo "Local First"
---

Este workflow optimiza el inicio del desarrollo asegurando un entorno sincronizado, **contextualizado** y validado.

1.  **Sintonización de Contexto (CRÍTICO)**:
    Actualiza y lee el contexto para entender "dónde nos quedamos".
    // turbo
    ```bash
    uv run ai-ctx analyze --path . && cat .agent/next_steps.md
    ```
    Revisa los siguientes archivos en este orden:
    *   `docs/plans/implementation_plan_v2.7.0.md`: **Mapa de Ruta Maestro**. Fuente de verdad sobre tareas completadas.
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

3.  **Verificación de Estado (Sanity Check)**:
    Confirma que el sistema está estable ("en verde"). Todos los tests (347) deben pasar.
    ```bash
    env PYTHONPATH=.. uv run python3 -m unittest discover tests
    ```

**Objetivo**: Empezar a codificar sabiendo *exactamente* qué pasó ayer.
