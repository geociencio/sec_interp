# Type Hints Implementation Plan

## Overview

Add comprehensive type hints throughout the SecInterp codebase to improve:
- IDE autocomplete and IntelliSense
- Static type checking with mypy
- Code documentation and readability
- Early error detection
- Maintainability

---

## Current State Analysis

### ✅ Good Coverage (Already Has Type Hints)
- `core/validation.py` - ~90% coverage
- `core/utils/geometry.py` - ~80% coverage
- `core/utils/spatial.py` - ~80% coverage
- `core/utils/sampling.py` - ~70% coverage
- `core/utils/geology.py` - ~90% coverage
- `exporters/` - Partial coverage

### ❌ Needs Type Hints
- `core/algorithms.py` - No type hints
- `core/data_cache.py` - No type hints
- `core/services/*.py` - Minimal type hints
- `gui/main_dialog.py` - No type hints
- `gui/preview_renderer.py` - No type hints
- `gui/legend_widget.py` - No type hints

---

## Common QGIS Types Reference

```python
from typing import Optional, List, Dict, Tuple, Any, Union
from pathlib import Path

# QGIS Core Types
from qgis.core import (
    QgsVectorLayer,
    QgsRasterLayer,
    QgsMapLayer,
    QgsGeometry,
    QgsPointXY,
    QgsFeature,
    QgsFields,
    QgsField,
    QgsCoordinateReferenceSystem,
    QgsRectangle,
    QgsDistanceArea,
    QgsVectorFileWriter,
    QgsMapSettings,
)

# PyQt Types
from qgis.PyQt.QtCore import QSize
from qgis.PyQt.QtGui import QColor, QImage, QPainter
from qgis.PyQt.QtWidgets import QDialog, QWidget

# Common Type Aliases
ProfileData = List[Tuple[float, float]]  # [(distance, elevation), ...]
GeologyData = List[Tuple[float, float, str]]  # [(distance, elevation, unit), ...]
StructureData = List[Tuple[float, float]]  # [(distance, dip), ...]
```

---

## Implementation Strategy

### Phase 1: Core Modules (High Priority)

#### 1.1 `core/algorithms.py`
**Priority:** High (Main orchestrator)

**Functions to Type:**
```python
class SecInterp:
    def __init__(self, iface: QgisInterface) -> None: ...

    def run(self) -> None: ...

    def _process_profile_data(
        self,
        line_layer: QgsVectorLayer,
        raster_layer: QgsRasterLayer,
        outcrop_layer: Optional[QgsVectorLayer] = None,
        structural_layer: Optional[QgsVectorLayer] = None,
        **kwargs
    ) -> Tuple[ProfileData, Optional[GeologyData], Optional[StructureData]]: ...
```

#### 1.2 `core/data_cache.py`
**Priority:** High (Performance critical)

**Methods to Type:**
```python
class DataCache:
    def __init__(self) -> None: ...

    def get_profile(self, key: str) -> Optional[ProfileData]: ...

    def set_profile(self, key: str, data: ProfileData) -> None: ...

    def invalidate(self, pattern: Optional[str] = None) -> None: ...
```

---

### Phase 2: Services (High Priority)

#### 2.1 `core/services/profile_service.py`
```python
class ProfileService:
    def generate_topographic_profile(
        self,
        line_layer: QgsVectorLayer,
        raster_layer: QgsRasterLayer,
        band_number: int = 1
    ) -> ProfileData: ...
```

#### 2.2 `core/services/geology_service.py`
```python
class GeologyService:
    def generate_geological_profile(
        self,
        line_layer: QgsVectorLayer,
        raster_layer: QgsRasterLayer,
        outcrop_layer: QgsVectorLayer,
        outcrop_name_field: str,
        band_number: int = 1
    ) -> GeologyData: ...
```

#### 2.3 `core/services/structure_service.py`
```python
class StructureService:
    def project_structures(
        self,
        line_layer: QgsVectorLayer,
        structural_layer: QgsVectorLayer,
        buffer_distance: float,
        line_azimuth: float,
        dip_field: str,
        strike_field: str
    ) -> StructureData: ...
```

