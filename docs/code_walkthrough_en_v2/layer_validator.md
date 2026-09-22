---
tags:
  - secinterp
  - code-walkthrough
  - core      # core | gui | exporters
  - validation     # services | managers | renderers | adapters | validation | etc.
aliases:
  - layer_validator.py  # e.g. path_resolver.py
  - layer_validator     # e.g. resolve_export_path
cssclass: secinterp-note
# note_lines: 700      # optional: ceiling > 500 for high-importance modules (max 700)
---

# `core/validation/layer_validator.py`

> [!abstract] One-line summary
> Spatial validation for layers (QGIS-agnostic). — what this module does in one sentence, without touching QGIS if it is core.

**Path**: `core/validation/layer_validator.py` (200 lines)
**Main class/function**: `layer_validator`
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
    A["layer_validator"]
    A --> B["Dependency 1"]
    A --> C["Dependency 2"]
```

> [!tip] How to read
> Solid arrow = imports/delegates; dashed = callback/injected.

---

## 📦 Imports — architectural reading

```python
# layer_validator.py
from __future__ import annotations
from typing import TYPE_CHECKING
from sec_interp.core.domain import FieldType
from sec_interp.core.validation.layer_metadata import GEOMETRY_LINE, GEOMETRY_POINT, GEOMETRY_POLYGON, KIND_RASTER, KIND_VECTOR, LayerMetadata
from .field_validator import validate_field_exists, validate_field_type
```

| # | Observation |
|---|-------------|
| ① | (pending) |
| ② | (pending) |

---

## 🏗️ Structure inventory

**Constantes:** `_TYPE_NAMES`
**Funciones/Métodos:**
- `validate_layer_has_features(def validate_layer_has_features(metadata: LayerMetadata) -> tuple[bool, str]:)`
- `validate_layer_geometry(def validate_layer_geometry(metadata: LayerMetadata, expected_type: str) -> tuple[bool, str]:)`
- `validate_raster_band(def validate_raster_band(metadata: LayerMetadata, band_number: int) -> tuple[bool, str]:)`
- `validate_structural_requirements(def validate_structural_requirements(metadata: LayerMetadata, dip_field: str | None, strike_field: str | None, context: ValidationContext | None=None) -> tuple[bool, str]:)`
- `_check_struct_layer_validity(def _check_struct_layer_validity(metadata: LayerMetadata) -> tuple[bool, str]:)`
- `validate_geology_requirements(def validate_geology_requirements(metadata: LayerMetadata, field_name: str | None, context: ValidationContext | None=None) -> tuple[bool, str]:)`
- `_check_geology_layer_validity(def _check_geology_layer_validity(metadata: LayerMetadata) -> tuple[bool, str]:)`
- `_validate_struct_field(def _validate_struct_field(metadata: LayerMetadata, field_name: str, label: str) -> tuple[bool, str]:)`
- `validate_crs_compatibility(def validate_crs_compatibility(metadata_list: list[LayerMetadata]) -> tuple[bool, str]:)`

---

## 📁 Files in the package

- `layer_validator.py` — individual note for this file.

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
| `validate_layer_has_features`, `validate_layer_geometry`, `validate_raster_band`, `validate_structural_requirements`, `validate_geology_requirements`, `validate_crs_compatibility` | `-` | - |

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
