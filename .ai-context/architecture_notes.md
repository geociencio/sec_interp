# SecInterp — Curated Architecture Notes

> Hand-maintained guidance injected into `AI_CONTEXT.md` (section "MANUAL
> ARCHITECTURE NOTES"). Keep it short, high-level and current; it complements —
> never duplicates — the auto-generated metrics. Canonical sources:
> `AGENTS.md`, `docs/ARCHITECTURE_EN.md`, `docs/CORE_DISTINCTION_GUIDE_EN.md`.

## What SecInterp is
A QGIS plugin (Python, PyQt via `qgis.PyQt`) for geological **section
interpretation**: it projects drillholes, geological polygons and structural
measurements onto a user-drawn section line, samples a DEM for topography, and
exports 2D/3D interpretations. UI is built **programmatically** (no `.ui` files).

## Layout
- `core/` — pure business logic, QGIS-agnostic (thread-safe). Services,
  algorithms, validation, DTO types. **Must never import `qgis.gui`.**
- `gui/` — QGIS/PyQt layer. Pages, dialogs, `QgsTask` background work, map tools.
- `exporters/` — output formats (CSV, DXF, GPKG, SHP, PNG, PDF, SVG, 3D).
- `tests/` — `unittest` (Mock-First, no real QGIS). `docs/` — Sphinx + vault.
- `.agent/` (framework submodule) + `.agent-state/` (project overlay/state).

## Non-negotiable principle: Extract-then-Compute
1. **GUI extracts** live QGIS data into DTOs / WKT / primitives.
2. **Core computes** with QGIS-agnostic types only.
3. **GUI converts** results back to QGIS objects when needed.

Consequences:
- No `QgsVectorLayer`/`QgsProject`/`qgis.gui` in `core/`.
- Prefer **WKT** over `QgsGeometry` across the boundary.
- Heavy work runs in `QgsTask` (background); no live QGIS objects off the main
  thread. Core services must be thread-safe.

## Conventions
- Python 3.9+ runtime (QGIS 3.28), 3.12 for development; `from __future__ import annotations`, full type annotations,
  Google-style docstrings, `ruff format` (100 cols) is the canonical formatter.
- Naming: `PascalCase` classes, `snake_case` functions, `UPPER_SNAKE` constants.
- Errors: custom hierarchy under `core/exceptions.py` (`SecInterpError` +
  `ValidationError`, ...); never leak raw exceptions to the UI.
- i18n: user-facing strings wrapped with `self.tr()` / `QCoreApplication.translate`;
  technical strings tagged `# no-i18n`.
- Commits: Conventional Commits, English. Package manager: `uv`.

## Data / geological logic
- Drillhole surveys and section interpolation use 3-level validation; structure
  parsing handles quadrant/dip conventions (see `geological-logic` skill).
- Sampling is **CRS-aware**: build a line→raster `QgsCoordinateTransform` and
  transform sample points; never densify by raw raster pixel size (it can explode
  vertex counts). Raster CRS labels can lie — verify vs the extent.
- Profile statistics deduplicate by raster cell, not by Z.

## Known traps (from AGENT_LESSONS)
- Page-internal signals must be wired in an **idempotent `connect_signals()`**,
  not `_setup_ui` (SignalManager disconnect→connect cycle loses them).
- `QDialog.accept()` does **not** fire `closeEvent` — clean up preview layers in
  both paths (`accept_handler`/`done`/`closeEvent`) or QGIS leaks scratch layers.
- Mocks must mirror the real Qt API only; never invent methods to satisfy code.
- Analyzer/ai-ctx analyze ALL plugin code (`core/`, `gui/`, `exporters/`) — see
  `.analyzerignore`. `qgis-plugin-analyzer` is the single source of quality
  metrics; `forge metrics validate` guards doc/ground-truth coherence.

## Where to look
- Architecture & boundaries: `docs/ARCHITECTURE_EN.md`, `AGENTS.md`.
- Core-vs-QGIS "core" confusion: `docs/CORE_DISTINCTION_GUIDE_EN.md`.
- Recent decisions/sessions: `docs/DEVELOPMENT_LOG.md`, `docs/maintenance/`.
- Agent workflow/state: `.agent/workflows/`, `.agent-state/next_steps.md`.
