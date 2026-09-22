---
tags:
  - secinterp
  - code-walkthrough
  - exporters
  - interpretations
  - 3d
aliases:
  - interpretation_3d_exporter.py
  - Interpretation3DExporter
cssclass: secinterp-note
---

# `exporters/interpretation_3d_exporter.py`

> [!abstract] Resumen en una línea
> Proyecta los polígonos 2D de interpretación (`distancia, elevación`) al plano vertical de la sección y los exporta como `PolygonZ` con estilo QML 2D categorizado + renderer 3D por reglas.

**Ruta**: `exporters/interpretation_3d_exporter.py` (465 líneas)
**Clase principal**: `Interpretation3DExporter(BaseExporter)`
**Capa**: Exporters (GUI · QGIS-dependiente, con import opcional de `qgis._3d`)
**Tags**: #secinterp #exporters #interpretations #3d

---

## 🎯 ¿Por qué existe este archivo?

Las interpretaciones se digitalizan sobre el perfil 2D (`vertices_2d` en distancia /
elevación, ver [[interpretations]]). Para visualizarlas en la vista 3D de QGIS hay que
**recolocarlas en el mundo real**: cada punto `(d, e)` se convierte en `(este, norte, elev)`
desplazándolo desde el origen de la línea de sección según su azimut:

| Problema | Solución |
|----------|----------|
| El polígono 2D no tiene coordenadas de mapa | `_calculate_section_geometry` deriva origen + azimut de `section_line`; `_create_3d_rings` aplica la rotación |
| Vértices duplicados o anillos sin cerrar rompen `QgsPolygon` | `_get_unique_vertices` + `_ensure_closed_polygon` + `makeValid()` |
| Cada unidad necesita su color en 2D y en 3D | `_setup_2d_renderer` (categorizado) + `_configure_3d_renderer` (reglas `qgis._3d`), guardados como `.qml` |
| Los atributos custom varían por polígono | `_prepare_fields` une todas las claves (`sorted_keys`) en campos `QString(255)` |
| `section_line` ausente o geometría degenerada | `_validate_export_input` (retorna `False` o lanza `ExportError`) |

> [!important] Nota arquitectónica — writer 3D, no `IRenderer3D`
> Como los exporters de [[drillhole_3d_exporter]], esta clase **escribe ficheros**, no
> implementa el puerto `IRenderer3D.render_3d/clear` (ver [[core_interfaces]]). La
> "renderización 3D" aquí significa: geometría `PolygonZ` + un `.qml` que configura
> el renderer 3D nativo de QGIS al cargar la capa.

---

## 🧬 Diagrama de relaciones

```mermaid
graph TD
    EXP["Interpretation3DExporter"]
    BASE["BaseExporter"]
    IO["core/utils/io (create_vector_writer)"]
    ENT["InterpretationPolygon (core/domain)"]
    IH["handlers/interpretations.py"]
    ORCH["ExportService (orchestrator)"]
    AC["AccessControlService (gate 3D)"]

    EXP -->|hereda| BASE
    EXP -->|create_vector_writer PolygonZ| IO
    EXP -->|lee vertices_2d/attributes| ENT
    EXP -->|QgsCategorizedSymbolRenderer| R2D["renderer 2D"]
    EXP -->|qgis._3d (opcional)| R3D["renderer 3D por reglas"]
    EXP -->|guarda .qml| QML["estilo QML"]
    IH -->|usa| EXP
    AC -->|autoriza| IH
    ORCH -->|exp_interp| IH
```

> [!tip] Cómo leer
> El handler `interpretations` (ver [[interpretations]]) decide 2D vs 3D y pasa
> `section_line` + `crs`. El gate `AccessControlService` vive en el handler, no aquí:
> este exporter asume que ya está autorizado.

---

## 📦 Imports — lectura arquitectónica

