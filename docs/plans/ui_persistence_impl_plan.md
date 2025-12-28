# Persistence for UI Selections

Implement saving and restoring of layer and field selections across all dialog pages.

## Proposed Changes

### [MODIFY] main_dialog_settings.py
- Add helper methods `_save_layer`, `_restore_layer`, `_save_field`, `_restore_field`, and `_restore_check`.
- Update `save_settings` and `load_settings` to handle all pages:
    - **SectionPage**: `line_combo`
    - **DemPage**: `raster_combo`, `band_combo`
    - **GeologyPage**: `layer_combo`, `field_combo`
    - **StructurePage**: `layer_combo`, `dip_combo`, `strike_combo`
    - **DrillholePage**: Collar, Survey, and Interval tags.

## Verification Plan
1. Select layers/fields in all tabs.
2. Close dialog without OK (direct close/QGIS quit).
3. Reopen and verify restoration.
