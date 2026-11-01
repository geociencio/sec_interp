# Implementation Plan: v3.12.1 — Signal Idempotency in Symbology Settings

> **Phase**: post-v3.12.0 polish (target v3.12.1)
> **Status**: ✅ **IMPLEMENTED** (2026-11-01) — pending release
> **Created**: 2026-11-01
> **Origin**: analysis of the 47 `SIGNAL_LEAK` entries reported by
> `qgis-plugin-analyzer` **1.18.0**, plus the **1.19.1** per-connection
> verification (adopted 2026-11-01).
> **Companion**: [upstream_signal_leak_rule.md](upstream_signal_leak_rule.md)
> (1.19.1 verification and residual defects R4–R6).
> **Upstream issue**: <https://github.com/geociencio/qgis-plugin-analyzer/issues/1>.

---

## 0. Executive summary

### 0.1 The 1.18.0 picture

The 47 "signal leaks" were **not 47 runtime leaks**. The 1.18.0 analyzer compared
literal `.connect()` / `.disconnect()` attribute chains inside one file, so it
could not follow loop variables, aliases or Qt object lifetimes:

| Category | Unique entries | Verdict |
| :--- | ---: | :--- |
| Disconnect exists but through a loop variable/alias | 29 | Analyzer false positive |
| Child widget destroyed with its parent or via `deleteLater()` | 15 | No leak |
| Real incomplete disconnect in `SymbologyTab` | 3 | **Bug** |
| Real incomplete disconnect hidden from the analyzer | 13 | **Bug** |
| **Reported total** | **47** | |

### 0.2 The 1.19.1 picture

`qgis-plugin-analyzer` 1.19.1 (PyPI, 2026-11-01) fixes R1 (sender equality).
On this repository it reports:

| Metric | Value |
| :--- | ---: |
| Connect sites | 176 |
| Matched | 127 |
| Unmatched | 27 |
| Benign | 22 |

The real 16 sites are now partially visible:

| File | Unmatched | Benign | Verdict |
| :--- | ---: | ---: | :--- |
| `gui/ui/pages/settings/symbology_tab.py:343` (15 real) | **11** | **4** | 11 visible; 4 hidden by R4 `parent_child` |
| `gui/ui/pages/settings/symbology_units.py:127` (reset) | 0 | **1** | Hidden by R4 `parent_child` |
| `gui/main_dialog.py:142-147` (panel) | 6 | 0 | Benign parent-child, not detected (R3) |
| `gui/preview_task_orchestrator.py:95-97,156-158` | 6 | 0 | Correct disconnects; alias unresolved (R5) |
| `gui/ui/pages/dem_page.py:376-380` | 3 | 1 | Tuple loop slot pairing (R6) |
| `gui/ui/pages/section_page.py:279` | 1 | 0 | Tuple loop slot pairing (R6) |

**Critical:** R1 is fixed, but R4 (`self.tr(...)` mistaken for a parent) hides
4 of the 15 real links and the reset button as `benign`. The P0 fix below
remains necessary; after it the analyzer should drop to **16 unmatched + 17
benign** (the remaining R3/R5/R6 false positives), not zero.

Residual defects R4–R6 are documented in the companion upstream plan.

### 0.3 The bug and the fix

`SymbologyTab.connect_signals()` adds 15 `source → self.changed.emit` connections
plus `btn_reset_units.clicked`, and `disconnect_signals()` does not remove them.
Because `connect_all()` runs once in `SecInterpDialog.__init__` and again in
`PluginLifecycle.run()` for every open, the dialog accumulates **N+1** copies
after N opens. Each symbology control change then emits `changed` N+1 times
(N+1 preview re-renders), and the reset button runs `reset_units()` N+1 times.

This plan fixes the duplication, adds a real-Qt regression test, and optionally
aligns `SectionFeatureSelector` and `PreviewSidePanel` with the project's
"every `connect` has a `disconnect_signals()`" rule. It does **not** try to
silence the analyzer by rewriting correct disconnect sites (the R4–R6 false
positives).

