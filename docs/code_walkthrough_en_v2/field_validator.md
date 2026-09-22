---
tags:
  - secinterp
  - code-walkthrough
  - core      # core | gui | exporters
  - validation     # services | managers | renderers | adapters | validation | etc.
aliases:
  - field_validator.py  # e.g. path_resolver.py
  - field_validator     # e.g. resolve_export_path
cssclass: secinterp-note
# note_lines: 700      # optional: ceiling > 500 for high-importance modules (max 700)
---

# `core/validation/field_validator.py`

> [!abstract] One-line summary
> Validation logic for layer fields and attributes (QGIS-agnostic). — what this module does in one sentence, without touching QGIS if it is core.

**Path**: `core/validation/field_validator.py` (184 lines)
**Main class/function**: `field_validator`
**Layer**: core (QGIS-agnostic / GUI · Type)
**Tags**: #secinterp #core #validation

---

## 🎯 Why does this file exist?

| Problem | Solution |
|---------|----------|
| (pending) | (pending) |
| (pending) | (pending) |

> [!important] Architectural note
> QGIS-agnóstico (e.g. "QGIS-agnostic", "Extract Adapter", "Factory").

---

## 🧬 Relationship diagram

```mermaid
graph TD
    A["field_validator"]
    A --> B["Dependency 1"]
    A --> C["Dependency 2"]
```

> [!tip] How to read
> Solid arrow = imports/delegates; dashed = callback/injected.

---

## 📦 Imports — architectural reading

```python
# field_validator.py
from __future__ import annotations
from sec_interp.core.domain import FieldType
from sec_interp.core.validation.layer_metadata import LayerMetadata
```

| # | Observation |
|---|-------------|
| ① | (pending) |
| ② | (pending) |

---

## 🏗️ Structure inventory

**Funciones/Métodos:**
- `validate_numeric_input(def validate_numeric_input(value: str, min_val: float | None=None, max_val: float | None=None, field_name: str='Value', allow_empty: bool=False) -> tuple[bool, str, float | None]:)`
- `validate_integer_input(def validate_integer_input(value: str, min_val: int | None=None, max_val: int | None=None, field_name: str='Value', allow_empty: bool=False) -> tuple[bool, str, int | None]:)`
- `validate_angle_range(def validate_angle_range(value: float, field_name: str, min_angle: float=0.0, max_angle: float=360.0) -> tuple[bool, str]:)`
- `validate_field_exists(def validate_field_exists(metadata: LayerMetadata, field_name: str | None) -> tuple[bool, str]:)`
- `validate_field_type(def validate_field_type(metadata: LayerMetadata, field_name: str, expected_types: list[FieldType]) -> tuple[bool, str]:)`

---

## 📁 Files in the package

- `field_validator.py` — individual note for this file.

---

## 📖 Method-by-method walkthrough

### `method_1`

```python
# (enriquecer)
```

_(enriquecer leyendo el fuente)_

### `method_2`

```python
# (enriquecer)
```

_(enriquecer leyendo el fuente)_

<!-- Add one subsection per public method of the module -->

---

## 🔄 Data flow

| Phase | Input | Transformation | Output |
|-------|-------|----------------|--------|
| - | - | - | - |
| - | - | - | - |

---

## 🏛️ Design patterns present

| Pattern | Where | Purpose |
|---------|-------|---------|
| - | - | - |

---

## 🧾 API summary

| Symbol | Signature / Inherits | Typical use |
|--------|----------------------|-------------|
| `validate_numeric_input`, `validate_integer_input`, `validate_angle_range`, `validate_field_exists`, `validate_field_type` | `-` | - |

---

## 🛡️ Error handling

_(pending)_

---

## 🧪 Associated tests

_(pending)_

---

## 👀 Observations and notes

> [!success] Strengths
> - (skeleton)

> [!warning] Points of attention
> - (skeleton)

> [!question] Open questions
> - (skeleton)

---

## 🔗 Related notes

- [[Index]] — vault index
- [[Index]] — index
- [[controller]] — orchestrator

---

*Note of the SecInterp Code Walkthrough v2 vault — v3.8.0*
