# Siguientes Pasos - SecInterp

## Estado Actual
- **Refactorización Core**: `GeologyService` y `DrillholeService` desacoplados de la API de QGIS mediante DTOs (WKT/dicts).
- **Integración UI**: `PreviewManager` simplificado delegando preparación de datos a servicios.
- **Calidad**: 359 tests OK en Docker. Implementado `MockQgsPointXY.azimuth`.

## Tareas Pendientes
- [ ] Implementar suite de tests de integración 3D específica (Objetivo 3 del plan v2.8.0).
- [ ] Revisar cobertura de `ParallelGeologyService` (ahora `GeologyGenerationTask`) para asegurar que todos los casos edge estén cubiertos en background.
- [ ] Optimizar el guardado de interpretaciones si el volumen de datos aumenta significativamente.

## Comandos Útiles
- **Sincronización**: `uv sync`
- **Tests**: `make docker-test`
- **Análisis**: `uv run ai-ctx analyze --path .`