```python
# exporters/interpretation_3d_exporter.py
from __future__ import annotations

import math
from pathlib import Path
from typing import Any

from qgis.core import (
    QgsCoordinateReferenceSystem,
    QgsFeature,
    QgsField,
    QgsFields,
    QgsGeometry,
    QgsLineString,
    QgsPoint,
    QgsPointXY,
    QgsPolygon,
    QgsVectorLayer,
    QgsWkbTypes,
)
from qgis.PyQt.QtCore import QCoreApplication, QMetaType
from qgis.PyQt.QtGui import QColor

import sec_interp.core.utils.io as scu_io
from sec_interp.core.domain import InterpretationPolygon
from sec_interp.core.exceptions import ExportError
from sec_interp.exporters.base_exporter import BaseExporter
from sec_interp.logger_config import get_logger
```

| # | Observación |
|---|-------------|
| ① | `QgsPolygon` + `QgsLineString(QgsPoint)` + `PolygonZ` → anillos 3D con interior rings (agujeros soportados). |
| ② | `QCoreApplication` solo para traducir el mensaje de `section_line` ausente (i18n, ver [[interpretation_exporters]]). |
| ③ | `ExportError` (no `return False`) en fallos estructurales: es el único exporter 2D/3D que **lanza**. |
| ④ | `QColor` para validar hex de unidad con fallback `#FF0000` (mismo criterio en 2D y 3D). |
| ⑤ | `QgsVectorLayer` en cabecera para la capa memoria del estilo; `qgis._3d` y `QgsVectorFileWriter` son **imports lazy** dentro de métodos. |
| ⑥ | `math` para `atan2/cos/sin` de la proyección azimutal (trigonometría explícita, sin `QgsCoordinateTransform`). |

---

## 🏗️ Inventario de estructura

**Clase:** `Interpretation3DExporter(BaseExporter)` — 1 público (`export`, `get_supported_extensions`) + 12 privados.

**Constantes:**

| Constante | Valor | Uso |
|-----------|------:|-----|
| `MIN_VALID_POLYGON_VERTICES` | 4 | Anillo cerrado mínimo (3 únicos + cierre) en `_prepare_2d_geometry` |
| `MIN_REQUIRED_FOR_CLOSURE` | 2 | Solo se cierra si hay más de 2 vértices |

**Métodos (pipeline de exportación):**
- `export(output_path, data, layer_name=None) -> bool`
- `_validate_export_input(interpretations, section_line) -> bool`
- `_prepare_fields(interpretations) -> tuple[list[QgsField], list[str]]`
- `_calculate_section_geometry(section_line) -> tuple[float, float, float]`
- `_collect_projected_features(interpretations, fields, sorted_keys, origin_x, origin_y, azimuth) -> list[QgsFeature]`
- `_prepare_2d_geometry(polygon) -> QgsGeometry | None`
- `_get_unique_vertices(vertices_2d) -> list`
- `_ensure_closed_polygon(vertices) -> list`
- `_project_to_3d_features(geom_2d, polygon, fields, origin_x, origin_y, azimuth, custom_keys, vert_exag=1.0) -> list[QgsFeature]`
- `_create_3d_rings(poly_2d, origin_x, origin_y, azimuth, vert_exag) -> list[QgsLineString]`
- `_write_shapefile(path, features, fields, wkb_type, crs, layer_name=None) -> bool`
- `_make_fields_obj(fields_list) -> QgsFields` / `_make_fields(fields_list) -> QgsFields`

**Métodos (estilo post-export):**
- `_handle_post_export_styles(output_path, interpretations, fields, crs) -> None`
- `_generate_qml_style(shp_path, interpretations, fields, crs) -> None`
- `_setup_2d_renderer(layer, interpretations) -> None`
- `_configure_3d_renderer(layer, interpretations) -> None`

---

## 📁 Archivos del paquete `exporters/`

