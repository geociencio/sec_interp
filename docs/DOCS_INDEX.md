# Documentation Index (MOC)

> Single entry point for the SecInterp documentation: canonical sources, the
> code-walkthrough vaults, the structure tree and the docs tooling.

## Canonical documents (source of truth)

| Topic | Canonical file | Notes |
|-------|----------------|-------|
| Architecture (detailed) | [ARCHITECTURE_EN.md](ARCHITECTURE_EN.md) | Sphinx copy: [source/ARCHITECTURE.md](source/ARCHITECTURE.md) |
| Monolithic vs Clean | [ARCHITECTURE_MONOLITHIC_VS_CLEAN_EN.md](ARCHITECTURE_MONOLITHIC_VS_CLEAN_EN.md) | |
| Plugin report & comparison | [PLUGIN_REPORT_AND_COMPARISON_EN.md](PLUGIN_REPORT_AND_COMPARISON_EN.md) | |
| Changelog | [CHANGELOG.md](CHANGELOG.md) | canonical; `docsec/CHANGELOG*` are legacy |
| Core distinction | [CORE_DISTINCTION_GUIDE.md](CORE_DISTINCTION_GUIDE.md) (ES) · [\_EN](CORE_DISTINCTION_GUIDE_EN.md) | synced to `source/` |
| User guide | [source/USER_GUIDE.md](source/USER_GUIDE.md) | Sphinx |
| User guide conventions | [USER_GUIDE_CONVENTIONS.md](USER_GUIDE_CONVENTIONS.md) | images, naming, translation |
| Docs style guide | [DOCS_STYLE_GUIDE.md](DOCS_STYLE_GUIDE.md) | MyST, links, duplicates |
| Development guide (published) | [source/DEVELOPMENT_GUIDE.md](source/DEVELOPMENT_GUIDE.md) | Sphinx |
| Development guide (repo) | [docsec/DEVELOPMENT_GUIDE.md](docsec/DEVELOPMENT_GUIDE.md) | |
| Commit guidelines | [docsec/COMMIT_GUIDELINES.md](docsec/COMMIT_GUIDELINES.md) | |
| Project structure | [docsec/PROJECT_STRUCTURE.md](docsec/PROJECT_STRUCTURE.md) | + generated tree below |
| Logging guidelines | [LOGGING_GUIDELINES.md](LOGGING_GUIDELINES.md) | |
| Dev environment | [../README_DEV.md](../README_DEV.md) | root |

## Code-walkthrough vaults (Obsidian)

- [code_walkthrough/Index.md](code_walkthrough/Index.md) — Spanish vault (file notes + layer notes).
- [code_walkthrough_en/Index.md](code_walkthrough_en/Index.md) — English vault.
- Mirror docs (`ARCHITECTURE_EN`, …) are auto-synced from `docs/` by `scripts/sync_vault_mirrors.sh`.

## Generated structure tree

- [structure/project_structure.md](structure/project_structure.md) · [structure/project_structure.txt](structure/project_structure.txt)

## Tooling

| Command | Purpose |
|---------|---------|
| `make docs` | Build all languages → `../sec_interp_docs` → publish to `geociencio/sec_interp_docs` |
| `make docs-check` | Fail on stale module refs, broken links, mirror drift |
| `make docs-version` | Sync version/date headers from `metadata.txt` |
| `make docs-i18n` | Report per-language translation coverage |
| `make docs-i18n-update` | Extract `.pot` + `sphinx-intl update` (sync catalogs) |
| `bash scripts/sync_docs_mirrors.sh --check` | `docs/` ↔ `docs/source/` mirror drift |
| `bash scripts/sync_vault_mirrors.sh --check` | vault mirror drift |

## Versioning

`metadata.txt` is the **single source of truth** for the version. `docs/source/conf.py`
reads it automatically, and `scripts/sync_docs_version.py` updates the hand-maintained
`Version … | Last Updated` headers.

## Published languages

- `DOCS_LOCALES` (default `en es`) controls the **published website**; a language joins
  only when its `USER_GUIDE.po` reaches ≥ 80%.
- `DOCS_HELP_LOCALES` (default: all UI languages) controls the **offline in-plugin help**.

## Historical records

Plans (`plans/`), `docsec/archive/`, releases (`releases/`), maintenance logs
(`maintenance/`), walkthroughs (`walkthroughs/`), ADRs (`adr/`), `maintainer/`,
`qa/` and `research/` document past states and are intentionally **not** kept
up to date.
