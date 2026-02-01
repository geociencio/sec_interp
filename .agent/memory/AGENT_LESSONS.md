# Memoria de Aprendizaje del Agente (SecInterp)

Este archivo registra lecciones técnicas, preferencias del usuario y soluciones a problemas complejos encontrados durante el desarrollo. Sirve como memoria semántica para evitar repetir errores y optimizar decisiones futuras.

## 🧠 Lecciones Críticas

### Infraestructura Agentica (2026-02-01)
- **Lección**: La sobre-simplificación de Skills durante refactorizaciones lingüísticas puede causar pérdida de manuales técnicos críticos (ej. `release-management`).
- **Acción**: Mantener siempre el "músculo" técnico en inglés mientras se traduce la estructura operativa al español.

### Arquitectura de Tests
- **Lección**: El mocking de `QgsGeometry` en entornos sin QGIS instalado requiere cuidado con métodos específicos como `pointN` o `is3D`.
- **Preferencia**: El usuario prefiere `unittest` estricto sobre `pytest` para este proyecto.

## ⚙️ Preferencias del Usuario
- **Idioma**: Comunicación y gestión en Español; código y commits en Inglés.
- **Formateo**: Uso obligatorio de `black` y gestión de dependencias con `uv`.
- **UI**: Diseño programático (sin archivos `.ui`) para mayor control y estética premium.

## 🛠️ Soluciones a Hotspots
- (Pendiente de registro tras próximas sesiones de refactorización).

---
*Última actualización: 2026-02-01*
