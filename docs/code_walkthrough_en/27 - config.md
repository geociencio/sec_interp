---
tags:
  - secinterp
  - code-walkthrough
  - core
  - config
aliases:
  - config.py
  - ConfigService
cssclass: secinterp-note
---

# 27 — `core/config.py`

> [!abstract] One-line summary
> The **configuration service**: reads/writes `QgsSettings` under `SecInterp/` and exposes a validated `PluginSettings`.

**Path**: `core/config.py` (250 lines)
**Class**: `ConfigService`
**Model**: `PluginSettings` in `core/models/settings_model.py`
**Layer**: Core (with `QgsSettings`)
**Tags**: #secinterp #core #config

---

## 🎯 Why does this file exist?

Without a service, every manager would read `QgsSettings` with ad-hoc keys (`"SecInterp/buffer_dist"`). This file **centralizes** them:

| Problem | Solution |
|---------|----------|
| Duplicate keys and scattered defaults | `PREFIX = "SecInterp/"` + `DEFAULT_*` constants |
| Unvalidated dicts | `PluginSettings` (pydantic/dataclass) |
| Repeated reads | Cache `_current_settings` + `reload` flag |

> [!warning] The only QGIS dependency in `core/`
> Of the 6 grey areas documented in `next_steps.md`, this is one: it touches `QgsSettings` (QGIS persistence). A pragmatic exception to *QGIS-agnostic*.

---

## 🧱 `ConfigService` — API

```python
class ConfigService:
    PREFIX = "SecInterp/"
    DEFAULT_SCALE = 50000.0
    DEFAULT_BUFFER_DIST = 100.0
    DEFAULT_VERT_EXAG = 1.0
    # ...

    def __init__(self):
        self.settings = QgsSettings()
        self._current_settings: PluginSettings | None = None

    def get_all_settings(self, reload: bool = False) -> PluginSettings:
        if reload or self._current_settings is None:
            self._current_settings = self._load_from_qgs_settings()
        return self._current_settings

    def get(self, key: str, default: Any = None) -> Any:
        return self.settings.value(self.PREFIX + key, default)

    def set(self, key: str, value: Any) -> None:
        self.settings.setValue(self.PREFIX + key, value)
```

| Method | Role |
|--------|------|
| `get_all_settings(reload)` | Returns cached or reloaded `PluginSettings` |
| `get(key, default)` / `set(key, value)` | Typed wrapper over `QgsSettings` |
| `_load_from_qgs_settings()` | Builds `section/dem/geology/structure/drillhole/export` dict → `PluginSettings` |
| `tr(message)` | `QCoreApplication.translate("ConfigService", ...)` |

---

## 🧱 `PluginSettings` (model)

Groups categories:

```python
PluginSettings(
    section={layer_id, layer_name, buffer_dist},
    dem={layer_id, layer_name, band, scale, vert_exag},
    geology={layer_id, layer_name, field},
    structure={layer_id, layer_name, dip_field, strike_field, dip_scale_factor},
    drillhole={collar_id, survey_*, interval_*},
    export={format, path, ...},
    preview={max_points, dpi, ...},
)
```

> [!tip] Validation
> `PluginSettings` validates ranges (e.g. `band >= 1`). This prevents the GUI from saving junk.

---

## 🔗 Related notes

- [[00 - Index]] — vault index
- [[10 - controller]] — `controller.reload_settings()` and `settings`
- [[20 - main_dialog]] — `StateManager` persists via `ConfigService`

---

*Note 27 of the SecInterp Code Walkthrough vault — v3.8.0*