| Archivo | Rol respecto a esta nota |
|---|---|
| `interpretation_3d_exporter.py` | Esta nota: `PolygonZ` + QML 2D/3D |
| [[interpretation_exporters]] | Gemelo 2D: `Interpretation2DExporter` (`fromPolygonXY`, sin QML) |
| [[drillhole_3d_exporter]] | El otro writer 3D: trazas e intervalos `LineStringZ` |
| [[base_exporter]] | `BaseExporter`: contrato común |
| [[exporters]] | Fachada del paquete + `get_exporter()` por extensión |

---

## 📖 Recorrido método por método

### `export` — pipeline en 5 fases

```python
def export(self, output_path: str, data: dict[str, Any], layer_name: str | None = None) -> bool:
    interpretations = data.get("interpretations", [])
    section_line = data.get("section_line")
    src_crs = data.get("crs", QgsCoordinateReferenceSystem())

    if not self._validate_export_input(interpretations, section_line):
        return False

    # Prepare fields
    fields, sorted_keys = self._prepare_fields(interpretations)

    # Calculate section azimuth and origin
    try:
        origin_x, origin_y, azimuth = self._calculate_section_geometry(section_line)
    except Exception as e:
        raise ExportError(f"Failed to calculate section geometry: {e}") from e

    # Transform and create features
    features = self._collect_projected_features(
        interpretations, fields, sorted_keys, origin_x, origin_y, azimuth
    )

    success = self._write_shapefile(
        output_path,
        features,
        fields,
        QgsWkbTypes.Type.PolygonZ,
        src_crs,
        layer_name=layer_name,
    )

    if success:
        self._handle_post_export_styles(output_path, interpretations, fields, src_crs)

    return success
```

| Fase | Qué hace |
|------|----------|
| 1. Extracción | `interpretations` (default `[]`), `section_line`, `crs` (default CRS vacío) |
| 2. Validación | Sin interpretaciones → `False`; sin `section_line` → **`ExportError`** |
| 3. Geometría de sección | Origen + azimut; cualquier fallo → `ExportError` con causa (`from e`) |
| 4. Proyección | Un `QgsFeature` 3D por cada parte de cada polígono (Multi cuenta como N) |
| 5. Estilo | Solo si la escritura tuvo éxito; los fallos de QML son `warning`, no abortan |

### `_validate_export_input` — doble régimen

Lista vacía = aviso + `False` (caso benigno); `section_line` ausente = `ExportError`
traducido con `QCoreApplication.translate` (sin línea no hay marco de referencia 3D).

### `_prepare_fields` — unión de atributos custom

Esquema fijo (`id`/`name`/`type`/`color`/`created_at` con longitudes SHP 50/100/50/10/30)
más una columna `QString(255)` por cada clave custom encontrada en **cualquier**
polígono (`sorted_keys` ordenado = columnas deterministas). Idéntico esquema al
exporter 2D; retorna `(fields, sorted_keys)`.

### `_calculate_section_geometry` — origen y azimut

```python
line_points = section_line.asMultiPolyline()[0] if section_line.isMultipart() else section_line.asPolyline()
p1, p2 = line_points[0], line_points[-1]
azimuth = math.atan2(p2.y() - p1.y(), p2.x() - p1.x())
return p1.x(), p1.y(), azimuth
```

Solo importan el **primer y último vértice**: la sección se modela como plano vertical
recto aunque la línea tenga quiebros (en multipart se usa la primera parte). El azimut
en radianes alimenta a `cos/sin` en `_create_3d_rings`; origen y azimut se loguean en
grados para diagnóstico.

### `_collect_projected_features` — bucle con filtro

Por cada polígono: `_prepare_2d_geometry` (los degenerados dan `None` y se saltan) y
`extend` con `_project_to_3d_features(..., vert_exag=1.0)`. La exageración vertical es
visual (canvas) y no se bakea en el SHP.

### `_prepare_2d_geometry` — saneo del anillo

