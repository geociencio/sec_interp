# Refactor: Restructure project layout following QGIS best practices

## 🎯 Objetivo

Reestructurar el proyecto SecInterp siguiendo las mejores prácticas de desarrollo de plugins QGIS, mejorando la mantenibilidad, escalabilidad y calidad del código.

## 📁 Nueva Estructura del Proyecto

```
sec_interp/
├── core/                    # Lógica de negocio
│   ├── __init__.py
│   ├── algorithms.py        # (antes: sec_interp.py)
│   ├── utils.py            # (antes: si_core_utils.py)
│   └── validation.py       # (antes: validation_utils.py)
├── gui/                     # Interfaz de usuario
│   ├── __init__.py
│   ├── main_dialog.py      # (antes: sec_interp_dialog.py)
│   ├── preview_renderer.py
│   └── ui/                 # Archivos UI compilados
│       ├── __init__.py
│       ├── main_dialog_base.py
│       └── main_dialog_base.ui
├── resources/               # Recursos (iconos, QRC)
│   ├── __init__.py
│   ├── resources.py
│   └── resources.qrc
├── tests/                   # Tests (NUEVO)
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_algorithms.py
│   ├── test_validation.py
│   └── test_integration.py
├── scripts/                 # Scripts de build
│   ├── deploy.sh
│   ├── compile-strings.sh
│   └── fix-ui-syntax.sh
└── .github/
    └── workflows/
        └── test.yml         # CI/CD (NUEVO)
```

## 📋 Cambios Principales

### 1. Estructura Modular
- ✅ Creación de paquetes `core/`, `gui/`, `resources/`
- ✅ Organización lógica de archivos por responsabilidad
- ✅ Archivos `__init__.py` con exports explícitos

### 2. Testing & CI/CD
- ✅ Directorio `tests/` con configuración QGIS
- ✅ Tests unitarios iniciales (3 tests pasando)
- ✅ GitHub Actions workflow para CI

### 3. Calidad de Código
- ✅ Pylint score: 8.33 → 10.00
- ✅ Imports actualizados a rutas relativas
- ✅ Configuración `.pylintrc` optimizada

### 4. Build & Deploy
- ✅ `Makefile` actualizado
- ✅ `scripts/deploy.sh` refactorizado
- ✅ `.gitignore` mejorado

## 📊 Métricas

| Métrica | Antes | Después |
|---------|-------|---------|
| Estructura | Plana | Modular |
| Tests | 0 | 3 |
| Pylint | 8.33 | 10.00 |
| Archivos raíz | ~15 | ~5 |

## 🔧 Cambios Técnicos Detallados

### Imports Actualizados

**Antes:**
```python
from .sec_interp import SecInterp
from . import si_core_utils as scu
from . import validation_utils as vu
```

**Después:**
```python
from .core.algorithms import SecInterp
from .core import utils as scu
from .core import validation as vu
```

### Scripts de Build

**Makefile:**
- Actualizado `SOURCES` y `PY_FILES` con nuevas rutas
- Modificado `UI_FILES` a `gui/ui/main_dialog_base.ui`
- Actualizado `COMPILED_RESOURCE_FILES` a `resources/resources.py`

**deploy.sh:**
- Refactorizado para copiar estructura de directorios
- Soporte para paquetes `core/`, `gui/`, `resources/`
- Creación automática de subdirectorios

## ✅ Verificación

- [x] Tests unitarios pasando (3/3)
- [x] Imports corregidos
- [x] Scripts de build actualizados
- [x] `make deploy` funcional
- [ ] Plugin cargado en QGIS (pendiente validación)

## 🚀 Próximos Pasos

1. Validar carga del plugin en QGIS
2. Ejecutar flujo completo de trabajo
3. Añadir más tests de integración
4. Documentar API de módulos core

## 📝 Commits

1. **Refactor: Restructure project layout following best practices**
   - Movimiento de archivos a nueva estructura
   - Creación de paquetes y `__init__.py`
   - Actualización de scripts de build
   - Configuración de tests y CI/CD

2. **Fix: Add missing PreviewRenderer import in core/algorithms.py**
   - Corrección de import faltante
   - Resolución de NameError al cargar plugin

## 🔗 Referencias

- [QGIS Plugin Best Practices](docs/QGIS_PLUGIN_BEST_PRACTICES.md)
- [GitHub Actions Workflow](.github/workflows/test.yml)
- [Pytest Configuration](tests/conftest.py)
