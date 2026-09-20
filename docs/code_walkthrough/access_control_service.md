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

> [!abstract] Resumen en una línea
> Gatea **features restringidas** (p. ej. export 3D) vía `QgsSettings` (`SecInterp/enable_3d`).

**Ruta**: `core/services/access_control_service.py` (36 líneas)
**Clase**: `AccessControlService`
**Capa**: Core · Services
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

> Default **enabled**; el usuario lo desactiva en Settings.

---

## 🔗 Notas relacionadas

- [[export_service]] — lo consulta antes de `*_3DExporter`

---

*Nota de la bóveda SecInterp Code Walkthrough — v3.8.0*