### 0.4 Implementation result (2026-11-01)

- **P0 implemented** in `gui/ui/pages/settings/symbology_tab.py` and
  `gui/ui/pages/settings/symbology_units.py`:
  - `_changed_sources()`, `_on_source_changed()`,
    `_disconnect_internal_signals()`.
  - `disconnect_unit_signals()` in `UnitsEditorMixin`.
  - `connect_signals()` disconnects its internal links before reconnecting and
    never calls `self.changed.disconnect()` (external receivers survive).
- **Tests**: 3 new mock-first tests in `tests/gui/test_symbology_tab.py`; 2 new
  real-Qt tests in `tests/integration/test_signal_idempotency.py` (skipped under
  mocks, executed in Docker).
- **Analyzer**: 176 connect sites → 162; **27 unmatched / 22 benign → 16
  unmatched / 17 benign**. The 15 `changed.emit` links and the reset button are
  gone; the 16 remaining are R3/R5/R6 false positives, not SecInterp leaks.
- **Verification**: 844 local tests OK (2 skipped); full `make docker-test`
  exit 0 (43 + 295 + 40 + 373 + 78 tests); `ruff check`/`format`, direct
  `flake8`, `mypy`, `qgis-validate`, `i18n-check`, `security-scan`, Qt6 checker
  and the analyzer CC gate pass.
- **Live smoke test** (QGIS 4.2.2 offscreen, `MURALLA.qgs`, MCP fork 0.15.1):
  status → open → preview → ready → results → export **PASS**. Preview: 430 topo
  points, 9 geology segments, 9 structures, 10 drillholes, 92 ms; export
  `/tmp/secinterp_preview.png` (130,248 B, 1872×900 RGBA).

---

## 1. Verified context

| Fact | Source |
| :--- | :--- |
| `SymbologyTab.connect_signals()` connects 15 sources to `self.changed.emit` in a loop | `gui/ui/pages/settings/symbology_tab.py:321-343` |
| `SymbologyTab.disconnect_signals()` only removes `_on_topo_mode_changed` and the receivers of `self.changed` | `gui/ui/pages/settings/symbology_tab.py:345-354` |
| `btn_reset_units.clicked` is connected in `connect_unit_signals()` | `gui/ui/pages/settings/symbology_units.py:125-127` |
| `UnitsEditorMixin` has no disconnect helper | `gui/ui/pages/settings/symbology_units.py` |
| `SettingsPage.connect_signals()` calls `symbology_tab.connect_signals()` | `gui/ui/pages/settings_page.py:128-136` |
| `SignalManager.connect_all()` calls `disconnect_all()` first, then `page.connect_signals()` | `gui/dialog_signal_manager.py:57-76, 362-376` |
| `SecInterpDialog.__init__` calls `connect_all()` once | `gui/main_dialog.py:101` |
| `PluginLifecycle.run()` calls `connect_all()` on every open | `plugin/lifecycle.py:99-105` |
| `closeEvent` calls `disconnect_all()` | `gui/dialog_lifecycle_mixin.py:57-60` |
| Other pages are already idempotent (slot-specific disconnects) | `dem_page.py:374-392`, `section_page.py:276-290`, `collar_tab.py:138-180`, `survey_tab.py:115-144`, `interval_tab.py:115-144`, `default_tab.py:137+`, `advanced_tab.py:87+`, `interpretation_tab.py:200-213` |
| `qgis-plugin-analyzer` 1.19.1 is adopted (`>=1.19.1`); per-connection output | `pyproject.toml:38`, `uv.lock` |
| 1.19.1 on this repo: 176 connect sites, 127 matched, 27 unmatched, 22 benign | `uv run qgis-analyzer analyze . --max-cc 10 --signals` (2026-11-01) |
| 11 of the 15 real `changed.emit` links are visible; 4 + reset are hidden by R4 | `.venv/.../analyzer/signal_analysis.py:155-164` |
| R5 unresolved `task.*` aliases produce 6 high-confidence FPs | `.venv/.../analyzer/signal_scope.py:131-144` |
| R6 tuple-loop slot pairing produces 3 `dem_page` + 1 `section_page` FPs | `.venv/.../analyzer/signal_analysis.py:259-320` |
| The rule remains informational (`emitted=False`); `--signals` is opt-in | `analyzer/rules/catalog_core.py:44-56` |
| Legacy `signal_leaks` is a sender-string list; `signal_connections` is the new JSON | `analyzer/signal_resolver.py:194-254` |

