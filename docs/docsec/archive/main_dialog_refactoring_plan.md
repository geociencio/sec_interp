# main_dialog.py Refactoring Implementation Plan

## Overview

Refactor `main_dialog.py` (1174 lines) into modular, maintainable components using composition pattern, type hints, and separation of concerns.

**Current State:** Single 1174-line file with 33 methods  
**Target State:** 5 focused modules, each <400 lines  
**Estimated Time:** 5-6 hours  
**Complexity:** High (major architectural change)

---

## Problems to Solve

### 1. God Object Anti-Pattern
- Single class handles UI, validation, preview, export, caching
- 1174 lines in one file
- Hard to test, maintain, and understand

### 2. Missing Type Hints
- Only GUI file without type hints
- No IDE autocomplete support
- Unclear parameter/return types

### 3. Complex Methods
- `validate_inputs()`: 160 lines
- `export_preview()`: 110 lines
- `preview_profile_handler()`: 90 lines

### 4. Magic Numbers
- Hardcoded values throughout
- No central configuration

---

## Proposed Architecture

### New Module Structure

```
gui/
├── main_dialog.py                    # Core UI (~400 lines)
│   └── SecInterpDialog (orchestrator)
│
├── main_dialog_validation.py         # Validation logic (~300 lines)
│   └── DialogValidator
│
├── main_dialog_preview.py            # Preview generation (~350 lines)
│   └── PreviewManager
│
├── main_dialog_export.py             # Export handling (~250 lines)
│   └── ExportManager
│
├── main_dialog_cache_handler.py     # Already exists ✅
│   └── CacheHandler
│
├── main_dialog_config.py             # New: Constants & config (~100 lines)
│   └── DialogConfig, DialogDefaults
│
└── ui/
    └── main_dialog_base.py           # Qt Designer generated
```

---

## Implementation Phases

### Phase 1: Setup & Configuration (30 min)

**1.1 Create `main_dialog_config.py`**
```python
from typing import Dict, Any
from qgis.PyQt.QtGui import QColor

class DialogDefaults:
    """Default values for dialog inputs."""
    SCALE = "50000"
    VERTICAL_EXAGGERATION = "1.0"
    BUFFER_DISTANCE = 100
    DPI = 300
    PREVIEW_WIDTH = 800
    PREVIEW_HEIGHT = 600
    BACKGROUND_COLOR = QColor(255, 255, 255)

class DialogConfig:
    """Configuration for dialog behavior."""
    ENABLE_CACHE = True
    AUTO_SAVE_SETTINGS = True
    SHOW_HELP_ON_START = False
```

**1.2 Update `task.md`**
- Add refactoring checklist
- Track progress by module

---

### Phase 2: Extract Validation Module (1.5 hours)

**2.1 Create `main_dialog_validation.py`**

```python
from typing import Tuple, Optional, Dict, Any
from qgis.core import QgsVectorLayer, QgsRasterLayer
from ..core import validation as vu

class DialogValidator:
    """Handles all validation logic for SecInterpDialog."""
    
    def __init__(self, dialog: 'SecInterpDialog'):
        self.dialog = dialog
    
    def validate_inputs(self) -> Tuple[bool, str]:
        """Main validation orchestrator."""
        validators = [
            self._validate_raster_layer,
            self._validate_section_line,
            self._validate_output_path,
            self._validate_geology_inputs,
            self._validate_structure_inputs,
        ]
        
        for validator in validators:
            is_valid, error = validator()
            if not is_valid:
                return False, error
        
        return True, ""
    
    def _validate_raster_layer(self) -> Tuple[bool, str]:
        """Validate raster DEM layer."""
        ...
    
    def _validate_section_line(self) -> Tuple[bool, str]:
        """Validate cross-section line layer."""
        ...
    
    def _validate_output_path(self) -> Tuple[bool, str]:
        """Validate output directory path."""
        ...
    
    def _validate_geology_inputs(self) -> Tuple[bool, str]:
        """Validate geological layer inputs."""
        ...
    
    def _validate_structure_inputs(self) -> Tuple[bool, str]:
        """Validate structural layer inputs."""
        ...
    
    def validate_preview_requirements(self) -> Tuple[bool, str]:
        """Validate minimum requirements for preview."""
        ...
```

**Methods to move:**
- `validate_inputs()` (lines 595-755)
- `_validate_preview_requirements()` (lines 924-952)
- Related validation helpers

---

### Phase 3: Extract Preview Module (1.5 hours)

**3.1 Create `main_dialog_preview.py`**

