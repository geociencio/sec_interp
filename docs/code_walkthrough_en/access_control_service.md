---
tags:
  - secinterp
  - code-walkthrough
  - core
  - access-control
aliases:
  - access_control_service.py
  - AccessControlService
cssclass: secinterp-note
---

# `core/services/access_control_service.py`

> [!abstract] One-line summary
> Gates **restricted features** (e.g. 3D export) via `QgsSettings` (`SecInterp/enable_3d`).

**Path**: `core/services/access_control_service.py` (36 lines)
**Class**: `AccessControlService`
**Layer**: Core · Services
**Tags**: #secinterp #core #access-control

---

## 🧱 `can_export_3d()` — gate

```python
def can_export_3d(self) -> bool:
    allowed = self.settings.value("SecInterp/enable_3d", True, type=bool)
    if not allowed:
        logger.info("Access denied for restricted feature: 3D Export")
    return bool(allowed)
```

> Defaults to **enabled**; user opts out in Settings.

---

## 🔗 Related notes

- [[export_service]] — checks it before `*_3DExporter`

---

*Note of the SecInterp Code Walkthrough vault — v3.8.0*
