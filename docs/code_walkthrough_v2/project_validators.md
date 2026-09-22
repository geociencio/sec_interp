---
tags:
  - secinterp
  - code-walkthrough
  - core      # core | gui | exporters
  - validation     # services | managers | renderers | adapters | validation | etc.
aliases:
  - project_validators.py  # ej. path_resolver.py
  - project_validators     # ej. resolve_export_path
cssclass: secinterp-note
# note_lines: 700      # opcional: tope > 500 para módulos de importancia alta (máx 700)
---

# `core/validation/project_validators.py`

> [!abstract] Resumen en una línea
> Specialized validators for project components (QGIS-agnostic). — qué hace este módulo en una frase, sin tocar QGIS si es core.

**Ruta**: `core/validation/project_validators.py` (240 líneas)
**Clase/Función principal**: `project_validators`
**Capa**: core (QGIS-agnóstico / GUI · Tipo)
**Tags**: #secinterp #core #validation

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
    A["project_validators"]
    A --> B["Dependencia 1"]
    A --> C["Dependencia 2"]
```

> [!tip] Cómo leer
> Flecha sólida = importa/delega; punteada = callback/injectado.

---

## 📦 Imports — lectura arquitectónica

```python
# project_validators.py
from __future__ import annotations
from typing import TYPE_CHECKING
from sec_interp.core.utils.i18n import TranslatableMixin
from sec_interp.core.validation.layer_metadata import GEOMETRY_LINE, KIND_RASTER
from .base_validator import IValidator
from .layer_validator import validate_layer_geometry, validate_layer_has_features, validate_raster_band, validate_structural_requirements
from .validation_helpers import DependencyRule, validate_dependencies, validate_reasonable_ranges
```

| # | Observación |
|---|-------------|
| ① | (pendiente) |
| ② | (pendiente) |

---

## 🏗️ Inventario de estructura

**Clases:** `class SectionValidator` — 1 métodos; `class DEMValidator` — 1 métodos; `class GeologyValidator` — 1 métodos; `class StructureValidator` — 1 métodos; `class DrillholeValidator` — 1 métodos; `class OutputValidator` — 1 métodos
**Funciones/Métodos:**
- `SectionValidator.validate(def validate(self, params: ValidationParams, context: ValidationContext) -> None:)`
- `DEMValidator.validate(def validate(self, params: ValidationParams, context: ValidationContext) -> None:)`
- `GeologyValidator.validate(def validate(self, params: ValidationParams, context: ValidationContext) -> None:)`
- `StructureValidator.validate(def validate(self, params: ValidationParams, context: ValidationContext) -> None:)`
- `DrillholeValidator.validate(def validate(self, params: ValidationParams, context: ValidationContext) -> None:)`
- `OutputValidator.validate(def validate(self, params: ValidationParams, context: ValidationContext) -> None:)`

---

## 📁 Archivos del paquete

- `project_validators.py` — nota individual de este archivo.

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
