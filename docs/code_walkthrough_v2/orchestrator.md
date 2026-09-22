---
tags:
  - secinterp
  - code-walkthrough
  - core      # core | gui | exporters
  - general     # services | managers | renderers | adapters | validation | etc.
aliases:
  - orchestrator.py  # ej. path_resolver.py
  - orchestrator     # ej. resolve_export_path
cssclass: secinterp-note
note_lines: 700
---

# `core/services/export/orchestrator.py`

> [!abstract] Resumen en una línea
> Export orchestrator — thin facade delegating to handlers. — qué hace este módulo en una frase, sin tocar QGIS si es core.

**Ruta**: `core/services/export/orchestrator.py` (207 líneas)
**Clase/Función principal**: `orchestrator`
**Capa**: core (QGIS-agnóstico / GUI · Tipo)
**Tags**: #secinterp #core #general

---

## 🎯 ¿Por qué existe este archivo?

| Problema | Solución |
|----------|----------|
| (pendiente) | (pendiente) |
| (pendiente) | (pendiente) |

> [!important] Nota arquitectónica
> QGIS-agnóstico (p. ej. "QGIS-agnóstico", "Adapter Extract", "Factory").

---

## 🧬 Diagrama de relaciones

```mermaid
graph TD
    A["orchestrator"]
    A --> B["Dependencia 1"]
    A --> C["Dependencia 2"]
```

> [!tip] Cómo leer
> Flecha sólida = importa/delega; punteada = callback/injectado.

---

## 📦 Imports — lectura arquitectónica

```python
# orchestrator.py
from __future__ import annotations
from pathlib import Path
from typing import Any
from qgis.PyQt.QtCore import QCoreApplication
from sec_interp.core.domain import PreviewParams
from sec_interp.core.exceptions import DataMissingError
from sec_interp.core.services.access_control_service import AccessControlService
from sec_interp.logger_config import get_logger
```

| # | Observación |
|---|-------------|
| ① | (pendiente) |
| ② | (pendiente) |

---

## 🏗️ Inventario de estructura

**Clases:** `class ExportService` — 6 métodos
**Funciones/Métodos:**
- `ExportService.__init__(def __init__(self, controller: Any | None=None) -> None:)`
- `ExportService.tr(def tr(self, message: str) -> str:)`
- `ExportService.export_data(def export_data(self, output_folder: Path, params: PreviewParams, profile_data: list[tuple], geol_data: list[Any] | None, struct_data: list[Any] | None, drillhole_data: list[Any] | None=None, interp_data: list[Any] | None=None, export_options: dict[str, bool] | None=None) -> list[str]:)`
- `ExportService._resolve_layers(def _resolve_layers(self, params: PreviewParams) -> tuple[Any, Any]:)`
- `ExportService._orchestrate_exports(def _orchestrate_exports(self, folder: Path, params: PreviewParams, profile_data: list[tuple], geol_data: list[Any] | None, struct_data: list[Any] | None, drillhole_data: list[Any] | None, interp_data: list[Any] | None, options: dict[str, Any], msg: list[str]) -> None:)`
- `ExportService.get_map_settings(def get_map_settings(self, layers: list[Any], extent: Any, size: Any | None, background_color: Any) -> Any:)`

---

## 📁 Archivos del paquete

- `orchestrator.py` — nota individual de este archivo.

---

## 📖 Recorrido método por método

### `método_1`

```python
# (enriquecer)
```

_(enriquecer leyendo el fuente)_

### `método_2`

```python
# (enriquecer)
```

_(enriquecer leyendo el fuente)_

<!-- Añade una subsección por cada método público del módulo -->

---

## 🔄 Flujo de datos

| Fase | Entrada | Transformación | Salida |
|------|---------|----------------|--------|
| - | - | - | - |
| - | - | - | - |

---

## 🏛️ Patrones de diseño presentes

| Patrón | Dónde | Propósito |
|--------|-------|-----------|
| - | - | - |

---

## 🧾 Resumen de la API

| Símbolo | Firma / Hereda | Uso típico |
|---------|----------------|------------|
| (no symbols) | `-` | - |

---

## 🛡️ Manejo de errores

_(pendiente)_

---

## 🧪 Tests asociados

_(pendiente)_

---

## 👀 Observaciones y notas

> [!success] Fortalezas
> - (skeleton)

> [!warning] Puntos de atención
> - (skeleton)

> [!question] Preguntas abiertas
> - (skeleton)

---

## 🔗 Notas relacionadas

- [[Index]] — índice de la bóveda
- [[Index]] — índice
- [[controller]] — orquestador

---

*Nota de la bóveda SecInterp Code Walkthrough v2 — v3.8.0*