---

### Phase 3: GUI Modules (Medium Priority)

#### 3.1 `gui/main_dialog.py`
**Priority:** Medium (Large file, many methods)

**Key Methods:**
```python
class MainDialog(QDialog):
    def __init__(self, iface: QgisInterface) -> None: ...

    def _get_dialog_values(self) -> Dict[str, Any]: ...

    def _validate_inputs(self) -> Tuple[bool, str]: ...

    def _generate_preview(self) -> None: ...

    def _export_results(self, format: str) -> bool: ...
```

#### 3.2 `gui/preview_renderer.py`
```python
class PreviewRenderer:
    def render(
        self,
        topo_data: ProfileData,
        geol_data: Optional[GeologyData] = None,
        struct_data: Optional[StructureData] = None,
        vert_exag: float = 1.0
    ) -> Tuple[Optional[QgsMapCanvas], List[QgsVectorLayer]]: ...

    def export_to_image(
        self,
        layers: List[QgsVectorLayer],
        extent: QgsRectangle,
        width: int,
        height: int,
        output_path: Union[str, Path],
        dpi: int = 300
    ) -> bool: ...
```

---

### Phase 4: Exporters (Low Priority - Already Partial)

Review and complete existing type hints in exporters.

---

## Type Hint Style Guide

### 1. Function Signatures
```python
# Good
def calculate_distance(
    point1: QgsPointXY,
    point2: QgsPointXY,
    crs: QgsCoordinateReferenceSystem
) -> float:
    """Calculate distance between two points."""
    ...

# Avoid
def calculate_distance(point1, point2, crs):
    """Calculate distance between two points."""
    ...
```

### 2. Optional Parameters
```python
# Use Optional for nullable parameters
def process_layer(
    layer: QgsVectorLayer,
    field_name: Optional[str] = None
) -> bool:
    ...
```

### 3. Collections
```python
# Be specific about collection contents
def get_features(layer: QgsVectorLayer) -> List[QgsFeature]:
    ...

def get_attributes(feature: QgsFeature) -> Dict[str, Any]:
    ...
```

### 4. Union Types
```python
# Use Union for multiple possible types
def load_layer(source: Union[str, Path, QgsVectorLayer]) -> QgsVectorLayer:
    ...
```

### 5. Type Aliases
```python
# Create aliases for complex types
ProfileData = List[Tuple[float, float]]
LayerDict = Dict[str, QgsVectorLayer]

def process_profile(data: ProfileData) -> LayerDict:
    ...
```

---

## Mypy Configuration

Create `mypy.ini` in project root:

```ini
[mypy]
python_version = 3.9
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = False  # Start permissive
disallow_incomplete_defs = False
check_untyped_defs = True
no_implicit_optional = True

# Ignore QGIS modules (no stubs available)
[mypy-qgis.*]
ignore_missing_imports = True

[mypy-qgis.core]
ignore_missing_imports = True

[mypy-qgis.PyQt.*]
ignore_missing_imports = True

# Gradually enable stricter checking per module
[mypy-sec_interp.core.validation]
disallow_untyped_defs = True

[mypy-sec_interp.core.utils.*]
disallow_untyped_defs = True
```

---

## Implementation Steps

### Step 1: Setup
1. Install mypy: `uv pip install mypy`
2. Create `mypy.ini` configuration
3. Create type aliases file: `core/types.py`

### Step 2: Core Modules
1. Add type hints to `core/algorithms.py`
2. Add type hints to `core/data_cache.py`
3. Run mypy, fix errors
4. Commit: "feat(types): add type hints to core modules"

### Step 3: Services
1. Add type hints to all service classes
2. Run mypy, fix errors
3. Commit: "feat(types): add type hints to services"

### Step 4: GUI
1. Add type hints to `gui/main_dialog.py`
2. Add type hints to `gui/preview_renderer.py`
3. Run mypy, fix errors
4. Commit: "feat(types): add type hints to GUI modules"

