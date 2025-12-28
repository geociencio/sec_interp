# Plan de Implementación: Interpretación 2D Simplificada

## Objetivo

Implementar una herramienta de dibujo de polígonos 2D sobre el perfil geológico, con exportación separada en dos formatos:
1. **Shapefile 2D**: Coordenadas del perfil (distancia, elevación)
2. **Shapefile 3D**: Geometrías proyectadas sobre la línea de sección (proceso posterior)

## Arquitectura Simplificada

### Fase 1: Herramienta de Dibujo 2D

#### 1.1 `InterpretationTool` (GUI)
**Ubicación**: `gui/tools/interpretation_tool.py`

**Funcionalidad**:
- Dibujo de polígonos usando `QgsRubberBand`
- Captura de vértices en coordenadas del canvas (distancia, elevación)
- Sin proyección en tiempo real
- Gestión de múltiples polígonos

```python
class InterpretationTool(QgsMapTool):
    """Herramienta para dibujar polígonos de interpretación en 2D."""
    
    def __init__(self, canvas):
        self.rubber_band = QgsRubberBand(canvas, QgsWkbTypes.PolygonGeometry)
        self.vertices = []  # Lista de (distancia, elevación)
        self.polygons = []  # Polígonos finalizados
    
    def canvasReleaseEvent(self, event):
        """Agregar vértice al polígono."""
        point = self.toMapCoordinates(event.pos())
        self.vertices.append((point.x(), point.y()))
        self.rubber_band.addPoint(point)
    
    def finish_polygon(self):
        """Finalizar polígono actual."""
        if len(self.vertices) >= 3:
            polygon = InterpretationPolygon(
                vertices_2d=self.vertices.copy(),
                name="Interpretation_" + str(len(self.polygons) + 1),
                color=self._generate_color()
            )
            self.polygons.append(polygon)
            self._reset()
```

#### 1.2 Modelo de Datos
**Ubicación**: `core/types.py`

```python
@dataclass
class InterpretationPolygon:
    """Polígono de interpretación en coordenadas 2D del perfil."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    type: str = "interpretation"  # lithology, structure, alteration
    vertices_2d: list[tuple[float, float]] = field(default_factory=list)  # (dist, elev)
    color: str = "#FF0000"
    description: str = ""
    created_at: datetime = field(default_factory=datetime.now)
```

#### 1.3 Integración en Preview
**Modificar**: `gui/ui/pages/preview_page.py`

- Agregar botón "Interpretación" en toolbar
- Checkbox "Mostrar Interpretaciones" en panel de capas
- Renderizar polígonos usando `QgsRubberBand`

### Fase 2: Exportación 2D

#### 2.1 `Interpretation2DExporter`
**Ubicación**: `exporters/interpretation_exporters.py`

**Funcionalidad**:
- Exportar polígonos tal cual fueron dibujados
- Coordenadas: (distancia, elevación)
- Sistema de referencia: Local del perfil

```python
class Interpretation2DExporter(BaseExporter):
    """Exporta interpretaciones en coordenadas 2D del perfil."""
    
    def export(self, output_path: Path, polygons: list[InterpretationPolygon]) -> None:
        """
        Exporta polígonos a Shapefile 2D.
        
        Estructura:
        - Geometría: Polygon (coordenadas del perfil)
        - Atributos: id, name, type, description, color
        """
        # Crear capa en memoria
        layer = QgsVectorLayer("Polygon?crs=", "interpretations_2d", "memory")
        
        # Definir campos
        fields = QgsFields()
        fields.append(QgsField("id", QVariant.String))
        fields.append(QgsField("name", QVariant.String))
        fields.append(QgsField("type", QVariant.String))
        fields.append(QgsField("descript", QVariant.String))
        fields.append(QgsField("color", QVariant.String))
        
        layer.dataProvider().addAttributes(fields)
        layer.updateFields()
        
        # Agregar features
        for poly in polygons:
            feature = QgsFeature()
            points = [QgsPointXY(x, y) for x, y in poly.vertices_2d]
            feature.setGeometry(QgsGeometry.fromPolygonXY([points]))
            feature.setAttributes([
                poly.id, poly.name, poly.type, 
                poly.description, poly.color
            ])
            layer.dataProvider().addFeature(feature)
        
        # Guardar a disco
        QgsVectorFileWriter.writeAsVectorFormat(
            layer, str(output_path), "UTF-8", 
            QgsCoordinateReferenceSystem(), "ESRI Shapefile"
        )
```