### Duplication timeline

```
SecInterpDialog.__init__  ──► SignalManager.connect_all()  ──► SymbologyTab.connect_signals()  #1
PluginLifecycle.run()     ──► SignalManager.connect_all()  ──► SymbologyTab.connect_signals()  #2
                                   │
                                   └─ disconnect_all() first, but SymbologyTab.disconnect_signals()
                                      leaves 15 changed.emit links + 1 reset button link alive

closeEvent                ──► disconnect_all()  (still leaves the 16 internal links)
next run()                ──► connect_signals() #3  (now 3 copies)
```

After N opens: `N + 1` connections per source signal. The first user interaction
already has two copies.

---

## 2. Scope

**In scope**

- Make `SymbologyTab.connect_signals()` / `disconnect_signals()` idempotent.
- Add `disconnect_unit_signals()` to `UnitsEditorMixin`.
- Add a mock-level symmetry test and a real-Qt integration test that proves a
  single `changed` emission and a single reset execution.
- Update the agent memory with the analyzer limitation and the real bug.

**Out of scope**

- Rewriting correct disconnect sites to satisfy the analyzer (the 3 `dem_page`
  + 1 `section_page` R6 false positives, the 6 `task.*` R5 entries, and the
  1.18.0 literal-path cases). That is churn without runtime benefit.
- Patching `qgis-plugin-analyzer` from this repository; that is the companion
  upstream plan (`R4`–`R6`).
- Changing preview/export behavior or persisted settings.

**Optional P1 (recommended if time allows)**

- Move `SectionFeatureSelector` wiring from `__init__` to an idempotent
  `connect_signals()` / `disconnect_signals()`, and call it from `SectionPage`.
- Move the six `PreviewSidePanel` connections from `MainDialog._init_managers`
  into `SignalManager` so `connect_all()` / `disconnect_all()` own them.
  **Do not add a disconnect without a matching reconnect on `run()`**; the panel
  and selector must keep working after closing and reopening the dialog.

---

## 3. Root cause

`SymbologyTab` has two groups of internal connections:

1. **Two direct connections**: `radio_gradient/radio_single.toggled →
   _on_topo_mode_changed`. These are correctly disconnected by
   `signal.disconnect(slot)` in `disconnect_signals()`.
2. **Sixteen loop/side-effect connections**:
   - 15 sources → `self.changed.emit` (the loop at `symbology_tab.py:326-343`,
     which also includes the two radio signals);
   - `btn_reset_units.clicked` → `self.reset_units` (`symbology_units.py:127`).

`disconnect_signals()` only handles group 1 and the external receivers of
`self.changed`. Group 2 survives every `disconnect_all()`, and every
`connect_signals()` adds another copy.

`self.changed.emit` is used as a slot. Disconnecting `self.changed` removes its
**receivers** (`_on_settings_changed`, `preview_manager.update_from_checkboxes`);
it does not remove the 15 connections whose sender is a widget signal and whose
slot is the `emit` bound method. That is the subtle part.

---

## 4. Design

### 4.1 `SymbologyTab` (recommended)

Introduce one private slot and one helper that returns the source signals, so the
connect and disconnect paths cannot drift:

