# SecInterp Development Guidelines for AI Agents

This document provides essential guidelines for agentic coding agents working on the SecInterp QGIS plugin. It covers build commands, code style, architectural principles, and development workflows.

---

## 🚀 Build/Lint/Test Commands

### Core Commands
```bash
# Environment setup
make init                    # Initialize complete dev environment (proposed)
uv sync                     # Install dependencies

# Building and deployment
make compile                 # Compile resources and UI
make deploy                  # Deploy to QGIS plugins directory
make zip                     # Create distributable package

# Testing
make test                    # Run full test suite (unittest discovery)
uv run pytest tests/         # Alternative pytest runner
make docker-test             # Run 361+ tests in Docker environment

# Single test execution
uv run pytest tests/core/test_algorithms.py::test_intersection -v
uv run python -m unittest tests.test_geology_service.TestGeologyService.test_method
```

### Code Quality
```bash
make pylint                  # Run static analysis
make pep8                    # Run ruff style checking
uv run ruff check .          # Direct ruff linting
uv run ruff format .         # Auto-format code
pre-commit run --all-files   # Run all pre-commit hooks
```

---

## 🏗️ Architectural Principles

### Core/GUI Separation (CRITICAL)
The project follows a strict **Extract-then-Compute** pattern:

1. **GUI Layer (`/gui`)**: Extracts data from QGIS objects into DTOs
2. **Core Layer (`/core`)**: Processes using QGIS-agnostic types (WKT, dicts, primitives)
3. **Results**: Core returns validated DTOs, GUI converts back to QGIS if needed

#### NEVER do this in `/core`:
```python
# ❌ FORBIDDEN - Direct QGIS dependencies in core
from qgis.core import QgsVectorLayer, QgsProject
layer = QgsProject.instance().mapLayerByName("geology")

# ❌ FORBIDDEN - GUI dependencies
from qgis.gui import QgsMapTool
iface.mapCanvas().refresh()
```

#### ALWAYS do this in `/core`:
```python
# ✅ CORRECT - Use primitive types and WKT
def process_geology(geometry_wkt: str, attributes: dict) -> GeologySegment:
    # Pure business logic with thread-safe operations
    return GeologySegment(geometry=geometry_wkt, props=attributes)
```

### Thread Safety Requirements
- Core services must be thread-safe for background processing
- Use `QgsTask` for heavy operations in GUI layer
- No live QGIS objects in background threads
- Prefer WKT over QgsGeometry in core processing

---

## 📝 Code Style Guidelines

### Import Organization
```python
from __future__ import annotations  # REQUIRED in all modules

# Standard library
import os
import logging
from typing import Dict, List, Optional

# Third-party
from PyQt5.QtCore import QObject, Signal
from qgis.core import QgsVectorLayer, QgsFeature

# Local imports (absolute)
from sec_interp.core.exceptions import ValidationError
from sec_interp.core.types import ProfileData
```

### Type Annotations (REQUIRED)
```python
def calculate_intersection(
    line_wkt: str,
    polygon_wkt: str,
    tolerance: float = 0.001
) -> Optional[GeologySegment]:
    """Calculate line-polygon intersection.

    Args:
        line_wkt: Line geometry in WKT format
        polygon_wkt: Polygon geometry in WKT format
        tolerance: Intersection tolerance in map units

    Returns:
        GeologySegment if intersection exists, None otherwise

    Raises:
        ValidationError: If input geometries are invalid
    """
```

### Naming Conventions
```python
# Classes: PascalCase
class GeologyService:
class ValidationError:

# Functions/Variables: snake_case
def parse_strike_dip(data: dict) -> tuple[float, float]:
buffer_distance = 50.0

# Constants: UPPER_SNAKE_CASE
MAX_SAMPLES = 1000
DEFAULT_TOLERANCE = 0.001

# Private members: Leading underscore
def _validate_core_params(self, params: dict) -> bool:
```

### Error Handling Patterns
```python
# Use custom exception hierarchy
class ValidationError(SecInterpError):
    def __init__(self, message: str, field: str = None):
        super().__init__(message)
        self.field = field

# Structured error handling
try:
    result = process_data(data)
except ValidationError as e:
    logger.error(f"Validation failed: {e.message}")
    return False, e.message
except Exception as e:
    logger.exception(f"Unexpected error in process_data")
    raise
```

