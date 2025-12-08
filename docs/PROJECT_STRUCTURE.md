# Sec Interp - Project Structure

## Project Overview

**Sec Interp** is a QGIS plugin for extracting and visualizing geological data along cross-section profiles. It enables geologists to create topographic profiles from DEMs, project geological outcrops, and visualize structural measurements (dip/strike) in a 2D section view.

**Version**: 1.0  
**Author**: Juan M Bernales  
**License**: GPL-2.0 / GPL-3.0  
**Repository**: https://github.com/geociencio/sec_interp  
**QGIS Minimum Version**: 3.0

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
│   ├── algorithms.py          ⭐ Main processing algorithms
│   ├── utils.py               ⭐ Utility functions (projections, calculations)
│   ├── validation.py          ⭐ Input validation logic
│   └── __init__.py
│
├── 📁 gui/                     # User interface components
│   ├── main_dialog.py         ⭐ Main dialog class (Plugin Manager style)
│   ├── legend_widget.py       ⭐ Legend overlay widget
│   ├── preview_renderer.py    ⭐ Profile rendering engine
│   ├── ui/                    # Qt Designer files
│   │   ├── main_dialog_base.ui    ⭐ UI definition (XML)
│   │   └── main_dialog_base.py    # Generated Python UI
│   └── __init__.py
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
Main processing engine containing:
- `topographic_profile()`: Extracts elevation data from DEM along a line.
- `geol_profile()`: Projects geological polygons onto the section.
- `project_structures()`: Projects structural point data (dip/strike).

#### `utils.py` ⭐
Utility functions for:
- Geometric calculations (azimuth, distance, projections).
- Coordinate transformations.
- Data parsing (dip/strike formats).

#### `validation.py` ⭐
Input validation for:
- Layer geometry types.
- Field existence and types.
- Numeric input ranges.
- Output path validation.

### GUI Module (`gui/`)

#### `main_dialog.py` ⭐
Main dialog class implementing:
- Plugin Manager style UI (sidebar + stacked widget).
- Preview generation and export.
- Input validation and user feedback.
- Integration with QGIS native widgets.

#### `legend_widget.py` ⭐
Transparent overlay widget for displaying geological legend on the map canvas.

#### `preview_renderer.py` ⭐
Rendering engine for:
- Drawing topographic profiles.
- Rendering geological units with colors.
- Plotting structural symbols (dip/strike).
- Generating legends.

#### `ui/main_dialog_base.ui` ⭐
Qt Designer XML file defining the UI layout with:
- Responsive layouts (QVBoxLayout, QHBoxLayout, QSplitter).
- QGIS native widgets (QgsMapLayerComboBox, QgsFileWidget).
- Preview canvas and results panel.

### Configuration Files

#### `metadata.txt` ⭐
QGIS plugin metadata including:
- Version number and changelog.
- Author and repository information.
- Plugin description and tags.

#### `Makefile` ⭐
Build automation for:
- Compiling UI files (`pyuic5`).
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
# Compile UI and resources
make

# Deploy to local QGIS
make deploy

# Run tests
pytest

# Create distribution package
make zip
```

### Key Make Targets
- `make`: Compile all resources and UI files.
- `make deploy`: Deploy to local QGIS plugins directory.
- `make zip`: Create distribution ZIP file.
- `make clean`: Remove compiled files.
- `make doc`: Generate Sphinx documentation.

## Plugin Architecture

### Design Patterns
- **MVC Pattern**: Separation of UI (`gui/`), business logic (`core/`), and data.
- **SOLID Principles**: Applied throughout, especially in `main_dialog.py`.
- **Plugin Manager Style**: Modern sidebar navigation with stacked pages.

### Data Flow
1. User selects layers and parameters in GUI.
2. `main_dialog.py` validates inputs using `validation.py`.
3. `algorithms.py` processes data (profile extraction, projection).
4. `preview_renderer.py` renders results on canvas.
5. User can export to various formats (PNG, SVG, PDF, CSV).

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
