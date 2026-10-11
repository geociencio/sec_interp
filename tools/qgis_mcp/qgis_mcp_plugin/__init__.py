from .plugin import classFactory

# QGIS plugin entry point - re-export via __all__ so both ruff and flake8 see it used.
__all__ = ["classFactory"]
