# Documentation Update Analysis — 2026-09-20

> Broader follow-up to `docs_staleness_audit_2026-09-20.md` (which covered stale
> module/file **references**). This report analyses **other** dimensions: version
> headers, published content drift, broken links, duplication, Sphinx toctree and CI.
> **Analysis only — no docs edited in this report.**

## Scope / method

Scanned the **active** docs (`docs/*.md`, `docs/docsec/`, `docs/source/`,
`docs/maintainer/`, `docs/qa/`, `docs/research/`, root `README*.md`), excluding
historical sets (plans, `docsec/archive/`, releases, maintenance session logs,
walkthroughs, ADRs). Signals: version headers, `pytest`/test commands, test counts,
`gh-pages`, relative links, toctree membership and duplication.

---

## 1. Stale version headers (P1)

| Doc | Header says | Should be |
|-----|-------------|-----------|
| `docs/ARCHITECTURE_EN.md` | `Version 3.4.0 · Last Updated: 2026-09-19` | `3.8.0` |
| `docs/ARCHITECTURE_MONOLITHIC_VS_CLEAN_EN.md` | `Version 3.4.0 · Last Updated: 2026-09-19` | `3.8.0` |
| `docs/source/ARCHITECTURE.md` | `Version 2.9.0 · Last update: 2026-02-01` | `3.8.0` (content too — see §2) |

Historical version mentions (leave): `docs/source/v2.9.0_technical_analysis.md`,
`docs/research/QWEN.md` (2.3.0), `docs/research/v2.9.0_technical_analysis.md`,
`docs/v250_fix_report.md`.

## 2. Published content drift (P1/P2)

| Doc | Issue |
|-----|-------|
| `docs/source/ARCHITECTURE.md` | Entire doc describes the **v2.9.0** architecture (`main_dialog_*` split). Names were patched but the structure/sizes are 2.9.0-era. Recommend rewriting to match `docs/ARCHITECTURE_EN.md` or retiring it in favour of it. |
| `docs/source/USER_GUIDE.md` | Section "Advanced Features (**v3.0.0**)" does not cover v3.7/v3.8 (collapsible preview controls, i18n quality gate, 3D export defaults, drillhole/settings tabs). |
| `docs/source/TECHNICAL_COMPENDIUM.md` | API reference likely predates the refactor packages (`core/services/export/`, `plugin/`, `*_mixin`, tabs). |
| `docs/PLUGIN_ANALYSIS.md` | Analysis likely pre-refactor; review module inventory/coverage. |

## 3. Broken relative links (P1)

| Doc | Broken link | Fix |
|-----|-------------|-----|
| `docs/docsec/DEVELOPMENT_GUIDE.md` | `../standards/COMMIT_GUIDELINES.md` | `COMMIT_GUIDELINES.md` (same dir) |
| `docs/docsec/DEVELOPMENT_GUIDE.md` | `README_DEV.md` | `../../README_DEV.md` |
| `docs/docsec/DEVELOPMENT_GUIDE_EN.md` | same two | same fixes |
| `docs/DEVELOPMENT_LOG.md` | ~35 `maintenance/session_*.md` links | **historical** — the files were pruned; leave (or mark) |
| `docs/ARCHITECTURE_EN.md` / `DEVELOPMENT_LOG.md` | `code_walkthrough/slug.md` | literal example inside the tip — no fix needed |

## 4. Duplication / divergence risk (P2)

| Pair | Note |
|------|------|
| `docs/CORE_DISTINCTION_GUIDE.md`/`_EN.md` ↔ `docs/source/CORE_DISTINCTION_GUIDE.md`/`_EN.md` | Exact duplicates; edits can drift (both were patched in the same commit). Consider a single source + sync, or a Sphinx `include`. |
| `docs/ARCHITECTURE_EN.md` ↔ `docs/source/ARCHITECTURE.md` | Different content and different ages (3.4.0 vs 2.9.0). |
| `docs/docsec/DEVELOPMENT_GUIDE*.md` ↔ `docs/source/DEVELOPMENT_GUIDE.md` | Different content. |
| `docs/CHANGELOG.md` (183 l.) ↔ `docs/docsec/CHANGELOG.md` (398 l.) | Different; canonical one unclear. |
| `docs/code_walkthrough*/ARCHITECTURE_EN.md` | Auto-synced mirrors (OK; `sync_vault_mirrors.sh`). |

## 5. Sphinx toctree (`docs/source/index.rst`) (P2)

Published tree includes: `USER_GUIDE`, `ARCHITECTURE` (2.9.0), `DEVELOPMENT_GUIDE`,
`TECHNICAL_COMPENDIUM`, `CORE_DISTINCTION_GUIDE(_EN)`, `MAINTENANCE_LOG`,
`v2.9.0_technical_analysis`, `modules`, and hidden `phase_closure_v2.7.0…v3.0.0`.

- `docs/source/ARCHITECTURE.md` (2.9.0) is published and stale.
- Historical docs (`v2.9.0_technical_analysis`, `phase_closure_*`) are published; consider
  moving them to an explicit "Archive" caption.

## 6. CI docs workflow (P3)

`.github/workflows/docs.yml` is broken/inconsistent: runs `make apidocs-html`
(target does not exist), deploys to the main repo's `gh-pages` instead of the external
`sec_interp_docs` repo, and triggers on `sec_interp/**` (layout mismatch). See the
staleness audit for details.

## 7. Minor / false positives (verified)

- `docs/docsec/DEVELOPMENT_GUIDE.md:36` — explicitly says "Do **not** use `pytest`" and uses
  `unittest`: correct, no change.
