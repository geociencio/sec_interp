# Sec Interp — Project Structure

## Project Overview

**Sec Interp** is a QGIS plugin for extracting and visualizing geological data along cross-section profiles. It creates topographic profiles from DEMs, projects geological outcrops, and visualizes structural measurements (dip/strike) and drillholes in a 2D section view, with multi-format export (SHP, GPKG, DXF, CSV, PDF, SVG).

**Version**: 3.8.0
**Author**: Juan M Bernales
**License**: GPL-2.0 / GPL-3.0
**Repository**: https://github.com/geociencio/sec_interp
**Documentation**: https://geociencio.github.io/sec_interp_docs/
**QGIS Minimum Version**: 3.28 (QGIS 4.x ready)

## Technology Stack

- **Python**: 3.x (QGIS 3.28+ / QGIS 4.x ready)
- **Qt**: via `qgis.PyQt` (Qt5/Qt6 agnostic)
- **QGIS API**: `qgis.core` / `qgis.gui`
- **Testing**: `unittest` (Mock-First; unit tests do not require QGIS)
- **Build/Deploy**: GNU Make + `uv`
- **Quality gates**: `ruff`, `qgis-plugin-analyzer` (CC ≤ 10, i18n, module size), Bandit
- **CI/CD**: GitHub Actions

## Architecture — Clean Architecture (Core/GUI separation)

- **`core/`** — QGIS-agnostic, thread-safe business logic (Extract-then-Compute).
- **`gui/`** — QGIS-dependent UI: Extract phase (adapters), managers, renderers, tools, tasks.
- **`exporters/`** — Strategy-per-format behind `BaseExporter`.
- **`plugin/`** — Plugin lifecycle / input / render mixins composed by `SecInterp`.

## Directory Structure

The full generated tree lives in [`docs/structure/project_structure.md`](../structure/project_structure.md). Summary:

```text
sec_interp/
├── sec_interp_plugin.py        # Entry point (facade over plugin/ mixins)
├── logger_config.py            # Logging
├── metadata.txt                # QGIS metadata
├── core/                       # QGIS-agnostic business logic
│   ├── domain/                 # DTOs, entities, enums, task inputs
│   ├── interfaces/             # ABCs (IGeologyService, IPreviewService, …)
│   ├── models/                 # Settings model
│   ├── services/               # geology, structure, drillhole, preview, access_control, export/
│   ├── utils/                  # pure helpers + geometry_utils/
│   └── validation/             # 3-level validation framework
├── gui/                        # UI layer
│   ├── adapters/               # Extract phase (QGIS → DTOs)
│   ├── dialogs/                # modal dialogs
│   ├── renderers/              # per-datatype preview renderers
│   ├── tasks/                  # QgsTask background jobs
│   ├── tools/                  # QgsMapTool (measure, interpretation)
│   └── ui/                     # programmatic window, sidebar, pages/
├── exporters/                  # SHP/GPKG/DXF/CSV/PDF/SVG strategies
├── plugin/                     # lifecycle, input_validator, render_pipeline
├── resources/                  # icons, styles, compiled resources.py
└── i18n/                       # .ts sources + .qm catalogs
```

## Key Modules

### Core (`core/`)

- **`controller.py`** — `ProfileController`: orchestrates the services with granular caching.
- **`services/`** — `GeologyService`, `StructureService`, `DrillholeService`, `PreviewService`, `AccessControlService`, and the `export/` package.
- **`services/export/`** — `ExportService` facade + `handlers/` (one per data type) + `path_resolver` / `map_settings_factory`.
- **`services/drillhole/`** — collar/survey/interval processors + trajectory/projection engines.
- **`validation/`** — `ProjectValidator`, `LayerMetadata`, and the validator pipeline.
- **`domain/`** — DTOs (`PreviewParams`, `ProfileData`, `GeologySegment`, …) and task contexts.

### GUI (`gui/`)

- **`main_dialog.py`** — `SecInterpDialog` composition root (mixins + managers).
- **`dialog_*_manager.py`** — Preview/Export/Input/Interpretation/Signal/State/Tool managers.
- **`dialog_*_mixin.py` / `interpretation_*_mixin.py` / `preview_*_mixin.py`** — decomposed behaviour.
- **`adapters/`** — Extract phase (`DrillholeExtractor`, `GeologyExtractor`, `StructureExtractor`, `ProfileExtractor`, …).
- **`ui/pages/`** — `BasePage` + per-domain pages (drillhole/settings have tab sub-packages).

### Exporters (`exporters/`)

- `BaseExporter` + `VectorExporter`, `CsvExporter`, `DxfExporter`, `ProfileExporters`, `Drillhole*Exporter`, `Interpretation*Exporter`, `PdfExporter`, `SvgExporter`, `ImageExporter`.

## Build and Deployment

```bash
make compile   # resources + translations
make deploy    # deploy to local QGIS (QGIS_VERSION=3|4)
make test      # unittest discovery (or: make docker-test)
make zip       # release ZIP
make docs      # Sphinx docs → ../sec_interp_docs
```

## Design Patterns

- **Extract-then-Compute**: GUI extracts to DTOs; core computes pure.
- **Manager / Mixin decomposition** for the dialog.
- **Facade/Orchestrator**: `ProfileController`, `ExportService`.
- **Strategy per format**: exporters behind `BaseExporter`.
- **Observer**: Qt signals, centralized by `SignalManager`.

## Contributing

- Commit style: `docs/docsec/COMMIT_GUIDELINES.md`.
- Agent/dev workflow: root `AGENTS.md` and `README_DEV.md`.

## License

Dual-licensed under GPL-2.0 and GPL-3.0. See `LICENSE-GPL-2.0.txt` and `LICENSE-GPL-3.0.txt`.
