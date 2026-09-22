---
tags:
  - secinterp
  - code-walkthrough
  - core
  - export
  - orchestrator
aliases:
  - orchestrator.py
  - ExportService
cssclass: secinterp-note
note_lines: 700
---

# `core/services/export/orchestrator.py`

> [!abstract] Resumen en una línea
> Fachada de exportación del core: recibe los datos ya calculados del perfil y **orquesta** la escritura CSV/vectorial por entidad, delegando en los handlers según las opciones y resolviendo capas, CRS y formato.

**Ruta**: `core/services/export/orchestrator.py` (207 líneas)
**Clase principal**: `ExportService(ExportServiceCompatMixin)`
**Capa**: Core (zona gris: importa `QCoreApplication` para `tr()`)
**Tags**: #secinterp #core #export #orchestrator

---

## 🎯 ¿Por qué existe este archivo?

La GUI ya tiene los datos de perfil calculados (`profile_data`, `geol_data`, …). Alguien
debe decidir **qué** se exporta, **cómo** (formato) y **a dónde** (rutas), sin que cada
entidad repita la lógica. `ExportService` centraliza esa decisión:

| Problema | Solución |
|----------|----------|
| Exportar 6 entidades distintas con una sola llamada | `export_data(...)` con un dict de opciones |
| Elegir formato (SHP/GPKG/DXF) sin lógica dispersa | `_orchestrate_exports` deriva `format_ext` de settings |
| Desacoplar el core del módulo `exporters/` | Imports **lazy** dentro de `_orchestrate_exports` |
| Validar capas mínimas antes de escribir | `_resolve_layers` lanza `DataMissingError` |
| Traducir mensajes sin acoplar a la GUI | `tr()` vía `QCoreApplication.translate` |

> [!important] Nota arquitectónica — zona gris
> `orchestrator.py` **importa** `qgis.PyQt.QtCore.QCoreApplication` (para `tr()`). Es una
> excepción controlada a la regla "core QGIS-agnóstico": el shim `qgis.PyQt` se usa solo
> para traducción (ver `tests/core/test_architecture_boundary.py`). El import de `qgis.core`
> pesado queda **aislado** en `map_settings_factory.py`.

---

## 🧬 Diagrama de relaciones

```mermaid
graph TD
    GUI["GUI (dialog_export_manager)"]
    SHIM["core/services/export_service.py (shim)"]

    GUI -->|export_data(...)| EXP["ExportService"]
    SHIM -->|re-export| EXP

    EXP -->|hereda| COMPAT["ExportServiceCompatMixin"]
    EXP --> CTRL["ProfileController (Any)"]
    EXP --> AC["AccessControlService"]
    EXP --> MAPF["create_map_settings (factory)"]

    EXP -->|_orchestrate_exports| CSV["CSVExporter"]
    EXP --> TOPO["handlers/topography.py"]
    EXP --> AXES["handlers/axes.py"]
    EXP --> GEO["handlers/geology.py"]
    EXP --> STR["handlers/structures.py"]
    EXP --> DH["handlers/drillholes.py"]
    EXP --> DH3["handlers/drillholes_3d.py"]
    EXP --> INTERP["handlers/interpretations.py"]

    classDef core fill:#95e1d3,stroke:#38a169,stroke-width:2px,color:#000
    classDef gray fill:#ffe08a,stroke:#f4a261,stroke-width:2px,color:#000
    classDef gui fill:#4ecdc4,stroke:#0a9396,stroke-width:2px,color:#000
    class EXP,COMPAT,AC,CSV core
    class MAPF gray
    class GUI,SHIM gui
```

> [!tip] Cómo leer
> `ExportService` es un **punto único**: la GUI entra por `export_data`, y el servicio
> dispersa el trabajo hacia los handlers según `options`. `COMPAT` (el mixin) aporta la
> API legacy; `MAPF` (la factory) aísla el único import de `qgis.core`.

---

## 📦 Imports — lectura arquitectónica

```python
"""Export orchestrator — thin facade delegating to handlers."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from qgis.PyQt.QtCore import QCoreApplication          # ①

from sec_interp.core.domain import PreviewParams       # ②
from sec_interp.core.exceptions import DataMissingError
from sec_interp.core.services.access_control_service import AccessControlService
from sec_interp.logger_config import get_logger

from .compat import ExportServiceCompatMixin           # ③
from .map_settings_factory import create_map_settings  # ④

logger = get_logger(__name__)
```

