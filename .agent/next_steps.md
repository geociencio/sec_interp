# Próximos Pasos (Ciclo v3.0.x / v3.1.x)

## 🎯 Prioridad Inmediata: Limpieza de Linting (v3.0.1)
**Objetivo**: Abordar los 85 issues reportados por el QGIS Security Scan para asegurar un código limpio y profesional en el repositorio oficial.

- [ ] `core/interfaces/*`: Corregir imports faltantes de `Any`, `QgsGeometry`.
- [ ] `core/services/drillhole/*`: Añadir imports de `QgsFeature`.
- [ ] `core/domain/dtos.py`: Ajustar line breaks (W503).
- [ ] `core/performance_metrics.py`: Limpiar imports y variables no usadas.

---

## 🏗️ Objetivos de Mediano Plazo
### Migración a QGIS 4.x (API Agnostic)
 Preparar el terreno para la futura API de QGIS 4.x eliminando dependencias directas de PyQt5.

1. **Refactor de Imports**: Reemplazar `from PyQt5...` por `from qgis.PyQt...` en todo el proyecto.
2. **Actualización de Recursos**: Recompilar `resources.py` con directivas compatibles.
3. **CI/CD**: Añadir job para detectar regresiones de imports.

### Preview 3D Engine (Fase 1)
Implementar una vista previa 3D ligera usando `Qt3D` o `PyVista` integrado en el dock widget.

1. **Motor**: Implementar `core/engines/preview_3d_engine.py`.
2. **UI**: Integrar widget 3D en la pestaña de preview existente.
3. **Sincronización**: Vincular la cámara 3D con el perfil 2D seleccionado.

---

## 🚀 Comando de Inicio
Para comenzar la siguiente sesión de trabajo:

> `/inicia-sesion`

Este comando sincronizará el entorno y cargará el contexto actualizado.
