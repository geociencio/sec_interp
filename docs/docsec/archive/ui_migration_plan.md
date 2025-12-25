# Implementation Plan - Native Programmatic UI Refactoring

Migrate the plugin's user interface from a Qt Designer `.ui` file to a fully programmatic, modular Python implementation using native QGIS widgets (`qgis.gui`). This is a prerequisite for adding complex features like Drillhole integration.

## User Review Required

> [!IMPORTANT]
> This is a major refactoring that will replace the entire UI layer.
> - The file `gui/ui/main_dialog_base.ui` and its compiled version `gui/ui/main_dialog_base.py` will be deleted.
> - The `Makefile` will be updated to stop compiling UI files.
> - Verification will require checking that all current functionality (DEM, Section, Geology, Structural) works exactly as before.

## Proposed Changes

### GUI Architecture
We will split the monolithic `main_dialog.py` into a modular structure:

`gui/ui/`
  - `main_window.py`: Main container (QDialog) with Sidebar + StackedWidget
  - `sidebar.py`: Custom QListWidget for navigation
  - `pages/base_page.py`: Abstract base class for config pages
  - `pages/dem_page.py`: DEM selection widget
  - `pages/section_page.py`: Cross-section selection widget
  - `pages/geology_page.py`: Geology inputs
  - `pages/structure_page.py`: Structural inputs
  - `pages/preview_page.py`: Preview area, including QgsMapCanvas and checkboxes

### Component Details

#### 1. Page Widgets (`gui/ui/pages/*.py`)
Each page will inherit from `QWidget` and implement `get_data()` and `validate()`.
- **DEM Page**: Uses `QgsMapLayerComboBox` (Raster), `QgsRasterBandComboBox`.
- **Section Page**: Uses `QgsMapLayerComboBox` (Line), `QgsDoubleSpinBox` for buffer.
- **Structure Page**: Uses `QgsMapLayerComboBox` (Point), `QgsFieldComboBox` (Dip/Strike), `QgsDoubleSpinBox` (Scale).

#### 2. Main Window (`gui/ui/main_window.py`)
- Replaces `Ui_SecInterpDialogBase`.
- Orchestrates the `QSplitter` layout.
- Connects the Sidebar signals to the StackedWidget slots.

#### 3. Main Dialog Logic (`gui/main_dialog.py`)
- Updates `SecInterpDialog` to inherit from the new `SecInterpMainWindow` (or instantiate it).
- Removes references to `self.setupUi(self)`.
- Connects the business logic to the new widget accessors.

#### 4. Build System (`Makefile`)
- Remove `pyuic5` compilation steps.
- Remove `gui/ui/main_dialog_base.ui` from `UI_FILES`.

## Implementation Steps

#### [NEW] [gui/ui/pages/base_page.py](file:///home/jmbernales/qgispluginsdev/sec_interp/gui/ui/pages/base_page.py)
- Define abstract base class for consistent interface.

#### [NEW] [gui/ui/pages/dem_page.py](file:///home/jmbernales/qgispluginsdev/sec_interp/gui/ui/pages/dem_page.py)
- Implement DEM configuration using `QgsMapLayerComboBox` and `QgsRasterBandComboBox`.

#### [NEW] [gui/ui/pages/section_page.py](file:///home/jmbernales/qgispluginsdev/sec_interp/gui/ui/pages/section_page.py)
- Implement Section Line configuration.

#### [NEW] [gui/ui/pages/geology_page.py](file:///home/jmbernales/qgispluginsdev/sec_interp/gui/ui/pages/geology_page.py)
- Implement Geology configuration.

#### [NEW] [gui/ui/pages/structure_page.py](file:///home/jmbernales/qgispluginsdev/sec_interp/gui/ui/pages/structure_page.py)
- Implement Structural configuration using `QgsFieldComboBox` and native spinboxes.

#### [NEW] [gui/ui/pages/preview_page.py](file:///home/jmbernales/qgispluginsdev/sec_interp/gui/ui/pages/preview_page.py)
- Implement the Preview area with `QgsMapCanvas` and controls.

#### [NEW] [gui/ui/main_window.py](file:///home/jmbernales/qgispluginsdev/sec_interp/gui/ui/main_window.py)
- Assemble the main dialog layout using the page components.

#### [MODIFY] [gui/main_dialog.py](file:///home/jmbernales/qgispluginsdev/sec_interp/gui/main_dialog.py)
- Update to use the new programmatic UI.
- Update signal connections and widget access logic.

#### [DELETE] [gui/ui/main_dialog_base.ui](file:///home/jmbernales/qgispluginsdev/sec_interp/gui/ui/main_dialog_base.ui)
- Delete the old UI definition file.

#### [MODIFY] [Makefile](file:///home/jmbernales/qgispluginsdev/sec_interp/Makefile)
- Remove UI compilation rules.

## Verification Plan

### Manual Verification
1.  **Launch Plugin**: Verify the dialog opens correctly without errors.
2.  **Navigation**: Click through sidebar items (DEM, Section, Geology, Structural) and verify pages switch correctly.
3.  **Widget Functionality**:
    - Check if ComboBoxes are populated with layers.
    - Check if FieldComboBoxes update when layers change.
    - Check if SpinBoxes work and have correct default values.
4.  **Workflow**: Run a full interpretation workflow (Preview -> Export) to ensure all data is correctly passed from the new UI to the core logic.
