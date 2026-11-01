# Next Steps (Updated 2026-11-01)

**Session closed**: `signal_idempotency_p0` — see
[`docs/maintenance/session_2026-11-01_signal_idempotency_p0.md`](../docs/maintenance/session_2026-11-01_signal_idempotency_p0.md).

## ✅ Current state

- **v3.12.1 published on GitHub (2026-11-01)**: 844 tests OK (2 skipped), Docker
  exit 0, `dist/sec_interp.3.12.1.zip` (342 files, 2.4 MB, SHA256
  `9b835bc76bd8a28f80c583a01bc89976d4838af2196a5beebc4ca969fc0bc8aa`), zero
  portal warnings; tag `v3.12.1`; GitHub release *Latest*:
  <https://github.com/geociencio/sec_interp/releases/tag/v3.12.1>. Portal upload pending.
- **P0 signal idempotency implemented**: `SymbologyTab.connect_signals()` now
  disconnects its 15 internal `changed.emit` links and the unit-reset button
  before reconnecting, without dropping external `changed` receivers.
  `UnitsEditorMixin.disconnect_unit_signals()` added.
- **Tests**: **844 local OK** (2 real-Qt skipped); full `make docker-test`
  **exit 0** (43 + 295 + 40 + 373 + 78); real-Qt idempotency tests **2/2 OK**
  (one `changed` emission and one reset after two `connect_signals` calls).
- **Analyzer**: `qgis-plugin-analyzer>=1.19.1` adopted. On this repo:
  **162 connect sites, 129 matched, 16 unmatched, 17 benign** (was 27/22
  before P0). The 15 real `SymbologyTab` links and the reset button are gone;
  the 16 remaining are upstream R3/R5/R6 false positives (6 panel + 6 `task.*`
  + 4 tuple loops).
- **Upstream issue**: <https://github.com/geociencio/qgis-plugin-analyzer/issues/1>
  (R1 fixed in 1.19.1; R4–R6 still open; 1.19.1 verification comment posted).
- **Smoke test**: QGIS 4.2.2 offscreen, `MURALLA.qgs`, MCP fork 0.15.1:
  status → open → preview → ready → results → export **PASS**; PNG 1872×900,
  130,248 B. Preview: 430 topo points, 9 geology segments, 9 structures,
  10 drillholes, 92 ms.
- **Gates**: ruff check/format, direct flake8, mypy (102 files),
  `qgis-validate`, i18n (6), security (0 findings), Qt6 (0), CC PASS,
  `check_docs` (37), `forge metrics validate`, `git diff --check`.
- **3.12.0 remains live on the QGIS repository** (marked QGIS 4 Ready); 3.12.1 is
  published on GitHub and awaits the manual portal upload.

## 📌 Pending

0. **Upload v3.12.1 to the QGIS repository**: the ZIP is built and validated
   (zero warnings); upload `dist/sec_interp.3.12.1.zip` at
   <https://plugins.qgis.org/plugins/sec_interp/> and wait for validation/approval.
   3.12.0 remains live until then.
1. **Upstream `qgis-plugin-analyzer` 1.19.2**:
   - R4: reject `self.tr(...)` as a parent in `_record_parented_assignment`
     (`signal_analysis.py:155-164`); 4 real `changed.emit` + reset are currently
     `benign`.
   - R5: unresolved `for task in list(self._active_tasks)` should be
     `confidence="low"` or resolved (`signal_scope.py:131-144`).
   - R6: zip the tuple-loop `sender`/`slot` bindings (`signal_analysis.py:259-320`).
   - After 1.19.2, the SecInterp count should be 16 real sites before P0 and 0
     after.
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
   - fix upstream **1.19.2** (R4–R6), or
   - interop §9 **B1**.
3. For local gates: `export MYPY_CACHE_DIR=$PWD/.mypy_cache` before `make mypy`
   (sandbox only), and `UV_CACHE_DIR=/tmp/uv-cache-secinterp` for `uv`.
4. Before closing: `/close-session` and confirm the release gate is green.
