---
tags:
  - secinterp
  - code-walkthrough
  - core
  - export-service
aliases:
  - export_service.py
  - ExportService
cssclass: secinterp-note
---

# `core/services/export_service.py`

> [!abstract] One-line summary
> Orchestrates **all exports** (SHP, GPKG, DXF, CSV + preview PNG/PDF/SVG): decides what to export per `export_options` and delegates to exporters.

**Path**: `core/services/export_service.py` (645 lines)
**Class**: `ExportService`
**Layer**: Core · Services
**Tags**: #secinterp #core #export-service

---

## 🎯 Why does this file exist?

Without a service, `ExportManager` would need to know 12 exporters + data access. This file **centralizes**:

| Flow | Method | Delegates to |
|------|--------|--------------|
| **Data** (SHP/CSV folders) | `export_data(output_folder, params, topo/geol/struct/drill/interp, export_options)` | `Profile*Exporter`, `GeologyVectorExporter`, `Drillhole*Exporter`, `Interpretation*Exporter`, `AxesVectorExporter` |
| **Preview** (image) | `get_map_settings(layers, extent, canvas_size, bg_color) -> QgsMapSettings` | native `QgsMapSettings` |
| **Access** | `AccessControlService` | Gates 3D |

> [!important] Orchestrator, not writer
> It does not write files directly; it builds `features_data` and passes it to exporters (`BaseExporter.export`).

---

## 🧱 `export_data()` — orchestration

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

### `_orchestrate_exports()` (private, ~400 lines)

- Creates `[SectionName]/` subfolder if GPKG multi-layer.
- Conditional per `export_options["exp_topo"]` → `ProfileLineVectorExporter` + `AxesVectorExporter`.
- `exp_geol` → `GeologyVectorExporter`.
- `exp_struct` → `StructureVectorExporter`.
- `exp_drill` → `DrillholeTraceVectorExporter` / `IntervalVectorExporter` + 3D variants if `AccessControl` allows.
- `exp_interp` → `Interpretation2D/3DExporter`.

> [!tip] 3D gated
> `self.access_control.is_3d_enabled()` decides whether `*_3DExporter` are generated.

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

> `ExportManager` uses it for `preview → Image/PDF/SVG` exporters.

---

## 🏛️ Design patterns present

| Pattern | Where | Purpose |
|---------|-------|---------|
| **Orchestrator / Facade** | `export_data` | Hides 12 exporters behind one API |
| **Strategy per format** | `*Exporter` | Each exporter implements `BaseExporter` |
| **Gate** | `AccessControlService` | 3D feature flag |

---

## 🔗 Related notes

- [[base_exporter]] — contract and `validate_export_path`
- [[vector_exporter]] / [[csv_exporter]] — generic exporters
- [[controller]] — `generate_profile_data` (data source)
- `exporters/` — implementations

---

*Note of the SecInterp Code Walkthrough vault — v3.8.0*
