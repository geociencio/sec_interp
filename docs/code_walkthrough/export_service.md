---
tags:
  - secinterp
  - code-walkthrough
  - core
  - export-service
  - orchestrator
aliases:
  - export_service.py
  - ExportService
cssclass: secinterp-note
---

# `core/services/export_service.py`

> [!abstract] Resumen en una línea
> Orquesta **toda la exportación** (SHP, GPKG, DXF, CSV + preview PNG/PDF/SVG): decide qué exportar según `export_options` y delega en los exporters.

**Ruta**: `core/services/export_service.py` (645 líneas)
**Clase**: `ExportService`
**Capa**: Core · Services
**Tags**: #secinterp #core #export-service #orchestrator

---

## 🎯 ¿Por qué existe este archivo?

Sin servicio, `ExportManager` tendría que conocer 12 exporters + acceso a datos. Este archivo **centraliza**:

| Flujo | Método | Delega en |
|-------|--------|-----------|
| **Datos** (carpetas SHP/CSV) | `export_data(output_folder, params, topo/geol/struct/drill/interp, export_options)` | `Profile*Exporter`, `GeologyVectorExporter`, `Drillhole*Exporter`, `Interpretation*Exporter`, `AxesVectorExporter` |
| **Preview** (imagen) | `get_map_settings(layers, extent, canvas_size, bg_color) -> QgsMapSettings` | `QgsMapSettings` nativo |
| **Acceso** | `AccessControlService` | Gatea 3D |

> [!important] Orquestador, no writer
> No escribe ficheros directamente; construye `features_data` y se lo pasa a los exporters (`BaseExporter.export`).

---

## 🧱 `export_data()` — orquestación

```python
def export_data(self, output_folder: Path, params: PreviewParams, profile_data, geol_data, struct_data, drillhole_data=None, interp_data=None, export_options=None) -> list[str]:
    if not any(export_options.values()):
        return [self.tr("⚠ No export options selected. Check Settings tab.")]
    if not profile_data:
        raise DataMissingError(self.tr("No profile data available for export"))
    result_msg = [self.tr("✓ Saving files...")]
    self._orchestrate_exports(output_folder, params, profile_data, geol_data, struct_data, drillhole_data, interp_data, export_options, result_msg)
    result_msg.append(self.tr("\n✓ All files saved to:\n{0}").format(output_folder))
    return result_msg
```

### `_orchestrate_exports()` (privado, ~400 líneas)

- Crea subcarpeta `[SectionName]/` si es GPKG multi-capa.
- Condicional por `export_options["exp_topo"]` → `ProfileLineVectorExporter` + `AxesVectorExporter`.
- `exp_geol` → `GeologyVectorExporter` (polígonos proyectados).
- `exp_struct` → `StructureVectorExporter` (dips).
- `exp_drill` → `DrillholeTraceVectorExporter` / `IntervalVectorExporter` + variantes 3D (`DrillholeTrace3DExporter` si `AccessControl` permite).
- `exp_interp` → `Interpretation2D/3DExporter` (2D polígonos + 3D `PolygonZ`).

> [!tip] 3D gateado
> `self.access_control.is_3d_enabled()` decide si se generan `*_3DExporter` (setting `SecInterp/enable_3d`).

### `get_map_settings()` — preview

```python
def get_map_settings(self, layers, extent: QgsRectangle, canvas_size: QSize, bg_color: QColor) -> QgsMapSettings:
    settings = QgsMapSettings()
    settings.setLayers(layers)
    settings.setExtent(extent)
    settings.setOutputSize(canvas_size)
    settings.setBackgroundColor(bg_color)
    settings.setDestinationCrs(layers[0].crs() if layers else QgsCoordinateReferenceSystem("EPSG:4326"))
    return settings
```

> El `ExportManager` lo usa para `preview → Image/PDF/SVG` exporters.

---

## 🏛️ Patrones de diseño presentes

| Patrón | Dónde | Propósito |
|--------|-------|-----------|
| **Orchestrator / Facade** | `export_data` | Oculta 12 exporters tras una API |
| **Strategy por formato** | `*Exporter` | Cada exporter implementa `BaseExporter` |
| **Gate** | `AccessControlService` | Feature flag 3D |

---

## 🔗 Notas relacionadas

- [[base_exporter]] — contrato y `validate_export_path`
- [[vector_exporter]] / [[csv_exporter]] — exporters genéricos
- [[controller]] — `generate_profile_data` (origen de datos)
- `exporters/` — implementaciones

---

*Nota de la bóveda SecInterp Code Walkthrough — v3.8.0*
