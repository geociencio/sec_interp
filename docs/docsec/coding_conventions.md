# QGIS & PyQt Coding Conventions

This document outlines the standard coding conventions and best practices for QGIS plugin development using PyQt5.

## Naming Conventions

### Python vs. Qt Style
Mixed styles are inevitable in QGIS plugins due to the intersection of Python (PEP 8) and Qt (C++ style) frameworks.

-   **Classes**: `CapWords` (e.g., `SecInterpDialog`, `ProfileService`).
-   **Variables/Functions**: standard `snake_case` (e.g., `calculate_azimuth`, `profile_data`).
-   **Qt Overrides**: `camelCase` (MUST match the Qt signature exactly).
    -   *Correct*: `def accept(self):`, `def showEvent(self, event):`
    -   *Incorrect*: `def show_event(self, event):` (Will not be called by Qt)
-   **Signals**: `camelCase` (PyQt convention).
    -   e.g., `dataChanged = pyqtSignal()`, `layerSelected = pyqtSignal(QgsMapLayer)`

## Imports

Use strict ordering to avoid "DLL load failed" errors and circular dependencies.

1.  **Future/Standard Library**: `import os`, `import sys`
2.  **Third-Party**: `import numpy`
3.  **QGIS Core**: `from qgis.core import QgsProject, QgsVectorLayer`
4.  **QGIS GUI**: `from qgis.gui import QgsMapTool`
5.  **PyQt**: `from qgis.PyQt.QtWidgets import QDialog` (Always use `qgis.PyQt`, never `PyQt5` directly, to ensure ABI compatibility with QGIS).
6.  **Local Modules**: `from .core import algorithms`

## Project Structure

-   `core/`: Pure logic, data processing, and algorithms. Should depend minimally on GUI classes.
-   `gui/`: Widgets, dialogs, map tools.
-   `gui/ui/`: `*.ui` files and resources.
-   `resources/`: Icons, images, QRC files.

## Signal/Slot Connections

Prefer the new-style signal connection syntax (type-safe):

```python
# GOOD
self.button.clicked.connect(self._on_button_clicked)

# BAD (Old style)
self.connect(self.button, SIGNAL("clicked()"), self._on_button_clicked)
```

## Logging

Do not use `print()`. Use the QGIS message log via a dedicated logger wrapper.

```python
from sec_interp.logger_config import get_logger
logger = get_logger(__name__)

logger.info("Processing started")
logger.error("Invalid geometry found")
```

## Error Handling

-   Catch specific exceptions (`ValueError`, `OSError`) rather than bare `except:`.
-   Display user-facing errors using `QgsMessageBar` (embedded in dialog) or `QMessageBox` (modal), not just console logs.
