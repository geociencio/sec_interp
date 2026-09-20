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
| 10 | `core/controller.py` | ⏳ | `ProfileController` — service orchestrator |
| 11 | `core/domain/` | ⏳ | DTOs: `PreviewParams`, `ProfileData`, `GeologySegment`… |
| 12 | `core/exceptions.py` | ⏳ | `SecInterpError` hierarchy |
| 13 | `core/services/profile_service.py` | ⏳ | Topography extraction |
| 14 | `core/services/geology_service.py` | ⏳ | Geological intersections |
| 15 | `core/services/drillhole_service.py` | ⏳ | Drillhole projection |
| 16 | `core/validation/` | ⏳ | Validation pipeline |
| 17 | `core/utils/safe_loader.py` | ⏳ | Fault-tolerant lazy loading |
| 18 | `core/utils/i18n.py` | ⏳ | `TranslatableMixin` |

### GUI layer (`gui/`)
| # | Module | Status | Short description |
|---|--------|:------:|-------------------|
| 20 | `gui/main_dialog.py` | ⏳ | `SecInterpDialog` — manager orchestrator |
| 21 | `gui/dialog_preview_manager.py` | ⏳ | Preview and canvas lifecycle |
| 22 | `gui/dialog_export_manager.py` | ⏳ | Export UI logic |
| 23 | `gui/renderers/` | ⏳ | Specialized renderers |
| 24 | `gui/tasks/` | ⏳ | Background `QgsTask` |
| 25 | `gui/adapters/` | ⏳ | "Extract" phase (QGIS → DTOs) |

### Exporters layer (`exporters/`)
| # | Module | Status | Short description |
|---|--------|:------:|-------------------|
| 30 | `exporters/base_exporter.py` | ⏳ | `BaseExporter` contract |
| 31 | `exporters/vector_exporter.py` | ⏳ | GPKG/SHP/DXF |

> [!tip] Legend
> ✅ documented · ⏳ pending · 🔄 under review

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
