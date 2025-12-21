# Implementation Plan - Main Dialog Fragmentation

Fragment the `SecInterpDialog` class (Complexity: 95) by decomposing it into specialized managers and utility modules.

## Proposed Changes

### GUI Components

#### [NEW] [main_dialog_settings.py](file:///home/jmbernales/qgispluginsdev/sec_interp/gui/main_dialog_settings.py)
Encapsulate user settings persistence logic.
- `DialogSettingsManager` class.
- `load_settings()`: Moved from `_load_user_settings`.
- `save_settings()`: Moved from `_save_user_settings`.

#### [NEW] [main_dialog_status.py](file:///home/jmbernales/qgispluginsdev/sec_interp/gui/main_dialog_status.py)
Manage UI state updates and status indicators.
- `DialogStatusManager` class.
- `update_ui_state()`: Orchestrate button and preview checkbox updates.
- `setup_indicators()`: Handle required field warning icons.
- `update_raster_status()`, `update_section_status()`.

#### [NEW] [main_dialog_utils.py](file:///home/jmbernales/qgispluginsdev/sec_interp/gui/main_dialog_utils.py)
Common UI utility functions.
- `populate_field_combobox()`: Helper for field selection.
- `get_layers_by_type()`, `get_layers_by_geometry()`.
- `get_theme_icon()`: Moved from `getThemeIcon`.

#### [MODIFY] [main_dialog.py](file:///home/jmbernales/qgispluginsdev/sec_interp/gui/main_dialog.py)
Refactor to use the new managers.
- Initialize `DialogSettingsManager`, `DialogStatusManager`, and `PreviewManager`.
- Delegate `open_help`, `wheelEvent`, and other UI event handlers to appropriate specialized components where possible.
- Remove legacy and redundant `_generate_*` methods that are now handled by `PreviewManager`.

## Verification Plan

### Automated Tests
- Run `analyze_project_optfixed.py` to verify the reduction in `main_dialog.py` complexity.
- Verify that `QgsSettings` are still preserved between sessions.

### Manual Verification
1. Open the plugin.
2. Verify that input indicators (warning icons) update correctly when selecting layers.
3. Verify that the "Preview" and "Ok" buttons enable/disable correctly based on inputs.
4. Verify that settings (Scale, Vert Exag, etc.) are remembered after closing and reopening the dialog.
5. Verify that help opens correctly.
