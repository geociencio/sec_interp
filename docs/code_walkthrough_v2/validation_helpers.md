---
tags:
  - secinterp
  - code-walkthrough
  - core      # core | gui | exporters
  - general     # services | managers | renderers | adapters | validation | etc.
aliases:
  - validation_helpers.py  # ej. path_resolver.py
  - validation_helpers     # ej. resolve_export_path
cssclass: secinterp-note
# note_lines: 700      # opcional: tope > 500 para módulos de importancia alta (máx 700)
---

# `core/validation/validation_helpers.py`

> [!abstract] Resumen en una línea
> Helper classes and functions for Level 2 (Business Validation). — qué hace este módulo en una frase, sin tocar QGIS si es core.

**Ruta**: `core/validation/validation_helpers.py` (195 líneas)
**Clase/Función principal**: `validation_helpers`
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
    A["validation_helpers"]
    A --> B["Dependencia 1"]
    A --> C["Dependencia 2"]
```

> [!tip] Cómo leer
> Flecha sólida = importa/delega; punteada = callback/injectado.

---

## 📦 Imports — lectura arquitectónica

```python
# validation_helpers.py
from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any
from sec_interp.core.exceptions import ValidationError
```

| # | Observación |
|---|-------------|
| ① | (pendiente) |
| ② | (pendiente) |

---

## 🏗️ Inventario de estructura

**Clases:** `class RichValidationError` — 1 métodos; `class ValidationContext` — 9 métodos; `class DependencyRule` — 1 métodos
**Funciones/Métodos:**
- `RichValidationError.__str__(def __str__(self) -> str:)`
- `ValidationContext.__init__(def __init__(self) -> None:)`
- `ValidationContext.add_error(def add_error(self, message: str, field_name: str | None=None, **kwargs) -> None:)`
- `ValidationContext.add_warning(def add_warning(self, message: str, field_name: str | None=None, **kwargs) -> None:)`
- `ValidationContext.has_errors(@property)`
- `ValidationContext.has_warnings(@property)`
- `ValidationContext.errors(@property)`
- `ValidationContext.warnings(@property)`
- `ValidationContext.merge(def merge(self, other: ValidationContext) -> None:)`
- `ValidationContext.raise_if_errors(def raise_if_errors(self) -> None:)`
- `DependencyRule.validate(def validate(self, context: ValidationContext) -> None:)`
- `validate_dependencies(def validate_dependencies(rules: list[DependencyRule], context: ValidationContext) -> None:)`
- `validate_reasonable_ranges(def validate_reasonable_ranges(values: dict[str, Any]) -> list[str]:)`
- `_validate_vert_exag(def _validate_vert_exag(value: Any) -> list[str]:)`
- `_validate_buffer(def _validate_buffer(value: Any) -> list[str]:)`
- `_validate_dip_scale(def _validate_dip_scale(value: Any) -> list[str]:)`

---

## 📁 Archivos del paquete

- `validation_helpers.py` — nota individual de este archivo.

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
| `validate_dependencies`, `validate_reasonable_ranges` | `-` | - |

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
