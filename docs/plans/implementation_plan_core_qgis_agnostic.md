# Implementation Plan — Make `core/` QGIS-Agnostic

**Status**: MERGEADO en `main` en `af0bfbbb`
**Created**: 2026-10-24
**Scope**: eliminar las 7 dependencias QGIS/PyQt de `core/` sin cambiar comportamiento
**Branch propuesta**: `refactor/core-qgis-agnostic`

---

## 1. Objetivo

`core/` es Python puro como lenguaje (84 archivos `.py`), pero **no es 100 %
QGIS-agnóstico**. La puerta de arquitectura
(`tests/core/test_architecture_boundary.py`) mantiene una allowlist con 7 archivos:

| Archivo | Dependencia | Líneas |
|---|---|---:|
| `core/config.py` | `QgsSettings`, `QCoreApplication` | 253 |
| `core/data_cache.py` | `QCoreApplication` | 169 |
| `core/services/access_control_service.py` | `QgsSettings` | 36 |
| `core/services/export/map_settings_factory.py` | `QgsMapSettings`, `QgsRectangle` | 34 |
| `core/services/export/orchestrator.py` | `QCoreApplication` | 215 |
| `core/utils/i18n.py` | `QCoreApplication` | 30 |
| `core/utils/io.py` | `QgsProject`, `QgsFields`, `QgsVectorFileWriter`… | 106 |

Total: **843 de 8.159 líneas (~10,3 %)**.

El objetivo final es una allowlist **vacía** y que `core/` pueda importarse sin QGIS
para los caminos de negocio, dejando los adaptadores QGIS en `gui/`, `plugin/` o
`exporters/`.

**No es un cambio funcional**: claves de settings, textos, formatos y API pública se
mantienen.

---

## 2. Estrategia

Tres workstreams independientes, en este orden:

1. **i18n** (bajo riesgo) — elimina `QCoreApplication` de 4 archivos.
2. **Settings** (riesgo medio) — elimina `QgsSettings` de 2 archivos.
3. **Export QGIS** (riesgo medio) — mueve `io.py` y `map_settings_factory.py` fuera
   de `core/`.

Cada fase es una rama/PR independiente. No hacer un big-bang: la puerta de
arquitectura exige que la allowlist se reduzca exactamente cuando el archivo queda
limpio.

---

## 3. Fase 1 — Puerto de traducción (i18n)

### Problema

`QCoreApplication.translate` está en:

- `core/utils/i18n.py` (`TranslatableMixin`);
- `core/config.py` (`ConfigService.tr`);
- `core/data_cache.py` (`DataCache.tr`);
- `core/services/export/orchestrator.py` (`ExportService.tr`).

Consumidores: `ProfileController`, `DrillholeService`, `StructureService`,
`OutputValidator` y `PreviewManager` (GUI).

### Diseño

En `core/utils/i18n.py`:

```python
from collections.abc import Callable

Translator = Callable[[str, str], str]

class TranslatableMixin:
    _translator: Translator | None = None

    @classmethod
    def set_translator(cls, translator: Translator | None) -> None:
        cls._translator = translator

    def tr(self, message: str) -> str:
        if self._translator is None:
            return message
        return self._translator(self.__class__.__name__, message)
```

Adaptador Qt fuera de core, por ejemplo `gui/adapters/qt_translator.py` o
`plugin/i18n.py`:

```python
from qgis.PyQt.QtCore import QCoreApplication

def qt_translate(context: str, message: str) -> str:
    return QCoreApplication.translate(context, message)
```

En el composition root (`plugin/lifecycle.py` o `sec_interp_plugin.py`), antes de
crear los servicios:

```python
TranslatableMixin.set_translator(qt_translate)
```

- `ConfigService`, `DataCache` y `ExportService` pasan a usar `TranslatableMixin` o
  un helper `translate(context, message)`; se eliminan sus métodos `tr` duplicados.
- Contextos actuales (`ConfigService`, `DataCache`, `ExportService`, nombre de
  clase) se conservan para no invalidar los 13 catálogos.
- Fallback identity: tests y core puro siguen funcionando sin Qt.
- `PreviewManager` (GUI) puede seguir usando su propio `tr`; no es core.

### Tests

- `TranslatableMixin` sin traductor devuelve el mensaje.
- Con traductor falso, recibe contexto + mensaje.
- `ConfigService`/`DataCache`/`ExportService` conservan contexto.
- `tests/core/test_architecture_boundary.py`: retirar `utils/i18n.py`,
  `config.py` (solo `qgis.PyQt`), `data_cache.py` y
  `services/export/orchestrator.py`.

### Riesgo / tiempo