```python
from typing import Optional, Tuple, Dict, Any
from qgis.core import QgsVectorLayer, QgsRasterLayer
from ..core.types import ProfileData, GeologyData, StructureData

class PreviewManager:
    """Manages preview generation and rendering."""
    
    def __init__(self, dialog: 'SecInterpDialog'):
        self.dialog = dialog
        self.renderer = None
        self.cached_data = {
            'topo': None,
            'geol': None,
            'struct': None
        }
    
    def generate_preview(
        self,
        line_layer: QgsVectorLayer,
        raster_layer: QgsRasterLayer,
        options: Dict[str, Any]
    ) -> Tuple[bool, str]:
        """Generate complete preview with all layers."""
        ...
    
    def update_from_checkboxes(self) -> None:
        """Update preview when checkboxes change."""
        ...
    
    def generate_topography(
        self,
        line_layer: QgsVectorLayer,
        raster_layer: QgsRasterLayer,
        band_num: int
    ) -> Optional[ProfileData]:
        """Generate topographic profile data."""
        ...
    
    def generate_geology(
        self,
        line_layer: QgsVectorLayer,
        raster_layer: QgsRasterLayer,
        band_num: int
    ) -> Optional[GeologyData]:
        """Generate geological profile data."""
        ...
    
    def generate_structures(
        self,
        line_layer: QgsVectorLayer,
        buffer_dist: float
    ) -> Optional[StructureData]:
        """Generate structural projection data."""
        ...
```

**Methods to move:**
- `preview_profile_handler()` (lines 371-463)
- `update_preview_from_checkboxes()` (lines 352-369)
- `_generate_topography()` (lines 954-958)
- `_generate_geology()` (lines 960-988)
- `_generate_structures()` (lines 990-1017)

---

### Phase 4: Extract Export Module (1 hour)

**4.1 Create `main_dialog_export.py`**

```python
from typing import Dict, Any, Optional
from pathlib import Path
from qgis.core import QgsVectorLayer, QgsMapSettings

class ExportManager:
    """Handles all export operations."""
    
    def __init__(self, dialog: 'SecInterpDialog'):
        self.dialog = dialog
    
    def export_preview(
        self,
        layers: list,
        extent,
        output_path: Path,
        format: str
    ) -> bool:
        """Export current preview to file."""
        ...
    
    def get_export_settings(
        self,
        width: int,
        height: int,
        dpi: int,
        extent
    ) -> Dict[str, Any]:
        """Get export settings dictionary."""
        ...
    
    def export_to_format(
        self,
        format: str,
        output_path: Path,
        data: Any
    ) -> bool:
        """Export to specific format using appropriate exporter."""
        ...
```

**Methods to move:**
- `export_preview()` (lines 465-575)
- `_get_export_settings()` (lines 1019-1037)

---

### Phase 5: Refactor Main Dialog (1.5 hours)

**5.1 Update `main_dialog.py`**

```python
from typing import Optional, Tuple, Dict, Any
from qgis.PyQt.QtWidgets import QDialog
from .ui.main_dialog_base import Ui_SecInterpDialogBase
from .main_dialog_config import DialogDefaults, DialogConfig
from .main_dialog_validation import DialogValidator
from .main_dialog_preview import PreviewManager
from .main_dialog_export import ExportManager
from .main_dialog_cache_handler import CacheHandler

class SecInterpDialog(QDialog, Ui_SecInterpDialogBase):
    """Main dialog for SecInterp plugin.
    
    This class orchestrates UI interactions and delegates specialized
    tasks to focused manager classes.
    """
    
    def __init__(
        self,
        iface: Optional['QgisInterface'] = None,
        plugin_instance: Optional[Any] = None,
        parent: Optional[QWidget] = None
    ) -> None:
        """Initialize dialog with composition pattern."""
        super().__init__(parent)
        self.setupUi(self)
        
        self.iface = iface
        self.plugin_instance = plugin_instance
        
        # Initialize specialized managers
        self.validator = DialogValidator(self)
        self.preview_manager = PreviewManager(self)
        self.export_manager = ExportManager(self)
        self.cache_handler = CacheHandler(self)
        
        # Setup UI
        self._setup_ui()
        self._connect_signals()
        self._load_user_settings()
    
    def preview_profile_handler(self) -> None:
        """Handle preview button click."""
        # Validate
        is_valid, error = self.validator.validate_preview_requirements()
        if not is_valid:
            self.messagebar.pushMessage("Error", error, Qgis.Critical)
            return
        
        # Generate preview
        success, error = self.preview_manager.generate_preview(
            self.get_selected_values()
        )
        if not success:
            self.messagebar.pushMessage("Error", error, Qgis.Critical)
    
    def export_preview(self) -> None:
        """Handle export button click."""
        # Delegate to export manager
        self.export_manager.export_preview(...)
    
    def validate_inputs(self) -> Tuple[bool, str]:
        """Validate all inputs."""
        return self.validator.validate_inputs()
```

**Keep in main_dialog.py:**
- UI setup and connections
- Event handlers (delegates to managers)
- Settings load/save
- Helper methods for UI state

