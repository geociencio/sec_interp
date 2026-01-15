# Plan de Implementación: Exportación de Polígonos 2.5D

## Objetivo
Permitir al usuario dibujar polígonos de interpretación sobre el perfil 2D y exportarlos como geometrías 2.5D (con coordenada M) proyectadas sobre la línea de sección original.

## Contexto Técnico

### Flujo de Datos Actual
1. **Entrada**: Línea de sección 3D (coordenadas X, Y, Z)
2. **Procesamiento**: Generación de perfil 2D (distancia, elevación)
3. **Visualización**: Preview en canvas 2D
4. **Exportación**: Shapefiles 2D de datos procesados

### Flujo Propuesto (2.5D)
1. Usuario dibuja polígonos de interpretación en el preview 2D
2. Sistema captura vértices del polígono (distancia, elevación)
3. Sistema proyecta cada vértice sobre la línea de sección 3D original
4. Sistema crea geometría 2.5D: (X, Y, M) donde M = elevación
5. Exporta como Shapefile con geometría PointM/LineStringM/PolygonM

## Arquitectura Propuesta

### Nuevos Componentes

#### 1. `InterpretationTool` (GUI)
**Ubicación**: `gui/tools/interpretation_tool.py`

**Responsabilidades**:
- Herramienta de dibujo de polígonos en el preview canvas
- Captura de vértices en coordenadas 2D (distancia, elevación)
- Gestión de múltiples polígonos de interpretación
- Atributos por polígono (nombre, tipo, descripción, color)

**Funcionalidades**:
```python
class InterpretationTool(QgsMapTool):
    - start_polygon(): Iniciar nuevo polígono
    - add_vertex(point): Agregar vértice
    - finish_polygon(): Finalizar polígono actual
    - edit_polygon(polygon_id): Editar polígono existente
    - delete_polygon(polygon_id): Eliminar polígono
    - get_all_polygons(): Obtener todos los polígonos
```

#### 2. `InterpretationService` (Core)
**Ubicación**: `core/services/interpretation_service.py`

**Responsabilidades**:
- Proyección de vértices 2D a coordenadas 3D sobre la línea
- Cálculo de coordenadas (X, Y) para cada distancia
- Asignación de M = elevación
- Validación de geometrías

**Métodos Clave**:
```python
class InterpretationService:
    def project_2d_to_25d(
        self,
        polygon_2d: list[tuple[float, float]],  # (distancia, elevación)
        section_line: QgsGeometry,
        line_start: QgsPointXY
    ) -> QgsGeometry:
        """Proyecta polígono 2D a geometría 2.5D."""

    def interpolate_point_on_line(
        self,
        distance: float,
        section_line: QgsGeometry,
        line_start: QgsPointXY
    ) -> QgsPointXY:
        """Calcula coordenadas X,Y para una distancia dada."""

    def create_25d_geometry(
        self,
        points_3d: list[tuple[float, float, float]],  # (X, Y, M)
        geom_type: str  # "Point", "LineString", "Polygon"
    ) -> QgsGeometry:
        """Crea geometría 2.5D con coordenada M."""
```

#### 3. `Interpretation25DExporter` (Exporters)
**Ubicación**: `exporters/interpretation_exporter.py`

**Responsabilidades**:
- Exportación de polígonos 2.5D a Shapefile
- Gestión de atributos de interpretación
- Configuración de CRS correcto

**Estructura de Atributos**:
```python
INTERPRETATION_FIELDS = {
    "id": int,
    "name": str,
    "type": str,  # "lithology", "structure", "alteration", etc.
    "description": str,
    "color": str,  # Hex color
    "created_at": datetime,
    "author": str
}
```

#### 4. `InterpretationManager` (GUI)
**Ubicación**: `gui/interpretation_manager.py`

**Responsabilidades**:
- Widget de gestión de polígonos de interpretación
- Lista de polígonos con preview
- Edición de atributos
- Importación/exportación de interpretaciones

---

## Implementación Detallada

### Fase 1: Modelo de Datos

#### 1.1 Dataclass para Interpretación
**Archivo**: `core/types.py`

