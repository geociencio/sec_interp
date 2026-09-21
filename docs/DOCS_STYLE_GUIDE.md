# Documentation Style Guide

> Conventions for writing and maintaining the SecInterp documentation.

## Language

- Code, commits and user-facing docs: **English**.
- Spanish is allowed for internal/agent notes; bilingual pairs use the `_EN.md` suffix.

## File naming

- `lowercase_with_underscores.md`; English variants: `*_EN.md`.
- One topic per file; keep the tree shallow.

## Links

| Context | Convention |
|---------|------------|
| Obsidian vault notes | short-slug wikilinks: `[[controller]]`, `[[layer_core]]` |
| `docs/` (GitHub/Sphinx) | `[text](code_walkthrough/slug.md)` or relative markdown links |
| Vault mirrors | auto-rewritten by `scripts/sync_vault_mirrors.sh` (`](code_walkthrough/` → `](`) |

- Do **not** use relative links that escape the Sphinx source dir (`docs/source/`) — use inline code or a full URL instead.
- Prefer linking to a canonical doc; avoid duplicating content.

## Headers and metadata

- Standalone docs start with `> Version X.Y.Z | Last Updated: YYYY-MM-DD` or `**Version**: X.Y.Z`.
- Version/date are synced from `metadata.txt` via `make docs-version`.

## Sphinx / MyST

- MyST Markdown; Mermaid via fenced ` ```mermaid ` blocks.
- Google-style docstrings (Napoleon) for all public APIs.

## Duplicates and mirrors

- **Canonical** lives in `docs/`; the `docs/source/` copy is synced by `scripts/sync_docs_mirrors.sh`.
- Run `--check` in CI/pre-push; never hand-edit a mirror.
- Historical material stays in `plans/`, `docsec/archive/`, `releases/`, `maintenance/`,
  `walkthroughs/`, `adr/`, `maintainer/`, `qa/`, `research/` and is **not** rewritten.

## Internationalization (docs)

The plugin **UI** is translated (~99–100% in 13 languages), but the **documentation**
catalogs (`docs/locales/*/LC_MESSAGES/*.po`) are largely empty. Policy:

- **Published website** = `DOCS_LOCALES` (default `en es`). A language joins the
  published set only when its `USER_GUIDE.po` reaches **≥ 80%** coverage.
- **Offline in-plugin help** = `DOCS_HELP_LOCALES` (default: all UI languages), so the
  plugin keeps its per-language manual.
- Translate only the user-facing pages (`USER_GUIDE`, `ARCHITECTURE`,
  `DEVELOPMENT_GUIDE`, `CORE_DISTINCTION_GUIDE`); the autodoc pages stay in English.

Workflow:

```bash
make docs-i18n-update   # extract .pot + sphinx-intl update (prune obsolete, add new)
make docs-i18n          # coverage report per language
```

## Quality gates

- `make docs-check` must pass: no stale `.py` references, no broken relative links,
  no mirror drift.
- Keep `make docs-i18n` coverage in mind when touching translated pages.

## Commit style

- `docs(scope): summary` (Conventional Commits), see `docsec/COMMIT_GUIDELINES.md`.
