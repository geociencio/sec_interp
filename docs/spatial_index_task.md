# Task: Optimización con Índice Espacial

## Objetivo
Implementar `QgsSpatialIndex` para filtrado espacial en `filter_features_by_buffer`, reemplazando `native:extractbylocation`.

## Motivación
- Solicitud explícita del usuario: "Consider using spatial indexing (QgsSpatialIndex)"
- `native:extractbylocation` crea una capa en memoria intermedia (copia datos)
- `QgsSpatialIndex` permite iterar sobre la capa original (zero copy)
- Mayor rendimiento para datasets grandes de puntos

## Tareas

### Fase 1: Implementación en Utils
- [x] Diseñar nueva función `filter_features_using_index`
- [x] Implementar usando `QgsSpatialIndex`
- [x] Retornar generador/lista en lugar de capa

### Fase 2: Integración
- [x] Modificar `project_structures` en `algorithms.py`
- [x] Adaptar código para manejar lista/generador
- [x] Eliminar dependencias de `QgsVectorLayer` intermedio

### Fase 3: Verificación
- [x] Verificar que el filtrado funciona igual
- [x] Confirmar mejora de rendimiento (teórica)

## Notas
- `QgsSpatialIndex` acelera consultas espaciales (R-tree)
- Se combinará index.intersects(bbox) + geometry.intersects(exact)
