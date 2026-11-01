<!--
Upstream issue draft for geociencio/qgis-plugin-analyzer.

Title: SIGNAL_LEAK 1.19.0: slot-less disconnect matches connections from other senders (false negative)
Labels: bug
-->

> **Published**: <https://github.com/geociencio/qgis-plugin-analyzer/issues/1>
> (2026-11-01). **1.19.1 verification**:
> <https://github.com/geociencio/qgis-plugin-analyzer/issues/1#issuecomment-6561009945>.

## Summary

`SIGNAL_LEAK` in 1.19.0 correctly moves from literal string matching to
per-connection records, but a **slot-less `disconnect()` resolves every pending
connect in the same class**, not only connections from the same sender. The rule
therefore reports a real duplicate-connection bug as `matched`.

This is a **false negative**: users who opt into `emit = true` get a false green,
and CI cannot catch duplicated signal connections that would otherwise leak.

Found while verifying the SecInterp corpus (176 connect sites):

| Metric | Value |
| :--- | ---: |
| Connect sites | 176 |
| Matched | 148 |
| Unmatched | 18 |
| Benign | 10 |

The 15 real `source → self.changed.emit` connections in
`gui/ui/pages/settings/symbology_tab.py:326-343` are all marked **matched** by
`symbology_tab.py:354 self.changed.disconnect()`. The only true positive in that
class is a separate reset button.

---

## Environment

- `qgis-plugin-analyzer` **1.19.0** (PyPI, 2026-11-01)
- Python 3.12, Linux
- Command: `qgis-analyzer analyze . --max-cc 10 --signals`

---

## Minimal reproduction

```python
class SignalTab:
    def connect_signals(self):
        for signal in (self.a.toggled, self.b.toggled):
            signal.connect(self.changed.emit)

    def disconnect_signals(self):
        self.changed.disconnect()


class DemTab:
    def connect_signals(self):
        self.raster.layerChanged.connect(self.band.setLayer)

    def disconnect_signals(self):
        for signal, slot in ((self.raster.layerChanged, self.band.setLayer),):
            signal.disconnect(slot)


class Row:
    def __init__(self):
        self.button.clicked.connect(lambda: self.changed.emit())
        self.button.deleteLater()


class UnitStyleEditor:
    def __init__(self):
        self.check.toggled.connect(self.visibility_changed.emit)


class UnitsEditor:
    def rebuild(self):
        row = UnitStyleEditor()
        row.deleteLater()


class SidePanel:
    def __init__(self, parent):
        self.parent = parent


class MainDialog:
    def init(self):
        self.panel = SidePanel(self)
        self.panel.changed.connect(self.on_changed)
```

### Actual output (1.19.0)

```text
connect_sites: 6, matched: 2, unmatched: 3, benign: 1

self.a.toggled            -> self.changed.emit         matched    (WRONG)
self.b.toggled            -> self.changed.emit         matched    (WRONG)
self.raster.layerChanged  -> self.band.setLayer        unmatched  (WRONG: tuple loop)
self.button.clicked       -> lambda: ...               benign     (OK)
self.check.toggled        -> self.visibility_changed.emit unmatched (WRONG: should be benign)
self.panel.changed        -> self.on_changed           unmatched  (WRONG: should be benign)
```

### Expected output

```text
self.a.toggled            -> self.changed.emit         unmatched
self.b.toggled            -> self.changed.emit         unmatched
self.raster.layerChanged  -> self.band.setLayer        matched
self.button.clicked       -> lambda: ...               benign
self.check.toggled        -> self.visibility_changed.emit benign
self.panel.changed        -> self.on_changed           benign
```

---

## Root cause

### R1 — slot-less disconnect matches every sender (critical)

`analyzer/signal_resolver.py:68-79` filters candidates by group, receiver and
slot, but **not by sender**:

```python
candidates = [
    record
    for record in pending.values()
    if _same_group(record, disconnect, scope)
    and _receiver_matches(record, disconnect)
    and _slot_matches(record, disconnect)
]
```

`_slot_matches` treats `disconnect.slot is None` as a wildcard
(`signal_resolver.py:187-191`) and `_receiver_matches` treats
`disconnect.receiver is None` as a wildcard (`:180-184`). A slot-less
`disconnect()` therefore consumes **every pending connect in the same class**.

In the reproduction, `self.changed.disconnect()` is recorded as
`sender="self.changed"`, `receiver=None`, `slot=None`; it matches
`self.a.toggled → self.changed.emit` and `self.b.toggled → self.changed.emit`
even though Qt only disconnects slots of `self.changed`.

Same pattern in SecInterp: `section_page.py:290 self.dataChanged.disconnect()`
hides its two connections.

