# Session 2026-11-01 — Signal Idempotency P0 + QGIS 4 Smoke Test

## Objective

The analyzer reported 47 `SIGNAL_LEAK` entries. The investigation showed that
none was a dangling connection, but it exposed a real duplicate-connection bug:
`SymbologyTab.connect_signals()` added 15 `source → self.changed.emit` links plus
`btn_reset_units.clicked` on every `connect_all()`, and `disconnect_signals()`
did not remove them. The dialog is re-connected on every `run()`, so the number
of copies grew with each open (N+1 after N opens), duplicating preview refreshes
and reset executions.

The session fixed that P0, added regression coverage, adopted
`qgis-plugin-analyzer` 1.19.1, and ran the live QGIS 4 smoke test.

## Result

### Code

- `gui/ui/pages/settings/symbology_tab.py`:
  - `_changed_sources()` returns the 15 controls.
  - `_on_source_changed()` forwards any change to `self.changed`.
  - `_disconnect_internal_signals()` removes only this tab's internal links.
  - `connect_signals()` disconnects its sources and the reset button before
    reconnecting; it never calls `self.changed.disconnect()`, so external
    receivers (preview/settings) survive.
  - `disconnect_signals()` removes internal links and then all `changed`
    receivers.
- `gui/ui/pages/settings/symbology_units.py`:
  - `disconnect_unit_signals()` disconnects `btn_reset_units.clicked`.
- Tests:
  - `tests/gui/test_symbology_tab.py`: 3 new mock-first symmetry tests
    (11 total).
  - `tests/integration/test_signal_idempotency.py`: 2 real-Qt tests that count
    one `changed` emission and one `reset_units` execution after two
    `connect_signals()` calls; skipped under mocks.

### Analyzer

`qgis-plugin-analyzer` 1.19.0 → **1.19.1** (`pyproject.toml`/`uv.lock`).
1.19.1 fixes R1 (sender equality in slot-less disconnects).

| Metric | Before P0 | After P0 |
| :--- | ---: | ---: |
| Connect sites | 176 | 162 |
| Matched | 127 | 129 |
| Unmatched | 27 | **16** |
| Benign | 22 | **17** |

The 15 real `changed.emit` links and the reset button disappeared. The 16
remaining entries are upstream R3/R5/R6 false positives: 6 panel, 6 `task.*`
aliases, 3 + 1 tuple loops. They are not SecInterp leaks.

Residual upstream defects documented in
[`docs/plans/upstream_signal_leak_rule.md`](../plans/upstream_signal_leak_rule.md):

- **R4:** `QRadioButton(self.tr("A"))` is treated as `parent_child` because
  `first_arg.startswith("self.")`; 4 real links + reset become `benign`.
- **R5:** `for task in list(self._active_tasks)` stays unresolved at
  `confidence="high"`; 6 false positives.
- **R6:** tuple-loop slots are canonicalized to the first slot; 3 `dem_page` +
  1 `section_page` false positives.

Issue: <https://github.com/geociencio/qgis-plugin-analyzer/issues/1>
(1.19.1 verification comment:
<https://github.com/geociencio/qgis-plugin-analyzer/issues/1#issuecomment-6561009945>).

## Tests and gates

- **844 local tests OK**, 2 real-Qt tests skipped under mocks.
- **Full `make docker-test`: exit 0** — 43 + 295 + 40 + 373 + 78 tests.
- Real-Qt integration: **2/2 OK**.
- `ruff check`/`format`, direct `flake8`, `mypy` (102 files),
  `qgis-manage validate --strict --repo`, i18n (6), security (0 findings),
  Qt6 checker (0), analyzer CC PASS, `check_docs` (37),
  `forge metrics validate`, `git diff --check`.
- Note: `make flake8` itself fails in this sandbox because the target writes to
  `/dev/stdout` (`OSError: [Errno 6]`); the same flake8 command without
  `--output-file` passes. CI is unaffected.

## QGIS 4 smoke test

QGIS 4.2.2 offscreen, `examples/sample_data/MURALLA.qgs`, MCP fork 0.15.1:

| Step | Result |
| :--- | :--- |
| status | PASS — loaded, dialog_ready |
| ping/diagnose | PASS — QGIS 4.2.2, Qt 6.11.2, plugin 0.15.1, healthy |
| open | PASS — opened, visible |
| preview | PASS — 430 topo points, 9 geology segments, 9 structures, 10 drillholes, 92 ms |
| ready | PASS — preview matches current inputs |
| results | PASS — 370 chars |
| export | PASS — `/tmp/secinterp_preview.png`, 1872×900 RGBA, 130,248 B |

The first attempt failed because the QGIS profile had the **upstream**
`qgis_mcp_plugin` 0.15.2 (no `secinterp_*` handlers). The fork 0.15.1 was
symlinked into the profile; the upstream copy is backed up as
`qgis_mcp_plugin.upstream-0.15.2-20261101121222`. Autostart was disabled after
the test and QGIS was stopped.

## Git

Session commit: `chore(agent): close session signal_idempotency_p0` (the code
fix is included in the same session commit).

## Pending

1. Release **3.12.1** (bump, changelog, notes, `make pre-release`, `make zip`,
   portal upload).
2. Upstream **1.19.2** for R4–R6.
3. Optional P1: move `PreviewSidePanel`/`SectionFeatureSelector` wiring to
   `SignalManager`/`SectionPage`.
4. Optional manual UI click test (the real-Qt integration already covers the
   duplicate-emission assertion).

## Notes

- The pre-existing modification to `docs/source/images/sec_interp_icon.svg`
  was not part of this session and was left untouched.
- `tests/TESTING_STATUS.md` was updated automatically by `make docker-test`
  (893 static tests, GUI 373, integration 78).