```python
# gui/ui/pages/settings/symbology_tab.py

def _changed_sources(self) -> tuple[Any, ...]:
    """Return every control whose change must emit ``changed``."""
    return (
        self.radio_gradient.toggled,
        self.radio_single.toggled,
        self.ramp_button.colorRampChanged,
        self.topo_color_button.colorChanged,
        self.topo_width_spin.valueChanged,
        self.struct_color_button.colorChanged,
        self.struct_width_spin.valueChanged,
        self.drill_color_button.colorChanged,
        self.drill_width_spin.valueChanged,
        self.chk_drill_labels.toggled,
        self.interp_color_button.colorChanged,
        self.chk_export_legend.toggled,
        self.combo_legend_pos.currentIndexChanged,
        self.spin_legend_font.valueChanged,
        self.spin_legend_max.valueChanged,
    )

def _on_source_changed(self, *_args: Any) -> None:
    """Forward any control change to the tab's public signal."""
    self.changed.emit()

def connect_signals(self) -> None:
    """Connect internal signals idempotently."""
    self._disconnect_internal_signals()
    self.radio_gradient.toggled.connect(self._on_topo_mode_changed)
    self.radio_single.toggled.connect(self._on_topo_mode_changed)
    for signal in self._changed_sources():
        signal.connect(self._on_source_changed)
    self.connect_unit_signals()

def _disconnect_internal_signals(self) -> None:
    """Remove only this tab's internal connections, never external receivers."""
    for signal, slot in (
        (self.radio_gradient.toggled, self._on_topo_mode_changed),
        (self.radio_single.toggled, self._on_topo_mode_changed),
    ):
        with contextlib.suppress(TypeError, RuntimeError):
            signal.disconnect(slot)
    for signal in self._changed_sources():
        with contextlib.suppress(TypeError, RuntimeError):
            signal.disconnect(self._on_source_changed)
    self.disconnect_unit_signals()

def disconnect_signals(self) -> None:
    """Disconnect internal and external receivers."""
    self._disconnect_internal_signals()
    with contextlib.suppress(TypeError, RuntimeError):
        self.changed.disconnect()
```

**Critical ordering rule:** `connect_signals()` must call
`_disconnect_internal_signals()`, **not** the full `disconnect_signals()`.
`_connect_preview_signals()` runs before `_connect_page_signals()`
(`dialog_signal_manager.py:259-296` vs `:298-376`), so a full disconnect inside
`connect_signals()` would drop the preview receiver that was just added.

### 4.2 `UnitsEditorMixin`

```python
# gui/ui/pages/settings/symbology_units.py
import contextlib

def disconnect_unit_signals(self) -> None:
    """Disconnect the per-unit reset button."""
    with contextlib.suppress(TypeError, RuntimeError):
        self.btn_reset_units.clicked.disconnect(self.reset_units)
```

`SymbologyTab._disconnect_internal_signals()` calls it. Row widgets are rebuilt
with `deleteLater()` (`symbology_units.py:79-82`), so their connections do not
need explicit disconnection.

### 4.3 Alternative considered: `UniqueConnection`

`signal.connect(self._on_source_changed, Qt.ConnectionType.UniqueConnection)`
would prevent duplicates without a disconnect, but PyQt raises `TypeError` when
the connection already exists and the behavior is less explicit. Rejected in
favor of the disconnect/connect symmetry used by the rest of the pages.

---

## 5. Tests

### 5.1 Unit (mock-first, local)

File: `tests/gui/test_symbology_tab.py`

- `test_disconnect_removes_every_changed_source`: after `connect_signals()` and
  `disconnect_signals()`, assert `.disconnect()` was called on every signal
  returned by `_changed_sources()` and on `btn_reset_units.clicked`.
- `test_connect_signals_does_not_drop_external_receivers`: connect a sentinel to
  `tab.changed`, call `connect_signals()` twice, assert the sentinel is still
  connected (the private helper must not call `self.changed.disconnect()`).
- Keep the existing `test_connect_disconnect` smoke test.

Mock signals cannot prove emission counts because `MagicMock.connect()` does not
invoke slots. The definitive test is the integration one.

### 5.2 Integration (real Qt, Docker)

New file: `tests/integration/test_signal_idempotency.py`