```python
# imports lazy dentro de _orchestrate_exports (no en cabecera)
from sec_interp.exporters import CSVExporter
from .handlers import axes as axes_h
from .handlers import drillholes as dh_h
from .handlers import drillholes_3d as dh3_h
from .handlers import geology as geo_h
from .handlers import interpretations as interp_h
from .handlers import structures as struct_h
from .handlers import topography as topo_h
```

| # | Observación |
|---|-------------|
| ① | `QCoreApplication` = única excepción QGIS; se usa solo para `tr()`. |
| ② | `PreviewParams` es el DTO de entrada (tipos QGIS como `Any` en su interior). |
| ③ | `ExportServiceCompatMixin` aporta la API legacy `_export_*` (ver [[compat]]). |
| ④ | `create_map_settings` aísla el import de `qgis.core` en `map_settings_factory.py`. |
| ⑤ | Los handlers y `CSVExporter` se importan **lazy** para no cargar `exporters/` en el import del paquete. |

---

## 🏗️ Inventario de estructura

**Clases:** `class ExportService(ExportServiceCompatMixin)` — 6 métodos propios + 7 heredados del mixin.

**Funciones/Métodos propios:**
- `__init__(controller: Any | None = None)` — guarda `controller` y crea `AccessControlService`
- `tr(message: str) -> str` — traducción vía `QCoreApplication.translate`
- `export_data(output_folder, params, profile_data, geol_data, struct_data, drillhole_data, interp_data, export_options) -> list[str]` — entrada principal
- `_resolve_layers(params) -> tuple[Any, Any]` — valida y devuelve `(line_layer, raster_layer)`
- `_orchestrate_exports(folder, params, …) -> None` — tabla de handlers + dispatch
- `get_map_settings(layers, extent, size, background_color) -> Any` — delega a `create_map_settings`

**Atributos:**
- `self.controller` — `ProfileController | None`
- `self.access_control` — `AccessControlService` (gate 3D)

---

## 📁 Archivos del paquete

| Archivo | Líneas | Rol |
|---|--:|---|
| `__init__.py` | 9 | Re-exports `ExportService`, `create_map_settings`, `get_profile_name`, `resolve_export_path` |
| `orchestrator.py` | 207 | `ExportService` — fachada de exportación |
| `compat.py` | 129 | `ExportServiceCompatMixin` — wrappers legacy |
| `path_resolver.py` | 60 | Resolución de rutas y nombres |
| `map_settings_factory.py` | 34 | `create_map_settings` — aísla `qgis.core` |
| `handlers/` | ~490 | Siete handlers por entidad |

> [!note] Shim externo
> `core/services/export_service.py` (fuera del paquete) re-exporta `ExportService` para
> mantener `from sec_interp.core.services.export_service import ExportService` en tests.

---

## 📖 Recorrido método por método

### `__init__`

```python
def __init__(self, controller: Any | None = None) -> None:
    self.controller = controller
    self.access_control = AccessControlService()
```

Constructor mínimo. `controller` es opcional y tipado `Any` (realmente un
`ProfileController`); se usa para recargar settings y derivar el nombre del perfil.
`AccessControlService` decide si el usuario puede exportar 3D.

### `tr`

```python
def tr(self, message: str) -> str:
    return QCoreApplication.translate("ExportService", message)  # type: ignore[no-any-return]
```

Traduce mensajes de usuario. Es el único punto donde el módulo toca QGIS. Todos los
mensajes de `result_msg` pasan por aquí (i18n).

### `export_data` — entrada principal

```python
def export_data(
    self, output_folder: Path, params: PreviewParams,
    profile_data: list[tuple], geol_data: list[Any] | None,
    struct_data: list[Any] | None, drillhole_data: list[Any] | None = None,
    interp_data: list[Any] | None = None,
    export_options: dict[str, bool] | None = None,
) -> list[str]:
    if export_options is None:
        export_options = {
            "exp_topo": True, "exp_geol": True, "exp_struct": True,
            "exp_drill": True, "exp_interp": True,
        }
    logger.info(f"Export options: {export_options}")

    if not any(export_options.values()):
        logger.warning("All export options are disabled. Nothing will be exported.")
        return [self.tr("⚠ No export options selected. Check Settings tab.")]

    if not profile_data:
        raise DataMissingError(self.tr("No profile data available for export"))

    line_layer = params.line_layer
    if not line_layer:
        raise DataMissingError(self.tr("Section line layer not found in parameters"))

    result_msg = [self.tr("✓ Saving files...")]
    self._orchestrate_exports(
        output_folder, params, profile_data, geol_data, struct_data,
        drillhole_data, interp_data, export_options, result_msg,
    )
    result_msg.append(self.tr("\n✓ All files saved to:\n{0}").format(output_folder))
    return result_msg
```

