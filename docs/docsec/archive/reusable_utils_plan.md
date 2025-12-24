# Plan: Crear Funciones de Utilidad Reusables

## Patrones Identificados

### 1. Creación de Memory Layers (4 ocurrencias)
**Patrón repetitivo:**
```python
temp_layer = QgsVectorLayer(geom_type, "temp_name", "memory")
temp_layer.setCrs(crs)
temp_feat = QgsFeature()
temp_feat.setGeometry(geometry)
temp_layer.dataProvider().addFeatures([temp_feat])
```

**Propuesta:** Crear `create_memory_layer(geometry, crs, name="temp")`

---

### 2. Extracción de Vértices de Líneas (10+ ocurrencias)
**Patrón repetitivo:**
```python
if geom.isMultipart():
    vertices = geom.asMultiPolyline()[0]
else:
    vertices = geom.asPolyline()
```

**Propuesta:** Crear `get_line_vertices(geometry) -> list[QgsPointXY]`

---

### 3. Obtención del Punto Inicial de Línea (5 ocurrencias)
**Patrón repetitivo:**
```python
if line_geom.isMultipart():
    line_start = line_geom.asMultiPolyline()[0][0]
else:
    line_start = line_geom.asPolyline()[0]
```

**Ya existe:** `get_line_start_point()` pero se repite el código inline

**Acción:** Usar consistentemente la función existente

---

### 4. Ejecución de Algoritmos de Processing (5 ocurrencias)
**Patrón repetitivo:**
```python
from qgis import processing
from qgis.core import QgsProcessingFeedback

feedback = QgsProcessingFeedback()
result = processing.run("algorithm_name", {...}, feedback=feedback)
```

**Propuesta:** Crear `run_processing_algorithm(algorithm, params, silent=True)`

---

## Nuevas Funciones Propuestas

### En `core/utils/geometry.py`

```python
def create_memory_layer(
    geometry: QgsGeometry,
    crs: QgsCoordinateReferenceSystem,
    name: str = "temp",
    fields: QgsFields = None
) -> QgsVectorLayer:
    """Create a temporary memory layer with a single geometry feature.
    
    Args:
        geometry: Geometry to add to the layer
        crs: Coordinate reference system
        name: Layer name (default: "temp")
        fields: Optional fields definition
        
    Returns:
        QgsVectorLayer: Memory layer with the geometry
    """
```

```python
def get_line_vertices(geometry: QgsGeometry) -> list[QgsPointXY]:
    """Extract vertices from a line geometry (handles multipart).
    
    Args:
        geometry: Line geometry (LineString or MultiLineString)
        
    Returns:
        list[QgsPointXY]: List of vertices from the first part
        
    Raises:
        ValueError: If geometry is not a line
    """
```

```python
def run_processing_algorithm(
    algorithm: str,
    parameters: dict,
    silent: bool = True
) -> dict:
    """Run a QGIS processing algorithm with consistent error handling.
    
    Args:
        algorithm: Algorithm name (e.g., "native:buffer")
        parameters: Algorithm parameters
        silent: If True, suppress feedback output
        
    Returns:
        dict: Algorithm result
        
    Raises:
        RuntimeError: If algorithm fails
    """
```

---

## Refactorizaciones a Realizar

### Archivos a Actualizar

1. **core/utils/geometry.py**
   - Agregar `create_memory_layer()`
   - Agregar `get_line_vertices()`
   - Agregar `run_processing_algorithm()`
   - Refactorizar `create_buffer_geometry()` para usar helpers
   - Refactorizar `densify_line_by_interval()` para usar helpers

2. **core/utils/sampling.py**
   - Usar `get_line_vertices()` en `sample_elevation_along_line()`

3. **core/services/geology_service.py**
   - Usar `get_line_start_point()` consistentemente
   - Usar `run_processing_algorithm()` para intersection

4. **core/services/structure_service.py**
   - Usar `get_line_start_point()` consistentemente

---

## Beneficios

✅ **Menos código duplicado**: Reducir ~100 líneas de código repetitivo  
✅ **Más consistencia**: Mismo comportamiento en todos los lugares  
✅ **Mejor testabilidad**: Funciones helper pueden testearse independientemente  
✅ **Más mantenible**: Cambios en un solo lugar  
✅ **Mejor documentación**: Funciones con docstrings claros  

---

## Implementación

1. Crear nuevas funciones helper en `geometry.py`
2. Refactorizar código existente para usar helpers
3. Verificar que todo compile
4. Probar funcionalidad en QGIS
5. Commit con mensaje descriptivo