```python
import unittest

from qgis.PyQt.QtWidgets import QApplication

from sec_interp.gui.ui.pages.settings.symbology_tab import SymbologyTab


class TestSymbologySignalIdempotency(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_changed_emits_once_after_two_connections(self):
        tab = SymbologyTab()
        emitted = []
        tab.changed.connect(lambda: emitted.append(1))

        tab.connect_signals()
        tab.connect_signals()
        tab.chk_drill_labels.setChecked(not tab.chk_drill_labels.isChecked())

        self.assertEqual(len(emitted), 1)

    def test_reset_runs_once_after_two_connections(self):
        tab = SymbologyTab()
        calls = []
        tab.reset_units = lambda: calls.append(1)

        tab.connect_signals()
        tab.connect_signals()
        tab.btn_reset_units.click()

        self.assertEqual(len(calls), 1)
```

> The integration suite runs in Docker with `FORCE_MOCKS=0` and
> `QT_QPA_PLATFORM=offscreen` (`Dockerfile:43-46`), so real Qt signals are
> available. If monkeypatching `reset_units` after `connect_signals()` does not
> intercept the bound-method connection, use a fake unit manager and assert that
> `set_order` is called once instead.

### 5.3 Lifecycle regression

Add a test that mirrors the real `run()` cycle at the `SignalManager` level:
call `connect_all()` twice on a dialog fixture, emit a symbology control, and
assert one `changed` emission. This is the regression that would have caught the
bug.

---

## 6. Acceptance criteria

- [x] Two `connect_signals()` calls produce exactly one `changed` emission per
      control change (real Qt, Docker).
- [x] Two `connect_signals()` calls produce exactly one `reset_units()` execution
      per reset click (real Qt, Docker).
- [x] `disconnect_signals()` removes every internal connection and leaves no
      duplicate after a `connect → disconnect → connect` cycle.
- [x] External receivers of `self.changed` survive `connect_signals()`.
- [x] Existing 844 local tests pass (2 real-Qt tests skipped under mocks); new
      tests pass.
- [x] `uv run ruff check .`, `uv run ruff format --check .`, direct `flake8` and
      `make mypy` pass. (`make flake8` itself hits the sandbox `/dev/stdout`
      issue; the same command without `--output-file` passes.)
- [x] `make docker-test` passes (exit 0; integration group included).
- [x] The analyzer dropped from **27 unmatched / 22 benign** to **16 unmatched /
      17 benign** after P0. The remaining 16 are upstream R3/R5/R6 false
      positives (6 panel + 6 task + 4 tuple loops), not SecInterp leaks.
      **The analyzer count is not the acceptance criterion** (see the companion
      upstream plan).

---

## 7. Files

| File | Change |
| :--- | :--- |
| `gui/ui/pages/settings/symbology_tab.py` | `_changed_sources()`, `_on_source_changed()`, `_disconnect_internal_signals()`, idempotent `connect_signals()` / `disconnect_signals()` |
| `gui/ui/pages/settings/symbology_units.py` | `disconnect_unit_signals()` + `contextlib` import |
| `tests/gui/test_symbology_tab.py` | symmetry tests |
| `tests/integration/test_signal_idempotency.py` | real-Qt emission/click tests (new) |
| `.agent-state/memory/AGENT_LESSONS.md` | lesson: literal connect/disconnect matching and the duplicate-connection bug |
| `docs/plans/upstream_signal_leak_rule.md` | companion upstream plan (1.19.1 verification + R4–R6) |
| `pyproject.toml` / `uv.lock` | **DONE**: `qgis-plugin-analyzer>=1.19.0` |
| `.agent-state/memory/agent_metrics.json` | **DONE**: analyzer tool version 1.19.0 |

**Optional P1 files**

| File | Change |
| :--- | :--- |
| `gui/ui/pages/section_feature_selector.py` | move wiring to `connect_signals()`, add `disconnect_signals()` |
| `gui/ui/pages/section_page.py` | call selector `connect_signals()` / `disconnect_signals()` |
| `gui/dialog_signal_manager.py` | own the six `PreviewSidePanel` connections |
| `gui/main_dialog.py` | remove the panel wiring from `_init_managers()` |

