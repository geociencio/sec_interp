# Implementación: Refactorizar Densificación de Líneas con Algoritmo Nativo

## Descripción del Problema

Actualmente, el código calcula manualmente un `step_size` y luego usa un loop con `interpolate()` para muestrear puntos a lo largo de una línea:

```python
# Calcular step_size manualmente
dist_step = scu.calculate_step_size(geom, raster_lyr)
length = geom.length()
current_dist = 0.0

# Loop manual con interpolación
while current_dist <= length:
    pt = geom.interpolate(current_dist).asPoint()  # ❌ Interpolación manual

    # Muestrear elevación
    dist_from_start = da.measureLine(line_start, pt)
    res = raster_lyr.dataProvider().identify(pt, ...).results()
    elev = res.get(band_number, 0.0)

    values.append((dist_from_start, elev, ...))
    current_dist += dist_step  # ❌ Incremento manual
```

**Limitaciones**:
- Cálculo manual de step_size complejo
- Loop manual con interpolación
- Código repetitivo en múltiples lugares
- Difícil de mantener

## Solución Propuesta

Usar `native:densifygeometriesgivenaninterval` para crear vértices a intervalos regulares, luego iterar sobre esos vértices.

**Beneficios**:
- ✅ Algoritmo nativo crea vértices automáticamente
- ✅ Código más simple (sin loop de interpolación)
- ✅ Mejor precisión (vértices exactos vs interpolación)
- ✅ Más fácil de mantener

---

## Cambios Propuestos

### 1. Crear Helper en `core/utils.py`

#### [NEW] Función `densify_line_by_interval()`

Añadir después de `filter_features_by_buffer()`:

```python
def densify_line_by_interval(
    geometry: QgsGeometry,
    interval: float,
) -> QgsGeometry:
    """Densify line geometry by adding vertices at regular intervals.

    Uses native:densifygeometriesgivenaninterval for precise vertex placement.

    Args:
        geometry: Line geometry to densify
        interval: Distance between vertices in geometry units

    Returns:
        QgsGeometry: Densified line geometry with vertices at regular intervals

    Raises:
        ValueError: If geometry is invalid or not a line
        RuntimeError: If densification algorithm fails

    Example:
        >>> line_geom = line_layer.geometry()
        >>> interval = raster_layer.rasterUnitsPerPixelX()
        >>> densified = densify_line_by_interval(line_geom, interval)
        >>> points = densified.asPolyline()  # Now has vertices at regular intervals
    """
    from qgis import processing
    from qgis.core import QgsProcessingFeedback, QgsVectorLayer, QgsFeature

    if not geometry or geometry.isNull():
        raise ValueError("Input geometry is null or invalid")

    if geometry.type() != QgsWkbTypes.LineGeometry:
        raise ValueError("Geometry must be a LineString")

    try:
        # Create temporary layer with geometry
        temp_layer = QgsVectorLayer("LineString", "temp_densify", "memory")
        temp_feat = QgsFeature()
        temp_feat.setGeometry(geometry)
        temp_layer.dataProvider().addFeatures([temp_feat])

        # Create feedback for logging
        feedback = QgsProcessingFeedback()

        logger.debug(f"Densifying line with interval={interval:.2f}")

        # Run densification algorithm
        result = processing.run(
            "native:densifygeometriesgivenaninterval",
            {
                "INPUT": temp_layer,
                "INTERVAL": interval,
                "OUTPUT": "memory:",
            },
            feedback=feedback,
        )

        # Extract densified geometry
        densified_layer = result["OUTPUT"]
        if densified_layer.featureCount() == 0:
            raise ValueError("Densification produced no features")

        densified_feat = next(densified_layer.getFeatures())
        densified_geom = densified_feat.geometry()

        if not densified_geom or densified_geom.isNull():
            raise ValueError("Densified geometry is invalid")

        # Get vertex count for logging
        if densified_geom.isMultipart():
            vertex_count = sum(len(part) for part in densified_geom.asMultiPolyline())
        else:
            vertex_count = len(densified_geom.asPolyline())

        logger.debug(f"✓ Densification complete: {vertex_count} vertices")
        return densified_geom

    except Exception as e:
        error_msg = f"Failed to densify line: {str(e)}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e
```

