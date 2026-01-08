---
description: Procedimiento estándar para iniciar una nueva sesión de trabajo
---

Este workflow establece la secuencia de pasos para arrancar una sesión de desarrollo de manera organizada y con contexto.

1.  **Limpieza y Preparación**:
    *   Verificar si existen artefactos de la sesión anterior (`task.md`, `implementation_plan.md`).
    *   Si existen y están concluidos, moverlos o resetearlos.

2.  **Análisis de Contexto**:
    *   Leer `docs/DEVELOPMENT_LOG.md` para entender el estado actual y la última actividad.
    *   Ejecutar `git log -n 5 --oneline` para ver los últimos cambios técnicos.
    *   Revisar archivos abiertos por el usuario para inferir el foco actual.

3.  **Inicialización de Artefactos**:
    *   Crear/Sobrescribir `task.md` con la fecha y una lista de tareas vacía o inferida.
    *   Crear/Sobrescribir `implementation_plan.md` con la plantilla base.

4.  **Confirmación de Objetivos**:
    *   Proponer al usuario un objetivo basado en el análisis (ej. "Continuar refactorización", "Debuggear crash").
    *   Esperar confirmación o ajuste del usuario.

// turbo
5.  **Verificación de Entorno (Opcional)**:
    *   Verificar estado de tests rápido si se sospecha inestabilidad.
    ```bash
    uv run python3 scripts/quick_health_check.py # (Si existe)
    ```
