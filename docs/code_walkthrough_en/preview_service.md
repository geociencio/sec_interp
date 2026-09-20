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

> [!abstract] One-line summary
> Orchestrates **synchronous** preview generation (topography + structures + geology) and exposes LOD + services for async tasks.

**Path**: `core/services/preview_service.py` (175 lines)
**Class**: `PreviewService`
**Layer**: Core · Services
**Tags**: #secinterp #core #preview-service

---

## 🎯 Why does this file exist?

`PreviewManager` (GUI) needs **one call** to get the whole preview without knowing 4 services. This service:

| Flow | Method |
|------|--------|
| Sync | `generate_all(params, transform_context) -> PreviewResult` (topo + geol + struct) |
| LOD | `calculate_max_points(canvas_width, manual_max, auto_lod, ratio)` |
| Drillholes async | Exposes `drillhole_service` / `geology_service` for `PreviewTaskOrchestrator` |

> Drillholes are generated **asynchronously** in the GUI; this service only generates the sync part.

---

## 🧱 `generate_all()` — orchestration

```python
def generate_all(self, params: PreviewParams, transform_context) -> PreviewResult:
    with PerformanceTimer("Total Preview Generation"):
        profile_data, geol_data, struct_data, _, messages = self.controller.generate_profile_data(params)
        return PreviewResult(topo=profile_data, geol=geol_data, struct=struct_data, metrics=...)
```

> Delegates to `controller.generate_profile_data` and packs into `PreviewResult`.

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

| Parameter | Role |
|-----------|------|
| `auto_lod` | If `True`, ignores `manual_max` |
| `ratio` | `full_extent / current_extent` → boost on zoom |

---

## 🔗 Related notes

- [[controller]] — `generate_profile_data` (source)
- [[preview_renderer]] — consumes `PreviewResult`
- [[tasks]] — async drillholes

---

*Note of the SecInterp Code Walkthrough vault — v3.8.0*