---

### 2. Refactorizar `geol_profile()`

#### [MODIFY] [`core/algorithms.py:756-780`](file:///home/jmbernales/qgispluginsdev/sec_interp/core/algorithms.py#L756-L780)

**Antes** (loop manual):
```python
# Sample elevation along intersection segment
dist_step = scu.calculate_step_size(geom, raster_lyr)
length = geom.length()
current_dist = 0.0

while current_dist <= length:
    pt = geom.interpolate(current_dist).asPoint()

    dist_from_start = da.measureLine(line_start, pt)

    # Get elevation
    res = raster_lyr.dataProvider().identify(pt, ...).results()
    elev = res.get(band_number, 0.0)

    glg_val = feature[glg_field]
    values.append((round(dist_from_start, 1), round(elev, 1), glg_val))

    current_dist += dist_step
```

**Después** (densificación nativa):
```python
# Densify line to create vertices at regular intervals
interval = raster_lyr.rasterUnitsPerPixelX()
try:
    densified_geom = scu.densify_line_by_interval(geom, interval)
except (ValueError, RuntimeError) as e:
    logger.warning(f"Densification failed, using original geometry: {e}")
    densified_geom = geom

# Sample elevation at each vertex
if densified_geom.isMultipart():
    points = densified_geom.asMultiPolyline()[0]
else:
    points = densified_geom.asPolyline()

for pt in points:
    dist_from_start = da.measureLine(line_start, pt)

    # Get elevation
    res = raster_lyr.dataProvider().identify(pt, ...).results()
    elev = res.get(band_number, 0.0)

    glg_val = feature[glg_field]
    values.append((round(dist_from_start, 1), round(elev, 1), glg_val))
```

**Cambios clave**:
1. ✅ Eliminado `calculate_step_size()`
2. ✅ Eliminado loop `while current_dist <= length`
3. ✅ Eliminado `geom.interpolate(current_dist)`
4. ✅ Usa vértices directamente de geometría densificada
5. ✅ Código más simple y directo

---

### 3. Refactorizar `sample_elevation_along_line()`

#### [MODIFY] [`core/utils.py:293-333`](file:///home/jmbernales/qgispluginsdev/sec_interp/core/utils.py#L293-L333)

**Antes**:
```python
def sample_elevation_along_line(geometry, raster_layer, band_number, distance_area, reference_point=None):
    dist_step = calculate_step_size(geometry, raster_layer)
    length = geometry.length()
    current_dist = 0.0
    points = []

    start_pt = reference_point if reference_point else geometry.interpolate(0).asPoint()

    while current_dist <= length:
        pt = geometry.interpolate(current_dist).asPoint()
        # ...
        current_dist += dist_step

    return points
```

**Después**:
```python
def sample_elevation_along_line(geometry, raster_layer, band_number, distance_area, reference_point=None):
    # Densify line at raster resolution
    interval = raster_layer.rasterUnitsPerPixelX()
    try:
        densified_geom = densify_line_by_interval(geometry, interval)
    except (ValueError, RuntimeError):
        densified_geom = geometry

    # Get vertices
    if densified_geom.isMultipart():
        vertices = densified_geom.asMultiPolyline()[0]
    else:
        vertices = densified_geom.asPolyline()

    points = []
    start_pt = reference_point if reference_point else vertices[0]

    for pt in vertices:
        dist_from_start = distance_area.measureLine(start_pt, pt)
        val, ok = raster_layer.dataProvider().sample(pt, band_number)
        elev = val if ok else 0.0
        points.append(QgsPointXY(dist_from_start, elev))

    return points
```

---

## Consideraciones Importantes

### 1. Intervalo de Densificación

**Antes**: Calculado con fórmula compleja basada en slope
**Después**: Usar resolución del raster directamente

```python
interval = raster_lyr.rasterUnitsPerPixelX()
```

**Ventaja**: Más simple y directo, garantiza al menos 1 muestra por píxel.

### 2. Manejo de Multi-part Geometries

El algoritmo nativo maneja multi-part automáticamente, pero debemos extraer los vértices correctamente:

```python
if densified_geom.isMultipart():
    points = densified_geom.asMultiPolyline()[0]  # Primera parte
else:
    points = densified_geom.asPolyline()
```

