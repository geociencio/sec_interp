---
tags:
  - secinterp
  - code-walkthrough
  - moc
aliases:
  - SecInterp Code Walkthrough
cssclass: secinterp-moc
---

# 🗺️ SecInterp — Code Walkthrough (MOC)

> [!abstract] Purpose
> This vault documents the SecInterp implementation **file by file**.
> Each note explains the role, patterns, and relationships of one module.
> It will grow progressively.

> [!info] Project context
> - **Plugin**: SecInterp (Section Interpreter) — QGIS ≥ 3.28, QGIS 4.x ready
> - **Architecture**: Clean Architecture (Core/GUI separation)
> - **Documented version**: 3.8.0
> - See also: [[ARCHITECTURE_EN]] · [[ARCHITECTURE_MONOLITHIC_VS_CLEAN_EN]] · [[PLUGIN_REPORT_AND_COMPARISON_EN]]

---

## 📚 Note index

### Root level (entry point)
| File | Status | Short description |
|---|:------:|------------------|
| [[sec_interp_plugin]] | ✅ | Root class `SecInterp`: plugin lifecycle, toolbar, DI |
| [[plugin_mixins]] | ✅ | `plugin/` mixins (lifecycle, input, render) |
| [[__init__]] | ✅ | `classFactory` that QGIS invokes |
| [[logger_config]] | ✅ | Centralized logging + QGIS handler |

### Core layer (`core/`)
| File | Status | Short description |
|---|:------:|------------------|
| [[controller]] | ✅ | `ProfileController` — service orchestrator |
| [[domain]] | ✅ | DTOs: `PreviewParams`, `ProfileData`, `GeologySegment`… |
| [[exceptions]] | ✅ | `SecInterpError` hierarchy |
| [[profile_service]] | ✅ | Topography extraction |
| [[geology_service]] | ✅ | Geological intersections |
| [[drillhole_service]] | ✅ | Drillhole projection |
| [[validation]] | ✅ | Validation pipeline |
| [[safe_loader]] | ✅ | Fault-tolerant lazy loading |
| [[i18n]] | ✅ | `TranslatableMixin` |
| [[structure_service]] | ✅ | Structural projection |
| [[config]] | ✅ | Configuration service |
| [[data_cache]] | ✅ | Per-bucket cache (SHA256 + TTL) |
| [[performance_metrics]] | ✅ | Timings, counts and memory |
| [[export_service]] | ✅ | Compatibility shim (13 lines) |
| [[export_package]] | ✅ | `export/` package: orchestrator + handlers |
| [[preview_service]] | ✅ | Preview generation |
| [[access_control_service]] | ✅ | Access control |
| [[trajectory_engine]] | ✅ | Drillhole trajectory |
| [[collar_processor]] | ✅ | Collar processor |
| [[survey_processor]] | ✅ | Survey processor |
| [[interval_processor]] | ✅ | Interval processor |
| [[projection_engine]] | ✅ | 3D→2D projection |

