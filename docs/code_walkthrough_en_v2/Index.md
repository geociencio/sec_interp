---
tags:
  - secinterp
  - code-walkthrough
  - moc
aliases:
  - SecInterp Code Walkthrough v2
  - SecInterp Code Guide v2
cssclass: secinterp-moc
---

# 🗺️ SecInterp — Code Walkthrough v2 (MOC)

> [!abstract] Purpose
> A **complete, self-contained** vault (v2) documenting the SecInterp implementation
> file by file. Each note reaches a depth of **400–500 lines** (substantive notes) with
> a method-by-method walkthrough, data flow, patterns, error handling and tests. The v1
> vault (`code_walkthrough/`) is kept untouched.

> [!info] Context
> - **Plugin**: SecInterp — QGIS ≥ 3.28, QGIS 4.x ready
> - **Architecture**: Clean Architecture (Core/GUI separation)
> - **Documented version**: 3.8.0
> - **Status**: 🚧 Phase 0 (pilot) — 3 reference notes complete

---

## 📚 Note index

### ✅ Phase 0 pilot (depth reference)

| Note | Tier | Source | Lines |
|---|:---:|---|---:|
| [[drillhole]] | A | `core/utils/drillhole.py` | ~410 |
| [[core_interfaces]] | C | `core/interfaces/` (package) | ~400 |
| [[path_resolver]] | B | `core/services/export/path_resolver.py` | ~300 |

### ⏳ Rest of the vault (Phases 1–4)

The remaining 175 notes will be generated and enriched by layer:
- **Phase 1** — Core (`domain`, `interfaces`, `models`, `utils`, `validation`, `services/export`)
- **Phase 2** — GUI (`adapters`, `renderers`, `tasks`, `tools`, `ui/`, managers, `preview_*`)
- **Phase 3** — Exporters / Plugin / Root
- **Phase 4** — `layer_*` + `Index` + mirrors

> [!warning] Link convention
> `[[...]]` links may appear **unresolved** until the note is created. This is
> intentional: they mark future work.

---

## 🧭 How to read these notes

Each note follows the v2 template (`_template.md`):

1. **Frontmatter** — tags and aliases.
2. **Summary + why does it exist?** — problem/solution.
3. **Diagram** — relationship Mermaid.
4. **Imports** — architectural reading.
5. **Inventory** — classes/functions/constants.
6. **Method-by-method walkthrough** — the depth core.
7. **Data flow** — input → transformation → output.
8. **Patterns / API / Errors / Tests / Observations**.
9. **Related notes** — wikilinks.

> [!tip] Structure documents
> See [[project_structure]] (tree) and [[project_structure_table]] (tabular depth view)
> for the full plugin map.

---

## 🔖 Tags used

`#secinterp` · `#code-walkthrough` · `#moc` · `#core` · `#gui` · `#exporters` · `#plugin` · `#interfaces` · `#services` · `#utils`

---

*Root note of the v2 vault — update when adding each new note.*
