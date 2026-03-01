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

  - date: 2026-02-19
    category: ARCHITECTURE
    topic: Resilience & Lazy Loading
    lesson: "When implementing experimental features or heavy domain services, use a SafeLoader/Lazy Loading pattern to prevent cascading failures during plugin initialization. This ensures the core plugin remains functional even if a specific module fails to load (e.g., due to missing dependencies)."
    action: "Implement SafeLoader for all optional or heavy services and use demand-based instantiation. IMPROVEMENT: Support constructor arguments in lazy_load."

  - date: 2026-02-25
    category: TECHNICAL
    topic: Data Modeling and Typing
    lesson: "Using tuples for complex data transfer makes code unreadable and hard to refactor (index-based access)."
    action: "Mandatory use of Dataclasses (entities) for all service returns. Avoid list[tuple]."

  - date: 2026-02-28
    category: ARCHITECTURE
    topic: Layer Caching and Mock Integrity
    lesson: "When centralizing layer resolution with caching (LayerResolver), mock layers must have unique IDs across tests to prevent cross-test cache pollution."
    action: "Implement a global UNIQUE_ID_COUNTER in test mocks and call LayerResolver.clear_cache() in BaseTestCase.setUp()."

  - date: 2026-02-28
    category: TECHNICAL
    topic: Strict QGIS Validation in Mocks
    lesson: "Strict validators use layer.wkbType() and check for formal QgsField existence. Mocks must support setWkbType and formal field addition to pass production-grade validation."
    action: "Update MockQgsMapLayer to support WKB types and use real QgsField objects instead of simpler mocks when validation is involved."



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
  - date: 2026-02-15
    category: QUALITY
    topic: qgis-analyzer Context
    lesson: "El analizador de QGIS incluye la carpeta tests/ en el score global de tipado, lo que puede distorsionar la percepción de calidad de producción."
    action: "Realizar desgloses por carpeta para validar el cumplimiento del código de producción (core/gui)."

  - date: 2026-02-15
    category: TECHNICAL
    topic: QGIS Signal Leaks
    lesson: "Las señales conectadas a herramientras de mapa (MapTools) o páginas de diálogos deben desconectarse explícitamente para evitar fugas y comportamientos erráticos."
    action: "Implementar siempre un método disconnect_signals() que se invoque al cerrar el contexto."

## ⚙️ Configuración Global de Preferencias

- **Idioma**: Comunicación (Español), Código/Commits (Inglés).
- **Estándares**: Google Docstrings, Pathlib, Strict Typing.
- **Workflow**: Inicia con `/inicia-sesion`, Cierra con `/cierra-sesion`.

---
  - date: 2026-02-16
    category: TECHNICAL
    topic: Signal Tracing vs Mocks
    lesson: "El uso de wrappers para conectar señales (como sm._connect_checked) puede romper los tests unitarios si estos esperan llamadas directas al Mock del slot. Las señales conectadas mdiante wrappers no son detectadas por `assert_called_with` de objetos Mock."
    action: "Para métodos que son mocks en tests unitarios, mantener conexiones de señal directas sin wrappers de rastreo, u orquestar la desconexión selectiva."

  - date: 2026-02-18
    category: TECHNICAL
    topic: qgis-manage Build Rigidity
    lesson: "La herramienta qgis-manage tiene exclusiones hardcoded y depende de pyrcc5 (PyQt5), lo que genera deuda técnica automática en resources.py."
    action: "Tras compilar recursos, aplicar siempre un parcheo de imports (sed) y verificar que no falten archivos necesarios en el despliegue debido a exclusiones ocultas."

  - date: 2026-02-18
    category: USER_PREFERENCE
    topic: Fast Deployment
    lesson: "Para iteraciones rápidas que no requieran cambios en recursos o traducciones, se prefiere evitar la compilación."
    action: "Utilizar el comando: 'uv run qgis-manage deploy --no-compile'"

---
*Última actualización: 2026-02-28 - Refactor LayerResolver y mejora de robustez de mocks.*
