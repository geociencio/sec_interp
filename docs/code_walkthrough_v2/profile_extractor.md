---
tags:
  - secinterp
  - code-walkthrough
  - gui
  - adapters
aliases:
  - profile_extractor.py
  - ProfileExtractor
cssclass: secinterp-note
---

# `gui/adapters/profile_extractor.py`

> [!abstract] Resumen en una línea
> Adaptador **Extract** de topografía (`ProfileExtractor`, 86 líneas) que muestrea elevaciones DEM a lo largo de la línea de sección y devuelve `ProfileData` (`list[(distancia, elevación)]` redondeada), más el cálculo del intervalo LOD para el preview.

**Ruta**: `gui/adapters/profile_extractor.py` (86 líneas)
**Clase principal**: `ProfileExtractor`
**Capa**: GUI · Adapter (lado Extract, depende de QGIS)
**Tags**: #secinterp #gui #adapters

---

## 🎯 ¿Por qué existe este archivo?

El perfil topográfico es la base de toda sección: la geología, las estructuras
y los sondajes se dibujan sobre él. Muestrear el DEM exige `QgsRasterLayer` vivo
y `QgsDistanceArea`, ambos prohibidos en el core:

| Problema | Solución |
|----------|----------|
| El core no puede muestrear un raster ni medir distancias | `extract_profile` densifica + muestrea + acumula aquí y devuelve tuplas |
| El preview necesita degradar resolución según el canvas | `calculate_lod_interval` calcula el paso de muestreo desde longitud/ancho |
| Los floats crudos del DEM meten ruido submilimétrico | Redondeo a 1 decimal en la salida (`round(p.x(), 1)`) |
| Sin línea no hay perfil posible | `DataMissingError` / `GeometryError` con `details={"layer": ...}` |

> [!important] Nota arquitectónica
> El adapter más fino del paquete: delega casi todo en `geometry.py`
> (`create_distance_area`, `sample_elevation_along_line`) y solo aporta la
> orquestación, el LOD y el redondeo. Lo llama `ProfileController` en dos
> momentos: `_process_topography` (`extract_profile`) y el preview con LOD
> (`calculate_lod_interval` → `extract_profile(interval=...)`).

---

## 🧬 Diagrama de relaciones

```mermaid
graph TD
    PE["ProfileExtractor"]
    LOD["calculate_lod_interval()"]
    EXT["extract_profile()"]
    GEO["geometry<br/>create_distance_area<br/>sample_elevation_along_line"]
    PD["ProfileData<br/>(domain/entities.py)"]
    CTRL["ProfileController"]
    PREV["PreviewResult.topo"]

    CTRL -->|LOD + perfil| PE
    LOD -->|interval| EXT
    PE --> GEO
    EXT -->|list[(dist, elev)]| PD
    PD --> PREV

    classDef gui fill:#ffe08a,stroke:#b8860b,stroke-width:2px,color:#000
    classDef core fill:#95e1d3,stroke:#38a169,stroke-width:2px,color:#000
    class PE,LOD,EXT,GEO gui
    class PD,PREV core
    classDef ctrl fill:#ff6b6b,stroke:#c92a2a,stroke-width:2px,color:#fff
    class CTRL ctrl
```

> [!tip] Cómo leer
> `ProfileExtractor` es casi un facade sobre `geometry.py`: el valor añadido son
> el intervalo LOD, las guardas de error y el redondeo a décimas.

---

## 📦 Imports — lectura arquitectónica

```python
# gui/adapters/profile_extractor.py
from __future__ import annotations

from qgis.core import QgsRasterLayer, QgsVectorLayer
from qgis.PyQt.QtCore import QCoreApplication

from sec_interp.core.domain import ProfileData
from sec_interp.core.exceptions import DataMissingError, GeometryError
from sec_interp.gui.adapters import geometry
```