```python
@dataclass
class InterpretationPolygon:
    """Polígono de interpretación 2D."""
    id: str
    name: str
    type: str
    vertices_2d: list[tuple[float, float]]  # (distancia, elevación)
    attributes: dict[str, Any]
    color: str
    created_at: datetime

@dataclass
class InterpretationPolygon25D:
    """Polígono de interpretación proyectado a 2.5D."""
    id: str
    name: str
    type: str
    geometry: QgsGeometry  # PolygonM
    attributes: dict[str, Any]
    crs: QgsCoordinateReferenceSystem
```

### Fase 2: Servicio de Proyección

#### 2.1 Algoritmo de Proyección
**Archivo**: `core/services/interpretation_service.py`

**Algoritmo**:
1. Para cada vértice (distancia, elevación) del polígono 2D:
   - Usar `QgsGeometry.interpolate(distance)` sobre la línea de sección
   - Obtener punto interpolado (X, Y)
   - Crear punto 2.5D: (X, Y, M=elevación)
2. Construir geometría PolygonM con los puntos proyectados
3. Validar geometría (no auto-intersección, cerrada)

**Consideraciones Especiales**:
- Manejar líneas de sección multipart
- Validar que distancia esté dentro del rango de la línea
- Interpolar correctamente en curvas
- Mantener orientación del polígono (clockwise/counterclockwise)

#### 2.2 Cálculo de Coordenadas M
```python
def calculate_m_coordinate(elevation: float, vertical_exag: float = 1.0) -> float:
    """
    Calcula coordenada M considerando exageración vertical.

    Args:
        elevation: Elevación real del punto
        vertical_exag: Factor de exageración vertical usado en el perfil

    Returns:
        Valor M (elevación sin exageración)
    """
    return elevation / vertical_exag
```

### Fase 3: Herramienta de Dibujo

#### 3.1 InterpretationTool
**Archivo**: `gui/tools/interpretation_tool.py`

**Funcionalidades**:
- Modo dibujo: Click para agregar vértices
- Modo edición: Mover vértices existentes
- Modo selección: Seleccionar polígonos
- Snap a geometrías existentes (topografía, geología)
- Preview en tiempo real del polígono

**Integración con Preview Canvas**:
- Agregar botón "Interpretación" en la toolbar del preview
- Activar/desactivar herramienta
- Renderizar polígonos de interpretación en capa separada

### Fase 4: Exportación

#### 4.1 Interpretation25DExporter
**Archivo**: `exporters/interpretation_exporter.py`

```python
class Interpretation25DExporter(BaseExporter):
    def export(self, output_path: Path, data: dict) -> None:
        """
        Exporta polígonos de interpretación a Shapefile 2.5D.

        Args:
            output_path: Ruta del shapefile de salida
            data: {
                "polygons": list[InterpretationPolygon],
                "section_line": QgsGeometry,
                "line_start": QgsPointXY,
                "crs": QgsCoordinateReferenceSystem,
                "vertical_exag": float
            }
        """
        # 1. Crear capa PolygonM
        # 2. Proyectar cada polígono 2D a 2.5D
        # 3. Agregar features con atributos
        # 4. Guardar shapefile
```

### Fase 5: Persistencia

#### 5.1 Guardar/Cargar Interpretaciones
**Formato**: JSON sidecar file

```json
{
  "version": "1.0",
  "section_line_id": "unique_id",
  "created_at": "2025-12-25T19:00:00",
  "polygons": [
    {
      "id": "poly_001",
      "name": "Granito Alterado",
      "type": "lithology",
      "vertices_2d": [[0.0, 100.0], [50.0, 100.0], [50.0, 80.0], [0.0, 80.0]],
      "attributes": {"confidence": "high"},
      "color": "#FF5733"
    }
  ]
}
```

**Ubicación**: `{output_folder}/interpretations.json`

---

## Interfaz de Usuario

### Nuevos Elementos UI

#### 1. Botón "Interpretación" en Preview Toolbar
- Icono: Polígono con lápiz
- Tooltip: "Dibujar polígonos de interpretación"
- Activa `InterpretationTool`

#### 2. Panel de Interpretaciones
**Ubicación**: Dock widget lateral en el diálogo principal

**Contenido**:
- Lista de polígonos con miniatura
- Botones: Nuevo, Editar, Eliminar, Exportar
- Campos de atributos por polígono
- Selector de color
- Checkbox de visibilidad

