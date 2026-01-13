---
description: Procedimiento estándar y robusto para iniciar una sesión de desarrollo "Local First"
---

Este workflow optimiza el inicio del desarrollo asegurando un entorno sincronizado, **contextualizado** y validado.

1.  **Sintonización de Contexto (CRÍTICO)**:
    Actualiza y lee el contexto para entender "dónde nos quedamos".
    // turbo
    ```bash
    uv run ai-ctx analyze --path .
    ```
    Revisa los siguientes archivos:
    *   `.ai-context/project_brain.md`: Memoria de largo plazo y métricas.
    *   `docs/DEVELOPMENT_LOG.md`: Ver resumen de la última sesión (orden cronológico inverso).
    *   `docs/LOGGING_GUIDELINES.md`: Seguir estrictamente para registrar nuevas actividades.
    *   `docs/source/MAINTENANCE_LOG.md`: Ver si hubo cambios de infraestructura recientes.
    *   `AI_CONTEXT.md`: Ver directrices de alto nivel y roadmap.
    *   `task.md`: Ver tareas pendientes de la sesión actual.

2.  **Sincronización de Entorno (Local)**:
    Asegura dependencias actualizadas.
    ```bash
    uv sync
    ```

3.  **Verificación de Estado (Sanity Check)**:
    Confirma que el sistema está estable ("en verde").
    ```bash
    PYTHONPATH=.. uv run python3 -m unittest discover tests
    ```

4.  **Despliegue Local al QGIS (Hot-Reload)**:
    Actualiza tu QGIS local.
    ```bash
    make deploy
    ```

**Objetivo**: Empezar a codificar sabiendo *exactamente* qué pasó ayer.