- **Riesgo**: bajo.
- **Archivos**: ~6-8.
- **Tiempo**: 0,5-1 día.
- **Rollback**: aislado; el fallback identity permite volver sin tocar consumidores.

---

## 4. Fase 2 — Puerto de settings

### Problema

`ConfigService` y `AccessControlService` instancian `QgsSettings()` directamente:

```python
self.settings = QgsSettings()
...
self.settings.value("SecInterp/enable_3d", True, type=bool)
```

`ProfileController` crea `ConfigService()`; `SettingsPage` crea otro
`ConfigService()`; `AccessControlService` es creado por `ExportService`.

### Diseño

Nuevo `core/interfaces/settings_store.py`:

```python
from typing import Any, Protocol

class SettingsStore(Protocol):
    def value(self, key: str, default: Any = None, type: Any = None) -> Any: ...
    def setValue(self, key: str, value: Any) -> None: ...
```

Adaptador fuera de core, `gui/adapters/qgs_settings_store.py`:

```python
class QgsSettingsStore:
    def __init__(self) -> None:
        self._settings = QgsSettings()

    def value(self, key, default=None, type=None):
        return self._settings.value(key, default, type=type)

    def setValue(self, key, value) -> None:
        self._settings.setValue(key, value)
```

`ConfigService`:

```python
class ConfigService:
    def __init__(self, store: SettingsStore) -> None:
        self.settings = store
        self._current_settings: PluginSettings | None = None
```

`AccessControlService`:

```python
class AccessControlService:
    def __init__(self, store: SettingsStore) -> None:
        self.settings = store
```

### Composición

En el composition root (`main_dialog.py` / `plugin`):

```python
settings_store = QgsSettingsStore()
config_service = ConfigService(settings_store)
controller = ProfileController(config_service=config_service)
export_service = ExportService(controller, settings_store=settings_store)
```

Cambios de firma:

- `ProfileController(..., config_service: ConfigService | None = None)`.
- `ExportService(..., access_control: AccessControlService | None = None)`.
- `SettingsPage(config_service: ConfigService | None = None)`.
- `DialogSettingsPersistence` obtiene el service del controller, como hoy.

### Compatibilidad

- **No** mantener `ConfigService()` con un `QgsSettings` por defecto dentro de core:
  volvería a introducir la dependencia.
- Para tests y consumidores puros, usar `DictSettingsStore` en
  `tests/mocks` o `core/adapters` (Python puro).
- Las claves `SecInterp/*` no cambian; no hay migración.

### Tests

- `ConfigService` con `DictSettingsStore`: get/set/defaults/reload.
- `AccessControlService` con store: allow/deny y clave `enable_3d`.
- `ProfileController` recibe el service por DI.
- `SettingsPage`/`DialogSettingsPersistence` reciben el service.
- `test_architecture_boundary.py`: retirar `config.py` (`qgis.core`) y
  `services/access_control_service.py`.

### Riesgo / tiempo

- **Riesgo**: medio (persistencia y orden de inicialización).
- **Archivos**: ~10-12.
- **Tiempo**: 1-2 días.
- **Mitigación**: tests de round-trip de settings y smoke de QGIS.

---

## 5. Fase 3 — Mover escritores QGIS fuera de core

### Problema

- `core/utils/io.py`: `QgsVectorFileWriter`, `QgsProject`, `QgsFields`.
- `core/services/export/map_settings_factory.py`: `QgsMapSettings`.
- `core/services/export/orchestrator.py` importa la factory y `QCoreApplication`.

Callers:

- 10+ exporters import `sec_interp.core.utils.io as scu_io`.
- `exporters/image_exporter.py`, `pdf_exporter.py`, `svg_exporter.py` ya usan
  `QgsMapSettings`.
- `core/services/export/__init__.py` reexporta `create_map_settings`.

### Diseño

1. Mover `core/utils/io.py` → `exporters/qgis_io.py`.
   - Actualizar los ~10 exporters a `from sec_interp.exporters import qgis_io`.
   - Actualizar tests que parchean `scu_io.create_vector_writer`.
2. Mover `map_settings_factory.py` → `exporters/map_settings.py`.
   - `create_map_settings` deja de exportarse desde `core/services/export/__init__.py`.
3. `ExportService` recibe una factory inyectada:

```python
class ExportService:
    def __init__(
        self,
        controller: Any | None = None,
        access_control: AccessControlService | None = None,
        map_settings_factory: Callable[..., Any] | None = None,
    ) -> None:
        ...
        self._map_settings_factory = map_settings_factory
```

En composición:

```python
ExportService(
    controller,
    access_control=AccessControlService(store),
    map_settings_factory=create_map_settings,
)
```