| Paso | Comportamiento |
|------|----------------|
| 1. Opciones | Si `export_options` es `None`, activa las 5 entidades por defecto |
| 2. Guardia | Si **ninguna** opción está activa, retorna un mensaje de aviso (no exporta) |
| 3. Validación | Lanza `DataMissingError` si `profile_data` está vacío o falta `line_layer` |
| 4. Orquestación | Delega en `_orchestrate_exports`, acumulando mensajes en `result_msg` |
| 5. Cierre | Añade el resumen final con la carpeta de destino |

> [!important] `export_data` es una fachada de dos niveles
> Hace la validación/guardas y luego delega TODO el trabajo a `_orchestrate_exports`.
> El retorno `list[str]` es el canal de feedback hacia la GUI (sin señales Qt).

### `_resolve_layers`

```python
def _resolve_layers(self, params: PreviewParams) -> tuple[Any, Any]:
    line_layer = params.line_layer
    if not line_layer or not line_layer.isValid():
        raise DataMissingError(self.tr("Section line layer not found or invalid"))
    raster_layer = params.raster_layer
    return line_layer, raster_layer
```

Valida que `line_layer` exista y sea válido (llama `isValid()`, un método QGIS que
cruza tipado como `Any`). Devuelve `(line_layer, raster_layer)`; `raster_layer` puede
ser `None` (no se valida aquí porque solo estructuras lo usan).

### `_orchestrate_exports` — núcleo de orquestación

```python
def _orchestrate_exports(
    self, folder: Path, params: PreviewParams, profile_data: list[tuple],
    geol_data: list[Any] | None, struct_data: list[Any] | None,
    drillhole_data: list[Any] | None, interp_data: list[Any] | None,
    options: dict[str, Any], msg: list[str],
) -> None:
    from sec_interp.exporters import CSVExporter
    from .handlers import axes as axes_h
    from .handlers import drillholes as dh_h
    from .handlers import drillholes_3d as dh3_h
    from .handlers import geology as geo_h
    from .handlers import interpretations as interp_h
    from .handlers import structures as struct_h
    from .handlers import topography as topo_h

    line_layer, raster_layer = self._resolve_layers(params)
    line_crs = line_layer.crs()

    export_settings = None
    if self.controller is not None:
        reload_func = getattr(self.controller, "reload_settings", None)
        if reload_func:
            reload_func()
        settings_obj = getattr(self.controller, "settings", None)
        if settings_obj:
            export_settings = getattr(settings_obj, "export", None)

    format_ext = ".shp"
    if export_settings:
        if export_settings.default_format == "GeoPackage":
            format_ext = ".gpkg"
        elif export_settings.default_format == "DXF":
            format_ext = ".dxf"

    csv_exporter = CSVExporter({})

    def topo_handler(settings=export_settings, ext=format_ext) -> None:
        topo_h.export_topography(
            folder, profile_data, line_crs, csv_exporter, msg,
            self.controller, settings, ext,
        )
        axes_h.export_axes(
            folder, profile_data, line_crs, msg, self.controller, settings, ext,
        )

    handlers = {
        "exp_topo": topo_handler,
        "exp_geol": lambda: geo_h.export_geology(
            folder, geol_data, line_crs, csv_exporter, msg,
            self.controller, export_settings, format_ext,
        ),
        "exp_struct": lambda: struct_h.export_structures(
            folder, struct_data, raster_layer, line_crs, csv_exporter, msg,
            options, self.controller, export_settings, format_ext,
        ),
        "exp_drill": lambda: dh_h.export_drillholes(
            folder, drillhole_data, line_crs, msg, self.controller, export_settings, format_ext,
        ),
        "exp_drill_3d": lambda: dh3_h.export_drillholes_3d(
            folder, drillhole_data, line_crs, msg, options,
            self.controller, export_settings, format_ext,
        ),
        "exp_interp": lambda: interp_h.export_interpretations(
            folder, interp_data, line_layer, line_crs, msg,
            self.controller, export_settings, format_ext, self.access_control,
        ),
    }
    for opt, handler in handlers.items():
        if options.get(opt, True):
            handler()
```

