---
description: Workflow para revisión crítica de planes de implementación por el Agent Auditor
agent: Agent Auditor
skills: [coding-standards, project-context, agentic-memory]
validation: |
  - Verificar que el plan cumple con la separación Core/GUI
  - Validar que no hay deuda técnica obvia introducida
  - Confirmar que las lecciones de AGENT_LESSONS.md fueron tomadas en cuenta
---

Este workflow debe ejecutarse tras la creación de un `implementation_plan.md` pero antes de iniciar la `EXECUTION`.

1.  **Carga de Contexto Crítico**:
    🤖 **Agent Action**: Cargar `AGENT_LESSONS.md` y buscar lecciones relevantes para el plan actual.

2.  **Análisis de Cumplimiento**:
    🤖 **Agent Action**: Contrastar el plan contra los estándares de codificación (Pathlib, Typing, Google Docstrings).

3.  **Detección de Riesgos**:
    *   ¿Introduce dependencias de QGIS en `core/`?
    *   ¿Propone cambios que rompan la compatibilidad con QGIS 4.x (PyQt5)?
    *   ¿El plan de verificación es suficiente?

4.  **Emisión de Veredicto**:
    🤖 **Agent Action**: Generar un reporte de auditoría indicando:
    *   **PASSED**: El plan es sólido.
    *   **FAILED**: El plan requiere correcciones específicas.
    *   **OBSERVATIONS**: Sugerencias de mejora no críticas.

---
*Filosofía: Es mejor encontrar un error en el plano que en la obra.*
