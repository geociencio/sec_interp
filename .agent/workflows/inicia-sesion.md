---
description: Procedimiento estándar y robusto para iniciar una sesión de desarrollo "Local First"
---

Este workflow optimiza el inicio del desarrollo asegurando un entorno sincronizado, **contextualizado** y validado.

1.  **Sintonización de Contexto (CRÍTICO)**:
    Antes de tocar código, lee los siguientes archivos para entender "dónde nos quedamos":
    *   `docs/DEVELOPMENT_LOG.md`: Ver fecha y resumen de la última sesión.
    *   `docs/source/MAINTENANCE_LOG.md`: Ver si hubo cambios de infraestructura recientes.
    *   `AI_CONTEXT.md`: Ver directrices de alto nivel y roadmap.
    *   `task.md`: Ver tareas pendientes.
    *   Comando útil: `tail -n 15 docs/DEVELOPMENT_LOG.md`

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
