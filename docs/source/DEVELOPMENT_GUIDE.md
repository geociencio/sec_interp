# SecInterp - Development Guide

Welcome to the **SecInterp** development guide. This document outlines the standards, best practices, and workflows for contributing to the project.

---

## 🏗️ Technical Stack

- **Language**: Python 3.10+ (QGIS 3.x compatible)
- **GUI Framework**: PyQt5 (Native QGIS integration)
- **Geospatial Engine**: PyQGIS API (`qgis.core`, `qgis.gui`)
- **Package Manager**: `uv` (recommended) or `pip`
- **Linter & Formatter**: `Ruff`
- **Testing**: `pytest`

---

## 🎨 Coding Standards

### 🧬 Design Principles
- **SOLID**: Follow SRP, OCP, and DIP strictly.
- **Separation of Concerns**: GUI code (Managers/UI) MUST NOT contain business logic. Delegating to `Core/Services` is mandatory.
- **DRY (Don't Repeat Yourself)**: If a calculation or check is used twice, move it to a `core/utils` module.

### 📝 Naming Conventions
- **Classes**: `CapWords` (e.g., `ProfileService`).
- **Variables/Functions**: `snake_case` (e.g., `calculate_apparent_dip`).
- **Qt Overrides**: `camelCase` (MUST match the original C++ signature, e.g., `showEvent`).
- **Signals**: `camelCase` (PyQt style, e.g., `dataChanged`).

### 🐍 Imports Ordering
1.  **Standard Library**: `os`, `sys`, `math`, etc.
2.  **Third-Party**: `numpy`, `pandas`, etc.
3.  **QGIS Core**: `from qgis.core import ...`
4.  **QGIS GUI**: `from qgis.gui import ...`
5.  **PyQt**: `from qgis.PyQt.QtWidgets import ...` (Always use `qgis.PyQt` shim).
6.  **Local Modules**: `from sec_interp.core import ...`

---

## ⚡ Git Workflow

### Conventional Commits
All commits MUST follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

**Format**: `<type>(<scope>): <description>`

- `feat`: A new feature (e.g., `feat(drill): add 3d projection`)
- `fix`: A bug fix (e.g., `fix(gui): resolve range attribute error`)
- `refactor`: Code change that neither fixes a bug nor adds a feature.
- `docs`: Documentation changes.
- `test`: Adding or correcting tests.
- `chore`: Build process or auxiliary tool changes.

**Language**: All commit messages must be in **English**.

---

## 🛠️ Tooling (Ruff)

We use **Ruff** for linting and formatting. It replaces Black, isort, and Flake8.

### Basic Commands
```bash
# Lint and auto-fix
ruff check . --fix

# Format code
ruff format .

# Check everything (QA)
ruff check . && ruff format . --check
```

### IDE Integration
It is highly recommended to install the **Ruff extension** in VS Code and enable "Format on Save".

---

## 🧪 Testing

### Running Tests
```bash
# Run all tests
pytest

# Run tests with coverage report
pytest --cov=sec_interp
```

### Mocking QGIS
When testing core services, use `unittest.mock` to avoid requiring a running QGIS instance. For integration tests, use the `qgis_app` fixture if available.

---

## 📝 Documentation Standards

### Docstrings
All public functions and methods MUST have docstrings in **Google Style**:

```python
def process_data(self, layer: QgsVectorLayer, factor: float) -> Optional[list]:
    """
    Processes the layer using the specified scaling factor.

    Args:
        layer: The input QGIS vector layer.
        factor: The vertical exaggeration factor.

    Returns:
        A list of processed coordinates or None if invalid.
    """
```

### Image Assets
Save all documentation images in `docs/images/` using the following convention:
- `workflow_DESC.png`: Step-by-step guides.
- `ui_DESC.png`: General interface screenshots.
- `feature_DESC.png`: Specific highlighted features.

---

## 📦 Deployment & Makefile

Use the `Makefile` for common development tasks:

- `make deploy`: Installs the plugin into your local QGIS plugins folder.
- `make zip`: Creates a release-ready ZIP file.
- `make docus`: Builds the Sphinx documentation.
- `make clean`: Removes temporary and compiled files.
