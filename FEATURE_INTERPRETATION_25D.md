# Feature Branch: Interpretación 2.5D

**Branch**: `feature/interpretation-25d`  
**Target Version**: v2.5.0  
**Created**: 2025-12-25

## Objetivo

Implementar funcionalidad para dibujar polígonos de interpretación sobre el perfil 2D y exportarlos como geometrías 2.5D (PolygonM) con coordenadas reales proyectadas sobre la línea de sección.

## Documentación

- **Plan de Implementación**: Ver artifacts en `.gemini/antigravity/brain/`
  - `interpretation_25d_plan.md` - Plan detallado de arquitectura
  - `task_interpretation_25d.md` - Checklist de tareas

## Componentes Principales

### Nuevos Módulos
- `core/services/interpretation_service.py` - Servicio de proyección 2D→2.5D
- `gui/tools/interpretation_tool.py` - Herramienta de dibujo
- `gui/interpretation_manager.py` - Panel de gestión
- `exporters/interpretation_exporter.py` - Exportación PolygonM

### Modificaciones
- `core/types.py` - Nuevos dataclasses
- `gui/main_dialog.py` - Integración de panel
- `core/controller.py` - Integración de servicio

## Workflow de Desarrollo

1. **Phase 1**: Modelo de datos (tipos, excepciones)
2. **Phase 2**: Servicio de proyección
3. **Phase 3**: Herramienta de dibujo
4. **Phase 4**: Exportación
5. **Phase 5**: UI y gestión
6. **Phase 6-10**: Integración, testing, documentación

## Estado Actual

- [x] Rama creada
- [x] Plan de implementación documentado
- [ ] Desarrollo en progreso

## Merge Strategy

Esta rama se mergeará a `main` cuando:
1. Todas las fases estén completas
2. Tests pasen exitosamente
3. Documentación esté actualizada
4. Code review aprobado

**NO** se mergeará a v2.4.0 para mantener estabilidad del release actual.