| # | Observación |
|---|-------------|
| ① | Solo dos clases `qgis.core` (las mínimas para "línea + raster"): el adapter con menor acoplamiento QGIS del paquete. |
| ② | `qgis.PyQt.QtCore.QCoreApplication` para `self.tr()` con contexto `"ProfileExtractor"` (agnóstico Qt5/Qt6). |
| ③ | Importa el alias `ProfileData` del dominio: la salida está tipada (`list[tuple[float, float]]`) aunque se construya aquí. |
| ④ | Dos excepciones de dominio con `details`: capa vacía (`DataMissingError`) vs geometría nula (`GeometryError`). |
| ⑤ | Todo el trabajo pesado (datum, densificado, muestreo) se delega en `geometry`. |

---

## 🏗️ Inventario de estructura

**Clase:** `class ProfileExtractor` — 3 métodos (`tr` + 2 públicos), sin `__init__` ni estado.

**Métodos:**
- `tr(message)` — traducción con `QCoreApplication.translate("ProfileExtractor", ...)`.
- `calculate_lod_interval(line_lyr, canvas_width)` — `line_len / max(200, canvas_width*2)` o `None` sin línea.
- `extract_profile(line_lyr, raster_lyr, band_number=1, interval=None)` — perfil redondeado a 1 decimal; `interval=None` → resolución del raster.

---

## 📁 Archivos del paquete

El extractor vive en el paquete `gui/adapters/` (fase Extract completa):

| Archivo | Líneas | Rol |
|---|--:|---|
| `__init__.py` | 7 | Docstring del paquete: contrato Extract-then-Compute |
| `drillhole_extractor.py` | 369 | `DrillholeExtractor` → `DrillholeContext` |
| `geology_extractor.py` | 235 | `GeologyExtractor` → `GeologyContext` |
| `geometry.py` | 226 | Helpers QGIS de geometría y muestreo (usado por esta nota) |
| `layer_resolver.py` | 113 | `LayerResolver` + `resolve_layer` (caché de capas) |
| `structure_extractor.py` | 226 | `SectionContext` + `StructureExtractor` |
| `validation_extractor.py` | 176 | `resolve_layer_metadata`, `build_validation_params` |
| `feature_fetcher.py` | 84 | `DataFetcher` (lecturas bulk de hijas) |
| `profile_extractor.py` | 86 | `ProfileExtractor` → `ProfileData` (esta nota) |

---

## 📖 Recorrido método por método

### `tr` — i18n del adaptador

```python
def tr(self, message: str) -> str:
    return QCoreApplication.translate("ProfileExtractor", message)
```

Idéntico patrón que sondajes y geología. Solo se usa en los dos `raise` de
`extract_profile` (`calculate_lod_interval` no genera mensajes: devuelve `None`).

### `calculate_lod_interval` — paso de muestreo según canvas

```python
def calculate_lod_interval(self, line_lyr: QgsVectorLayer, canvas_width: int) -> float | None:
    line_feat = next(line_lyr.getFeatures(), None)
    if not line_feat:
        return None
    line_geom = line_feat.geometry()
    if not line_geom or line_geom.isNull():
        return None
    line_len = line_geom.length()
    max_pts = max(200, int(canvas_width * 2))
    return line_len / max_pts if max_pts > 0 else None
```

| Paso | Detalle |
|------|---------|
| **Guardas** | Sin features o geometría nula → `None` (no excepción: sin LOD se usa resolución nativa). |
| **Presupuesto** | `max(200, canvas_width*2)`: mínimo 200 puntos (legibilidad) y 2 puntos por píxel en canvas grandes (anti-aliasing del perfil). |
| **Paso** | `line_len / max_pts` en unidades del CRS; `max_pts > 0` siempre por el `max`, pero la guarda protege de `canvas_width` negativos extremos. |

> [!note] LOD = Level of Detail
> Un canvas de 800 px pide ~1600 puntos; una sección de 3200 m sale a paso de
> 2 m. El preview se mantiene fluido sin perder fidelidad visible.

### `extract_profile` — muestreo y redondeo

