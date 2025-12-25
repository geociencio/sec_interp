# Plan de Implementación: Herramienta de Medición Multi-Punto

Mejoramiento de la herramienta de medición para permitir medir afloramientos siguiendo la traza a lo largo del perfil geológico mediante clics sucesivos, finalizando con doble clic.

## Contexto

Actualmente, `ProfileMeasureTool` permite medir distancias entre dos puntos:
1. Primer clic establece el punto inicial
2. Segundo clic establece el punto final
3. Tercer clic reinicia la medición

Esta funcionalidad es limitada para medir afloramientos que siguen trazas complejas a lo largo del perfil. Se requiere una herramienta que permita:
- Múltiples clics para seguir la geometría del afloramiento
- Medición acumulada a lo largo de todos los segmentos
- Finalización mediante doble clic
- Visualización clara de la polilínea completa

## User Review Required

> [!IMPORTANT]
> **Cambio de Comportamiento de Usuario**
>
> Este cambio modificará la interacción con la herramienta de medición:
> - **Antes**: Dos clics para medir (inicio → fin)
> - **Después**: Múltiples clics para seguir la traza + doble clic para finalizar
>
> El comportamiento de dos puntos seguirá siendo posible (clic → doble clic), pero el flujo de interacción cambia ligeramente.

> [!NOTE]
> **Compatibilidad con Mediciones Simples**
>
> Las mediciones simples de dos puntos seguirán siendo posibles:
> 1. Primer clic en punto inicial
> 2. Doble clic en punto final
>
> Esto mantiene la funcionalidad existente mientras añade capacidades avanzadas.

## Proposed Changes

### Core Measurement Tool

#### [MODIFY] [measure_tool.py](file:///home/jmbernales/qgispluginsdev/sec_interp/gui/tools/measure_tool.py)

**Cambios en `ProfileMeasureTool`:**

1. **Estructura de Datos Multi-Punto**
   - Cambiar `start_point` y `end_point` por una lista `points: List[QgsPointXY]`
   - Mantener lista de segmentos con sus distancias individuales
   - Rastrear tiempo del último clic para detectar doble clic

2. **Detección de Doble Clic**
   - Añadir atributo `last_click_time: Optional[float]`
   - Añadir constante `DOUBLE_CLICK_THRESHOLD_MS = 300`
   - En `canvasReleaseEvent()`, calcular tiempo desde último clic
   - Si tiempo < threshold y distancia < tolerancia → finalizar medición

3. **Gestión de Puntos**
   - `_handle_first_point()`: Inicializar lista de puntos
   - `_handle_intermediate_point()`: Añadir punto a la lista
   - `_handle_final_point()`: Finalizar medición y calcular totales
   - `_is_double_click()`: Detectar doble clic por tiempo y distancia

4. **Actualización de Rubber Band**
   - Modificar `_update_rubber_band()` para soportar polilíneas
   - Añadir todos los puntos de la lista
   - Mostrar punto temporal durante movimiento del mouse

5. **Cálculo de Mediciones**
   - Modificar `_calculate_and_emit()` para calcular:
     - Distancia de cada segmento
     - Distancia total acumulada
     - Distancia horizontal total (suma de dx)
     - Cambio de elevación total (dy final - dy inicial)
     - Pendiente promedio ponderada

6. **Señales Actualizadas**
   - Modificar `measurementChanged` para incluir:
     - `total_distance`: Distancia acumulada total
     - `horizontal_distance`: Distancia horizontal total
     - `elevation_change`: Cambio total de elevación
     - `avg_slope`: Pendiente promedio
     - `segment_count`: Número de segmentos
     - `segments`: Lista de distancias por segmento (opcional)

7. **Visualización de Puntos Intermedios**
   - Añadir marcadores circulares en cada punto intermedio
   - Usar `QgsVertexMarker` para puntos
   - Color diferenciado: verde para intermedios, rojo para inicio/fin

**Estructura de código propuesta:**

