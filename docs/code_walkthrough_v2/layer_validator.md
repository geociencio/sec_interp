---
tags:
  - secinterp
  - code-walkthrough
  - core      # core | gui | exporters
  - validation     # services | managers | renderers | adapters | validation | etc.
aliases:
  - layer_validator.py  # ej. path_resolver.py
  - layer_validator     # ej. resolve_export_path
cssclass: secinterp-note
# note_lines: 700      # opcional: tope > 500 para módulos de importancia alta (máx 700)
---

# `core/validation/layer_validator.py`

> [!abstract] Resumen en una línea
> Spatial validation for layers (QGIS-agnostic). — qué hace este módulo en una frase, sin tocar QGIS si es core.

**Ruta**: `core/validation/layer_validator.py` (200 líneas)
**Clase/Función principal**: `layer_validator`
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
    A["layer_validator"]
    A --> B["Dependencia 1"]
    A --> C["Dependencia 2"]
```

> [!tip] Cómo leer
> Flecha sólida = importa/delega; punteada = callback/injectado.

---

## 📦 Imports — lectura arquitectónica

```python
# layer_validator.py
from __future__ import annotations
from typing import TYPE_CHECKING
from sec_interp.core.domain import FieldType
from sec_interp.core.validation.layer_metadata import GEOMETRY_LINE, GEOMETRY_POINT, GEOMETRY_POLYGON, KIND_RASTER, KIND_VECTOR, LayerMetadata
from .field_validator import validate_field_exists, validate_field_type
```

| # | Observación |
|---|-------------|
| ① | (pendiente) |
| ② | (pendiente) |

---

## 🏗️ Inventario de estructura

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

## 📁 Archivos del paquete

- `layer_validator.py` — nota individual de este archivo.

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
| `validate_layer_has_features`, `validate_layer_geometry`, `validate_raster_band`, `validate_structural_requirements`, `validate_geology_requirements`, `validate_crs_compatibility` | `-` | - |

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
