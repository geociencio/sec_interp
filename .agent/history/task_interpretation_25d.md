# Task: Interpretación 2.5D - v2.5.0

## Session Overview
**Date**: 2025-12-25
**Focus**: Implementación de Polígonos de Interpretación 2.5D
**Branch**: `feature/interpretation-25d`
**Target Version**: v2.5.0

## Phase 1: Modelo de Datos y Tipos
- [ ] Agregar `InterpretationPolygon` dataclass a `core/types.py`
- [ ] Agregar `InterpretationPolygon25D` dataclass a `core/types.py`
- [ ] Definir enums para tipos de interpretación
- [ ] Crear excepciones específicas (`InterpretationError`, `ProjectionError`)

## Phase 2: Servicio de Proyección
- [ ] Crear `core/services/interpretation_service.py`
- [ ] Implementar `project_2d_to_25d()` - proyección de polígono 2D a 2.5D
- [ ] Implementar `interpolate_point_on_line()` - cálculo de coordenadas X,Y
- [ ] Implementar `create_25d_geometry()` - creación de geometría PolygonM
- [ ] Implementar `calculate_m_coordinate()` - manejo de exageración vertical
- [ ] Validación de geometrías (cerradas, sin auto-intersección)

## Phase 3: Herramienta de Dibujo
- [ ] Crear `gui/tools/interpretation_tool.py`
- [ ] Implementar `InterpretationTool` (QgsMapTool)
- [ ] Modo dibujo: captura de vértices con clicks
- [ ] Modo edición: mover/agregar/eliminar vértices
- [ ] Preview en tiempo real del polígono
- [ ] Diálogo de atributos al finalizar polígono

## Phase 4: Exportación
- [ ] Crear `exporters/interpretation_exporter.py`
- [ ] Implementar `Interpretation25DExporter`
- [ ] Exportación a Shapefile PolygonM
- [ ] Configuración de campos de atributos
- [ ] Manejo correcto de CRS

## Phase 5: Gestión y UI
- [ ] Crear `gui/interpretation_manager.py`
- [ ] Panel de lista de polígonos
- [ ] Botones: Nuevo, Editar, Eliminar, Exportar
- [ ] Campos de atributos editables
- [ ] Selector de color por polígono
- [ ] Checkbox de visibilidad

## Phase 6: Integración
- [ ] Agregar botón "Interpretación" en preview toolbar
- [ ] Integrar `InterpretationService` en `ProfileController`
- [ ] Conectar señales entre herramienta y manager
- [ ] Renderizar polígonos en capa separada del preview

## Phase 7: Persistencia
- [ ] Implementar guardado a JSON (`interpretations.json`)
- [ ] Implementar carga desde JSON
- [ ] Auto-guardar al cerrar diálogo
- [ ] Validación de versión de formato

## Phase 8: Testing
- [ ] Unit tests para `InterpretationService`
- [ ] Unit tests para `Interpretation25DExporter`
- [ ] Integration test: flujo completo dibujo → exportación
- [ ] Validación con datos reales

## Phase 9: Documentación
- [ ] Docstrings en todos los métodos nuevos
- [ ] Actualizar `USER_GUIDE.md` con nueva funcionalidad
- [ ] Screenshots de la herramienta en uso
- [ ] Ejemplo de uso en `examples/`

## Phase 10: Release
- [ ] Actualizar `CHANGELOG.md` con v2.5.0
- [ ] Actualizar `metadata.txt` version y changelog
- [ ] Merge a `main`
- [ ] Tag v2.5.0
- [ ] Deploy a repositorio QGIS