| Etapa | Detalle |
|-------|---------|
| **Resolución** | `_resolve_layers` + `line_crs = line_layer.crs()` (CRS real de la línea) |
| **Settings** | Si hay `controller`, recarga settings y lee `settings.export.default_format` |
| **Formato** | `default_format`: `GeoPackage → .gpkg`, `DXF → .dxf`, resto `→ .shp` |
| **Dispatch** | `handlers` es un **dict de callables** indexado por la opción |
| **Topo especial** | `topo_handler` es un closure que exporta topografía **y** ejes juntos |

> [!important] Tabla de dispatch (`handlers`)
> Es el corazón del patrón **Registry/Command**: cada clave de opción mapea a un callable.
> El bucle final `for opt, handler in handlers.items()` ejecuta solo los habilitados.
> Nota: `exp_drill_3d` **no** está en el dict por defecto de `export_data`, pero el
> dispatch lo soporta si `options` lo incluye.

> [!tip] `exp_topo` usa closure, el resto `lambda`
> `topo_handler` necesita dos llamadas (topografía + ejes), por eso es una función con
> `def`; el resto son `lambda` de una sola llamada. Ambos capturan `format_ext`/`export_settings`.

### `get_map_settings`

```python
def get_map_settings(
    self, layers: list[Any], extent: Any, size: Any | None, background_color: Any,
) -> Any:
    return create_map_settings(layers, extent, size, background_color)
```

Delega en `create_map_settings` (la factory que aísla `qgis.core`). Usado para render de
canvas/imagen. Retorno `Any` (= `QgsMapSettings`) para no importar QGIS aquí.

---

## 🔄 Flujo de datos

| Fase | Entrada | Transformación | Salida |
|------|---------|----------------|--------|
| Entrada | `(output_folder, params, profile_data, …)` | validación de opciones y datos | `list[str]` mensajes |
| Resolución | `params.line_layer` | `isValid()` + `crs()` | `(line_layer, raster_layer)`, `line_crs` |
| Formato | `settings.export.default_format` | mapa `.shp/.gpkg/.dxf` | `format_ext` |
| Dispatch | `options` (dict de flags) | bucle `handlers` | llamada a cada handler habilitado |
| Escritura | `data` + `crs` + `csv_exporter` | `exporter.export(...)` | archivos CSV + vector |

---

## 🏛️ Patrones de diseño presentes

| Patrón | Dónde | Propósito |
|--------|-------|-----------|
| **Facade** | `ExportService` / `export_data` | Una sola entrada para todo el subsistema de export |
| **Registry / Dispatch table** | dict `handlers` | Mapear opciones → callables y ejecutar solo los activos |
| **Command (callables)** | `topo_handler` y `lambda`s | Encapsular cada exportación como objeto invocable |
| **Strategy (formato)** | `format_ext` | Conmutar SHP/GPKG/DXF según settings |
| **Factory** | `CSVExporter({})` / `create_map_settings` | Crear colaboradores sin acoplar a sus constructores |
| **Mixin** | `ExportServiceCompatMixin` | Añadir API legacy sin herencia profunda |
| **Lazy import** | imports dentro de `_orchestrate_exports` | Evitar cargar `exporters/` en tiempo de import |

---

## 🧾 Resumen de la API

| Símbolo | Firma / Hereda | Uso típico |
|---------|----------------|------------|
| `ExportService` | `(ExportServiceCompatMixin)` | Fachada de exportación |
| `__init__` | `(controller: Any | None = None) -> None` | Guardar controller + access_control |
| `tr` | `(message: str) -> str` | Traducción de mensajes |
| `export_data` | `(output_folder, params, profile_data, geol_data, struct_data, drillhole_data=None, interp_data=None, export_options=None) -> list[str]` | Exportación completa |
| `_resolve_layers` | `(params) -> tuple[Any, Any]` | Validar capa de sección |
| `_orchestrate_exports` | `(folder, params, …, options, msg) -> None` | Dispatch a handlers |
| `get_map_settings` | `(layers, extent, size, background_color) -> Any` | Crear `QgsMapSettings` |

---