```python
def extract_profile(
    self,
    line_lyr: QgsVectorLayer,
    raster_lyr: QgsRasterLayer,
    band_number: int = 1,
    interval: float | None = None,
) -> ProfileData:
    line_feat = next(line_lyr.getFeatures(), None)
    if not line_feat:
        raise DataMissingError(
            self.tr("Line layer has no features"), {"layer": line_lyr.name()}
        )
    geom = line_feat.geometry()
    if not geom or geom.isNull():
        raise GeometryError(self.tr("Line geometry is not valid"), {"layer": line_lyr.name()})
    da = geometry.create_distance_area(line_lyr.crs())
    points = geometry.sample_elevation_along_line(
        geom, raster_lyr, band_number, da, interval=interval
    )
    return [(round(p.x(), 1), round(p.y(), 1)) for p in points]
```

| Paso | Detalle |
|------|---------|
| **Guardas estrictas** | Aquí sí hay excepciones (a diferencia del LOD): sin línea no hay perfil que degradar. |
| **Datum** | `create_distance_area` con el CRS de la línea (distancias elipsoidales). |
| **Muestreo** | `sample_elevation_along_line` con `interval` del LOD o `None` (→ resolución del raster). |
| **Redondeo** | `round(..., 1)` en distancia y cota: el `QgsPointXY(dist, elev)` del espacio perfil se convierte al `ProfileData` del dominio. |

> [!tip] Doble lectura de la línea
> `calculate_lod_interval` y `extract_profile` leen la primera feature por
> separado (dos iteradores). Si el LOD precede al perfil, la línea se lee dos
> veces; aceptable (primera feature, sin escaneo), pero unifica si se mide
> contención en el proyecto.

---

## 🔄 Flujo de datos

| Fase | Entrada | Transformación | Salida |
|------|---------|----------------|--------|
| LOD | `line_lyr` + `canvas_width` | `length / max(200, w*2)` | `interval` o `None` |
| Guardas | 1ª feature | vacía → `DataMissingError`; nula → `GeometryError` | geometría válida |
| Datum | CRS de la línea | `create_distance_area` | `QgsDistanceArea` |
| Muestreo | línea + DEM + `da` | densificar → acumular → `sample` | `list[QgsPointXY(dist, elev)]` |
| Dominio | puntos perfil | `round(1 decimal)` | `ProfileData` |
| Entrega | `ProfileData` | (vía `controller`) | `PreviewResult.topo` |

---

## 🏛️ Patrones de diseño presentes

| Patrón | Dónde | Propósito |
|--------|-------|-----------|
| **Facade fina** | `extract_profile` | Orquesta `geometry.*` tras validar |
| **LOD (Level of Detail)** | `calculate_lod_interval` | Resolución proporcional al canvas |
| **Fail-fast validado** | `raise` con `details` | Sin línea no hay perfil |
| **Redondeo de dominio** | `round(..., 1)` | Precisión pactada con el render |

---

## 🧾 Resumen de la API

| Símbolo | Firma | Uso típico |
|---------|-------|------------|
| `ProfileExtractor` | clase GUI sin estado | `ProfileExtractor()` (inyectado en el controller) |
| `calculate_lod_interval` | `(line_lyr, canvas_width: int) -> float \| None` | paso previo al preview |
| `extract_profile` | `(line_lyr, raster_lyr, band_number=1, interval=None) -> ProfileData` | perfil topográfico |
| `tr` | `(message: str) -> str` | i18n de los dos errores |

---

## 🛡️ Manejo de errores

| Situación | Comportamiento |
|-----------|----------------|
| LOD sin features / geometría nula | `None` (se usa resolución nativa) |
| Perfil sin features | `DataMissingError` + `details={"layer": ...}` |
| Geometría de perfil nula | `GeometryError` + `details={"layer": ...}` |
| `sample` con `ok=False` (dentro de `geometry`) | elevación `0.0` por punto |

> [!tip] LOD tolerante, perfil estricto
> La asimetría es intencional: el LOD es una optimización (puede faltar) y el
> perfil es un requisito (sin él no hay sección). Cada uno falla a su nivel.

---

## 🧪 Tests asociados

Sin tests dedicados (no existe `test_profile_extractor.py`); cobertura
indirecta:

