---
tags:
  - secinterp
  - code-walkthrough
  - core
  - config
  - settings
aliases:
  - config.py
  - ConfigService
  - PluginSettings
cssclass: secinterp-note
---

# 27 — `core/config.py`

> [!abstract] Resumen en una línea
> Es el **servicio de configuración**: lee/escribe `QgsSettings` bajo `SecInterp/` y expone un `PluginSettings` validado.

**Ruta**: `core/config.py` (250 líneas)
**Clase**: `ConfigService`
**Modelo**: `PluginSettings` en `core/models/settings_model.py`
**Capa**: Core (con `QgsSettings`)
**Tags**: #secinterp #core #config #settings

---

## 🎯 ¿Por qué existe este archivo?

Sin servicio, cada manager leería `QgsSettings` con claves sueltas (`"SecInterp/buffer_dist"`). Este archivo **centraliza**:

| Problema | Solución |
|----------|----------|
| Claves duplicadas y defaults dispersos | `PREFIX = "SecInterp/"` + constantes `DEFAULT_*` |
| Dicts sin validar | `PluginSettings` (pydantic/dataclass) |
| Lectura repetida | Caché `_current_settings` + `reload` flag |

> [!warning] La única dependencia QGIS en `core/`
> De las ~6 áreas grises documentadas en `next_steps.md`, esta es una: toca `QgsSettings` (persistencia QGIS). Es una excepción pragmática al *QGIS-agnostic*.

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

| Método | Rol |
|--------|-----|
| `get_all_settings(reload)` | Devuelve `PluginSettings` cacheado o recargado |
| `get(key, default)` / `set(key, value)` | Wrapper tipado sobre `QgsSettings` |
| `_load_from_qgs_settings()` | Construye dict `section/dem/geology/structure/drillhole/export` → `PluginSettings` |
| `tr(message)` | `QCoreApplication.translate("ConfigService", ...)` |

---

## 🧱 `PluginSettings` (modelo)

Agrupa categorías:

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

> [!tip] Validación
> `PluginSettings` valida rangos (p. ej. `band >= 1`). Así la GUI no guarda basura.

---

## 🔗 Notas relacionadas

- [[00 - Index]] — índice de la bóveda
- [[10 - controller]] — `controller.reload_settings()` y `settings`
- [[20 - main_dialog]] — `StateManager` persiste vía `ConfigService`

---

*Nota 27 de la bóveda SecInterp Code Walkthrough — v3.8.0*
