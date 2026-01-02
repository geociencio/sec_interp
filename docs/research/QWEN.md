# SecInterp QGIS Plugin - Development Context

## Project Overview

SecInterp (Section Interpreter) is a sophisticated QGIS plugin designed for geological interpretation and cross-section analysis. It enables geologists to extract and visualize geological data including topographic profiles, geological outcrops, structural measurements, and drillhole data in a unified 2D view.

### Key Features
- **Interactive Preview System**: Real-time visualization of topography, geology, and structures along section lines
- **Performance Optimizations**: Parallel processing, adaptive Level of Detail (LOD), and smart caching
- **Multi-point Measurement Tool**: Polyline tracing with comprehensive metrics
- **Drillhole Support**: 3D drillhole trace projection and geological interval visualization
- **Professional Export**: Multiple formats (SHP, CSV, DXF, PDF, SVG, PNG)

### Architecture
The project follows a well-structured architecture with clear separation of concerns:

```
GUI Layer: Main Dialog
├── PreviewManager
├── DialogToolManager
├── ExportManager
└── ValidationManager
Core Services
├── PreviewService
├── DrillholeService
├── StructureService
├── ProfileService
├── GeologyService
└── ParallelGeologyService
Utilities
├── geometry_utils/
│   ├── extraction.py
│   ├── processing.py
│   └── filtering.py
└── sampling.py
```

## Project Structure

```
sec_interp/
├── core/                 # Business logic and services
│   ├── controller.py     # Main orchestration controller
│   ├── services/         # Domain-specific services
│   ├── utils/            # Utility functions
│   └── validation/       # Input validation
├── gui/                  # User interface components
│   ├── main_dialog.py    # Main dialog implementation
│   ├── main_dialog_*.py  # Specialized managers
│   ├── preview_renderer.py
│   └── ui/               # UI components
├── exporters/            # Data export functionality
├── docs/                 # Documentation
├── tests/                # Test suite
├── resources/            # UI resources
└── i18n/                 # Internationalization files
```

## Development Environment

### Prerequisites
- Python 3.9+
- QGIS 3.28+ LTR
- PyQt5 (5.15.x)
- Development tools: `uv` preferred for package management

### Dependencies
- Runtime: PyQt5 (for IDE support, QGIS provides runtime)
- Development: Listed in `requirements-dev.txt`

## Building and Running

### Development Setup
1. Clone the repository
2. Install dependencies: `pip install -r requirements-dev.txt`
3. Use the Makefile for development tasks

### Key Commands
- `make test` - Run test suite
- `make deploy` - Deploy plugin to QGIS
- `make zip` - Create plugin package for distribution
- `make pylint` - Run code quality checks
- `make pep8` - Run style checking with Ruff

### Testing
- Test suite uses pytest with configuration in `pytest.ini`
- Tests are located in the `tests/` directory
- Run with: `pytest -v` or `make test`

## Development Conventions

### Architecture Principles
1. **Separation Core/GUI**: No PyQt or qgis.gui imports in core/
2. **Specialized Services**: Business logic in core/services/
3. **UI Managers**: MainDialog delegates to manager classes
4. **Pure Geometry Functions**: Use core/utils/geometry_utils/ for spatial operations

### Code Quality
- Follow PEP 8 style guidelines (enforced by Ruff)
- Use type hints throughout the codebase
- Write comprehensive docstrings
- Maintain low cyclomatic complexity (<15 per function)
- Use conventional commits

### Configuration
- Ruff configuration in `ruff.toml`
- Pylint configuration in `.pylintrc`
- Makefile for build automation

### Performance Considerations
- Implement hash-based caching in PreviewManager
- Use spatial indexing (QgsSpatialIndex) for efficient filtering
- Implement Level of Detail (LOD) for topography
- Use parallel processing for heavy computations

## Key Components

### Core Services
- **ProfileController**: Main orchestration of data services
- **PreviewService**: Coordinates preview generation
- **DrillholeService**: Handles drillhole data processing
- **GeologyService**: Processes geological outcrop data
- **StructureService**: Processes structural measurements

### UI Managers
- **PreviewManager**: Handles preview generation and rendering
- **DialogToolManager**: Manages map tools (measurement, snapping)
- **ExportManager**: Handles data export functionality
- **DialogValidator**: Input validation

## Internationalization
- Translation files in `i18n/` directory
- Use `make transup` to update translation strings
- Use `make transcompile` to compile translation files

## Documentation
- User Guide: docs/USER_GUIDE.md
- Architecture: ARCHITECTURE.md
- Development Guide: DEVELOPMENT_GUIDE.md
- API documentation: Generated with Sphinx

## Version Information
- Current version: 2.3.0
- Plugin type: Vector
- QGIS minimum version: 3.0
- License: GPL v3

## Special Considerations
- The plugin is designed for geological interpretation workflows
- Heavy use of QGIS API for spatial operations
- Performance optimization critical for large datasets
- Extensive caching mechanism to avoid redundant computations
