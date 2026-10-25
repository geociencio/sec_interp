# Session 2026-10-25 — qgis-manage 0.12.0 Adoption & Release Readiness

## Objective

Consume the three consecutive `qgis-manage` releases (0.10.1, 0.11.0, 0.12.0),
verify which 0.10.0 findings they fix, adopt the new tooling in SecInterp, and
re-assess the release gate for **3.12.0** without changing plugin runtime code.

## Result

`qgis-manage` 0.12.0 is installed and pinned; the Makefile, release CI and package
configuration use its new capabilities. All quality gates are green, but the
**3.12.0 release artifacts are not prepared** (version, changelog, notes, README,
tag, portal). The plugin ZIP builds with the stamped 3.12.0 version
and 340 files.

## Changes

### Dependency and tooling

- `pyproject.toml`: `qgis-manage>=0.10.0` → `>=0.12.0`; `uv.lock` at 0.12.0.
- `[tool.qgis-manager]`: `qgis_version = 4`, `max_backups = 1`,
  `auto_compile = false` (a bare deploy cannot target QGIS 3 or trigger a Sphinx
  build).
- `.gitignore` / `.qgisignore`: `.qgis-manage/` (deploy manifest) and the local
  screenshot staging folder `docs/source/images_v3.12.0/`.

### Makefile

- `compile`: one `--type resources --type translations` invocation when the
  `.qrc`/icon changed, translations-only otherwise, plus `--jobs` (`COMPILE_JOBS`,
  default 4). The manual `sed` patch is gone (0.10.0+ auto-patches rcc/uic imports).
- `clean`: project-owned cleanup (caches, `help/html`, `.qgis-manage`) because
  `qgis-manage clean` deletes every `*.cpg/*.qpj` and the generated `resources.py`;
  both are tracked here (`examples/sample_data/*.cpg`).
- `zip`: `package --repo-check`.
- `docker-test`: metrics post-step now uses `uv run python` (the system `python3`
  lacks `qgis_plugin_analyzer`).
- `test`/`deploy`: `transcompile` removed (already covered by `compile`).

### Release automation

- Retired the scheduled/queue train: removed `.release-queue.json`,
  `scripts/next_scheduled_release.py` and `.github/workflows/scheduled-release.yml`.
  v3.9.1–v3.11.0 were the last queue-driven releases; 3.12.0 onward are manual.
- Manual packaging still uses `package --repo-check --stamp --release-version X.Y.Z`
  when needed: `--stamp` makes the packaged `metadata.txt` match the ZIP name and adds
  `commitSha1`/`commitNumber`/`dateTime`.

### Documentation

- `docs/research/qgis_manage_0.12.0_analysis.md` replaces the 0.10.0 analysis:
  fixed findings, 0.10.0 vs 0.12.0 measurements, remaining limitations.
- Updated `docs/maintainer/qgis_manage_deployment_guide.md` (repeatable `--type`,
  clean caveat, manifest, `--dry-run`/`--yes`, non-shell hooks, `--require-docs`).
- Updated the roadmap status banner and `docs/CHANGELOG.md` `[Unreleased]`.

## Measurements (0.10.0 → 0.12.0)

| Flow | 0.10.0 | 0.12.0 |
| :--- | ---: | ---: |
| `package --repo-check` | 3 193 ms | **671 ms** (4.8×) |
| `package` | 577 ms | 609 ms |
| `deploy` with backup | 454 ms | 442–446 ms |
| `deploy` manifest vs `--no-manifest` | — | 455 ms vs 425 ms |
| 13 translations, `--jobs 4` | 132 ms | 128 ms |
| Translations with fresh `.qm` | 132 ms | **111 ms** (skipped) |
| Consecutive deploys in the same second | `rc=1` | `rc=0` |

## Upstream limitations found

- `package --require-docs` hardcodes `help/html/index.html`; SecInterp publishes
  `help/html/<lang>/index.html`, so the flag is a false negative (not used).
- `clean` deletes tracked `*.cpg`/`*.qpj`; `--keep-generated` only protects `.py`.
- `profiles list` only enumerates QGIS 3 and has no `--qgis-version`.
- The deploy manifest (165 KB for 340 files) is neutral/slower on small plugins.
- Hooks are non-shell by default (0.12.0, breaking); SecInterp has no
  `plugin_hooks.py`, so no impact.

## Verification results

| Gate | Result |
| :--- | :--- |
| Local tests | **839 OK** (888 static) |
| Docker suite | exit 0 (agentic/core/exporters/gui/integration; 76 integration OK) |
| `ruff check` / `ruff format --check` | PASS (206 files formatted) |
| `mypy` | PASS, 102 files (sandbox: `MYPY_CACHE_DIR` inside the workspace) |
| `check_docs.py` | PASS (37 active docs) |
| `i18n-check` | 6 tests OK, gate PASS |
| `security-scan` | bandit/detect-secrets PASS (flake8 info only) |
| Qt6 checker | 0 findings |
| Analyzer | CC PASS, 37 issues, docstring 99.1 %, security 100, module size PASS |
| Packaging | 340 files, 2.4 MB, stamped 3.12.0, no dev dirs |

## Release readiness

Green: code, tests, static gates, Docker, Qt6, packaging. Missing: version bump
(3.11.0), `[Unreleased]` → `[3.12.0]`, release notes, README badge/"What's New",
development-log milestone, commit/push/tag, GitHub release and manual portal
upload. **Queue releases were retired** (3.9.1–3.11.0 were the last entries and all are
published): the queue, its selector script and the scheduled workflow were removed, so
3.12.0 is cut manually from `main` (no queue entry, no `release/v3.12.0` branch). The
Gen 8 release workflow still contains obsolete steps (`docsec` changelog,
`make package VERSION=main`, `plugin_upload.py`, partial `git add`).

## Impact

- The repository no longer fights the tooling: compile is clean, cleaning cannot
  delete tracked data, and release CI cannot publish a ZIP whose metadata version
  differs from its filename.
- `--repo-check` dropped from ~3.2 s to ~0.7 s, so it is cheap enough to run in
  every package build.
- The remaining work before 3.12.0 is editorial/release, not technical.