---

## 🔧 Development Workflow

### 1. Making Changes
```bash
# 1. Create feature branch
git checkout -b feature/new-geological-algorithm

# 2. Make changes (following style guidelines)
# 3. Run quality checks
uv run ruff check .
uv run ruff format .
make pylint

# 4. Run tests
uv run pytest tests/core/test_new_feature.py -v
make docker-test  # Full integration test
```

### 2. Testing Strategy
```bash
# Core logic tests (standalone, no QGIS required)
uv run pytest tests/core/ -v

# Integration tests (require QGIS)
uv run pytest tests/integration/ -v

# Performance benchmarks
uv run pytest tests/benchmarks/ -v

# Single test with coverage
uv run pytest tests/core/test_algorithms.py::test_intersection -v --cov=core.algorithms
```

### 3. Commit Standards
- Use conventional commits: `feat:`, `fix:`, `refactor:`, `test:`, `docs:`
- Pre-commit hooks enforce formatting and commit message standards
- Each commit should pass tests locally

---

## 📊 Project Structure Overview

```
core/                    # 🧠 Pure business logic (QGIS-agnostic)
├── services/           # Data processing services
├── utils/              # Utility functions
├── types.py             # Domain types and DTOs
├── exceptions.py       # Custom exception hierarchy
└── validation/         # Validation framework

gui/                     # 🖥️ UI and QGIS interaction layer
├── tasks/              # Background processing (QgsTask)
├── tools/              # Interactive tools
├── ui/pages/           # UI components
└── services/           # GUI-specific services

exporters/               # 📤 Data export functionality
tests/                   # 🧪 Comprehensive test suite
├── core/               # Core logic tests (standalone)
├── integration/        # Full QGIS integration tests
└── benchmarks/         # Performance tests
```

---

## ⚡ Performance Guidelines

### 1. Core Processing
- Use NumPy for numerical operations where applicable
- Implement caching for expensive calculations
- Profile critical paths with `@performance_metrics.track()`

### 2. GUI Operations
- Use `QgsTask` for operations > 100ms
- Implement progress reporting for user feedback
- Batch QGIS operations to minimize canvas refreshes

---

## 🛡️ Quality Assurance

### 1. Code Quality Gates
- All code must pass `ruff check` and `ruff format`
- Pylint score > 8.0 required
- Test coverage > 80% for new features

### 2. Testing Requirements
- Unit tests for all new functions/classes
- Integration tests for QGIS interactions
- Performance tests for algorithmic changes

### 3. Documentation
- Docstrings following Google style for all public APIs
- Type annotations required for all function signatures
- Update relevant documentation for API changes

---

## 🔍 Debugging & Development Tips

### 1. QGIS Development
```bash
# Source QGIS environment for development
source /path/to/qgis/share/qgis/python/qgisenv.sh

# Debug QGIS plugins
export QGIS_DEBUG=3
export QGIS_LOG_FILE=qgis_debug.log
```

### 2. Common Issues
- **Import errors**: Ensure `uv sync` has been run and environment is activated
- **QGIS not found**: Check that QGIS Python environment matches development environment
- **Thread crashes**: Verify no QGIS GUI objects are used in background threads

---

## 📚 Key Resources

- **Architecture**: `docs/ARCHITECTURE_EN.md`
- **Core Distinction**: `docs/CORE_DISTINCTION_GUIDE_EN.md`
- **Agent Configuration**: `.agent/AGENTS.md`
- **Development**: `README_DEV.md`

---

## ⚠️ Critical Reminders

1. **NEVER** import `qgis.gui` in `/core` modules
2. **ALWAYS** follow the Extract-then-Compute pattern
3. **MAINTAIN** thread safety in core services
4. **USE** type annotations everywhere
5. **RUN** tests before committing changes
6. **FOLLOW** the established naming and formatting conventions

This project maintains high architectural standards to ensure long-term maintainability and performance. Respect these principles in all contributions.
