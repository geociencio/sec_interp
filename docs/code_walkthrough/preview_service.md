---
tags:
  - secinterp
  - code-walkthrough
  - core
  - preview-service
aliases:
  - preview_service.py
  - PreviewService
cssclass: secinterp-note
---

# `core/services/preview_service.py`

> [!abstract] Resumen en una línea
> Orquesta la **generación síncrona** del preview (topografía + estructuras + geología) y expone LOD + servicios para tasks asíncronos.

**Ruta**: `core/services/preview_service.py` (175 líneas)
**Clase**: `PreviewService`
**Capa**: Core · Services
**Tags**: #secinterp #core #preview-service

---

## 🎯 ¿Por qué existe este archivo?

El `PreviewManager` (GUI) necesita **una sola llamada** para obtener todo el preview, sin conocer 4 servicios. Este servicio:

| Flujo | Método |
|-------|--------|
| Síncrono | `generate_all(params, transform_context) -> PreviewResult` (topo + geol + struct) |
| LOD | `calculate_max_points(canvas_width, manual_max, auto_lod, ratio)` |
| Drillholes async | Expone `drillhole_service` / `geology_service` para `PreviewTaskOrchestrator` |

> Drillholes se generan **asíncronamente** en la GUI; este servicio solo genera lo síncrono.

---

## 🧱 `generate_all()` — orquestación

```python
def generate_all(self, params: PreviewParams, transform_context) -> PreviewResult:
    with PerformanceTimer("Total Preview Generation"):
        profile_data, geol_data, struct_data, _, messages = self.controller.generate_profile_data(params)
        # + transform_context para CRS
        return PreviewResult(topo=profile_data, geol=geol_data, struct=struct_data, metrics=...)
```

> Delega en `controller.generate_profile_data` y empaqueta en `PreviewResult`.

---

## 🧱 `calculate_max_points()` — LOD

```python
@staticmethod
def calculate_max_points(canvas_width, manual_max=1000, auto_lod=True, ratio=1.0) -> int:
    if auto_lod:
        base_points = max(200, int(canvas_width * 2))
        if ratio > 1.1:
            detail_boost = 1.0 + (math.log10(ratio) * 0.5)
            return int(base_points * detail_boost)
        return base_points
    return manual_max
```

| Parámetro | Rol |
|-----------|-----|
| `auto_lod` | Si `True`, ignora `manual_max` |
| `ratio` | `full_extent / current_extent` → boost al hacer zoom |

---

## 🔗 Notas relacionadas

- [[controller]] — `generate_profile_data` (origen)
- [[preview_renderer]] — consume `PreviewResult`
- [[tasks]] — drillholes asíncronos

---

*Nota de la bóveda SecInterp Code Walkthrough — v3.8.0*
