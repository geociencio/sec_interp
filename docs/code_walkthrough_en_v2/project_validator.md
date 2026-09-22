---
tags:
  - secinterp
  - code-walkthrough
  - core      # core | gui | exporters
  - validation     # services | managers | renderers | adapters | validation | etc.
aliases:
  - project_validator.py  # e.g. path_resolver.py
  - project_validator     # e.g. resolve_export_path
cssclass: secinterp-note
# note_lines: 700      # optional: ceiling > 500 for high-importance modules (max 700)
---

# `core/validation/project_validator.py`

> [!abstract] One-line summary
> Validation for project state and layer presence (QGIS-agnostic). — what this module does in one sentence, without touching QGIS if it is core.

**Path**: `core/validation/project_validator.py` (151 lines)
**Main class/function**: `project_validator`
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
    A["project_validator"]
    A --> B["Dependency 1"]
    A --> C["Dependency 2"]
```

> [!tip] How to read
> Solid arrow = imports/delegates; dashed = callback/injected.

---

## 📦 Imports — architectural reading

```python
# project_validator.py
from __future__ import annotations
from dataclasses import dataclass
from sec_interp.core.validation.layer_metadata import LayerMetadata
from .validation_helpers import ValidationContext
```

| # | Observation |
|---|-------------|
| ① | (pending) |
| ② | (pending) |

---

## 🏗️ Structure inventory

**Clases:** `class ValidationParams` — 0 métodos; `class ProjectValidator` — 6 métodos
**Constantes:** `MIN_FLOAT_THRESHOLD`
**Funciones/Métodos:**
- `ProjectValidator.validate_all(@classmethod)`
- `ProjectValidator.validate_preview_requirements(@classmethod)`
- `ProjectValidator.is_drillhole_complete(@classmethod)`
- `ProjectValidator.is_dem_complete(@classmethod)`
- `ProjectValidator.is_geology_complete(@classmethod)`
- `ProjectValidator.is_structure_complete(@classmethod)`

---

## 📁 Files in the package

- `project_validator.py` — individual note for this file.

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
| (no symbols) | `-` | - |

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
