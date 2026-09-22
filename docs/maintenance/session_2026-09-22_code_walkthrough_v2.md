# Maintenance Session: 2026-09-22 - Code Walkthrough Vault v2 (Complete Bilingual Vault)

## Technical Summary

Started building a **new, complete, self-contained bilingual code-walkthrough vault v2**
(`docs/code_walkthrough_v2/` ES + `docs/code_walkthrough_en_v2/` EN), leaving the
existing v1 vaults untouched. The v2 vault targets **400–500 lines per note** (a
method-by-method depth standard), with a per-note `note_lines` ceiling of **700** for a
curated list of high-importance orchestrator modules. This is a docs-only initiative:
no Python source changed.

## Changes Made

### Tooling (new scripts)

- **`scripts/generate_vault_v2.py`**: AST-based generator. Scans `core/`, `gui/`,
  `exporters/`, `plugin/`, `resources/` and the root entry points (178 `.py` files) and
  tiers them by size: Tier A (≥100 lines) → individual 400–500-line note, Tier B
  (50–99) → individual ~300–400, Tier C (<50) → grouped into one note per package
  directory (24 groups). Collision-safe slugs (`resolve_individual_slugs`), package
  **file enumeration** (a `Archivos del paquete` table with file, lines, and docstring
  role), `--layer` filter, and a `HIGH_IMPORTANCE` set that injects
  `note_lines: 700` into the frontmatter of 10 orchestrator modules. A `_is_skeleton`
  guard makes `--write` overwrite skeletons but never enriched notes.
- **`scripts/check_notes.py`**: note-size/completeness gate. Hard cap 500 (or the
  frontmatter `note_lines`, max 700); tiered minimums (A/C 400, B 300); placeholder
  detection (`(pendiente)`, `(skeleton)`, …) with a `--strict` mode; ES↔EN slug parity.
- **`scripts/check_docs.py`**: added `code_walkthrough_v2` / `code_walkthrough_en_v2`
  to `EXCLUDE_PARTS` (mirrors the v1 exclusion).
- **`scripts/sync_vault_mirrors.sh`**: mirrors architecture/report docs into all four
  vaults and structure docs (`project_structure*.md/txt`) into the v2 vaults only.

### Structure docs

- Added `docs/structure/project_structure_table.md` (tabular depth view of the plugin
  tree, Depth 1–5), committed earlier as `46fd3b45`.

### Vault v2 content

- `_template.md` (ES+EN): extended template (12 sections incl. method walkthrough, data
  flow, error handling, tests) + optional `note_lines` field.
- `Index.md` (ES+EN): MOC for the v2 vault (Phase 0 pilot + phased roadmap).
- 3 mirror docs + 3 structure docs synced per vault.
- **56 Core skeletons generated** (29 A + 16 B + 11 C groups).
- **7 Core notes enriched** (ES+EN): `controller` (500 l., `note_lines: 700`),
  `drillhole` (408), `path_resolver` (306), `core_interfaces` (423, with self-anchor
  file table), `dtos` (407), `entities` (401), `exceptions` (307).

## Verification Results

- `check_notes.py` PASS (112 notes, 98 skeletons; enriched notes within 400–500/300+).
- `check_docs.py` PASS (36 active docs).
- `sync_vault_mirrors.sh --check` PASS.
- `ruff check .` PASS (scripts excluded by project config).
- Docs-only: Python source unchanged; ground-truth tests unchanged.

## Impact

The v2 vault is now a standalone, tooling-backed knowledge base in progress: generators
and a size gate are in place, and the enrichment pattern (400–500-line notes with
self-anchor package tables) is demonstrated on 7 Core notes. Remaining work: enrich the
~49 Core skeletons, then generate/enrich GUI, exporters and plugin, then add `layer_*`
notes and finalize the MOC.

## Commits

`46fd3b45` `docs(structure): add tabular depth view of the plugin directory`
`59f3984` `docs(code-walkthrough): add v2 vault, tooling and enriched Core notes`
