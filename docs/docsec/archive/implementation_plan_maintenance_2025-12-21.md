---

# Refactor GUI Validation

Decouple validation logic from PyQt5 widgets to improve testability and reduce GUI complexity.

## Proposed Changes

### Core Validation

#### [MODIFY] [validation.py](file:///home/jmbernales/qgispluginsdev/sec_interp/core/validation.py)
- **[NEW] `ValidationParams`**: A `@dataclass` to hold all input parameters needed for validation.
- **[NEW] `ProjectValidator`**: A class or set of functions to orchestrate full project validation using `ValidationParams`.
- Move specific range checks (scale, vert_exag, etc.) to the core.

### GUI Validation

#### [MODIFY] [main_dialog_validation.py](file:///home/jmbernales/qgispluginsdev/sec_interp/gui/main_dialog_validation.py)
- Refactor `DialogValidator` to act as a data collector.
- It will create a `ValidationParams` object from the current state of UI widgets.
- It will call `core.validation.ProjectValidator` to perform the actual checks.

## Verification Plan

### Automated Tests
- Run `python3 analyze_project_optfixed.py` to check for "Heavy Logic in GUI" reduction.
- Create a small unit test for `ProjectValidator` (optional but recommended if environment allows).

### Manual Verification
- Verify that clicking "Preview" or "Export" still triggers validation correctly.
- Ensure error messages are still displayed in a dialog as before.
