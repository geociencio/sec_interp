---
name: qgis-migration-4x
description: Expert guide for QGIS 4.x migration and agnostic API usage
---

# Skill: QGIS Migration & Future-Proofing (4.x)

This skill provides technical guidelines to prepare the SecInterp code for the next major version of QGIS (4.x), focusing on the elimination of technical debt related to API changes and Qt dependencies.

## 1. "API Agnostic" Principle

Code should be agnostic of the underlying Qt version (Qt5 vs. Qt6) whenever possible. QGIS provides proxies for this.

### Golden Rule: Qt Imports
❌ **FORBIDDEN**: Importing directly from `PyQt5` or `PyQt6`.
✅ **MANDATORY**: Importing from `qgis.PyQt`.
- *Migration Lesson*: Removing hard PyQt5 dependencies is critical for Qt6 compatibility. In v4.0 environments, PyQt5 should be completely removed from `pyproject.toml` and `requirements.txt`.

**Incorrect Example**:
```python
from PyQt5.QtCore import pyqtSignal, QObject
from PyQt5.QtWidgets import QWidget
```

**Correct Example**:
```python
from qgis.PyQt.QtCore import pyqtSignal, QObject
from qgis.PyQt.QtWidgets import QWidget
```

This ensures that when QGIS migrates to Qt6, the code will work without changes (as long as QGIS maintains the shim).

## 2. Detected API Changes (v3 -> v4)

### 2.1. QgsProject
*   Avoid `QgsProject.instance()` in tight loops or static methods if it's possible to pass the instance explicitly. Implement dependency injection.

### 2.2. Background Processing
*   Any calculation taking > 100ms must use `QgsTask`.
*   The UI must never be blocked.
*   Strict use of `QgsTask.fromFunction` or `QgsTask` subclasses with `finished` signals.

## 3. Refactoring Strategy

### Phase 1: Import Cleanup (Immediate)
Run scripts or manual refactors to normalize all `PyQt` imports.

### Phase 2: Deprecated Removal (Ongoing)
Monitor deprecation warnings in the QGIS console and act immediately.
*   Configure `pytest` to fail on `DeprecationWarning` from `qgis.*` modules.

### Phase 3: Resources (resources.py)
Recompile `resources.qrc` using tools that support Qt abstraction, or ensure the compiler (`pyrcc5`) is compatible with the execution environment.

## 4. Migration Checklist

- [ ] All Qt imports come from `qgis.PyQt`.
- [ ] No use of methods marked as `@deprecated` in QGIS 3.34+ documentation.
- [ ] Integration tests run without emitting `DeprecationWarning`.
- [ ] The UI is responsive and does not block the main thread.
