# SecInterp Development Guide

This document provides guidelines for extending and maintaining the SecInterp plugin following the new decoupled architecture.

## 🛠️ Development Environment
- **Python**: 3.9+
- **QGIS**: 3.28 LTR or higher.
- **Package Manager**: `uv` is preferred for dependency management and analysis scripts.

## 📐 Design Principles
1. **Core/GUI Separation**: Never import `PyQt5`, `PyQt6`, or `qgis.gui` within `core/`. If you need QGIS-specific data types, use `qgis.core`.
2. **Specialized Services**: All heavy business logic should reside in a service within `core/services/`.
3. **UI Managers**: The `MainDialog` should delegate responsibilities to Manager classes (e.g., `PreviewManager`, `DialogToolManager`).
4. **Pure Geometries**: Use `core/utils/geometry.py` (and its subgroups) for common spatial operations.

## 🧪 Adding a New Feature
If you want to add a new type of preview:
1. **Core**: Create a method in `PreviewService` (or a new service) that processes the data and returns a type defined in `core/domain/entities.py`.
2. **GUI Manager**: Update `PreviewManager` to call the new service and store the result in `cached_data`. Update the hash calculation if the data depends on new parameters.
3. **Renderer**: Update `PreviewRenderer` and `PreviewLayerFactory` to create the new visualization layer and apply symbology.

## 📈 Performance and Caching
- **Hash-based Cache**: If you add parameters to the dialog, include them in `PreviewManager._calculate_params_hash()`.
- **Simplification**: Implement LOD if the feature involves processing thousands of geometries.
- **Spatial Indexing**: Always use `QgsSpatialIndex` when you need to filter vector layers by proximity.

## 🔄 Recommended Workflows

### 🧪 Running Tests
The project uses `unittest` strictly. To run tests correctly and resolve the `sec_interp` package, use the following command from the root directory:

```bash
PYTHONPATH=.. uv run python3 -m unittest discover sec_interp/tests
```

**Note**: Do not use `pytest`. Ensure `PYTHONPATH=..` is set for proper imports.

### 💾 Clean Commits
To avoid conflicts with pre-commit hooks (which might reformat code and fail the commit), it is recommended to follow this order:

1. **Pre-Format**:
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
- **Metrics Analysis**: Run `uv run ai-ctx analyze .` regularly to monitor cyclomatic complexity.
- **QGIS Audit**: Use `uv run qgis-analyzer analyze .` for QGIS-specific compliance checks.
- Follow the conventions in [COMMIT_GUIDELINES.md](../standards/COMMIT_GUIDELINES.md) (Conventional Commits).
- **Important**: Try to fix pre-commit errors instead of bypassing them. Use `--no-verify` only if absolutely necessary and temporary.
- Keep cyclomatic complexity per function below 15 whenever possible.

---
**Version**: 2.9.0 | **Ref**: [README_DEV.md](README_DEV.md)