### R2 — tuple-unpacked loops are not expanded

`analyzer/signal_analysis.py:289-300` expands only a single `Name`/`Attribute`
loop target. `for signal, slot in (...)` has an `ast.Tuple` target,
`_target_name` returns `None`, and the collector falls back to
`generic_visit`. The disconnect is recorded as sender `signal`, slot `slot`, so
the real connects remain unmatched.

SecInterp examples: `dem_page.py:384-392` (5 connections) and
`section_page.py:283-288` (2 connections).

### R3 — lifetime hints do not propagate from a container to its children

`_lifetime_for` (`signal_analysis.py:314-321`) attaches hints to the variable
that owns the connection. It catches `row.* → self.*` when `row.deleteLater()`
is visible, but not:

- `self.check.toggled` inside `UnitStyleEditor`: the row is `deleteLater()`d,
  not the child widget.
- `self.panel.changed` in `MainDialog`: the panel is a child of the dialog and
  is destroyed with it.
- `SectionFeatureSelector` combos: permanent children of the section page.

SecInterp: 6 panel + 4 side-panel lambda + 2 selector entries are reported as
unmatched instead of benign.

---

## Suggested fix

### R1

Add sender equality to the candidate filter:

```python
if (
    _same_group(record, disconnect, scope)
    and record.get("sender") == disconnect.get("sender")
    and _receiver_matches(record, disconnect)
    and _slot_matches(record, disconnect)
)
```

Keep `slot is None` as "all slots of **this sender**", not "all senders".

### R2

Expand tuple/list targets, e.g. pair each element of
`for signal, slot in ((a, b), (c, d))` and record `(sender, slot)` per element.
A minimal implementation can handle `ast.Tuple` targets where every element is a
simple `Name`/`Attribute`.

### R3

Propagate `deleteLater`/parent lifetime from the container to its child widgets
and lambdas. If full propagation is too broad, accept
`ignore_senders`/`ignore_paths` for known-benign UI rows and mark these entries
`confidence="medium"` instead of `high`.

---

## Regression tests

Suggested fixtures under `tests/fixtures/signal_leaks/`:

| Fixture | Expected |
| :--- | :--- |
| `slotless_disconnect_same_class.py` | sender A connected, sender B slot-less disconnected → A remains `unmatched` |
| `loop_tuple_disconnect.py` | `for signal, slot in (...)`: 0 unmatched |
| `child_widget_lifetime.py` | child widget of a `deleteLater()` container → `benign` |
| `parent_child_panel.py` | panel child of the dialog → `benign` |
| `symbology_tab_shape.py` | 15 connects to `self.changed.emit` + `self.changed.disconnect()` → 15 `unmatched` |

On the SecInterp corpus, after R1–R3 the rule should report the 16 real sites
(15 `changed.emit` + 1 reset button) on the current code, with no alias/tuple or
lifetime false positives.

---

## Impact

- The rule is informational by default, but `emit = true` is advertised as a
  gate; a false negative makes that gate unreliable.
- The real SecInterp duplication (`SymbologyTab`) is invisible: each open/close
  cycle adds 15 duplicate `changed.emit` connections and one reset button
  connection.
- R2/R3 add noise that hides the true positives.

## Additional context

- The 1.19.0 changelog says loop variables and aliases are handled; R2 shows
  tuple-unpacked targets are not.
- The SecInterp fix plan and the full verification are in
  `docs/plans/upstream_signal_leak_rule.md` in `geociencio/sec_interp`.
- I can provide a reduced SecInterp corpus or a failing fixture PR if useful.

---

## Update — verified with 1.19.1 (2026-11-01)

R1 is fixed: a slot-less `disconnect()` now matches only the same sender, and 11
of the 15 real `SymbologyTab` links are reported as `unmatched`.

Three residual defects remain:

- **R4:** `_record_parented_assignment` treats `QRadioButton(self.tr("A"))` as
  parented because `first_arg.startswith("self.")`; 4 of the 15 links and the
  reset button are classified `benign` / `parent_child`. Require a real parent
  expression (`ast.Name`/`ast.Attribute`), not a `Call`.
- **R5:** `for task in list(self._active_tasks): task.finished.disconnect()` leaves
  `task` unresolved but `confidence="high"`; 6 false positives in
  `preview_task_orchestrator.py`.
- **R6:** tuple targets are recognized, but `_call_parts` uses the first slot for
  every sender; 3 `dem_page` + 1 `section_page` false positives. Zip the
  `sender`/`slot` bindings.

Current SecInterp measurement: **127 matched, 27 unmatched, 22 benign**. After
SecInterp P0: 16 unmatched / 17 benign (the remaining R3/R5/R6 false positives).
