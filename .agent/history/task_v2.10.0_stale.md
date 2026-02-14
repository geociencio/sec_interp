# Tareas - Fase v2.10.0 (Calidad y QGIS 4.x)

## Objetivo 1: Deuda Técnica Crítica (QGIS 4.x) <!-- id: 1 -->
- [ ] Eliminar importación directa `PyQt5` en `resources.py` <!-- id: 2 -->
- [ ] Verificar compatibilidad con script `scripts/security_scan.py` <!-- id: 3 -->

## Objetivo 2: Refactorización ExportService (Reducción CC) <!-- id: 4 -->
- [ ] Analizar complejidad actual de `export_service.py` <!-- id: 5 -->
- [ ] Extraer lógica 3D a `exporters/drillhole_3d_exporter.py` <!-- id: 6 -->
- [ ] Implementar patrón Strategy para formatos vectoriales <!-- id: 7 -->

## Objetivo 3: Optimizaciones y Calidad <!-- id: 8 -->
- [ ] Aplicar optimizaciones detectadas por `ai-ctx` (24 items) <!-- id: 9 -->
- [ ] Mejorar cobertura de docstrings en `core/` (Meta: 85%) <!-- id: 10 -->
- [ ] Estandarizar Type Hints en utilerías <!-- id: 11 -->

## Cierre de Fase <!-- id: 12 -->
- [ ] Ejecutar validación final (`make pre-release`) <!-- id: 13 -->
- [ ] Actualizar documentación y CHANGELOG <!-- id: 14 -->
