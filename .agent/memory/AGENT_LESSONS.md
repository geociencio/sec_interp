# Memoria de Aprendizaje del Agente (SecInterp)

Este archivo registra lecciones técnicas, preferencias del usuario y soluciones a problemas complejos. Utiliza un formato estructurado para permitir una recuperación eficiente por parte del sistema de agentes.

## 🧠 Registro de Lecciones (YAML Structured)

```yaml
lessons:
  - date: 2026-02-01
    category: ARCHITECTURE
    topic: Skill Localization
    lesson: "La sobre-simplificación de Skills durante traducciones puede causar pérdida de manuales técnicos."
    action: "Mantener núcleos técnicos en Inglés; estructura operativa en Español."

  - date: 2026-02-01
    category: TECHNICAL
    topic: QgsGeometry Mocking
    lesson: "Mocking de QgsGeometry requiere cuidado con métodos como pointN o is3D."
    action: "Preferir unittest para este proyecto según preferencia del usuario."

  - date: 2026-02-05
    category: USER_PREFERENCE
    topic: Development Tools
    lesson: "Preferencia por black (formateo), uv (dependencias) y UI programática (sin .ui)."
    action: "Aplicar estos estándares en cada nueva implementación de GUI."

  - date: 2026-02-05
    category: ARCHITECTURE
    topic: Agentic Brain Evolution
    lesson: "La Gen 3 introduce autocrítica (Auditor) y memoria semántica para mayor estabilidad cognitiva."
    action: "Invocación de /ia-critic tras planificación y /cierra-sesion para aprendizaje continuo."
```

## ⚙️ Configuración Global de Preferencias

- **Idioma**: Comunicación (Español), Código/Commits (Inglés).
- **Estándares**: Google Docstrings, Pathlib, Strict Typing.
- **Workflow**: Inicia con `/inicia-sesion`, Cierra con `/cierra-sesion`.

---
*Última actualización: 2026-02-05 - Estructura optimizada para Agentic Memory.*