### 3. Fallback en Caso de Error

Si la densificación falla, usar geometría original:

```python
try:
    densified_geom = densify_line_by_interval(geom, interval)
except (ValueError, RuntimeError) as e:
    logger.warning(f"Densification failed: {e}")
    densified_geom = geom  # Usar original
```

---

## Beneficios

### 1. Código Más Simple
- ✅ Eliminado cálculo complejo de step_size
- ✅ Eliminado loop manual con interpolación
- ✅ Menos líneas de código

### 2. Mejor Precisión
- ✅ Vértices exactos vs interpolación aproximada
- ✅ Garantiza muestreo uniforme
- ✅ Sin errores de acumulación en el loop

### 3. Más Mantenible
- ✅ Lógica centralizada en helper
- ✅ Fácil de entender
- ✅ Menos código duplicado

---

## Plan de Verificación

### Tests Automatizados

Añadir en `tests/test_utils.py`:

```python
class TestLineDensification:
    """Tests for densify_line_by_interval."""

    @patch("core.utils.processing")
    def test_densify_line_basic(self, mock_processing):
        """Test basic line densification."""
        # Mock line geometry
        mock_geom = Mock(spec=QgsGeometry)
        mock_geom.isNull.return_value = False
        mock_geom.type.return_value = QgsWkbTypes.LineGeometry

        # Mock densified result
        mock_densified_geom = Mock(spec=QgsGeometry)
        mock_densified_geom.isNull.return_value = False
        mock_densified_geom.isMultipart.return_value = False
        mock_densified_geom.asPolyline.return_value = [
            QgsPointXY(0, 0),
            QgsPointXY(10, 0),
            QgsPointXY(20, 0),
        ]

        mock_feat = Mock()
        mock_feat.geometry.return_value = mock_densified_geom

        mock_layer = Mock()
        mock_layer.featureCount.return_value = 1
        mock_layer.getFeatures.return_value = [mock_feat]

        mock_processing.run.return_value = {"OUTPUT": mock_layer}

        # Call function
        result = scu.densify_line_by_interval(mock_geom, 10.0)

        # Verify
        assert result == mock_densified_geom
        mock_processing.run.assert_called_once()
        assert mock_processing.run.call_args[0][0] == "native:densifygeometriesgivenaninterval"
```

### Verificación Manual

1. **Test con perfil topográfico**
   - Generar perfil con DEM
   - Comparar con versión anterior
   - Verificar que puntos son similares

2. **Test con perfil geológico**
   - Generar perfil geológico
   - Verificar número de puntos
   - Comparar elevaciones

3. **Test con diferentes resoluciones**
   - DEM de 10m
   - DEM de 30m
   - Verificar que densificación se ajusta

---

## Riesgos y Mitigaciones

### Riesgo 1: Cambio en Número de Puntos
**Mitigación**: El número puede variar ligeramente, pero la precisión mejora

### Riesgo 2: Rendimiento
**Mitigación**: Densificación nativa es eficiente, similar o mejor que loop manual

### Riesgo 3: Geometrías Muy Largas
**Mitigación**: Algoritmo nativo maneja eficientemente

---

## Decisión sobre `calculate_step_size()`

**Opción 1**: Deprecar pero mantener para compatibilidad
**Opción 2**: Eliminar completamente

**Recomendación**: **Mantener pero marcar como deprecated** porque:
- Podría usarse en código externo
- Fácil de eliminar después si no se usa
- Añadir docstring de deprecación

```python
def calculate_step_size(geom, raster_lyr):
    """Calculate step size based on slope and raster resolution.

    .. deprecated::
        Use densify_line_by_interval() instead for better precision.

    This function is kept for backward compatibility but may be removed
    in future versions.
    """
    # ... código existente
```

---

## Recomendación

**Proceder con la implementación** por las siguientes razones:

1. ✅ Código significativamente más simple
2. ✅ Mejor precisión con vértices exactos
3. ✅ Elimina código duplicado
4. ✅ Usa algoritmo nativo optimizado
5. ✅ Fácil de revertir si es necesario

**Riesgo**: Mínimo - solo cambia cómo se crean los puntos de muestreo, la lógica de muestreo permanece igual.