## 🛡️ Manejo de errores

| Situación | Comportamiento |
|-----------|----------------|
| `export_options` todo en `False` | No exporta; retorna aviso `⚠ No export options selected` |
| `profile_data` vacío | Lanza `DataMissingError` |
| `params.line_layer` ausente | Lanza `DataMissingError` |
| `line_layer` inválido (`_resolve_layers`) | Lanza `DataMissingError` |
| Error en un handler | El handler envuelve en `ExportError` y **propaga** (no se captura aquí) |
| `controller` es `None` | Se salta la recarga de settings y usa `.shp` por defecto |

> [!note] Sin `try/except` en el orquestador
> El orquestador confía en la jerarquía `SecInterpError` (ver [[exceptions]]) para tipar
> los fallos. Cada handler decide si aborta (`raise ExportError`) o sigue (early-return
> cuando `data` es vacío). El orquestador solo **valida precondiciones** con
> `DataMissingError`.

---

## 🧪 Tests asociados

**Unit (mock-first)** en `tests/core/test_export_service.py`:

- `test_export_data_minimal` — topografía + ejes con mocks de exporters.
- `test_export_data_all_types` — geología, estructuras, sondajes e interpretaciones.
- `test_export_data_3d_restricted` — gate 3D vía `AccessControlService`.
- `test_export_data_missing_profile` — `DataMissingError` sin `profile_data`.
- `test_export_data_no_line_layer` — `DataMissingError` sin `line_layer`.
- `test_export_*_error` (geology/structures/drillholes/axes/interpretation/topography) — propagación de `ExportError`.
- `test_get_map_settings` — delegación a `create_map_settings`.

**Integración** en `tests/integration/test_export_service_e2e.py` (con QGIS real):

- `test_export_topography_creates_csv` / `_creates_shp` — escritura real de archivos.
- `test_export_nothing_when_all_options_disabled` — guardia de opciones.
- `test_export_raises_when_no_profile_data` — validación.
- `test_export_geology_creates_csv_and_shp`, `test_export_interpretations_creates_2d_shp`, etc.

**Flujo completo** en `tests/integration/test_export_workflow.py` (lógica de proyección 3D).

---

## 👀 Observaciones y notas

> [!success] Fortalezas
> - Fachada limpia: una sola entrada, retorno `list[str]` sin señales Qt.
> - Tabla de dispatch declarativa (`handlers`) fácil de extender.
> - Imports lazy aíslan el módulo pesado `exporters/`.
> - `qgis.core` queda aislado en `map_settings_factory.py`; el resto usa `Any`.

> [!warning] Puntos de atención
> - **Zona gris**: importa `QCoreApplication` en un módulo del "core" (excepción documentada).
> - `exp_drill_3d` no figura en el dict por defecto de `export_data`: depende de que `options` lo inyecte.
> - `_resolve_layers` valida `line_layer` pero no `raster_layer` (asimetría sutil).
> - Mensajes de UI (`✓ Saving files...`) se construyen en el core; el formateo debería ser de la GUI.
> - Duplicación de firmas: `_orchestrate_exports` repite casi todos los parámetros de `export_data`.

> [!question] Preguntas abiertas
> - ¿Añadir `exp_drill_3d` al dict por defecto para simetría con `exp_drill`?
> - ¿Mover el formato de mensajes (`✓ …`, emojis) a la capa GUI?
> - ¿Unificar la validación de capas (`line` y `raster`) en `_resolve_layers`?
> - ¿Extraer la tabla `handlers` a un `Mapping` declarativo en un módulo propio?

---

## 🔗 Notas relacionadas

- [[Index]] — índice de la bóveda
- [[compat]] — `ExportServiceCompatMixin`, mixin heredado por esta clase
- [[path_resolver]] — `get_profile_name` / `resolve_export_path`
- [[core_services_export_handlers]] — los siete handlers a los que delega
- [[core_services_export]] — paquete `export/` (re-exports)
- [[controller]] — `self.controller` (origen de settings y datos)
- [[dtos]] — `PreviewParams`, DTO de entrada
- [[exceptions]] — `DataMissingError` / `ExportError`
- [[topography]] / [[geology]] / [[structures]] / [[drillholes]] / [[drillholes_3d]] / [[interpretations]] — handlers individuales

---

*Nota de la bóveda SecInterp Code Walkthrough v2 — v3.8.0*