```python
def _prepare_2d_geometry(self, polygon: Any) -> QgsGeometry | None:
    vertices = self._get_unique_vertices(polygon.vertices_2d)
    if not vertices:
        return None

    vertices = self._ensure_closed_polygon(vertices)

    if len(vertices) < MIN_VALID_POLYGON_VERTICES:
        logger.warning(f"Polygon {polygon.id} has insufficient unique vertices. Skipping.")
        return None

    qgs_points_3d = [QgsPoint(x, y, 0.0) for x, y in vertices]
    polygon_2d = QgsPolygon()
    polygon_2d.setExteriorRing(QgsLineString(qgs_points_3d))
    geom_2d = QgsGeometry(polygon_2d)

    if not geom_2d.isGeosValid():
        logger.info(f"Correcting 2D geometry for polygon {polygon.id}")
        geom_2d = geom_2d.makeValid()

    return geom_2d
```

Cadena: dedup → cierre → conteo mínimo (4 = triángulo cerrado) → construcción con
`z=0.0` → `isGeosValid()` y `makeValid()` si hace falta. El `x` del punto es distancia,
el `y` es elevación; la georreferenciación real ocurre después, en `_create_3d_rings`.

### Saneo de vértices — `_get_unique_vertices` / `_ensure_closed_polygon`

`_get_unique_vertices` elimina solo duplicados **consecutivos** (`v != dedup[-1]`,
barato y sin tolerancia); `_ensure_closed_polygon` añade el primer vértice al final
(`[*vertices, vertices[0]]`, sin mutar el original) cuando hay más de 2 vértices
(`MIN_REQUIRED_FOR_CLOSURE`) y el anillo está abierto.

### `_project_to_3d_features` — Multi como N features

```python
polygons_2d = geom_2d.asMultiPolygon() if geom_2d.isMultipart() else [geom_2d.asPolygon()]

for poly_2d in polygons_2d:
    rings_3d = self._create_3d_rings(poly_2d, origin_x, origin_y, azimuth, vert_exag)
    ...
    polygon_3d = QgsPolygon()
    polygon_3d.setExteriorRing(rings_3d[0])
    for i in range(1, len(rings_3d)):
        polygon_3d.addInteriorRing(rings_3d[i])
    ...
    feat.setAttribute("id", polygon.id)
    feat.setAttribute("name", polygon.name)
    for key in custom_keys:
        feat.setAttribute(key, str(polygon.attributes.get(key, "")))
```

El anillo 0 es exterior, el resto interiores (agujeros). Los atributos fijos van por
nombre y los custom con `str(val)` (simetría con el exporter 2D). Nótese `QgsFeature()`
vacío + `setFields`: a diferencia del 2D, aquí no se construye con `QgsFeature(fields)`.

### `_create_3d_rings` — la proyección azimutal

```python
rings_3d = []
cos_a = math.cos(azimuth)
sin_a = math.sin(azimuth)

for ring_2d in poly_2d:
    points_3d = []
    for p_2d in ring_2d:
        east = origin_x + (p_2d.x() * cos_a)
        north = origin_y + (p_2d.x() * sin_a)
        elev = p_2d.y() / vert_exag
        points_3d.append(QgsPoint(east, north, elev))

    rings_3d.append(QgsLineString(points_3d))
return rings_3d
```

`cos_a`/`sin_a` se precalculan una vez por polígono (no por vértice). La distancia
`p_2d.x()` avanza sobre el azimut; la elevación `p_2d.y()` se conserva (dividida por
`vert_exag`, hoy siempre 1.0). Es una transformación rígida: preserva distancias y
ángulos del perfil.

### `_write_shapefile` — escritura con chequeo de writer

```python
writer = scu_io.create_vector_writer(
    str(path), crs, qgs_fields, wkb_type, layer_name=layer_name
)

if writer.hasError() != QgsVectorFileWriter.WriterError.NoError:
    raise ExportError(writer.errorMessage())

for feat in features:
    writer.addFeature(feat)

del writer
return True
```

A diferencia de los exporters de sondajes, aquí un writer defectuoso **lanza**
`ExportError` con el mensaje nativo en vez de retornar `False`. `_make_fields_obj`
convierte la lista de `QgsField` al contenedor `QgsFields` que exige el writer.

