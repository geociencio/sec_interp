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
| 12 | [[12 - exceptions]] | ⏳ | `SecInterpError` hierarchy |
| 13 | [[13 - profile_service]] | ⏳ | Topography extraction |
| 14 | [[14 - geology_service]] | ⏳ | Geological intersections |
| 15 | [[15 - drillhole_service]] | ⏳ | Drillhole projection |
| 16 | [[16 - validation]] | ⏳ | Validation pipeline |
| 17 | [[17 - safe_loader]] | ✅ | Fault-tolerant lazy loading |
| 18 | [[18 - i18n]] | ⏳ | `TranslatableMixin` |

### GUI layer (`gui/`)
| # | Module | Status | Short description |
|---|--------|:------:|-------------------|
| 20 | [[20 - main_dialog]] | ⏳ | `SecInterpDialog` — manager orchestrator |
| 21 | [[21 - dialog_preview_manager]] | ⏳ | Preview and canvas lifecycle |
| 22 | [[22 - dialog_export_manager]] | ⏳ | Export UI logic |
| 23 | [[23 - renderers]] | ⏳ | Specialized renderers |
| 24 | [[24 - tasks]] | ⏳ | Background `QgsTask` |
| 25 | [[25 - adapters]] | ⏳ | "Extract" phase (QGIS → DTOs) |

### Exporters layer (`exporters/`)
| # | Module | Status | Short description |
|---|--------|:------:|-------------------|
| 30 | [[30 - base_exporter]] | ⏳ | `BaseExporter` contract |
| 31 | [[31 - vector_exporter]] | ⏳ | GPKG/SHP/DXF |

> [!tip] Legend
> ✅ documented · ⏳ pending · 🔄 under review

> [!note] Mirror documents
> The files `ARCHITECTURE_EN.md`, `ARCHITECTURE_MONOLITHIC_VS_CLEAN_EN.md`, and `PLUGIN_REPORT_AND_COMPARISON_EN.md` inside this vault are **mirror copies** of `docs/` (source of truth). They are kept here so wikilinks resolve in Obsidian. If you update the original in `docs/`, re-sync these copies.

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
