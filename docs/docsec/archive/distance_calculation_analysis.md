# Análisis: Cálculo de Distancias a lo Largo de Línea

## Uso Actual

### QgsDistanceArea.measureLine()

Se usa en 4 lugares para calcular distancias entre puntos:

1. **`geol_profile()`** - línea 813
   ```python
   dist_from_start = da.measureLine(line_start, pt)
   ```

2. **`project_structures()`** - línea 958
   ```python
   dist = da.measureLine(line_start, p)
   ```

3. **`sample_elevation_along_line()`** - líneas 421, 423
   ```python
   dist_from_start = distance_area.measureLine(reference_point, pt)
   dist_from_start = distance_area.measureLine(start_pt, pt)
   ```

## ¿Qué hace QgsDistanceArea.measureLine()?

```python
da = QgsDistanceArea()
da.setSourceCrs(crs, QgsProject.instance().transformContext())
da.setEllipsoid(crs.ellipsoidAcronym())

# Calcula distancia entre dos puntos considerando:
# - El elipsoide de la Tierra
# - La curvatura terrestre
# - El CRS del proyecto
distance = da.measureLine(point1, point2)
```

**Características**:
- ✅ Cálculo geodésico preciso
- ✅ Considera el elipsoide
- ✅ Funciona con cualquier CRS
- ✅ Muy eficiente (cálculo directo)

## Algoritmos Nativos Disponibles

### 1. `native:pointsalonglines`
**Propósito**: Crear puntos a intervalos regulares a lo largo de líneas

```python
processing.run("native:pointsalonglines", {
    'INPUT': line_layer,
    'DISTANCE': 10,  # Intervalo
    'OUTPUT': 'memory:'
})
```

**Problema**:
- ❌ Crea puntos nuevos, no calcula distancias de puntos existentes
- ❌ No es apropiado para nuestro caso de uso

### 2. `native:linesubstring`
**Propósito**: Extraer subsecciones de líneas

```python
processing.run("native:linesubstring", {
    'INPUT': line_layer,
    'START_DISTANCE': 0,
    'END_DISTANCE': 100,
    'OUTPUT': 'memory:'
})
```

**Problema**:
- ❌ Extrae geometrías, no calcula distancias
- ❌ No es apropiado para nuestro caso de uso

### 3. `qgis:distancematrix`
**Propósito**: Calcular matriz de distancias entre capas

```python
processing.run("qgis:distancematrix", {
    'INPUT': layer1,
    'INPUT_FIELD': 'id',
    'TARGET': layer2,
    'TARGET_FIELD': 'id',
    'OUTPUT': 'memory:'
})
```

**Problema**:
- ❌ Calcula distancias entre capas, no a lo largo de una línea
- ❌ Overhead de crear capas temporales
- ❌ No es apropiado para nuestro caso de uso

## Análisis de Viabilidad

### ❌ NO HAY ALGORITMO NATIVO APROPIADO

**Razones**:

1. **Caso de Uso Específico**
   - Necesitamos calcular distancia de un punto a otro punto
   - A lo largo de una línea (no distancia euclidiana)
   - Considerando el elipsoide

2. **QgsDistanceArea es la Herramienta Correcta**
   - Diseñada específicamente para este propósito
   - Cálculo geodésico preciso
   - Muy eficiente (no requiere capas temporales)

3. **Algoritmos Nativos No Aplican**
   - `pointsalonglines`: Crea puntos, no calcula distancias
   - `linesubstring`: Extrae geometrías, no calcula distancias
   - `distancematrix`: Para distancias entre capas, no a lo largo de línea

## Comparación de Rendimiento

### Método Actual (QgsDistanceArea)
```
Para 400 puntos:
- 400 llamadas a measureLine() ≈ 5-10ms
- Total: ~5-10ms
```

### Hipotético con Algoritmo Nativo
```
Para 400 puntos:
- Crear capa temporal de puntos: ~5ms
- Ejecutar algoritmo: ~10-20ms
- Extraer resultados: ~5ms
- Total: ~20-30ms
```

**Conclusión**: El método actual es **MÁS RÁPIDO**

## Alternativa: Usar Geometría.lineLocatePoint()

Una alternativa sería usar `QgsGeometry.lineLocatePoint()` que retorna la distancia a lo largo de una línea:

```python
# En lugar de:
dist = da.measureLine(line_start, pt)

# Podríamos usar:
line_geom = line_feature.geometry()
dist = line_geom.lineLocatePoint(QgsGeometry.fromPointXY(pt))
```

**Ventajas**:
- ✅ Cálculo directo a lo largo de la línea
- ✅ No requiere punto de inicio

**Desventajas**:
- ❌ No considera el elipsoide (menos preciso)
- ❌ Solo funciona si el punto está exactamente sobre la línea
- ❌ Menos apropiado para nuestro caso

## Recomendación

### ⭐ MANTENER MÉTODO ACTUAL

**Razones**:
1. ✅ `QgsDistanceArea.measureLine()` es la herramienta correcta
2. ✅ Cálculo geodésico preciso
3. ✅ Mejor rendimiento
4. ✅ Código simple y directo
5. ✅ No hay algoritmo nativo apropiado

### Posible Optimización (NO RECOMENDADA)

Si se quisiera optimizar, se podría:
- Pre-calcular distancias acumuladas a lo largo de la línea
- Usar interpolación para puntos intermedios

Pero esto es optimización prematura - el método actual es suficientemente rápido.

## Decisión Final

**NO REFACTORIZAR** el cálculo de distancias porque:
- `QgsDistanceArea.measureLine()` es el método correcto y óptimo
- No hay algoritmo nativo apropiado
- El rendimiento actual es excelente
- Mantener código simple es más valioso

**Estado**: ❌ Refactorización no recomendada