---

## 8. Risks and mitigations

| Risk | Mitigation |
| :--- | :--- |
| Removing duplicate emissions changes observable behavior | The duplicates were unintended; `changed` only triggers idempotent UI refresh. Verify preview, legend and settings persistence manually in QGIS. |
| `connect_signals()` drops the preview receiver | Use `_disconnect_internal_signals()`, not `disconnect_signals()`, inside `connect_signals()`; add the sentinel test. |
| P1 adds a disconnect without reconnection | Panel/selector wiring must move into `SignalManager` / `SectionPage.connect_signals()` so every close is paired with an open. |
| Real-Qt tests are skipped locally | Run them in Docker (`make docker-test`); keep the mock tests as a fast local gate. |
| Analyzer still reports 16 after P0 | Upstream R4–R6 hide/duplicate the remaining entries; fix the analyzer in 1.19.2 instead of chasing the number. |

---

## 9. Implementation checklist

1. [x] Add `_changed_sources()` / `_on_source_changed()` /
       `_disconnect_internal_signals()` to `SymbologyTab`.
2. [x] Rewrite `connect_signals()` / `disconnect_signals()` as in §4.1.
3. [x] Add `disconnect_unit_signals()` to `UnitsEditorMixin` and call it.
4. [x] Add the mock symmetry tests and the real-Qt integration tests.
5. [x] Run `uv sync`, then the targeted tests (11/11 OK).
6. [x] Run `make docker-test` (full suite, exit 0) and the real-Qt integration
       tests (2/2 OK).
7. [x] Manual smoke test in QGIS 4.2.2 via `/smoke-qgis4`: status, open,
       preview, ready, results and export **PASS**; PNG 1872×900, 130,248 B.
       The duplicate-emission assertion is covered by the real-Qt integration
       test (2/2 OK).
8. [ ] Update `.agent-state/memory/AGENT_LESSONS.md` and the session log at close.

---

## 10. Verification commands

```bash
# Fast local gate (mock-first)
PYTHONPATH=.. uv run python3 -m unittest tests.gui.test_symbology_tab -v

# Real Qt (Docker)
make docker-test

# Quality gates
uv run ruff check .
uv run ruff format --check .
make flake8
make mypy

# Optional: confirm the analyzer output is still informational
make context
```

Expected after P0: the analyzer should drop from **27 unmatched / 22 benign**
to **16 unmatched / 17 benign**. The 15 real `changed.emit` links and the reset
button disappear; the remaining 16 are upstream R3/R5/R6 false positives
(6 panel + 6 `task.*` + 4 tuple loops), so do not expect zero yet. The
regression test is the source of truth for this fix.

---

## 11. References

- Analysis of the 47 entries (1.18.0), the 1.19.0 verification and the 1.19.1
  re-verification: conversation of 2026-11-01 (this plan captures the verified
  sources).
- 1.19.1 collector: `analyzer/signal_analysis.py:31-53, 82-96, 218-320`.
- 1.19.1 resolver: `analyzer/signal_resolver.py:18-88, 163-254`.
- **R1 (sender missing, fixed in 1.19.1)**: `analyzer/signal_resolver.py:73`.
- **R4 (`self.tr` parent)**: `analyzer/signal_analysis.py:155-164`.
- **R5 (unresolved loop confidence)**: `analyzer/signal_scope.py:131-144`.
- **R6 (tuple slot pairing)**: `analyzer/signal_analysis.py:259-320`.
- **R3 residual (panel lifetime)**: `analyzer/signal_analysis.py:322-336`.
- Rule catalog: `analyzer/rules/catalog_core.py:44-56`.
- Summary output: `analyzer/reporters/summary_reporter.py:127-166`.
- Companion upstream plan: [upstream_signal_leak_rule.md](upstream_signal_leak_rule.md).