- `docs/maintainer/uv_modernization_guide.md` — `pytest` mentions belong to a **generic**
  `uv` migration guide, not the SecInterp test workflow.
- `docs/ARCHITECTURE_EN.md:759` — `pyproject.toml | Ruff, pytest, mypy config` describes
  config files (minor wording).
- Test-count numbers (`620`, `572`, `361`, `124`) live in **logs** (`source/MAINTENANCE_LOG`,
  `docsec/CHANGELOG`, `logs/session_*`) — historical, leave.

## Status of the fixes

> [!success] Resolved in this session (same day)
> - **§1 Version headers**: `ARCHITECTURE_EN.md`, `ARCHITECTURE_MONOLITHIC_VS_CLEAN_EN.md` and `source/ARCHITECTURE.md` → `3.8.0`.
> - **§2 Content drift**: `source/ARCHITECTURE.md` managers/diagram/export-service/parallel-geology/PyQt5 sections refreshed to the refactor; `USER_GUIDE` Advanced Features de-versioned + collapsible-controls note + 3D default note; `TECHNICAL_COMPENDIUM` API reference updated (`build_segments`/`project_structures`/`process_context`, `PreviewService`, `AccessControlService`, `export/`, `GeologySegment.geometry_wkt`).
> - **§3 Broken links**: fixed in `docsec/DEVELOPMENT_GUIDE.md` / `_EN.md`.
>
> - **§4 Duplication/canonical**: added `scripts/sync_docs_mirrors.sh` (+`--check`) keeping `docs/source/CORE_DISTINCTION_GUIDE*.md` in sync with `docs/`; the Sphinx `CORE_DISTINCTION_GUIDE.md` was actually an EN duplicate and is now the ES guide. Marked `docsec/CHANGELOG*.md` as non-canonical (canonical: `docs/CHANGELOG.md`) and cross-referenced the two DEVELOPMENT_GUIDE copies.
> - **§5 Toctree**: moved `v2.9.0_technical_analysis` into the hidden "Project Archive" section of `docs/source/index.rst`.
>
> - **§6 CI**: `.github/workflows/docs.yml` rewritten to build all languages with `scripts/build_docs.sh` and publish to `geociencio/sec_interp_docs` (needs `DOCS_DEPLOY_TOKEN`).
>
> **Also added:** `scripts/check_docs.py` + `make docs-check` (stale module refs, broken links, mirror sync); `docs/source/conf.py` now auto-reads the version from `metadata.txt` and inserts the correct `sys.path` (autodoc previously failed to import `sec_interp`, leaving API pages empty).

## Documentation i18n status

`make docs-i18n` (`scripts/docs_i18n_status.py`) reports per-language coverage of
`docs/locales/*/LC_MESSAGES/*.po`. Current state (13 languages × 147 files):

| lang | coverage |
|------|---------:|
| es | 1.6% |
| de/fr/ja/ru/zh_CN | 0.6–0.9% |
| it/pt_BR | 0.5% |
| pl | 0.2% |
| fi/hi/id/nl | 0.1% |

**Finding:** the documentation translations are essentially empty (≈1%) while the
plugin **UI is ~99–100% translated** in 13 languages. The 14-language build was
publishing near-English content.

**Resolution (policy implemented):**
- Published website = `DOCS_LOCALES` (default `en es`); a language joins only when its
  `USER_GUIDE.po` reaches ≥ 80%.
- Offline in-plugin help = `DOCS_HELP_LOCALES` (default: all UI languages), unchanged.
- `translate_docs.py update` (`make docs-i18n-update`) extracts `.pot` and runs
  `sphinx-intl update` to prune obsolete entries and add new msgids (previously missing).
- **Catalog pruning**: removed 1820 autodoc/historical `.po` and untracked 1911 generated
  `.mo`; kept only the 7 user-facing catalogs per language. `docs/locales` shrank from
  **20 MB / 3822 tracked files to 2.4 MB / 98 `.po`** (`.mo` are now gitignored and
  regenerated by `build_docs.sh`).

## Docs tooling added

- `scripts/check_docs.py` + `make docs-check` (wired into CI `test.yml` and the local pre-push hook).
- `scripts/sync_docs_version.py` + `make docs-version` (headers from `metadata.txt`; also run by `build_docs.sh`).
- `scripts/docs_i18n_status.py` + `make docs-i18n`.
- `docs/DOCS_INDEX.md` (canonical map) and `docs/DOCS_STYLE_GUIDE.md`.
- `build_docs.sh` now uses `sphinx-build -j auto` (parallel) and syncs version headers.

## 8. Recommendations (priority)

1. **P1** — Fix version headers (`ARCHITECTURE_EN`, `ARCHITECTURE_MONOLITHIC_VS_CLEAN_EN`,
   `source/ARCHITECTURE`) and the two broken links in `docsec/DEVELOPMENT_GUIDE(_EN)`.
2. **P1** — Rewrite or retire `docs/source/ARCHITECTURE.md` (2.9.0) and refresh
   `docs/source/USER_GUIDE.md` advanced-features section.
3. **P2** — Decide the canonical source for the duplicated guides
   (`CORE_DISTINCTION_GUIDE`, `DEVELOPMENT_GUIDE`, `CHANGELOG`) and add a sync/include.
4. **P2** — Refresh `TECHNICAL_COMPENDIUM` API reference; move historical docs to an Archive section.
5. **P3** — Fix `.github/workflows/docs.yml` to publish to `sec_interp_docs`.

> Historical docs (plans, archive, releases, maintenance logs, walkthroughs, ADRs, research)
> were intentionally excluded from correction: they document past states.

---
*Generated by the documentation update analysis — no docs were modified.*