### Step 5: Polish
1. Review and improve existing type hints
2. Add missing type hints in utils
3. Update documentation
4. Commit: "feat(types): complete type hint coverage"

---

## Type Aliases File

Create `core/types.py`:

```python
"""Common type aliases for SecInterp plugin."""

from typing import List, Tuple, Dict, Any
from qgis.core import QgsVectorLayer, QgsRasterLayer

# Profile data types
ProfileData = List[Tuple[float, float]]
"""List of (distance, elevation) tuples."""

GeologyData = List[Tuple[float, float, str]]
"""List of (distance, elevation, unit_name) tuples."""

StructureData = List[Tuple[float, float]]
"""List of (distance, apparent_dip) tuples."""

# Layer collections
LayerDict = Dict[str, QgsVectorLayer]
"""Dictionary mapping layer names to QgsVectorLayer objects."""

# Settings and configuration
SettingsDict = Dict[str, Any]
"""Dictionary of plugin settings."""

ExportSettings = Dict[str, Any]
"""Dictionary of export configuration."""
```

---

## Benefits

### Before Type Hints:
```python
def process_data(layer, field, buffer):
    # What types are these? IDE doesn't know
    # No autocomplete
    # Runtime errors only
    ...
```

### After Type Hints:
```python
def process_data(
    layer: QgsVectorLayer,
    field: str,
    buffer: float
) -> List[QgsFeature]:
    # IDE knows types
    # Full autocomplete
    # Static type checking
    # Better documentation
    ...
```

---

## Testing Strategy

### 1. Mypy Checks
```bash
# Check entire codebase
mypy sec_interp/

# Check specific module
mypy sec_interp/core/algorithms.py

# Strict mode for specific files
mypy --strict sec_interp/core/validation.py
```

### 2. IDE Verification
- Test autocomplete in VS Code/PyCharm
- Verify type hints appear in hover tooltips
- Check that type errors are highlighted

### 3. Runtime Verification
- Ensure type hints don't break existing functionality
- Run all unit tests
- Test plugin in QGIS

---

## Migration Strategy

### Gradual Adoption
1. **Week 1:** Core modules + Services
2. **Week 2:** GUI modules
3. **Week 3:** Polish and documentation

### Backward Compatibility
- Type hints are optional at runtime (Python 3.9+)
- No breaking changes to existing code
- Can be added incrementally

---

## Common Pitfalls to Avoid

### 1. Over-Specification
```python
# Too specific - hard to maintain
def process(data: List[Tuple[float, float, str, int, bool]]) -> ...:
    ...

# Better - use type alias
ProfilePoint = Tuple[float, float, str, int, bool]
def process(data: List[ProfilePoint]) -> ...:
    ...
```

### 2. Circular Imports
```python
# Avoid circular imports with TYPE_CHECKING
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sec_interp.gui.main_dialog import MainDialog

def process(dialog: 'MainDialog') -> None:  # Forward reference
    ...
```

### 3. Any Overuse
```python
# Avoid
def process(data: Any) -> Any:  # Not helpful
    ...

# Better
def process(data: Union[ProfileData, GeologyData]) -> ProfileData:
    ...
```

---

## Expected Outcomes

✅ **Better IDE Support**: Full autocomplete and type checking
✅ **Early Error Detection**: Catch type errors before runtime
✅ **Improved Documentation**: Types serve as inline documentation
✅ **Easier Refactoring**: IDE can safely rename and refactor
✅ **Better Onboarding**: New developers understand code faster

---

## Effort Estimation

| Phase | Files | Estimated Time |
|-------|-------|----------------|
| Setup | 2 files | 30 minutes |
| Core Modules | 2 files | 2 hours |
| Services | 3 files | 2 hours |
| GUI | 3 files | 3 hours |
| Polish | All | 1 hour |
| **Total** | **~13 files** | **~8.5 hours** |

---

**Priority:** High (Code Quality Improvement)
**Complexity:** Medium (Gradual, incremental work)
**Impact:** High (Significantly improves maintainability)
