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
| # | Module | Status | Short description |
|---|--------|:------:|-------------------|
| 01 | [[01 - sec_interp_plugin]] | ✅ | Root class `SecInterp`: plugin lifecycle, toolbar, DI |
| 02 | [[02 - __init__]] | ✅ | `classFactory` that QGIS invokes |
| 03 | [[03 - logger_config]] | ✅ | Centralized logging + QGIS handler |

### Core layer (`core/`)
| # | Module | Status | Short description |
|---|--------|:------:|-------------------|
| 10 | [[10 - controller]] | ✅ | `ProfileController` — service orchestrator |
| 11 | [[11 - domain]] | ✅ | DTOs: `PreviewParams`, `ProfileData`, `GeologySegment`… |
| 12 | [[12 - exceptions]] | ✅ | `SecInterpError` hierarchy |
| 13 | [[13 - profile_service]] | ✅ | Topography extraction |
| 14 | [[14 - geology_service]] | ✅ | Geological intersections |
| 15 | [[15 - drillhole_service]] | ✅ | Drillhole projection |
| 16 | [[16 - validation]] | ✅ | Validation pipeline |
| 17 | [[17 - safe_loader]] | ✅ | Fault-tolerant lazy loading |
| 18 | [[18 - i18n]] | ✅ | `TranslatableMixin` |
| 19 | [[19 - structure_service]] | ✅ | Structural projection |
| 27 | [[27 - config]] | ✅ | Configuration service |
| 28 | [[28 - data_cache]] | ✅ | Per-bucket cache (SHA256 + TTL) |
| 29 | [[29 - performance_metrics]] | ✅ | Timings, counts and memory |

### GUI layer (`gui/`)
| # | Module | Status | Short description |
|---|--------|:------:|-------------------|
| 20 | [[20 - main_dialog]] | ✅ | `SecInterpDialog` — manager orchestrator |
| 21 | [[21 - dialog_preview_manager]] | ✅ | Preview and canvas lifecycle |
| 22 | [[22 - dialog_export_manager]] | ✅ | Export UI logic |
| 23 | [[23 - renderers]] | ✅ | Specialized renderers |
| 24 | [[24 - tasks]] | ✅ | Background `QgsTask` |
| 25 | [[25 - adapters]] | ✅ | "Extract" phase (QGIS → DTOs) |
| 26 | [[26 - ui_pages]] | ✅ | Window + pages (Sidebar/Stack) |
| 32 | [[32 - state_manager]] | ✅ | Visual state + persistence delegation |
| 33 | [[33 - input_manager]] | ✅ | Input aggregation + validation |
| 34 | [[34 - signal_manager]] | ✅ | Idempotent signal wiring |
| 35 | [[35 - interpretation_manager]] | ✅ | Polygons + inheritance + dual persistence |
| 36 | [[36 - tool_manager]] | ✅ | Pan + Measure + Interpretation tools |
| 37 | [[37 - layer_notification_manager]] | ✅ | dataChanged → invalidate(bucket) |
| 38 | [[38 - ui_status_manager]] | ✅ | Indicators + enable/disable |
| 39 | [[39 - preview_state]] | ✅ | PreviewCache + RenderState |
| 40 | [[40 - preview_layer_factory]] | ✅ | Memory layer factory |

### Exporters layer (`exporters/`)
| # | Module | Status | Short description |
|---|--------|:------:|-------------------|
| 30 | [[30 - base_exporter]] | ✅ | `BaseExporter` contract |
| 31 | [[31 - vector_exporter]] | ✅ | GPKG/SHP/DXF |

> [!tip] Legend
> ✅ documented · ⏳ pending · 🔄 under review

> [!note] Mirror documents
> The files `ARCHITECTURE_EN.md`, `ARCHITECTURE_MONOLITHIC_VS_CLEAN_EN.md`, and `PLUGIN_REPORT_AND_COMPARISON_EN.md` inside this vault are **mirror copies** of `docs/` (source of truth). They are kept here so wikilinks resolve in Obsidian. If you update the original in `docs/`, re-sync these copies.

> [!info] Naming convention
> Existing notes with `NN -` prefix are kept as legacy. New notes use **number-free names** (e.g. `preview_renderer.md`), navigable by sections/tags. The number is just a historic ID, not reading order.

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