- `tests/gui/tasks/test_geology_task.py` — tareas que consumen `topo` extraído.
- `tests/integration/test_geology_structure_workflow.py` — perfil integrado de extremo a extremo.
- `tests/integration/test_async_orchestrators.py` — orquestación con `ProfileExtractor` inyectado.
- `tests/core/test_preview_service.py` — el consumidor core de `ProfileData`.
- `tests/core/test_geometry_utils.py` — matemática espejo del muestreo.

> [!warning] Hueco de cobertura
> `calculate_lod_interval` (ancho 0, canvas enorme, línea sin features) y el
> redondeo a 1 decimal son casos mock-first triviales sin test. Un
> `test_profile_extractor.py` de ~50 líneas los cerraría.

---

## 🧵 Thread-safety e i18n

| Aspecto | Detalle |
|---------|---------|
| **Hilo** | `getFeatures`, `create_distance_area` (usa `QgsProject.transformContext`) y `dataProvider().sample` → hilo principal. Solo `ProfileData` (tuplas) viaja al `QgsTask`. |
| **Redondeo** | `round()` sobre floats puros: seguro en cualquier hilo; podría hacerse en el worker, pero aquí mantiene la salida pactada. |
| **i18n** | `self.tr()` con contexto `"ProfileExtractor"` vía `qgis.PyQt`; distancias y cotas no se traducen (datos). |

---

## 📐 `ProfileData` y su redondeo

| Aspecto | Detalle |
|---------|---------|
| **Tipo** | `ProfileData = list[tuple[float, float]]` (`(distancia, elevación)`, ver dominio) |
| **Precisión** | 1 decimal (~10 cm): por debajo del ruido DEM habitual y estable para el hash de caché |
| **LOD típico** | canvas 800 px → ~1600 puntos; `interval = line_len / 1600` |
| **Sin LOD** | `interval=None` → `rasterUnitsPerPixelX` (un vértice por píxel) |

> [!note] El redondeo estabiliza la caché
> `PreviewParams` se hashea para `DataCache`: dos muestreos del mismo DEM con
> ruido float distinto darían claves distintas sin el `round`. Ver
> [[preview_param_hasher]] y [[data_cache]].

---

## 👀 Observaciones y notas

> [!success] Fortalezas
> - Delegación casi total en `geometry.py`: el adapter no duplica matemática.
> - LOD con suelo de 200 puntos: legible incluso en canvas diminutos.
> - Errores con `details` por capa para mensajes GUI precisos.
> - Redondeo que estabiliza render y caché a la vez.

> [!warning] Puntos de atención
> - Doble lectura de la primera feature (LOD + perfil) sin compartir iterador.
> - `extract_profile` no valida el raster (delegado en `geometry`, que devuelve `0.0` por punto): un DEM inválido produce un perfil plano en silencio.
> - `max_pts > 0` inalcanzable por el `max(200, ...)`: guarda defensiva pero muerta.
> - `band_number` sin validar contra `bandCount()` (geología sí lo valida).

> [!question] Preguntas abiertas
> - ¿Validar `raster_lyr.isValid()` y `band_number` aquí como hace `GeologyExtractor`?
> - ¿Compartir la geometría leída entre `calculate_lod_interval` y `extract_profile`?
> - ¿Hacer configurable el decimal del `round` (p. ej. según unidades del CRS)?

---

## 🔗 Notas relacionadas

- [[Index]] — índice de la bóveda
- [[gui_adapters]] — nota de paquete de los adapters Extract
- [[geometry]] — `create_distance_area` y `sample_elevation_along_line` (trabajo real)
- [[controller]] — `ProfileController` (llama LOD + perfil)
- [[dtos]] — `PreviewParams` (`band_num`, `canvas_width`, `auto_lod`) y `PreviewResult.topo`
- [[domain]] — alias `ProfileData`
- [[data_cache]] — caché hasheada que el redondeo estabiliza
- [[drillhole_extractor]] — `pre_sampled_z` con el mismo DEM muestreado aquí

---

*Nota de la bóveda SecInterp Code Walkthrough v2 — v3.8.0*
