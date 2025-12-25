# Sec Interp - Project Structure

## Project Overview

**Sec Interp** is a QGIS plugin for extracting and visualizing geological data along cross-section profiles. It enables geologists to create topographic profiles from DEMs, project geological outcrops, and visualize structural measurements (dip/strike) in a 2D section view.

**Version**: 2.3.0
**Author**: Juan M Bernales
**License**: GPL-2.0 / GPL-3.0
**Repository**: https://github.com/geociencio/sec_interp
**QGIS Minimum Version**: 3.0

> **Note**: Version 2.3.0 includes major architectural improvements including modular geometry utilities, manager-based UI delegation, and enhanced performance optimizations. See [CHANGELOG.md](CHANGELOG.md) for details.

## Technology Stack

### Python Environment
- **Python**: 3.x (compatible with QGIS 3.x)
- **PyQt5**: ≥5.12, <6
- **QGIS Python API**: Provided by QGIS installation (qgis.core, qgis.gui)

### Development Tools
- **Build System**: GNU Make
- **Testing**: pytest with QGIS support
- **Code Quality**: Pylint (score: 10/10)
- **CI/CD**: GitHub Actions

## Directory Structure

```
sec_interp/
├── 📁 core/                    # Core business logic
│   ├── algorithms.py          ⭐ Main orchestrator class
│   ├── data_cache.py          # Caching mechanism for performance
│   ├── validation.py          ⭐ Input validation logic
│   ├── services/              # Business logic encapsulated in services
│   │   ├── profile_service.py
│   │   ├── geology_service.py
│   │   └── structure_service.py
│   └── utils/                 # Package of utility modules
│       ├── geometry.py        # Facade for geometry operations
│       ├── geometry_utils/    ⭐ Modular geometry sub-package (v2.3.0)
│       │   ├── extraction.py  # Vertex and line extraction
│       │   ├── processing.py  # Buffer, densify, memory layers
│       │   └── filtering.py   # Spatial filtering with CRS support
│       ├── spatial.py
│       ├── sampling.py
│       ├── drillhole.py
│       └── ...
│
├── 📁 gui/                     # User interface components
│   ├── main_dialog.py         ⭐ Main dialog orchestrator (refactored v2.3.0)
│   ├── main_dialog_tools.py   ⭐ DialogToolManager (map tools, v2.3.0)
│   ├── main_dialog_preview.py ⭐ PreviewManager (centralized preview logic)
│   ├── main_dialog_signals.py # DialogSignalManager (signal connections)
│   ├── preview_renderer.py    ⭐ Profile rendering engine
│   ├── legend_widget.py       # Legend overlay widget
│   └── ui/                    # Programmatic UI modules
│       ├── main_window.py     ⭐ Main UI layout assembly
│       ├── sidebar.py         # Navigation sidebar
│       └── pages/             # Individual settings pages
│           ├── dem_page.py
│           ├── drillhole_page.py
│           └── ...
│
├── 📁 resources/               # Plugin resources
│   ├── resources.qrc          # Qt resource file
│   └── resources.py           # Compiled resources
│
├── 📁 docs/                    # Documentation
│   ├── COMMIT_GUIDELINES.md   ⭐ Commit message standards
│   ├── RELEASE_PROCESS.md     ⭐ Release workflow
│   ├── drilllogs_research.md  # Future: Drillhole integration
│   ├── ves_research.md        # Future: VES/SEV integration
│   ├── sp_research.md         # Future: SP data integration
│   └── REFACTORING_PR.md      # Historical refactoring notes
│
├── 📁 scripts/                 # Build and deployment scripts
│   ├── deploy.sh              # Local QGIS deployment
│   ├── fix-ui-syntax.sh       ⭐ Post-UI-generation fixes
│   └── compile-strings.sh     # Translation compilation
│
├── 📁 tests/                   # Unit tests
│   ├── conftest.py            # pytest configuration
│   └── test_*.py              # Test modules
│
├── 📁 i18n/                    # Internationalization
│   ├── SecInterp_es.ts        # Spanish translation source
│   └── SecInterp_es.qm        # Compiled Spanish translation
│
├── 📁 help/                    # Plugin help documentation
│   └── build/html/            # Sphinx-generated HTML docs
│
├── 📄 __init__.py             ⭐ Plugin entry point
├── 📄 metadata.txt            ⭐ QGIS plugin metadata
├── 📄 logger_config.py        # Logging configuration
├── 📄 Makefile                ⭐ Build automation
├── 📄 requirements.txt        # Runtime dependencies
├── 📄 requirements-dev.txt    # Development dependencies
├── 📄 .pylintrc               # Pylint configuration
├── 📄 README.md               # Project overview
└── 📄 icon.png                # Plugin icon
```

