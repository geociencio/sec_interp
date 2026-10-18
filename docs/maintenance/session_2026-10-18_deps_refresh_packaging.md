# Maintenance Session: 2026-10-18 — Dependency Refresh, Security Scope & Packaging Hygiene

Second session of the day, after
[session_2026-10-18_v311_merge_vault_portal.md](session_2026-10-18_v311_merge_vault_portal.md).
Tooling-only work plus a local deploy; **no plugin-runtime behaviour changed**.

## Technical Summary

Refreshed the `uv`-managed Python toolchain in two batches (safe + majors), committed the
pending `.agent` submodule update, fixed two scope leaks found while verifying (bandit and
`.qgisignore`) and deployed v3.11.0 to the local QGIS 4 profile.

## 1. Agentic-forge submodule (pending change from 2026-10-11)

The QGIS domain-pack workflow `release-plugin.md` still validated `763` tests. Committed
inside the submodule (`96a70d9`, `docs(qgis): refresh the release-plugin test count to 792`)
and bumped the superproject pointer (`d7963cc7`). The submodule was pushed to Codeberg, so
`git submodule update` resolves for other clones. The `v1.2.0` tag stays on `2de22cf`.

## 2. Safe batch (direct + patch/minor transitivity)

`uv lock --upgrade-package …` + `uv sync`:

- **Gates**: `ruff` 0.17.0 → **0.17.1**, `pre-commit` 4.6.2 → **4.7.0**,
  `pytest-mock` 3.16.0 → **3.17.0**.
- **Transitive (19)**: click 8.5.0, requests 2.34.2, urllib3 2.8.0, certifi 2026.10.18,
  charset-normalizer 3.5.2, platformdirs 4.13.4, pathspec 1.1.1, pluggy 1.7.0,
  stevedore 5.9.1, typing-extensions 4.16.0, pygments 2.21.0, distlib 0.4.4,
  identify 2.6.20, idna 3.20, iniconfig 2.3.1, markupsafe 3.0.4, nodeenv 1.11.0,
  packaging 26.3, snowballstemmer 3.1.1, babel 2.18.0, ast-serialize 0.13.1.

## 3. Major bumps (each verified against its consumer)

| Package | Change | Consumer exercised |
| :--- | :--- | :--- |
| `rich` | 14.2.0 → **15.0.0** | `ai-context-core` / `bandit` CLI (`make context`, `make security-scan`) |
| `virtualenv` | 20.36.1 → **21.14.11** | `pre-commit` hook environments (cache wiped, envs rebuilt from scratch) |
| `filelock` | 3.20.3 → **4.2.2** | pulled by virtualenv; same pre-commit rebuild |
| `imagesize` | 1.4.1 → **2.0.1** | Sphinx HTML build |
| `python-discovery` | new 1.6.3 | dependency of virtualenv 21 |

`docutils` stays at **0.22.4**: Sphinx 9.1 and myst-parser cap it at `<0.23`, so 0.23 is not
installable yet (not a choice).

Minimums bumped for the gated tools (`ruff>=0.17.1`, `pre-commit>=4.7.0`) and
`ruff-pre-commit` synced to `v0.17.1`.

## 4. Bandit scope leak (pre-existing, found during verification)

`make security-scan` was **red before any change**: bandit ran `-r .` and picked up
`.agent/tools/*` and `tools/qgis_mcp/install.py` → 15 findings (LOW/MEDIUM), none of them
shipped in the plugin ZIP. Added both directories to `.bandit` `exclude_dirs`, mirroring
`.analyzerignore` and `[tool.ruff] exclude` → **0 findings**, scan PASS.

A related oddity: bandit writes its progress bar to **stdout**, so
`scripts/security_scan.py` stores `{"raw_output": …}` instead of parsed JSON. The gate only
uses the exit code, so it still works; the report file is just unparseable.

## 5. Packaging/deploy leak (`graphify-out`)

`qgis-manage deploy` shares `.qgisignore` with packaging, but the file did not exclude
`graphify-out/` (23 MB of local code-graph output), `logs/`, or the agentic metadata
(`forge.toml`, `context_manifest.json`, `.gitmodules`). The deploy copied them (30 MB
installed); the release ZIP only looked clean because CI builds from a clean checkout.
Added all four to `.qgisignore`.

Note: `sync_directory`/`_cleanup_destination` **preserve** destination entries that match
an ignore pattern, so once junk lands in an install it never gets cleaned automatically —
it must be removed by hand.

## 6. Local deploy (QGIS 4)

`uv run qgis-manage deploy --no-compile --qgis-version 4`:

- Installed **3.11.0** (previous copy was v3.9.1 from 2026-10-04).
- Backup: `sec_interp.bak.20261018170158` (rotation keeps 3).
- `--no-compile` was safe: `resources/` has not changed since 2026-09-27.
- Post-deploy cleanup removed `graphify-out/`, `logs/`, `__pycache__/` and the agentic
  metadata → **30 MB → 4.9 MB**. Verified: 0 `.pyc`, 0 `.ts`, 13 `.qm`, no
  `legend_widget.py`, 0 syntax errors across all modules.
- Caveat: `help/html` still holds the previous (v3.9.1) build because `--no-compile` does
  not rebuild docs; `make deploy` is the full path.

## Verification Results

- `ruff check` / `format --check`: clean (177 files).
- `make mypy`: **Success, 89 source files**.
- `pre-commit run --all-files` with a **cleaned cache**: hooks reinstall fine on
  virtualenv 21 (only the pre-existing trailing whitespace in
  `docs/maintenance/analysis_v3.3.0_refactoring.md` remains; reverted to keep the tree clean).
- `make context`: analyzer 1.16.0 + ai-ctx, **2,641/8,000 tokens**, `Context check: fresh`.
- Sphinx `-b html`: build OK (pre-existing duplicate-object/xref warnings).
- `make security-scan`: bandit PASS (0 findings) · detect-secrets PASS · flake8 INFO.
- `make docker-test`: **728 executed OK** (23/237/40/352/76) = 792 tests discovered.
- `qgis-manage package -o /tmp`: 2.3 MB, **311 files — same name set as the published
  `sec_interp.3.11.0.zip`**, no dev artifacts.
- `forge metrics validate`: PASS (tests 792, quality 55.7, CC ≤ 10).

## Metrics (unchanged)

Stability 55.7 · Maintainability 99.9 · Security 100.0 · issues 36 (`GOD_OBJECT` 20,
`MISSING_DOCSTRING` 9, `NON_PYTHONIC_LOOP` 4, `POTENTIAL_MISSING_SLOT` 2,
`SPAGHETTI_CODE` 1) · CC PASS · i18n 0 · `module_size_gate` **FAIL** (5 modules).

## Commits

`96a70d9` (submodule: release-plugin test count) · `d7963cc7` (submodule pointer) ·
`0a9156c8` (deps refresh) · `b4c150d0` (bandit scope) · `a2193112` (packaging ignore).

## Pending

1. **Portal QGIS**: v3.11.0 still **pending approval**.
2. **`module_size_gate`**: 5 modules > 400 lines — `gui/adapters/geometry.py` 598,
   `gui/preview_layer_factory.py` 535, `exporters/interpretation_3d_exporter.py` 472,
   `gui/preview_renderer.py` 439, `core/controller.py` 428. The 2026-09-20 spec is stale.
3. **`uv` 0.12.10 → 0.13.0**: via pacman; Manjaro stable still serves 0.12.10.
4. **Plans saved, no code**: interop §9 (B1 first) and structural-notation parser.