```python
class ProfileMeasureTool(QgsMapToolEmitPoint):
    # Nueva señal con más información
    measurementChanged = pyqtSignal(dict)  # dict con todas las métricas
    measurementCleared = pyqtSignal()

    DOUBLE_CLICK_THRESHOLD_MS = 300
    DOUBLE_CLICK_DISTANCE_TOLERANCE = 5  # pixels

    def __init__(self, canvas: QgsMapCanvas):
        super().__init__(canvas)
        self.canvas = canvas
        self.points: List[QgsPointXY] = []
        self.last_click_time: Optional[float] = None
        self.last_click_pos: Optional[QPoint] = None

        self.rubber_band: Optional[QgsRubberBand] = None
        self.vertex_markers: List[QgsVertexMarker] = []
        self.snapper = ProfileSnapper(canvas)

    def canvasReleaseEvent(self, event):
        if event.button() == Qt.RightButton:
            self.reset()
            return

        snapped_point = self.snapper.snap(event.pos())

        # Detectar doble clic
        if self._is_double_click(event.pos()):
            self._finalize_measurement()
            return

        # Añadir punto
        self._add_point(snapped_point)
        self.last_click_time = time.time() * 1000
        self.last_click_pos = event.pos()

    def _is_double_click(self, pos: QPoint) -> bool:
        if not self.last_click_time or not self.last_click_pos:
            return False

        current_time = time.time() * 1000
        time_diff = current_time - self.last_click_time

        if time_diff > self.DOUBLE_CLICK_THRESHOLD_MS:
            return False

        # Verificar distancia en pixels
        dx = pos.x() - self.last_click_pos.x()
        dy = pos.y() - self.last_click_pos.y()
        pixel_dist = math.sqrt(dx*dx + dy*dy)

        return pixel_dist < self.DOUBLE_CLICK_DISTANCE_TOLERANCE

    def _add_point(self, point: QgsPointXY):
        self.points.append(point)
        self._ensure_rubber_band()
        self.rubber_band.addPoint(point, True)
        self._add_vertex_marker(point)

        if len(self.points) > 1:
            self._calculate_and_emit()

    def _finalize_measurement(self):
        if len(self.points) < 2:
            return

        # Calcular métricas finales
        metrics = self._calculate_metrics()
        self.measurementChanged.emit(metrics)
        logger.info(f"Measurement finalized: {len(self.points)} points, "
                   f"{metrics['total_distance']:.2f}m total")

    def _calculate_metrics(self) -> dict:
        if len(self.points) < 2:
            return {}

        total_dist = 0.0
        total_dx = 0.0
        segments = []

        for i in range(len(self.points) - 1):
            p1 = self.points[i]
            p2 = self.points[i + 1]

            dx = abs(p2.x() - p1.x())
            dy = p2.y() - p1.y()
            seg_dist = math.sqrt(dx*dx + dy*dy)

            total_dist += seg_dist
            total_dx += dx
            segments.append({
                'distance': seg_dist,
                'dx': dx,
                'dy': dy
            })

        # Cambio de elevación total
        elevation_change = self.points[-1].y() - self.points[0].y()

        # Pendiente promedio
        avg_slope = 0.0
        if total_dx > 0:
            avg_slope = math.degrees(math.atan(abs(elevation_change) / total_dx))

        return {
            'total_distance': total_dist,
            'horizontal_distance': total_dx,
            'elevation_change': elevation_change,
            'avg_slope': avg_slope,
            'segment_count': len(segments),
            'segments': segments,
            'point_count': len(self.points)
        }
```

---

### GUI Integration

#### [MODIFY] [main_dialog.py](file:///home/jmbernales/qgispluginsdev/sec_interp/gui/main_dialog.py)

**Actualización del Display de Resultados:**

1. **Actualizar conexión de señal**
   - Cambiar handler de `measurementChanged` para recibir diccionario
   - Mostrar información multi-segmento

2. **Mejorar visualización de resultados**
   - Mostrar distancia total prominentemente
   - Mostrar número de segmentos
   - Mostrar distancia horizontal y cambio de elevación
   - Opcionalmente: tabla con distancias por segmento

**Código propuesto:**

```python
def _on_measurement_changed(self, metrics: dict):
    """Handle measurement updates from the tool."""
    if not metrics:
        return

    total_dist = metrics.get('total_distance', 0)
    horiz_dist = metrics.get('horizontal_distance', 0)
    elev_change = metrics.get('elevation_change', 0)
    avg_slope = metrics.get('avg_slope', 0)
    seg_count = metrics.get('segment_count', 0)

    result_text = (
        f"<b>Medición Multi-Punto</b><br>"
        f"Segmentos: {seg_count}<br>"
        f"Distancia Total: {total_dist:.2f} m<br>"
        f"Distancia Horizontal: {horiz_dist:.2f} m<br>"
        f"Cambio Elevación: {elev_change:+.2f} m<br>"
        f"Pendiente Promedio: {avg_slope:.1f}°"
    )

    self.measure_results_label.setText(result_text)
```

---