## Key Files Description

### Core Module (`core/`)

#### `algorithms.py` ⭐
The main orchestrator class (`SecInterp`) that connects the UI to the backend services. It initializes all components, handles UI events, and coordinates the data processing and exporting workflows.

#### `services/` (Package) ⭐
Contains specialized services that encapsulate the core business logic for specific domains:
- `ProfileService`: Generates the topographic profile.
- `GeologyService`: Handles geological outcrop processing.
- `StructureService`: Manages structural data projection and apparent dip calculation.

#### `utils/` (Package) ⭐
A package of utility modules providing reusable functions for:
- Geometry operations, data parsing, spatial calculations, and more.

#### `validation.py` ⭐
Handles all input validation, ensuring that layers, fields, and parameters are correct before processing.

### GUI Module (`gui/`)

#### `main_dialog.py` ⭐
The main dialog class that contains the application's business logic. It inherits the UI layout from `main_window.py` and connects UI signals to backend functionality. It uses a set of manager/handler classes to delegate tasks like validation, previewing, and exporting.

#### `ui/main_window.py` ⭐
Assembles the main programmatic UI using a `QSplitter` to create a three-panel layout (Sidebar, Settings, Preview).

#### `ui/pages/` (Package) ⭐
A package containing self-contained page widgets for each settings group (e.g., `DemPage`, `SectionPage`). Each page manages its own inputs and validation.

#### `preview_renderer.py` ⭐
A powerful rendering engine that draws the interactive profile preview on a `QgsMapCanvas`, handling topography, geology, structures, and vertical exaggeration.

### Configuration Files

#### `metadata.txt` ⭐
QGIS plugin metadata including:
- Version number and changelog.
- Author and repository information.
- Plugin description and tags.

#### `Makefile` ⭐
Build automation for:
- Compiling resources (`pyrcc5`).
- Compiling translations (`lrelease`).
- Creating distribution ZIP.
- Deploying to local QGIS.

#### `.pylintrc`
Pylint configuration achieving 10/10 score with:
- Disabled irrelevant checks.
- Project-specific naming conventions.
- Import organization rules.

## Build and Deployment

### Development Workflow
```bash
# Compile resources and translations
make

# Deploy to local QGIS
make deploy

# Run tests
pytest

# Create distribution package
make zip
```

### Key Make Targets
- `make`: Compile all resources and translations.
- `make deploy`: Deploy to local QGIS plugins directory.
- `make zip`: Create distribution ZIP file.
- `make clean`: Remove compiled files.
- `make doc`: Generate Sphinx documentation.

## Plugin Architecture

### Design Patterns
- **Service Layer**: Core logic is encapsulated in specialized services in `core/services/`.
- **Orchestrator/Controller**: The `SecInterp` class in `algorithms.py` acts as a central controller that coordinates between the UI and the backend services.
- **Component-Based UI**: The UI is programmatically built from modular, reusable components (Pages, Sidebar, etc.).
- **Factory/Strategy**: Used in the `exporters` module to provide a flexible and extensible way to export data.

### Data Flow
1. User selects layers and parameters in the `gui`.
2. The `main_dialog` validates inputs via the `DialogValidator`.
3. The `SecInterp` class in `algorithms.py` orchestrates the process, calling the necessary services from `core/services/`.
4. `ProfileService`, `GeologyService`, and `StructureService` process the data and return the results.
5. `preview_renderer.py` renders the results on the map canvas.
6. The user can export the data, which uses the `exporters` module.

## Future Enhancements

Planned features documented in `docs/`:
1. **Drillhole Integration** (`drilllogs_research.md`): Visualize drill hole trajectories and intervals.
2. **VES/SEV Integration** (`ves_research.md`): Display vertical electrical sounding data.
3. **SP Integration** (`sp_research.md`): Show spontaneous potential measurements.

## Contributing

See `docs/COMMIT_GUIDELINES.md` for commit message standards (Conventional Commits).
See `docs/RELEASE_PROCESS.md` for version release workflow.

## License

Dual-licensed under GPL-2.0 and GPL-3.0. See `LICENSE-GPL-2.0.txt` and `LICENSE-GPL-3.0.txt`.