### QML post-export — estilo 2D + 3D que nunca aborta

`_generate_qml_style` crea una capa memoria `Polygon?crs=...&z=yes`, le aplica
simbología 2D categorizada por `name` (`_setup_2d_renderer`: relleno con alfa 180,
borde oscurecido `darker(150)`) y, si `import qgis._3d` funciona (`HAS_3D`), un renderer
3D por reglas con una regla por unidad (`"name" = '...'`, material `QgsPhongMaterialSettings`
con difuso + ambiente `lighter(120)`). El `.qml` se guarda junto al SHP vía
`saveNamedStyle`; cualquier fallo es `warning` en `_handle_post_export_styles` y la
exportación sigue siendo `True`.

---

## 🔄 Flujo de datos

| Fase | Entrada | Transformación | Salida |
|------|---------|----------------|--------|
| Validación | `interpretations`, `section_line` | vacía → `False`; sin línea → `ExportError` | Guardas |
| Campos | `attributes` de todos los polígonos | unión ordenada de claves | `fields` + `sorted_keys` |
| Sección | `section_line` (simple/multi) | primer/último vértice → `atan2` | `(origin_x, origin_y, azimuth)` |
| Saneo 2D | `vertices_2d` | dedup → cierre → `makeValid` | `QgsGeometry` válida o `None` |
| Proyección | `(d, e)` + origen/azimut | `east/north/elev` por vértice | `PolygonZ` por parte |
| Escritura | features + `PolygonZ` | writer + chequeo `hasError` | SHP/GPKG/DXF |
| Estilo | capa memoria + unidades | categorizado 2D + reglas 3D | `.qml` junto al SHP |

---

## 🏛️ Patrones de diseño presentes

| Patrón | Dónde | Propósito |
|--------|-------|-----------|
| **Template Method** | `BaseExporter` → `export` | Contrato común de exportación |
| **Pipeline** | `export` en 5 fases | Cada fase validable por separado |
| **Null Object (skip)** | `_collect_projected_features` | Polígonos degenerados se omiten |
| **Fail fast** | `ExportError` en validación/geometría | Sin marco 3D no hay salida parcial |
| **Graceful degradation** | `HAS_3D`, `_handle_post_export_styles` | Sin `qgis._3d` solo hay estilo 2D; sin QML sigue habiendo SHP |
| **Lazy import** | `qgis._3d`, `QgsVectorFileWriter`, renderers | Módulos pesados solo cuando se usan |

---

## 🧾 Resumen de la API

| Símbolo | Firma / Hereda | Uso típico |
|---------|----------------|------------|
| `Interpretation3DExporter` | `(BaseExporter)` | Polígonos de sección → `PolygonZ` + `.qml` |
| `export` | `(output_path, data, layer_name=None) -> bool` | `data = {"interpretations": [...], "section_line": geom, "crs": ...}` |
| `_validate_export_input` | `(interpretations, section_line) -> bool` | `False` si vacía; `ExportError` sin línea |
| `_prepare_fields` | `(interpretations) -> tuple[list[QgsField], list[str]]` | 5 fijos + custom ordenados |
| `_calculate_section_geometry` | `(section_line) -> tuple[float, float, float]` | `(origin_x, origin_y, azimuth)` |
| `_collect_projected_features` | `(interpretations, fields, sorted_keys, ox, oy, az) -> list[QgsFeature]` | Bucle con `vert_exag=1.0` |
| `_prepare_2d_geometry` | `(polygon) -> QgsGeometry \| None` | Saneo + `makeValid` |
| `_project_to_3d_features` | `(geom_2d, polygon, fields, ox, oy, az, keys, vert_exag=1.0)` | Multi → N features |
| `_create_3d_rings` | `(poly_2d, ox, oy, azimuth, vert_exag) -> list[QgsLineString]` | Rotación azimutal por vértice |
| `_write_shapefile` | `(path, features, fields, wkb_type, crs, layer_name=None) -> bool` | Writer + `ExportError` si falla |
| `_generate_qml_style` | `(shp_path, interpretations, fields, crs) -> None` | Capa memoria → `.qml` |
| `_setup_2d_renderer` / `_configure_3d_renderer` | `(layer, interpretations) -> None` | Categorizado 2D / reglas 3D |