## Verification Plan

### Automated Tests

**Nuevo archivo**: `tests/test_multipoint_measure_tool.py`

```python
def test_multipoint_measurement():
    """Test multi-point polyline measurement."""
    tool = ProfileMeasureTool(mock_canvas)

    # Simular 4 puntos
    points = [
        QgsPointXY(0, 0),
        QgsPointXY(100, 50),
        QgsPointXY(200, 30),
        QgsPointXY(300, 100)
    ]

    for pt in points:
        tool._add_point(pt)

    metrics = tool._calculate_metrics()

    assert metrics['point_count'] == 4
    assert metrics['segment_count'] == 3
    assert metrics['total_distance'] > 0
    assert metrics['elevation_change'] == 100  # 100 - 0

def test_double_click_detection():
    """Test double-click finalization."""
    tool = ProfileMeasureTool(mock_canvas)

    # Simular primer clic
    tool.last_click_time = time.time() * 1000
    tool.last_click_pos = QPoint(100, 100)

    # Simular segundo clic cercano y rápido
    time.sleep(0.1)  # 100ms
    is_double = tool._is_double_click(QPoint(102, 101))

    assert is_double is True
```

### Manual Verification

1. **Medición Simple (2 puntos)**
   - Abrir preview y activar herramienta de medición
   - Clic en punto inicial
   - Doble clic en punto final
   - ✅ Verificar que se muestra distancia correcta
   - ✅ Verificar que la línea se dibuja correctamente

2. **Medición Multi-Punto (3+ puntos)**
   - Clic en punto inicial
   - Clic en 2-3 puntos intermedios
   - Doble clic en punto final
   - ✅ Verificar que se muestran todos los segmentos
   - ✅ Verificar distancia total acumulada
   - ✅ Verificar marcadores en puntos intermedios

3. **Snapping en Multi-Punto**
   - Realizar medición multi-punto sobre líneas geológicas
   - ✅ Verificar que cada punto hace snap correctamente
   - ✅ Verificar que los marcadores aparecen en posiciones snapped

4. **Cancelación con Clic Derecho**
   - Iniciar medición multi-punto
   - Clic derecho en cualquier momento
   - ✅ Verificar que se limpia toda la medición
   - ✅ Verificar que desaparecen marcadores y rubber band

5. **Medición de Afloramiento Real**
   - Cargar datos geológicos con trazas complejas
   - Medir a lo largo de un contacto geológico sinuoso
   - ✅ Verificar que la medición sigue la traza fielmente
   - ✅ Verificar que la distancia total es realista

---

## Consideraciones Técnicas

### Rendimiento
- La lista de puntos y marcadores debe limpiarse adecuadamente en `reset()`
- Considerar límite máximo de puntos (ej. 100) para evitar problemas de rendimiento
- Los marcadores deben removerse del canvas al finalizar

### UX/UI
- Cursor debe cambiar visualmente durante medición activa
- Tooltip podría mostrar "Doble clic para finalizar"
- Color de rubber band podría cambiar al finalizar (rojo → verde)

### Compatibilidad
- Mantener compatibilidad con QGIS 3.x
- Asegurar que funciona con diferentes CRS del canvas
- Verificar comportamiento con zoom/pan durante medición

### Documentación
- Actualizar docstrings en `measure_tool.py`
- Actualizar `USER_GUIDE.md` con instrucciones de uso
- Añadir capturas de pantalla del flujo multi-punto
- Actualizar `ARCHITECTURE.md` con nuevos diagramas de flujo

---

## Cronograma Estimado

| Fase | Esfuerzo | Duración |
|------|----------|----------|
| Implementación Core | Alto | 2-3 días |
| Integración UI | Medio | 1 día |
| Testing Manual | Medio | 1 día |
| Documentación | Bajo | 0.5 días |
| **Total** | | **4-5 días** |

---

## Riesgos y Mitigaciones

| Riesgo | Impacto | Mitigación |
|--------|---------|------------|
| Detección de doble clic inconsistente | Alto | Usar threshold configurable, probar en diferentes sistemas |
| Confusión de usuarios con nuevo flujo | Medio | Documentación clara, tooltip visual |
| Problemas de rendimiento con muchos puntos | Bajo | Límite máximo de puntos, limpieza eficiente |
| Incompatibilidad con versiones antiguas QGIS | Bajo | Probar en QGIS 3.16+ (LTR) |

---

*Plan creado: 2025-12-23*
*Versión objetivo: 2.3.0 o 2.4.0*
