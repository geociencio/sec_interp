# SecInterp Development Guide

This document provides guidelines for extending and maintaining the SecInterp plugin following the new decoupled architecture.

## 🛠️ Development Environment
- **Python**: 3.9+
- **QGIS**: 3.28 LTR or higher.
- **Package Manager**: `uv` is preferred for dependency management and analysis scripts.

## 📐 Design Principles
1. **Core/GUI Separation**: Never import `PyQt5`, `PyQt6`, or `qgis.gui` inside `core/`. If you need QGIS-specific data types, use `qgis.core`.
2. **Specialized Services**: All heavy business logic must reside in a service within `core/services/`.
3. **UI Managers**: `MainDialog` must delegate responsibilities to Manager classes (e.g., `PreviewManager`, `DialogToolManager`).
4. **Pure Geometry**: Use `core/utils/geometry.py` (and its subgroups) for common spatial operations.

## 🧪 Adding a New Feature
If you want to add a new preview type:
1. **Core**: Create a method in `PreviewService` (or a new service) that processes the data and returns a type defined in `core/domain/entities.py`.
2. **GUI Manager**: Update `PreviewManager` to call the new service and store the result in `cached_data`. Update the hash calculation if the data depends on new parameters.
3. **Renderer**: Update `PreviewRenderer` and `PreviewLayerFactory` to create the new visualization layer and apply symbology.

## 📈 Performance & Caching
- **Hash-based Cache**: If you add parameters to the dialog, include them in `PreviewManager._calculate_params_hash()`.
- **Simplification**: Implement LOD if the feature involves processing thousands of geometries.
- **Spatial Indexing**: Always use `QgsSpatialIndex` when you need to filter vector layers by proximity.

## 🔄 Workflows (Recommended)

### 🧪 Running Tests
The project uses `unittest`. To run tests correctly and resolve the `sec_interp` package, use the following command from the root:

```bash
PYTHONPATH=.. uv run python3 -m unittest discover sec_interp/tests
```

**Note**: Do not use `pytest`. Make sure to include `PYTHONPATH=..` so that imports work correctly.

### 💾 Clean Commits
To avoid conflicts with pre-commit hooks (which may reformat code and cause the commit to fail), it is recommended to follow this order:

1. **Pre-formatting**:
   ```bash
   uv run ruff check --fix .
   uv run ruff format .
   ```
2. **Commit**:
   ```bash
   git add .
   git commit -m "type: description"
   ```

## 🧹 Code Quality
- **Pre-commit**: Install with `uv run pre-commit install`. Checks run on every commit.
- **Linting**: Run `uv run ruff check .` to validate standards.
- **Metrics Analysis**: Run `uv run ai-ctx analyze .` regularly to monitor complexity.
- **QGIS Audit**: Use `uv run qgis-analyzer analyze .` for QGIS regulatory validations.
- Follow the conventions in [COMMIT_GUIDELINES.md](../standards/COMMIT_GUIDELINES.md) (Conventional Commits).
- **Important**: Try to fix pre-commit errors instead of skipping them. Use `--no-verify` only if absolutely necessary and temporary.
- Keep cyclomatic complexity per function below 15 whenever possible.

---
**Version**: 2.9.0 | **Ref**: [README_DEV.md](README_DEV.md)