---

## 🛡️ Manejo de errores

| Situación | Comportamiento |
|-----------|----------------|
| `interpretations` vacía | `warning` + `return False` |
| `section_line` ausente | `ExportError` traducido con `QCoreApplication.translate` |
| `_calculate_section_geometry` falla | `ExportError(...) from e` (conserva la causa) |
| Polígono con < 4 vértices tras saneo | `warning` con `polygon.id`; se salta |
| Geometría inválida | `makeValid()` + `info`; si sigue mal, QGIS la escribe igual |
| Writer con error | `ExportError(writer.errorMessage())` |
| Fallo de estilo QML | `warning`; la exportación sigue siendo `True` |
| `qgis._3d` no instalado | `HAS_3D=False`; solo estilo 2D |

> [!note] Único exporter que mezcla `bool` y excepciones
> `False` = "nada que exportar" (benigno); `ExportError` = "marco 3D imposible o
> escritura rota" (estructural). Ver [[exceptions]] para la jerarquía completa.

---

## 🧪 Tests asociados

**Unit** en `tests/exporters/test_interpretation_3d_exporter.py`:

- `test_azimuth_calculation_east` — azimut de una línea este.
- `test_geometric_transformation_north` — proyección con línea norte.
- `test_overturned_fold_geometry` — geometría de pliegue volcado (anillos complejos).

**Integración** (proyección y workflow):

- `tests/integration/test_export_workflow.py::test_3d_projection_logic` y `test_3d_projection_north` — proyección al plano de sección.
- `tests/integration/test_3d_projections.py` — proyecciones 3D de punta a punta.
- `tests/integration/test_export_service_e2e.py::test_export_interpretations_creates_2d_shp` — gemelo 2D e2e.
- `tests/integration/test_interpretation_workflow.py` — workflow de interpretaciones.

---

## 👀 Observaciones y notas

> [!success] Fortalezas
> - Pipeline legible en 5 fases con responsabilidades separadas (validar → campos → sección → proyectar → estilo).
> - Saneo 2D completo (dedup, cierre, conteo mínimo, `makeValid`) antes de tocar Z.
> - `ExportError` con causa encadenada (`from e`) en vez de `False` mudo.
> - Degradación elegante: sin `qgis._3d` o sin QML, el SHP sigue siendo válido.
> - `cos/sin` precalculados por polígono, no por vértice.

> [!warning] Puntos de atención
> - La sección se reduce a primer/último vértice: líneas con quiebros se aplanan a un plano recto.
> - `vert_exag` cableado a `1.0`: el parámetro existe pero el llamante no lo varía.
> - Sin simplificación de vértices: polígonos densos se proyectan punto a punto.

> [!question] Preguntas abiertas
> - ¿Soportar secciones polilínea por tramos (un plano por segmento) en vez de un solo azimut?
> - ¿Exponer `vert_exag` desde `data` para bakear exageración en el SHP?

---

## 🔗 Notas relacionadas

- [[Index]] — índice de la bóveda
- [[exporters]] — fachada del paquete `exporters/`
- [[base_exporter]] — `BaseExporter`, clase base
- [[interpretation_exporters]] — gemelo 2D (`fromPolygonXY`, mismo esquema de campos)
- [[drillhole_3d_exporter]] — el otro writer 3D (`LineStringZ`)
- [[interpretations]] — handler `exp_interp` (dispatch 2D/3D + gate de acceso)
- [[orchestrator]] — `ExportService`, orquestación general
- [[domain]] — `InterpretationPolygon` (`vertices_2d`, `attributes`, `color`)

---

*Nota de la bóveda SecInterp Code Walkthrough v2 — v3.8.0*