### Fase 3: Exportación 3D (Proceso Separado)

#### 3.1 `Interpretation3DService`
**Ubicación**: `core/services/interpretation_service.py`

**Funcionalidad**:
- Leer Shapefile 2D de interpretaciones
- Proyectar vértices sobre la línea de sección 3D
- Generar geometrías con coordenada M (elevación)

```python
class Interpretation3DService:
    """Servicio para proyectar interpretaciones 2D a 3D."""
    
    def project_to_3d(
        self,
        polygon_2d: InterpretationPolygon,
        section_line: QgsGeometry,
        line_start: QgsPointXY
    ) -> QgsGeometry:
        """
        Proyecta polígono 2D a geometría 3D.
        
        Args:
            polygon_2d: Polígono en coordenadas (distancia, elevación)
            section_line: Línea de sección 3D
            line_start: Punto inicial de la línea
            
        Returns:
            Geometría PolygonM con coordenadas (X, Y, M=elevación)
        """
        points_3d = []
        
        for dist, elev in polygon_2d.vertices_2d:
            # Interpolar punto en la línea
            point_on_line = section_line.interpolate(dist)
            xy = point_on_line.asPoint()
            
            # Crear punto con M
            point_m = QgsPoint(xy.x(), xy.y(), m=elev)
            points_3d.append(point_m)
        
        # Crear polígono M
        ring = QgsLineString(points_3d)
        polygon_m = QgsPolygon()
        polygon_m.setExteriorRing(ring)
        
        return QgsGeometry(polygon_m)
```

#### 3.2 `Interpretation3DExporter`
**Ubicación**: `exporters/interpretation_exporters.py`

```python
class Interpretation3DExporter(BaseExporter):
    """Exporta interpretaciones proyectadas a 3D."""
    
    def export(
        self,
        input_2d_path: Path,
        output_3d_path: Path,
        section_line: QgsGeometry,
        line_start: QgsPointXY,
        crs: QgsCoordinateReferenceSystem
    ) -> None:
        """
        Lee Shapefile 2D y genera Shapefile 3D proyectado.
        
        Args:
            input_2d_path: Shapefile 2D de entrada
            output_3d_path: Shapefile 3D de salida
            section_line: Línea de sección para proyección
            line_start: Punto inicial
            crs: Sistema de coordenadas de salida
        """
        service = Interpretation3DService()
        
        # Leer polígonos 2D
        layer_2d = QgsVectorLayer(str(input_2d_path), "temp", "ogr")
        
        # Crear capa 3D
        layer_3d = QgsVectorLayer(
            f"PolygonM?crs={crs.authid()}", 
            "interpretations_3d", 
            "memory"
        )
        
        # Copiar campos
        layer_3d.dataProvider().addAttributes(layer_2d.fields())
        layer_3d.updateFields()
        
        # Proyectar cada polígono
        for feat in layer_2d.getFeatures():
            # Extraer vértices 2D
            geom_2d = feat.geometry()
            vertices_2d = [(p.x(), p.y()) for p in geom_2d.asPolygon()[0]]
            
            # Crear objeto temporal
            poly_2d = InterpretationPolygon(
                vertices_2d=vertices_2d,
                name=feat["name"]
            )
            
            # Proyectar a 3D
            geom_3d = service.project_to_3d(poly_2d, section_line, line_start)
            
            # Crear feature 3D
            feat_3d = QgsFeature()
            feat_3d.setGeometry(geom_3d)
            feat_3d.setAttributes(feat.attributes())
            layer_3d.dataProvider().addFeature(feat_3d)
        
        # Guardar
        QgsVectorFileWriter.writeAsVectorFormat(
            layer_3d, str(output_3d_path), "UTF-8", 
            crs, "ESRI Shapefile"
        )
```

## Interfaz de Usuario

### Toolbar del Preview

```
[Zoom In] [Zoom Out] [Pan] [Measure] [Interpretation] [Clear]
```

### Panel de Interpretaciones