#### 3. Diálogo de Exportación 2.5D
**Campos**:
- Ruta de salida
- Formato: Shapefile PolygonM
- CRS (heredado de línea de sección)
- Opción: Incluir solo polígonos seleccionados
- Opción: Aplicar exageración vertical inversa

---

## Flujo de Trabajo del Usuario

### Escenario Típico

1. **Generar Perfil**
2. **Activar Herramienta de Interpretación**
3. **Dibujar Polígono**
4. **Editar Polígono** (Opcional)
5. **Exportar a 2.5D**
6. **Visualizar en QGIS**

---

## Consideraciones Técnicas

### Geometrías QGIS con Coordenada M

```python
# Crear punto con M
point_m = QgsPoint(x, y, m=elevation)

# Crear línea con M
line_m = QgsLineString([
    QgsPoint(x1, y1, m=m1),
    QgsPoint(x2, y2, m=m2)
])

# Crear polígono con M
ring = QgsLineString([...])  # Puntos con M
polygon_m = QgsPolygon()
polygon_m.setExteriorRing(ring)
```

### Validaciones Necesarias

1. **Distancia válida**: Vértices dentro del rango de la línea
2. **Geometría válida**: Polígono cerrado, sin auto-intersecciones
3. **CRS consistente**: Mismo CRS que la línea de sección
4. **Atributos completos**: Nombre y tipo obligatorios

## Testing

### Unit Tests
- `tests/test_interpretation_service.py`
- `tests/test_interpretation_exporter.py`

### Integration Tests
- `test_full_interpretation_workflow()`

---

## Roadmap de Implementación

### v2.5.0 - Interpretación Básica
- [ ] Modelo de datos (`InterpretationPolygon`)
- [ ] Servicio de proyección (`InterpretationService`)
- [ ] Herramienta de dibujo básica
- [ ] Exportación a Shapefile PolygonM
- [ ] Persistencia JSON

### v2.6.0 - Interpretación Avanzada
- [ ] Edición de polígonos existentes
- [ ] Panel de gestión de interpretaciones
- [ ] Importación de interpretaciones
- [ ] Snap a geometrías
- [ ] Múltiples tipos de interpretación

### v2.7.0 - Análisis 3D
- [ ] Visualización 3D de interpretaciones
- [ ] Exportación a formatos 3D (GeoPackage, GML)
- [ ] Análisis volumétrico
- [ ] Integración con QGIS 3D View

---

## Archivos a Crear/Modificar

### Nuevos Archivos
```
core/services/interpretation_service.py
core/types.py (agregar dataclasses)
gui/tools/interpretation_tool.py
gui/interpretation_manager.py
exporters/interpretation_exporter.py
tests/test_interpretation_service.py
tests/test_interpretation_exporter.py
```

### Archivos a Modificar
```
gui/main_dialog.py (agregar panel de interpretaciones)
gui/ui/pages/preview_page.py (agregar botón de herramienta)
core/controller.py (integrar InterpretationService)
exporters/__init__.py (exportar nuevo exporter)
```

---

## Beneficios de esta Implementación

1. **Flujo Natural**: Usuario dibuja directamente sobre el perfil
2. **Datos Georreferenciados**: Polígonos con coordenadas reales
3. **Análisis 3D**: Coordenada M permite análisis volumétrico
4. **Interoperabilidad**: Shapefile estándar compatible con otros software
5. **Trazabilidad**: Atributos detallados por polígono
6. **Reutilización**: Guardar/cargar interpretaciones

---

## Estrategia Revisada (Enero 2026)

**Nota: Nueva dirección arquitectónica definida por el usuario (Sesión Refactoring/Persistence)**

Se ha decidido simplificar el enfoque para la próxima versión:
1.  **Drafting 2D Puro**: La herramienta de interpretación funcionará exclusivamente en 2D (visualización de sección), permitiendo dibujar polígonos sobre el canvas.
2.  **Exportación Separada**:
    *   **Shapefile 2D**: Se guardará la interpretación tal cual se dibuja (coordenadas de lienzo/perfil).
    *   **Interpolación 3D Desacoplada**: La generación de geometrías 3D/2.5D se realizará en un proceso posterior o exportación dedicada a un archivo Shapefile separado, sin mezclar la lógica en tiempo real.

Esto simplifica la implementación inicial y evita la complejidad de la proyección en tiempo real durante el dibujo.
