# Test Implementation Plan - Phase 10

## Goal
Achieve comprehensive test coverage for `gui/main_dialog_tools.py`, `gui/main_dialog_validation.py`, and `sec_interp_plugin.py`.

## Target Files Analysis

### 1. `gui/main_dialog_tools.py` (162 lines)
**Classes:**
- `DialogToolManager`: Manages map tools (pan, measure, interpretation)
- `NavigationManager`: Handles canvas zooming

**Key Methods:**
- `initialize_tools()`: Creates and configures tools
- `toggle_measure_tool(checked)`: Switches between measure and pan
- `toggle_interpretation_tool(checked)`: Switches between interpretation and pan
- `update_measurement_display(metrics)`: Displays measurement results
- `handle_wheel_event(event)`: Handles zoom via mouse wheel

### 2. `gui/main_dialog_validation.py` (70 lines)
**Classes:**
- `DialogValidator`: Delegates validation to core validators

**Key Methods:**
- `_collect_params()`: Gathers UI widget values
- `validate_inputs()`: Full validation via `ProjectValidator`
- `validate_preview_requirements()`: Minimal validation for preview

### 3. `sec_interp_plugin.py` (491 lines)
**Classes:**
- `SecInterp`: Main plugin orchestrator

**Key Methods:**
- `__init__(iface)`: Plugin initialization
- `initGui()`: Creates menu/toolbar
- `unload()`: Cleanup
- `run()`: Opens dialog
- `_get_and_validate_inputs()`: Collects and validates
- `process_data(inputs)`: Delegates to preview manager
- `save_profile_line()`: Delegates to export manager
- `draw_preview(...)`: Renders preview

## Proposed Changes

### Tests

#### [NEW] [test_main_dialog_tools.py](file:///home/jmbernales/qgispluginsdev/sec_interp/tests/gui/test_main_dialog_tools.py)

**DialogToolManager Tests:**
1. **Initialization**: Verify tools are created if not provided
2. **Toggle Measure**: Verify canvas tool switching and button visibility
3. **Toggle Interpretation**: Verify tool switching and measure deactivation
4. **Update Display**: Verify HTML formatting and group expansion
5. **Edge Cases**: Empty metrics, insufficient points

**NavigationManager Tests:**
1. **Wheel Zoom In/Out**: Verify zoom methods called
2. **Mouse Not Over Canvas**: Verify event not handled

#### [NEW] [test_main_dialog_validation.py](file:///home/jmbernales/qgispluginsdev/sec_interp/tests/gui/test_main_dialog_validation.py)

**DialogValidator Tests:**
1. **Collect Params**: Verify all widget values extracted
2. **Validate Inputs Success**: Mock `ProjectValidator.validate_all` to pass
3. **Validate Inputs Failure**: Mock to raise `ValidationError`
4. **Validate Preview Success**: Mock `validate_preview_requirements` to pass
5. **Validate Preview Failure**: Mock to raise `ValidationError`

#### [NEW] [test_sec_interp_plugin.py](file:///home/jmbernales/qgispluginsdev/sec_interp/tests/gui/test_sec_interp_plugin.py)

**SecInterp Tests:**
1. **Initialization**: Verify iface, translator, actions setup
2. **initGui**: Verify menu/toolbar creation
3. **unload**: Verify cleanup
4. **run**: Verify dialog creation and signal connections
5. **_resolve_layer_obj**: Test layer resolution logic
6. **_get_and_validate_inputs**: Mock validation success/failure
7. **process_data**: Mock preview manager delegation
8. **save_profile_line**: Mock export manager delegation
9. **draw_preview**: Mock renderer calls

> [!IMPORTANT]
> These are integration tests that require extensive mocking of QGIS interfaces (`QgisInterface`, dialog widgets, etc.). Coverage may be lower than unit tests due to complexity.

## Verification Plan
1. Run `uv run python3 -m unittest tests/gui/test_main_dialog_tools.py`
2. Run `uv run python3 -m unittest tests/gui/test_main_dialog_validation.py`
3. Run `uv run python3 -m unittest tests/gui/test_sec_interp_plugin.py`
4. Run coverage report to assess overall coverage_log.md