```
┌─ Interpretaciones ────────────────┐
│ ☑ Mostrar interpretaciones        │
│                                    │
│ Lista:                             │
│ • Granito Alterado    [Edit] [Del]│
│ • Zona de Falla       [Edit] [Del]│
│ • Veta Cuarzo         [Edit] [Del]│
│                                    │
│ [+ Nuevo] [Exportar 2D] [→ 3D]    │
└────────────────────────────────────┘
```

### Diálogo de Exportación 3D

```
┌─ Exportar a 3D ───────────────────┐
│ Archivo 2D:                        │
│ [interpretations_2d.shp] [Browse] │
│                                    │
│ Archivo 3D:                        │
│ [interpretations_3d.shp] [Browse] │
│                                    │
│ Línea de Sección:                 │
│ [Section_Line_01      ▼]          │
│                                    │
│ CRS: EPSG:32719 (WGS 84 / UTM 19S)│
│                                    │
│           [Cancelar] [Exportar]    │
└────────────────────────────────────┘
```

## Flujo de Trabajo

### Escenario 1: Dibujo e Interpretación

1. Usuario genera perfil 2D
2. Activa herramienta de interpretación
3. Dibuja polígonos sobre el perfil
4. Asigna nombres y tipos
5. Exporta a Shapefile 2D

### Escenario 2: Proyección a 3D

1. Usuario abre diálogo "Exportar a 3D"
2. Selecciona Shapefile 2D de entrada
3. Especifica ruta de salida 3D
4. Selecciona línea de sección del proyecto
5. Sistema genera Shapefile 3D con geometrías PolygonM

## Persistencia

### Formato JSON (Sesión)
**Ubicación**: `{output_folder}/interpretations.json`

```json
{
  "version": "1.0",
  "section_line_id": "layer_id_123",
  "created_at": "2026-01-15T10:30:00",
  "polygons": [
    {
      "id": "uuid-1234",
      "name": "Granito Alterado",
      "type": "lithology",
      "vertices_2d": [[0, 100], [50, 100], [50, 80], [0, 80]],
      "color": "#FF5733",
      "description": "Zona de alteración hidrotermal"
    }
  ]
}
```

## Roadmap de Implementación

### v2.5.0 - Interpretación 2D Básica
- [x] Modelo de datos (`InterpretationPolygon`)
- [ ] Herramienta de dibujo (`InterpretationTool`)
- [ ] Renderizado con `QgsRubberBand`
- [ ] Exportación 2D (`Interpretation2DExporter`)
- [ ] Persistencia JSON
- [ ] Panel de gestión básico

### v2.6.0 - Proyección 3D
- [ ] Servicio de proyección (`Interpretation3DService`)
- [ ] Exportador 3D (`Interpretation3DExporter`)
- [ ] Diálogo de exportación 3D
- [ ] Validación de geometrías
- [ ] Manejo de errores

### v2.7.0 - Funcionalidades Avanzadas
- [ ] Edición de polígonos existentes
- [ ] Snap a geometrías del perfil
- [ ] Múltiples tipos de interpretación
- [ ] Importación de interpretaciones
- [ ] Visualización 3D en QGIS

## Archivos a Crear/Modificar

### Nuevos Archivos
```
gui/tools/interpretation_tool.py
core/services/interpretation_service.py
exporters/interpretation_exporters.py
tests/test_interpretation_tool.py
tests/test_interpretation_service.py
```

### Archivos a Modificar
```
gui/ui/pages/preview_page.py (botón + checkbox)
gui/main_dialog.py (panel de interpretaciones)
core/types.py (dataclass InterpretationPolygon)
exporters/__init__.py (exportar nuevos exporters)
```

## Ventajas de este Enfoque

1. **Simplicidad**: Dibujo directo sin cálculos complejos
2. **Rendimiento**: Sin proyecciones en tiempo real
3. **Flexibilidad**: Usuario decide cuándo proyectar a 3D
4. **Trazabilidad**: Dos archivos separados (2D original + 3D proyectado)
5. **Iteración**: Fácil modificar interpretaciones 2D sin rehacer 3D
6. **Compatibilidad**: Shapefiles estándar para ambos formatos

## Próximos Pasos

1. Implementar `InterpretationTool` básico
2. Crear modelo de datos y persistencia JSON
3. Implementar exportación 2D
4. Testing con datos reales
5. Implementar servicio de proyección 3D
6. Crear diálogo de exportación 3D