### GUI layer (`gui/`)
| File | Status | Short description |
|---|:------:|------------------|
| [[main_dialog]] | ✅ | `SecInterpDialog` — manager orchestrator |
| [[dialog_mixins]] | ✅ | `main_dialog` mixins (message/lifecycle/facade) |
| [[dialog_preview_manager]] | ✅ | Preview and canvas lifecycle |
| [[preview_mixins]] | ✅ | Preview mixins (callbacks/render) |
| [[dialog_export_manager]] | ✅ | Export UI logic |
| [[renderers]] | ✅ | Specialized renderers |
| [[tasks]] | ✅ | Background `QgsTask` |
| [[adapters]] | ✅ | "Extract" phase (QGIS → DTOs) |
| [[ui_pages]] | ✅ | Window + pages (Sidebar/Stack) |
| [[state_manager]] | ✅ | Visual state + persistence delegation |
| [[input_manager]] | ✅ | Input aggregation + validation |
| [[signal_manager]] | ✅ | Idempotent signal wiring |
| [[interpretation_manager]] | ✅ | Polygons + inheritance + dual persistence |
| [[interpretation_mixins]] | ✅ | Interpretation mixins (persistence/inheritance) |
| [[tool_manager]] | ✅ | Pan + Measure + Interpretation tools |
| [[layer_notification_manager]] | ✅ | dataChanged → invalidate(bucket) |
| [[ui_status_manager]] | ✅ | Indicators + enable/disable |
| [[preview_state]] | ✅ | PreviewCache + RenderState |
| [[preview_layer_factory]] | ✅ | Memory layer factory |
| [[preview_renderer]] | ✅ | Render orchestrator |
| [[preview_axes_manager]] | ✅ | Grid + axes (nice 1-2-5) |
| [[drillhole_extractor]] | ✅ | Drillhole extract |
| [[structure_extractor]] | ✅ | Structure extract |
| [[geology_extractor]] | ✅ | Geology extract |
| [[validation_extractor]] | ✅ | Validation extract |
| [[measure_tool]] | ✅ | Measure tool |
| [[interpretation_tool]] | ✅ | Interpretation tool |
| [[drillhole_page]] | ✅ | Drillhole page (coordinator) |
| [[drillhole_tabs]] | ✅ | Collar/Survey/Interval tabs |
| [[settings_page]] | ✅ | Settings page (coordinator) |
| [[settings_tabs]] | ✅ | Default/Advanced/Info tabs + persistence |

### Exporters layer (`exporters/`)
| File | Status | Short description |
|---|:------:|------------------|
| [[base_exporter]] | ✅ | `BaseExporter` contract |
| [[vector_exporter]] | ✅ | GPKG/SHP/DXF |
| [[csv_exporter]] | ✅ | CSV tabular |
| [[interpretation_3d_exporter]] | ✅ | 3D interpretation export |
| [[drillhole_3d_exporter]] | ✅ | 3D drillhole export |
| [[pdf_exporter]] | ✅ | PDF |
| [[svg_exporter]] | ✅ | SVG |
| [[image_exporter]] | ✅ | Raster image |
| [[profile_exporters]] | ✅ | Profile export |
| [[dxf_exporter]] | ✅ | DXF |
| [[interpretation_exporters]] | ✅ | 2D interpretation export |
| [[drillhole_exporters]] | ✅ | Drillhole vector export |

> [!tip] Legend
> ✅ documented · ⏳ pending · 🔄 under review

> [!note] Mirror documents
> The files `ARCHITECTURE_EN.md`, `ARCHITECTURE_MONOLITHIC_VS_CLEAN_EN.md`, and `PLUGIN_REPORT_AND_COMPARISON_EN.md` inside this vault are **mirror copies** of `docs/` (source of truth). They are kept here so wikilinks resolve in Obsidian. If you update the original in `docs/`, re-sync these copies.

> [!info] Naming convention
> **Updated 2026-09-20**: `NN -` prefixes were removed from all notes. Names are now the file slug (e.g. `preview_renderer.md`). Navigation is by sections/tags, not by number.

> [!info] Refactor 2026-09-20 — Module Size Gate
> All 7 modules over 400 lines were decomposed. New notes: [[export_package]], [[plugin_mixins]], [[dialog_mixins]], [[preview_mixins]], [[interpretation_mixins]], [[drillhole_tabs]] and [[settings_tabs]]. The former notes ([[export_service]], [[sec_interp_plugin]], [[main_dialog]], [[dialog_preview_manager]], [[interpretation_manager]], [[drillhole_page]], [[settings_page]]) are kept as historical context and link to the new ones.

---

## 🧭 How to read these notes

Every note follows the same template:

1. **Frontmatter** — tags and aliases for search.
2. **Summary** — what it does and why it exists.
3. **Diagram** — Mermaid of relationships.
4. **Code walkthrough** — method by method.
5. **Patterns** — which design patterns it applies.
6. **Relationships** — wikilinks to related modules.
7. **Observations** — notes, risks, and improvements.

> [!warning] Link convention
> `[[...]]` links may appear **unresolved** until the note is created.
> That is intentional: they mark future work.

---

## 🔖 Tags used

`#secinterp` · `#code-walkthrough` · `#moc` · `#core` · `#gui` · `#exporters` · `#entry-point` · `#di` · `#i18n` · `#qgstask`

---

*Root note of the vault — update it when adding each new note.*