---

## Type Hints Strategy

### Common Types

```python
# In main_dialog_config.py
from typing import TypeAlias
from qgis.core import QgsVectorLayer, QgsRasterLayer

LayerSelection: TypeAlias = Optional[QgsVectorLayer]
RasterSelection: TypeAlias = Optional[QgsRasterLayer]
ValidationResult: TypeAlias = Tuple[bool, str]
DialogValues: TypeAlias = Dict[str, Any]
```

### Apply to All Modules

- All method signatures
- All return types
- All parameter types
- Use type aliases for clarity

---

## Testing Strategy

### Unit Tests

```python
# tests/test_dialog_validation.py
def test_validate_raster_layer():
    validator = DialogValidator(mock_dialog)
    is_valid, error = validator._validate_raster_layer()
    assert is_valid == True

# tests/test_preview_manager.py
def test_generate_topography():
    manager = PreviewManager(mock_dialog)
    data = manager.generate_topography(line_layer, raster_layer, 1)
    assert len(data) > 0
```

### Integration Tests

- Test full preview generation
- Test export workflows
- Test validation chains

---

## Migration Strategy

### Backward Compatibility

1. **Keep public API stable**
   - `validate_inputs()` still exists
   - `preview_profile_handler()` still exists
   - Just delegates internally

2. **Gradual migration**
   - Old code still works
   - New code uses managers
   - No breaking changes

3. **Deprecation warnings** (optional)
   ```python
   @deprecated("Use validator.validate_inputs() instead")
   def validate_inputs(self):
       return self.validator.validate_inputs()
   ```

---

## File Size Targets

| File | Current | Target | Reduction |
|------|---------|--------|-----------|
| main_dialog.py | 1174 | ~400 | -66% |
| validation.py | 0 | ~300 | new |
| preview.py | 0 | ~350 | new |
| export.py | 0 | ~250 | new |
| config.py | 0 | ~100 | new |

**Total:** 1174 lines → 1400 lines (distributed across 5 files)

---

## Benefits

### Maintainability
- ✅ Smaller, focused files
- ✅ Clear separation of concerns
- ✅ Easier to understand and modify

### Testing
- ✅ Each manager can be tested independently
- ✅ Easier mocking
- ✅ Better test coverage

### Collaboration
- ✅ Less merge conflicts
- ✅ Easier code reviews
- ✅ Parallel development possible

### Type Safety
- ✅ Complete type coverage
- ✅ Better IDE support
- ✅ Catch errors early

---

## Risks & Mitigation

### Risk 1: Breaking Changes
**Mitigation:** Keep public API stable, delegate internally

### Risk 2: Import Cycles
**Mitigation:** Use TYPE_CHECKING, forward references

### Risk 3: Testing Overhead
**Mitigation:** Start with critical paths, expand gradually

### Risk 4: Performance
**Mitigation:** Managers are lightweight, minimal overhead

---

## Implementation Checklist

### Phase 1: Setup
- [ ] Create `main_dialog_config.py`
- [ ] Add constants and defaults
- [ ] Update `task.md`

### Phase 2: Validation
- [ ] Create `main_dialog_validation.py`
- [ ] Move validation methods
- [ ] Add type hints
- [ ] Test validation logic

### Phase 3: Preview
- [ ] Create `main_dialog_preview.py`
- [ ] Move preview methods
- [ ] Add type hints
- [ ] Test preview generation

### Phase 4: Export
- [ ] Create `main_dialog_export.py`
- [ ] Move export methods
- [ ] Add type hints
- [ ] Test export workflows

### Phase 5: Main Dialog
- [ ] Refactor `main_dialog.py`
- [ ] Add composition pattern
- [ ] Add type hints
- [ ] Update all method calls

### Phase 6: Testing
- [ ] Create unit tests
- [ ] Test in QGIS
- [ ] Verify all workflows
- [ ] Performance testing

### Phase 7: Documentation
- [ ] Update docstrings
- [ ] Create architecture diagram
- [ ] Update README
- [ ] Create migration guide

---

## Timeline

| Phase | Time | Cumulative |
|-------|------|------------|
| 1. Setup | 30 min | 0.5h |
| 2. Validation | 1.5h | 2h |
| 3. Preview | 1.5h | 3.5h |
| 4. Export | 1h | 4.5h |
| 5. Main Dialog | 1.5h | 6h |
| 6. Testing | 1h | 7h |
| 7. Documentation | 0.5h | 7.5h |

**Total:** ~7.5 hours (including testing & docs)

---

## Success Criteria

✅ All files < 400 lines  
✅ Complete type hint coverage  
✅ All tests passing  
✅ No breaking changes  
✅ Plugin works in QGIS  
✅ Better IDE autocomplete  
✅ Easier to maintain  

---

**Ready to proceed with implementation?**
