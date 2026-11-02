# Next Steps (Updated 2026-11-01)

**Session closed**: `release_tooling_blendergis` — see
[`docs/maintenance/session_2026-11-01_release_tooling_blendergis.md`](../docs/maintenance/session_2026-11-01_release_tooling_blendergis.md).

## ✅ Current state

- **Tooling (2026-11-01)**: `qgis-manage 0.16.1` (zero runtime dependencies;
  internal console replaces `click`, plus manifest/clean/bump/artifact fixes) and
  `qgis-plugin-analyzer 1.19.2` adopted; no plugin-runtime change.
- **Docs/design (2026-11-01)**: `uv_modernization_guide.md` rewritten against the
  real QGIS/uv constraints; `docs/research/blendergis_export_design.md` defines the
  `SectionFrame`, 3D layer contract and BlenderGIS bundle.
- **v3.12.1 published on GitHub (2026-11-01)**: 844 local OK (2 skipped), Docker
  exit 0, `dist/sec_interp.3.12.1.zip` (342 files, 2.4 MB, SHA256
  `9b835bc76bd8a28f80c583a01bc89976d4838af2196a5beebc4ca969fc0bc8aa`), zero
  portal warnings; tag `v3.12.1`; GitHub release *Latest*:
  <https://github.com/geociencio/sec_interp/releases/tag/v3.12.1>. **Uploaded to the
  QGIS repository on 2026-11-01; validation pending** (the feed still serves 3.12.0).
- **P0 signal idempotency implemented**: `SymbologyTab.connect_signals()` now
  disconnects its 15 internal `changed.emit` links and the unit-reset button
  before reconnecting, without dropping external `changed` receivers.
  `UnitsEditorMixin.disconnect_unit_signals()` added.
- **Tests**: **844 local OK** (2 real-Qt skipped); full `make docker-test`
  **exit 0** (43 + 295 + 40 + 373 + 78); real-Qt idempotency tests **2/2 OK**
  (one `changed` emission and one reset after two `connect_signals` calls).
- **Analyzer**: `qgis-plugin-analyzer>=1.19.2` adopted. On this repo:
  **12 unmatched signal paths** (down from 16): six `PreviewSidePanel`
  connections in `main_dialog.py` and six `task.*` connections in
  `preview_task_orchestrator.py`. R4–R6 are fixed in 1.19.2; these remaining
  paths are lifetime/P1 candidates, not the P0 duplicate-connection bug.
- **Upstream issue**: <https://github.com/geociencio/qgis-plugin-analyzer/issues/1>
  (R1 fixed in 1.19.1; R4–R6 fixed in 1.19.2; verify/close the issue).
- **Smoke test**: QGIS 4.2.2 offscreen, `MURALLA.qgs`, MCP fork 0.15.1:
  status → open → preview → ready → results → export **PASS**; PNG 1872×900,
  130,248 B. Preview: 430 topo points, 9 geology segments, 9 structures,
  10 drillholes, 92 ms.
- **Gates**: ruff check/format, direct flake8, mypy (102 files),
  `qgis-validate`, i18n (6), security (0 findings), Qt6 (0), CC PASS,
  `check_docs` (37), `forge metrics validate`, `git diff --check`.
- **3.12.0 remains live on the QGIS repository** (marked QGIS 4 Ready); 3.12.1 is
  published on GitHub and uploaded to the portal, awaiting validation/approval.

## 📌 Pending

0. **Await QGIS portal validation/approval for v3.12.1**: the ZIP was uploaded on
   2026-11-01 after passing `validate --zip` with zero warnings. Confirm the email
   status and that the plugin page switches from 3.12.0 to 3.12.1.
1. **Review the 12 remaining signal paths (P1)**: six `PreviewSidePanel`
   connections in `main_dialog.py` and six `task.*` connections in
   `preview_task_orchestrator.py`; move the panel wiring to `SignalManager` and
   the task wiring into the orchestrator lifecycle, with matching reconnects.
2. **P1 optional**: move the six `PreviewSidePanel` connections into
   `SignalManager` and `SectionFeatureSelector` wiring into
   `SectionPage.connect_signals()`; never add a disconnect without a matching
   reconnect on `run()`.
3. **Manual UI click test**: open/close/reopen the dialog and press “Reset unit
   styles”; the one-emission/one-reset behavior is already covered by the
   real-Qt integration test.
4. **`uv` 0.12.10 → 0.13.0** — blocked by pacman (Manjaro stable serves 0.12.10).
5. **Interop §9** — start with **B1** (drillhole 3D styles) → B3 → B2 → B4 →
   Phase A: `docs/plans/implementation_plan_interop_stereonet_3d.md`.
6. **Optional docs i18n** — native review of the machine-assisted translations;
   refresh `help/html` with `make docs` (`USER_GUIDE` fr 28 % / de 18 %).

7. **BlenderGIS export P0** — add `SectionFrame`, 3D topography/geology/structures,
   SHP bundle + manifest, metric CRS, per-unit geology, and a Blender 4.x smoke test
   (`docs/research/blendergis_export_design.md`).
8. **Close qgis-plugin-analyzer issue #1** — R4–R6 are fixed in 1.19.2; verify the
   remaining 12 paths and close/update the issue.

## 🧾 Remaining debt (documented, non-blocking)

- **Analyzer**: 37 issues (20 `GOD_OBJECT`, 9 `MISSING_DOCSTRING`,
  4 `NON_PYTHONIC_LOOP`, 2 `POTENTIAL_MISSING_SLOT`, 1 `SPAGHETTI_CODE`,
  1 `UNPRECISE_LAYER`).
- **`ProfileController` GOD_OBJECT** (21 attributes) — deferred.
- **Upstream `qgis-manage`**: `clean` deletes tracked `*.cpg`; `profiles list`
  only enumerates QGIS 3; deploy manifest is neutral/slower on small plugins.
- **Framework pytest**: `.agent/tests` cannot run (pytest not installed); the
  workflow step is skipped, `conftest.py` remains.
- **`make flake8` in this sandbox**: the target writes to `/dev/stdout` and
  fails with `OSError: [Errno 6]`; run the same flake8 command without
  `--output-file`, or use it in CI.

## 🖥️ Environment notes

- The QGIS 4 profile now loads the **SecInterp MCP fork 0.15.1** (symlink to
  `tools/qgis_mcp/qgis_mcp_plugin`). The previous upstream 0.15.2 copy is backed
  up as `qgis_mcp_plugin.upstream-0.15.2-20261101121222`.
- The MCP server autostart was disabled after the smoke test; start it from the
  QGIS MCP dock when running `/smoke-qgis4`.
- QGIS was stopped after the test; port `9877` is closed.
- `docs/source/images/sec_interp_icon.svg` was already modified before this
  session and was not touched.

## 🚀 How to resume

1. Run `/start-session` to refresh `AI_CONTEXT.md` and read this file.
2. Choose one:
   - prepare release **3.12.1** (recommended), or
   - review the 12 remaining signal paths (P1), or
   - implement the BlenderGIS P0 export, or
   - interop §9 **B1**.
3. For local gates: `export MYPY_CACHE_DIR=$PWD/.mypy_cache` before `make mypy`
   (sandbox only), and `UV_CACHE_DIR=/tmp/uv-cache-secinterp` for `uv`.
4. Before closing: `/close-session` and confirm the release gate is green.