Si no se inyecta factory, `_create_map_settings` lanza un error claro (solo
se usa para export de imagen/PDF/SVG).

4. `core/services/export/__init__.py` deja de reexportar la factory.
5. `core/utils/__init__.py` deja de exportar `create_shapefile_writer`.

### Tests

- `ExportService` con factory falsa verifica que se llama una vez.
- Tests de exporters actualizan patch targets a `exporters.qgis_io`.
- `tests/core/test_architecture_boundary.py`: retirar
  `services/export/map_settings_factory.py`, `utils/io.py` y el `qgis.PyQt`
  de `orchestrator.py`.
- Verificar que `core` no importa `exporters` (dirección correcta); la factory se
  inyecta desde GUI/composition.

### Riesgo / tiempo

- **Riesgo**: medio (muchos patch targets, orden de import).
- **Archivos**: ~15-20.
- **Tiempo**: 1-2 días.
- **Mitigación**: mover primero `io.py` con un commit mecánico; luego factory y
  orquestador; correr suite de exporters en cada paso.

---

## 6. Fase 4 — Cerrar la puerta

- `tests/core/test_architecture_boundary.py`:

```python
CORE_VIOLATIONS: dict[str, frozenset[str]] = {}
```

- Añadir un test que importe los módulos de negocio de core en un subproceso
  **sin QGIS** (mock de import prohibido) o un AST scan que prohíba
  `qgis`/`PyQt` en `core/`.
- Actualizar `core/AGENTS.md` (la restricción pasa a ser real).
- Actualizar `docs/ARCHITECTURE_EN.md`:
  - `core/` 100 % QGIS-agnóstico;
  - adaptadores QGIS en `gui/adapters`, `exporters/`;
  - allowlist vacía.
- Actualizar `docs/plans`/devlog/changelog.

---

## 7. Orden de commits

1. `refactor(core): add translation port` + adapter + tests.
2. `refactor(core): inject settings store` + adapters + composition.
3. `refactor(export): move qgis writer helpers` (mecánico).
4. `refactor(export): move map settings factory` + factory injection.
5. `test(core): close qgis boundary allowlist`.
6. `docs(architecture): mark core qgis-agnostic`.

Cada commit debe pasar la suite completa y la puerta de arquitectura.

---

## 8. Riesgos transversales

| Riesgo | Mitigación |
|---|---|
| Composición olvida inyectar el adapter | tests de `MainDialog`/smoke; fallar explícito |
| Settings no persisten | round-trip `ConfigService`/`AccessControlService` |
| Traducciones pierden contexto | conservar contextos actuales; test de contexto |
| Tests de exporters con patch targets viejos | actualización mecánica + grep de `scu_io` |
| `core` importa `exporters` | factory inyectada; test de dirección de imports |
| Fases mezcladas | ramas/PRs separadas; no big-bang |
| Regresión QGIS 3.28 | suite + smoke QGIS 4; código sin cambios de UI |

---

## 9. Estimación

| Fase | Archivos | Tiempo | Riesgo |
|---|---:|---:|---|
| i18n | 6-8 | 0,5-1 día | Bajo |
| Settings | 10-12 | 1-2 días | Medio |
| Export QGIS | 15-20 | 1-2 días | Medio |
| Cierre/docs | 5-8 | 0,5 día | Bajo |
| **Total** | **~30-40** | **3-5 días** | **Medio** |

No es dramático, pero sí es un refactor arquitectónico real: la mayor parte del
trabajo es composición, tests de patch y verificación de persistencia, no lógica de
negocio.

---

## 10. Criterios de aceptación

- `CORE_VIOLATIONS == {}`.
- Ningún `core/*.py` importa `qgis.*` ni `qgis.PyQt`.
- `ConfigService` y `AccessControlService` reciben un `SettingsStore`.
- `ExportService` recibe la factory de map settings; `qgis_io` vive en `exporters/`.
- Los 13 catálogos de traducción siguen funcionando con los mismos contextos.
- Settings existentes se leen/escriben sin migración.
- Suite completa (≥829) y gates `ruff`, `format`, `mypy`, `check_docs`,
  `forge validate` verdes.
- QGIS 3.28 y QGIS 4 sin regresión.

---

## 11. Resultado

Implementado y mergeado en `main` en `af0bfbbb`:

- `core/` no importa `qgis.*` ni `qgis.PyQt`;
- traducciones, settings y map-settings factory inyectados desde el composition root;
- `exporters/qgis_io.py` y `exporters/map_settings.py`;
- `CORE_VIOLATIONS == {}`;
- `core.controller` y `ExportService` importan en un venv sin QGIS;
- **839 tests OK / 888 static**; gates verdes.
