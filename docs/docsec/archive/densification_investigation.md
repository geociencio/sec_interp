# Análisis: Problema de Densificación de Líneas

## Contexto

La densificación con `native:densifygeometriesgivenaninterval` funciona en algunos casos pero no en otros.

## Casos de Uso

### ✅ Caso 1: Perfil Topográfico (FUNCIONA)
```python
# En topographic_profile()
geom = line_feat.geometry()  # LineString simple de capa vectorial
points = scu.sample_elevation_along_line(geom, raster_lyr, band_number, da)
# Dentro de sample_elevation_along_line():
densified_geom = densify_line_by_interval(geometry, interval)  # ✓ Funciona
```

**Características**:
- Geometría: `LineString` simple
- Fuente: Capa vectorial del usuario
- CRS: Heredado de la capa
- Resultado: Funciona correctamente

### ❌ Caso 2: Perfil Geológico (NO FUNCIONÓ)
```python
# En geol_profile()
intersection_layer = result["OUTPUT"]  # Resultado de native:intersection
for feature in intersection_layer.getFeatures():
    geom = feature.geometry()  # MultiLineString
    densified_geom = densify_line_by_interval(geom, interval)  # ✗ Falló
```

**Características**:
- Geometría: `MultiLineString` (tipo 5)
- Fuente: Capa temporal en memoria (resultado de intersection)
- CRS: ¿Heredado correctamente?
- Resultado: No funcionó inicialmente

## Hipótesis del Problema

### Hipótesis 1: Tipo de Geometría ✓ CONFIRMADA
**Problema**: `densify_line_by_interval()` espera `LineString` pero recibe `MultiLineString`

**Evidencia**:
```
Intersection segment geometry type: MultiLineString (5)
```

**Solución Implementada**: Extraer partes de MultiLineString
```python
if geom.wkbType() in [QgsWkbTypes.MultiLineString, ...]:
    multi_geom = geom.asMultiPolyline()
    for part in multi_geom:
        line_geom = QgsGeometry.fromPolylineXY(part)
        geometries_to_process.append(line_geom)
```

### Hipótesis 2: CRS no Preservado ❓ POSIBLE
**Problema**: La capa temporal en `densify_line_by_interval()` no tiene CRS definido

**Código Actual**:
```python
temp_layer = QgsVectorLayer("LineString", "temp_densify", "memory")
```

**Problema Potencial**: No se establece el CRS de la geometría original

**Posible Solución**:
```python
temp_layer = QgsVectorLayer("LineString", "temp_densify", "memory")
temp_layer.setCrs(source_crs)  # ← Falta esto
```

### Hipótesis 3: Geometrías Inválidas ❓ NO VERIFICADA
**Problema**: Las geometrías de intersección podrían tener problemas de validez

**Verificación Necesaria**:
```python
if not geom.isGeosValid():
    geom = geom.makeValid()
```

## Solución Actual

Por ahora, se usa **interpolación manual** en lugar de densificación para el perfil geológico:

```python
# Método manual (funciona siempre)
dist_step = scu.calculate_step_size(process_geom, raster_lyr)
length = process_geom.length()
current_dist = 0.0

while current_dist <= length:
    pt = process_geom.interpolate(current_dist).asPoint()
    # ... muestrear elevación
    current_dist += dist_step
```

**Ventajas**:
- ✅ Funciona con cualquier tipo de geometría
- ✅ No depende de algoritmos nativos
- ✅ Código probado y estable

**Desventajas**:
- ❌ Menos eficiente que densificación nativa
- ❌ Código más complejo

## Recomendaciones

### Opción A: Mantener Solución Actual ⭐ RECOMENDADA
- La interpolación manual funciona correctamente
- El código es estable
- La diferencia de rendimiento es mínima para perfiles geológicos

### Opción B: Investigar y Arreglar Densificación
Pasos necesarios:
1. Verificar si el problema es el CRS
2. Añadir `temp_layer.setCrs()` en `densify_line_by_interval()`
3. Probar con geometrías de intersección reales
4. Validar que funciona en todos los casos

### Opción C: Híbrido
- Usar densificación para LineString simple
- Usar interpolación manual para MultiLineString

## Conclusión

La solución actual (interpolación manual) es **válida y funcional**. La densificación nativa es una optimización que puede investigarse en el futuro, pero no es crítica para la funcionalidad del plugin.

**Estado**: ✅ Problema resuelto con método alternativo
**Prioridad de investigación adicional**: Baja
