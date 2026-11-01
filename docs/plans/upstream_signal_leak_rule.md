# Upstream Fix Plan and 1.19.x Verification: `SIGNAL_LEAK`

> **Audience**: `qgis-plugin-analyzer` maintainer or an AI coding agent working on
> that repository.
> **Baseline analysed**: `qgis-plugin-analyzer` **1.18.0** (original proposal),
> **1.19.0**, and **1.19.1** (2026-11-01, published on PyPI and adopted by
> SecInterp).
> **Status**: ✅ **R1 fixed in 1.19.1**; ⚠️ **R2/R3 partially fixed and new
> residuals R4–R6 found** — a follow-up 1.19.2 is required before the rule is
> trustworthy for duplicate connections and unresolved loop aliases.
> **Tracking issue**: <https://github.com/geociencio/qgis-plugin-analyzer/issues/1>
> (published 2026-11-01; [1.19.1 verification comment](https://github.com/geociencio/qgis-plugin-analyzer/issues/1#issuecomment-6561009945)).
> **Companion**: SecInterp's implementation plan
> [implementation_plan_v3.12.1_signal_idempotency.md](implementation_plan_v3.12.1_signal_idempotency.md).
> **Why this matters**: 1.19.1 fixes the slot-less sender bug, so the 15
> `SymbologyTab` links are no longer silently *matched*. But a new parent-child
> heuristic classifies 4 of them (and the reset button) as **benign**, and
> unresolved loop variables add 6 false `task.*` entries. The real 16 are still
> not all reported as `unmatched`.

---

## 1. Executive summary

### 1.1 What 1.19.0 shipped

`qgis-plugin-analyzer` 1.19.0 (2026-11-01) implements the staged proposal:

- Per-connection records with `file`, `line`, `scope`, `sender`, `receiver`,
  `slot`, `status`, `confidence`, `lifetime` and `connection_type`.
- Loop-variable and simple-alias resolution (`SignalEvent` collection in
  `signal_analysis.py`).
- Slot-aware matching and duplicate counting (`signal_resolver.py`).
- `Qt.UniqueConnection` handling and first lifetime heuristics (`deleteLater`,
  parented constructors, `destroyed.connect`).
- `--signals` for the detailed list; the `🚨` banner is gone.
- `[tool.qgis-analyzer.profiles.<p>.rules.SIGNAL_LEAK]` with `emit`, `scope`,
  `confidence`, `include_benign`, `ignore_senders`, `ignore_paths`.
- Stable JSON at `signal_connections`; `signal_leaks` is now a deprecated
  sender-string list.

### 1.2 SecInterp measurement with 1.19.0

| Metric | Value |
| :--- | ---: |
| Connect sites | 176 |
| Matched | 148 |
| Unmatched | 18 |
| Benign | 10 |
| Confidence | all `high` |

The 18 unmatched entries:

| File | N | Classification |
| :--- | ---: | :--- |
| `gui/main_dialog.py:142-147` | 6 | Panel signals; parent-child, should be benign (R3) |
| `gui/preview_side_panel.py:84,94,110,124` | 4 | Row-local lambda connections; should be benign (R3) |
| `gui/ui/pages/dem_page.py:376-380` | 5 | Correct disconnects inside a **tuple-unpacked** loop; false positives (R2) |
| `gui/ui/pages/section_feature_selector.py:163-164` | 2 | Permanent child widget; should be benign (R3) |
| `gui/ui/pages/settings/symbology_units.py:127` | 1 | **True positive**: reset button never disconnected |

The 10 benign entries are the `row.*` connections in `preview_side_panel.py:308-315`
(6) and `symbology_units.py:93-96` (4).

### 1.3 Residual defects

| ID | Severity | Defect |
| :--- | :--- | :--- |
| **R1** | **Critical false negative** | A slot-less `disconnect()` matches **every connect in the class**, regardless of sender. `symbology_tab.py:354 self.changed.disconnect()` marks the 15 `changed.emit` connections (the real bug) and the 2 `_on_topo_mode_changed` connections as matched. `section_page.py:290 self.dataChanged.disconnect()` does the same for its two connects. |
| **R2** | False positive | Tuple-unpacked loop targets are not expanded: `for signal, slot in (...): signal.disconnect(slot)` is recorded as sender `signal`, slot `slot`. The 5 `dem_page` disconnects are not matched. |
| **R3** | Benign misclassification | Lifetime hints do not propagate from a container widget to its internal widgets/lambdas; 6 panel + 4 side-panel + 2 selector connections are reported as unmatched instead of benign. |

R1 is the blocker: the rule is **greener than reality** precisely where the real
bug lives. The 1.19.0 release fixed the false-positive problem but introduced (or
exposed) a sender-scoping false negative in the resolver.

### 1.4 Required follow-up (1.19.1)

1. Add sender equality to the candidate filter in `signal_resolver.py`.
2. Expand `ast.Tuple`/`ast.List` loop targets in `signal_analysis.py`.
3. Propagate lifetime evidence to child widgets/lambdas (or allow a documented
   `ignore_senders`/`ignore_paths` policy for the known-benign rows).
4. Add the regression fixtures in §7, including the SecInterp `symbology_tab`
   shape: 15 connects to `self.changed.emit` + `self.changed.disconnect()`.

### 1.5 SecInterp measurement with 1.19.1

| Metric | Value |
| :--- | ---: |
| Connect sites | 176 |
| Matched | 127 |
| Unmatched | 27 |
| Benign | 22 |
| Confidence | 172 high, 4 medium |

| File | Unmatched | Benign | Diagnosis |
| :--- | ---: | ---: | :--- |
| `gui/main_dialog.py` | 6 | 0 | Panel parent-child not detected (R3 residual) |
| `gui/preview_task_orchestrator.py` | 6 | 0 | `for task in list(self._active_tasks)` not resolved; false positives (R5) |
| `gui/ui/pages/dem_page.py` | 3 | 1 | Tuple loop pairs only the first slot; false positives (R6) |
| `gui/ui/pages/section_page.py` | 1 | 0 | Same tuple-loop pairing bug (R6) |
| `gui/ui/pages/settings/symbology_tab.py` | **11** | **4** | 11 real links visible; 4 real links hidden as `parent_child` (R4) |
| `gui/ui/pages/settings/symbology_units.py` | 0 | **5** | 4 rows + the **reset button** hidden as `parent_child` (R4) |

The real 16 sites are now split: **11 unmatched + 5 benign** (4 `changed.emit` +
reset button). The parent-child heuristic is over-broad, so the summary still
under-reports the real bug.

### 1.6 Residual defects after 1.19.1

| ID | Severity | Defect | Evidence |
| :--- | :--- | :--- | :--- |
| **R1** | ✅ Fixed | Sender equality added; slot-less disconnect no longer matches other senders | `signal_resolver.py:73` |
| **R2** | ⚠️ Partial | Tuple targets are recognized, but the **slot** is canonicalized to the first element; sender/slot pairs are not zipped | 3 `dem_page` + 1 `section_page` |
| **R3** | ⚠️ Partial | Rows/lambdas/selector are benign, but the panel is not detected | 6 `main_dialog` |
| **R4** | **Critical false negative** | `_record_parented_assignment` treats `QPushButton(self.tr(...))` as an explicit parent because the first arg text starts with `self.`; real duplicates become `parent_child` | 4 `changed.emit` + reset button |
| **R5** | False positive | `for task in list(self._active_tasks)` leaves `task` unresolved but `confidence="high"`; the disconnect is correct | 6 `preview_task_orchestrator` |
| **R6** | False positive | Tuple-loop slot pairing uses `canonical(args[0])` (first slot only) instead of zipping the `sender`/`slot` bindings | 3 `dem_page` + 1 `section_page` |

R4 is the new blocker: it re-hides real duplicates as benign. R2/R6 share the
same root cause and should be fixed together.

### 1.7 Required follow-up (1.19.2)

1. **R4:** only treat a constructor's first argument as a parent when it is a
   real parent expression (`self`, `parent`, or an attribute chain), not a call
   such as `self.tr(...)`. A widget created with `QRadioButton(self.tr("X"))`
   must not be `parent_child`.
2. **R5:** mark unresolved loop bindings (`for task in list(...)`) as
   `confidence="low"`, or resolve `list(self._active_tasks)` to the receiver's
   members; do not report high-confidence leaks for a correct disconnect.
3. **R2/R6:** pair the `sender` and `slot` loop bindings element-wise, not
   `sender × first_slot`.
4. Add fixtures for the three cases in §7.

Staged expectation on the **current** SecInterp code:

| State | Unmatched | Benign | Composition |
| :--- | ---: | ---: | :--- |
| 1.19.0 | 18 | 10 | 15 real hidden by R1 |
| **1.19.1 (measured)** | **27** | **22** | 11 real + 5 real-benign + 6 R5 + 4 R6 + 6 R3 |
| 1.19.2 (R4) | 32 | 17 | 16 real + 6 R5 + 4 R6 + 6 R3 |
| 1.19.2 (R4+R5+R6) | 22 | 17 | 16 real + 6 panel (R3) |
| 1.19.2 (R4+R5+R6+R3) | 16 | 23 | all 16 real sites visible |
| + SecInterp P0 | 0 | 23 | duplication fixed |

The target is: **all 16 real sites must be `unmatched`**, and the alias/tuple/
lifetime false positives must be gone. After SecInterp P0 the count must be 0.

---

## 2. Prior implementation (1.18.0, verified)

| Element | Location | Behaviour |
| :--- | :--- | :--- |
| State | `analyzer/visitors/safety_visitor.py:31-32` | `self.connections: set[str]`, `self.disconnections: set[str]` |
| Collection | `safety_visitor.py:72-83` | `if func_name.endswith(".connect")`: store `func_name.rsplit(".connect", 1)[0]`; same for `.disconnect` |
| Chain builder | `safety_visitor.py:124-130` | Handles only `ast.Name` and `ast.Attribute`; returns `""` for anything else |
| Result | `safety_visitor.py:132-135` | `sorted(connections - disconnections)` |
| Docstring claim | `safety_visitor.py:13-14` | "Signals connected but not disconnected in 'unload'" — **not what the code does** |
| Rule catalog | `analyzer/rules/catalog_core.py:44-53` | `SIGNAL_LEAK`, severity `low`, `emitted=False` |
| Aggregation | `analyzer/aggregators.py:116, 147, 167` | `set.update(...)` across modules; unique strings only |
| Summary | `analyzer/reporters/summary_reporter.py:122-126` | Prints `🚨 Signal Leaks Detected: N` unconditionally |

Consequences already observed:

- 49 per-module entries → 47 unique because `row.color_requested` and
  `row.visibility_changed` appear in two files and are deduplicated by the global
  `set`.
- 67 `.connect()` call sites in SecInterp produce those 47 strings; several
  strings represent 4–5 connections.

### 2.2 1.19.0 implementation (verified)

| Element | Location (1.19.0) | Behaviour |
| :--- | :--- | :--- |
| Event model | `analyzer/signal_analysis.py:31-53` | `SignalEvent` with `file`, `line`, `scope`, `class_name`, `function_name`, `kind`, `sender`, `receiver`, `slot`, `connection_type`, `confidence`, `text`, `order`, `lifetime` |
| Collector | `signal_analysis.py:239-369` | Single-pass AST collector with local alias/loop resolution; `visit_For` expands a single `Name`/`Attribute` target (`:289-300`) |
| Lifetime | `signal_analysis.py:314-321`, `_lifetime_for` | Attaches `local_widget`, `parent_child`, `destroyed_hook` hints |
| Resolver | `analyzer/signal_resolver.py:18-88` | Matches per class/function/file scope; `_slot_matches` treats a `None` slot as wildcard (`:187-191`) |
| Candidate filter | `signal_resolver.py:68-79` | 1.19.0 lacked sender equality (R1); **1.19.1 adds it at `:73`** |
| Report | `signal_resolver.py:194-254` | `matched` / `unmatched` / `benign`, legacy `signal_leaks` |
| Engine | `analyzer/engine.py:378-424` | Resolves at project scope; optional emission via `emit=true` |
| Summary | `analyzer/reporters/summary_reporter.py:127-166` | Informational, detailed only with `--signals`; no `🚨` banner |

---

## 3. Defects (1.18.0) and their 1.19.x status

| Defect | 1.18.0 | 1.19.1 status |
| :--- | :--- | :--- |
| D1 literal matching | False positives | ✅ Fixed for single-name loops and aliases; ⚠️ tuple loop slot pairing (R6) |
| D2 file-wide scope | No scope | ✅ Fixed: `function`/`class`/`file` |
| D3 unique sender strings | Collapsed | ✅ Fixed: per-connection records |
| D4 global aggregation | Lost file/line | ✅ Fixed: records carry `file`/`line`; summary aggregates records |
| D5 no slot identity | False negatives | ✅ Fixed: slot-aware + sender equality (R1) |
| D6 no lifetime awareness | False positives | ⚠️ Partially fixed: rows/lambdas/selector benign; panel missing (R3); parent heuristic over-broad (R4) |
| D7 loop-connected signals invisible | False negatives | ✅ Fixed for single-name loops; ⚠️ tuple loop slot pairing (R6) |
| D8 misleading banner | `🚨` unconditional | ✅ Fixed: informational, `--signals` opt-in |
| **R4** | New in 1.19.1 | `self.tr(...)` mistaken for a parent → real duplicates `benign` |
| **R5** | New in 1.19.1 | Unresolved `for task in list(...)` reported at `confidence="high"` |
| **R6** | New in 1.19.1 | Tuple loop pairs sender with the first slot only |

### D1 — Literal matching only (false positives)

A disconnect through a loop variable is recorded as `signal`, not as the real
sender:

```python
for signal in (self.a.toggled, self.b.toggled):
    signal.disconnect()
# connects: self.a.toggled, self.b.toggled
# disconnects: signal
# => both reported as leaks
```

SecInterp: 29 of the 47 entries are this pattern
(`dialog_signal_manager.py:147,160,183,219-233`,
`preview_task_orchestrator.py:47-49`, `dem_page.py:392`, `section_page.py:288`).

### D2 — File-wide scope (semantic mismatch)

The docstring says `initGui()` → `unload()`, but the implementation has no
function/class scope. A connect in `__init__` and an unrelated `.disconnect()`
with the same literal text anywhere in the file is treated as matched, even if
the disconnect never runs. Conversely, a correct `initGui`/`unload` pair is not
verified as a lifecycle pair.

### D3 — Unique sender strings collapse connections (false negatives)

Five connections to `self.raster_combo.layerChanged` are one set entry. Two
connections to the same signal are one entry. The rule cannot say "4 of 5
connections are unresolved".

### D4 — Global aggregation hides per-file context

The cross-module `set` loses file and line. `row.color_requested` in
`preview_side_panel.py` and in `symbology_units.py` becomes one entry with no
location. It also makes the summary count unstable as files move.

### D5 — No slot identity (false negatives)

Qt distinguishes `sender.disconnect()` (remove all slots) from
`sender.disconnect(slot)` (remove one). The current sets do not model slots. Once
one slot of a signal is disconnected with a literal path, the whole sender looks
resolved. SecInterp's `radio_gradient.toggled` has two slots
(`_on_topo_mode_changed` and `changed.emit`); disconnecting only the first is
enough to silence the rule, even though the second leaks. Note that in the
current code the disconnect is written through `signal`, so the rule reports the
signal for the wrong reason. **Fixing the code to a literal
`sender.disconnect(slot)` would hide the real bug.**

### D6 — No Qt lifetime awareness (false positives)

The rule flags child widgets that are destroyed with their parent or via
`deleteLater()`:

```python
row = UnitStyleEditor(...)
row.color_requested.connect(self.unit_color_requested.emit)
row.deleteLater()          # Qt removes the connection
```

SecInterp: 15 unique entries are this pattern (`preview_side_panel.py`,
`symbology_units.py`, `section_feature_selector.py`, the `main_dialog` panel).

### D7 — Loop-connected signals are invisible (false negatives)

The inverse of D1:

```python
for signal in (self.a.toggled, self.b.toggled):
    signal.connect(self.changed.emit)
# connect path is "signal" → not collected
```

SecInterp: 13 connections in `symbology_tab.py:326-343` are invisible, including
the real duplication bug.

### D8 — Misleading presentation

The rule says "leak" and the summary prints a `🚨` alert, but:

- `emitted=False` means it is not an issue and cannot fail a gate;
- the output has no `file:line`, no slot, no confidence, no lifetime;
- there is no way to opt out of the banner or to mark known-benign patterns.

### R1 — Slot-less disconnect matched every sender (✅ fixed in 1.19.1)

1.19.0 filtered candidates by group, receiver and slot but **not by sender**.
1.19.1 adds `record.get("sender") == disconnect.get("sender")`
(`signal_resolver.py:73`), so a slot-less `disconnect()` now resolves only
connections from the same sender. Verified: `self.changed.disconnect()` no longer
marks the 15 `SymbologyTab` links as matched.

### R2 — Tuple-unpacked loops (⚠️ partially fixed in 1.19.1; R6 remains)

1.19.0 expanded only single `Name`/`Attribute` targets. 1.19.1 adds
`_target_names()` and `loop_bindings()` (`signal_analysis.py:82-96`, `:218-231`;
`signal_scope.py:80-93`), so tuple targets are recognized. However, the **slot**
is still canonicalized to the first element (R6), so only part of the loop is
matched.

### R3 — Lifetime hints (⚠️ partially fixed in 1.19.1; R4 remains)

1.19.1 propagates `deleteLater` from a row to its class and handles explicit
parents, so rows, lambdas and the selector are now benign. It still misses the
`main_dialog` panel (6), and the new parent heuristic is over-broad (R4).

### R4 — `self.tr(...)` is mistaken for a parent (critical false negative)

`_record_parented_assignment` (`signal_analysis.py:155-164`) classifies a widget
as `parent_child` when its constructor's first argument starts with `self.`:

```python
self.btn_reset_units = QPushButton(self.tr("Reset unit styles"))
self.radio_gradient = QRadioButton(self.tr("Gradient"))
```

`self.tr("...")` is a **call**, not a parent widget, but
`first_arg.startswith("self.")` is true. Those connections become
`lifetime="parent_child"`, so they are excluded from the leak count.

SecInterp: 4 of the 15 real `changed.emit` links and the reset button are hidden
as benign. A minimal fixture with `QRadioButton(self.tr("A"))` shows 3/3 real
connections reported as benign.

**Fix:** require the first argument to be a parent **expression**
(`ast.Name`/`ast.Attribute`), not a call; explicitly reject `self.tr(...)` and
other method calls. Parent-child prevents a dangling reference, not a duplicate
connection when `connect_signals()` is re-invoked.

### R5 — Unresolved loop aliases are high confidence (false positives)

`for task in list(self._active_tasks): task.finished_with_results.disconnect()`
is a correct disconnect, but `loop_values` only expands literal tuples/lists
(`signal_scope.py:71-78`). `task` stays unresolved and `expr_confidence` returns
`high` (`signal_scope.py:131-144`), so 6 task connections in
`preview_task_orchestrator.py` are reported as unmatched.

**Fix:** mark unknown loop bindings `confidence="low"` (or resolve
`list(self._active_tasks)` to the receiver's members). At minimum, do not report
them as high-confidence leaks.

### R6 — Tuple loop pairs every sender with the first slot (false positives)

`_record_signal_call` expands the sender list (`signal_analysis.py:259-280`) but
`_call_parts` canonicalizes the slot with `canonical(args[0])`
(`signal_analysis.py:288-320`), which returns the first value only. For:

```python
for signal, slot in (
    (self.raster.layerChanged, self.band.setLayer),
    (self.raster.layerChanged, self.update_stats),
    (self.band.bandChanged, self.update_stats),
):
    signal.disconnect(slot)
```

the three disconnect events all use `slot=self.band.setLayer`; the other two
connects remain unmatched. SecInterp: 3 `dem_page` + 1 `section_page` false
positives.

**Fix:** zip the expanded `sender` and `slot` bindings element-wise instead of
`sender × first_slot`.

---

## 4. Design goals

1. **No false green.** A signal with two slots and one disconnect must report the
   other slot.
2. **No false alarm.** A correct disconnect through a loop variable or alias must
   be resolved.
3. **Location and confidence.** Every entry carries `file`, `line`, `scope`,
   `sender`, `slot`, `status`, `confidence`, `lifetime`.
4. **Count connections, not strings.** Duplicate connections are visible; the
   summary uses counts of connection sites.
5. **Lifetime is not a leak.** `deleteLater` / parent-child / `destroyed` cleanup
   are reported as `benign` when `include_benign=true`, never as leaks by default.
6. **Backward compatible.** `qgis_context.signal_leaks` keeps working until the
   next major version.
7. **No new gate by default.** The rule remains informational unless a project
   opts in with `emit=true`.

---

## 5. Algorithm: 1.19.0 implementation and required fixes

### 5.0 Minimal 1.19.2 patch set

R1 (sender equality) and the first pass of R2/R3 are already in 1.19.1. The
remaining correctness fixes are:

1. **R4 — `signal_analysis.py:155-164`:** only treat the first constructor
   argument as a parent if it is an `ast.Name`/`ast.Attribute` expression.
   `self.tr("...")` is a `Call` and must be rejected. Parent-child means no
   dangling reference, **not** no duplicate connection on a re-invoked
   `connect_signals()`.
2. **R5 — `signal_scope.py:131-144`:** mark a `Name` bound by an unresolved loop
   (`for task in list(self._active_tasks)`) as `confidence="low"`, or resolve
   `list(<receiver>)` to its members. Do not report high-confidence leaks for a
   correct disconnect.
3. **R6 — `signal_analysis.py:259-320`:** zip the expanded `sender` and `slot`
   bindings element-wise. Do not use `canonical(args[0])` (first slot) for every
   sender in a tuple loop.
4. **R3 residual — `main_dialog` panel:** propagate parent-child lifetime from
   `self.preview_widget.side_panel` to the dialog, or allow the existing
   `ignore_senders`/`ignore_paths` policy for that panel.

The rest of this section is the design reference that 1.19.0 followed; keep it
for the 1.19.2 review.

### 5.1 Data model

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class SignalEvent:
    file: str
    line: int
    scope: str              # "Class.method" / "function" / "module"
    kind: str               # "connect" | "disconnect"
    sender: str             # canonical attribute chain
    slot: str | None        # None for disconnect() with no args
    lifetime: str | None    # "local_widget" | "parent_child" | "destroyed_hook"
    confidence: str         # "high" | "medium" | "low"
    text: str               # original source excerpt, for the report
```

### 5.2 Collection with local resolution

Per function/class scope, build a small symbol table:

1. **Alias assignments**
   ```python
   widget = self.dialog.preview_widget
   symbology = self.dialog.page_settings.symbology_tab
   ```
   Map `widget` → `self.dialog.preview_widget`, `symbology` →
   `self.dialog.page_settings.symbology_tab`.

2. **Signal loops**
   ```python
   for signal in (self.a.toggled, self.b.toggled):
       signal.connect(...)      # or .disconnect(...)
   ```
   Expand the loop target to each expression in the tuple/list for the loop body.
   Resolve each event individually, so `self.a.toggled` and `self.b.toggled` are
   distinct events.

3. **Simple local aliases of a signal**
   ```python
   changed = self.changed
   changed.connect(...)
   ```
   Resolve `changed` → `self.changed`. Chains of aliases: resolve transitively,
   with a depth cap (e.g., 8) to avoid cycles.

4. **Do not attempt** dict/list indexing, `getattr(obj, name)`, runtime
   composition or cross-module imports. Emit `confidence: low` and keep the
   literal text instead of dropping the event.

### 5.3 Matching

Match within a scope selected by config (default `class`):

```text
for each connect event C:
    candidates = disconnect events D in the same scope where
        D.sender == C.sender and (D.slot is None or D.slot == C.slot)
    if a candidate exists:
        consume one D (Qt semantics: one disconnect removes one connection)
        C.status = "resolved"
    else:
        C.status = "unmatched"
```

- `disconnect()` with no args consumes **all** matching connects for that sender
  in the scope.
- `disconnect(slot)` consumes **one** matching `(sender, slot)` pair. Duplicate
  connects of the same pair remain unmatched.
- `initGui` → `unload` is matched only inside the same class and when both
  methods exist; do not match a connect in `__init__` with an `unload`
  disconnect unless the config says `scope="file"`.
- If a sender is connected in one module and disconnected in another, report
  `status="unmatched"` with `confidence="low"` and a note
  `"cross-module disconnect not resolved"`. Never mark it resolved by default.

### 5.4 Lifetime classification

Run a separate pass over the event to set `lifetime`:

| Pattern | Classification |
| :--- | :--- |
| Sender/receiver is a local widget variable that receives `.deleteLater()` | `local_widget` |
| Sender is assigned to `self.*` in `__init__` and never reassigned; receiver is `self` | `parent_child` (heuristic, `confidence=medium`) |
| `sender.destroyed.connect(cleanup)` exists | `destroyed_hook` |
| `signal.connect(..., Qt.ConnectionType.UniqueConnection)` | `unique_connection` (dedupe) |

`lifetime != None` → `status = "benign"` when `include_benign=true`; excluded
from the leak count by default. Keep the item in the JSON so a reviewer can see
why it was excluded.

### 5.5 Reporting

Per connection, not per unique string:

```json
{
  "file": "gui/ui/pages/settings/symbology_tab.py",
  "line": 327,
  "scope": "SymbologyTab.connect_signals",
  "sender": "self.radio_gradient.toggled",
  "slot": "self.changed.emit",
  "status": "unmatched",
  "confidence": "high",
  "lifetime": null,
  "reason": "no matching disconnect in scope",
  "text": "signal.connect(self.changed.emit)"
}
```

Summary:

```json
{
  "connect_sites": 176,
  "matched": 127,
  "unmatched": 27,
  "benign": 22,
  "by_confidence": {"high": 172, "medium": 4, "low": 0}
}
```

The SecInterp expectation after the code fix is **16 unmatched** (15
`changed.emit` + 1 reset button). 1.19.1 reports 11 of them as unmatched and 5
as benign (R4), plus 16 false positives (R5/R6/R3). After 1.19.2 the count must
be 16 on the current code; SecInterp P0 then takes it to 0.

---

## 6. Output and CLI contract

### JSON

Add a structured block; keep the legacy key:

```json
{
  "research_metrics": {
    "qgis_context": {
      "signal_leaks": ["self.radio_gradient.toggled", "..."],
      "signal_connections": {
        "summary": { "...": "..." },
        "items": [ "..."]
      }
    }
  }
}
```

- `signal_leaks` remains a **deprecated** sorted list of `sender` strings with
  `status="unmatched"` for one minor release.
- `signal_connections.items` is the new source of truth.
- Add `schema_version` to the block so consumers can evolve.

### CLI (as implemented in 1.19.0)

- Default: one informational line, `Unmatched signal paths: N`; the `🚨` banner
  is gone.
- `--signals` prints the detailed per-connection list.
- The full block is always written to `project_context.json` /
  `PROJECT_SUMMARY.md`; the flag only controls the terminal detail.
- Keep the label "Unmatched signal paths", not "Signal Leaks".

### Configuration

```toml
[tool.qgis-analyzer.profiles.default.rules.SIGNAL_LEAK]
emit = false            # opt-in gate; default stays informational
scope = "class"         # function | class | file
include_benign = false  # show deleteLater/parent-child entries
confidence = "medium"   # minimum confidence to report
ignore_senders = []     # exact or simple glob, e.g. "self.dialog.preview_widget.*"
ignore_paths = []       # file globs
```

The existing `rules_config` mechanism (`base.py:91,107`) can carry this dict;
`SIGNAL_LEAK` needs to read it in the visitor and in the summary reporter. If
`emit=true`, emit a normal issue with `rule_id="SIGNAL_LEAK"` and the configured
severity.

---

## 7. Test matrix

Add fixtures under `tests/fixtures/signal_leaks/` and golden JSON for each:

| Fixture | Expected |
| :--- | :--- |
| `direct_match.py` | 0 unmatched |
| `loop_disconnect.py` | 0 unmatched (D1 regression) |
| `loop_tuple_disconnect.py` | 0 unmatched; **R2** regression (`for signal, slot in (...)`) |
| `alias_disconnect.py` | 0 unmatched |
| `loop_connect.py` | N unmatched (D7 regression) |
| `partial_slot.py` | 1 unmatched (one of two slots) |
| `duplicate_connect.py` | 1 duplicate after one disconnect |
| `disconnect_all.py` | `disconnect()` resolves every slot of **that sender** |
| `slotless_disconnect_same_class.py` | **R1** regression: a slot-less disconnect for sender A must not resolve sender B in the same class |
| `parent_tr_call.py` | **R4** regression: `QRadioButton(self.tr("A"))` + slot-less disconnect → `unmatched`, never `parent_child` |
| `loop_list_alias.py` | **R5** regression: `for task in list(self.tasks): task.finished.disconnect()` → matched (or `confidence="low"`), not high unmatched |
| `loop_tuple_pairs.py` | **R6** regression: three `(sender, slot)` pairs with different slots → 0 unmatched |
| `child_widget_lambda.py` | **R3** regression: lambda connections on a child widget with `deleteLater()` are `benign` |
| `delete_later.py` | `benign` / `local_widget`, 0 leaks |
| `parent_child.py` | `benign` / `parent_child`, 0 leaks by default |
| `destroyed_hook.py` | `benign` / `destroyed_hook`, 0 leaks |
| `init_gui_unload.py` | resolved within the same class |
| `init_gui_no_unload.py` | unmatched, `confidence=high` |
| `cross_function.py` | unmatched by default; resolved with `scope="file"` |
| `cross_module.py` | unmatched, `confidence=low` |
| `unique_connection.py` | one connection, no duplicate |
| `config_ignore.py` | ignored sender/path produces no entry |

Additional requirements:

- The summary count must equal `len(items)` with `status="unmatched"`; no
  unique-string dedupe.
- The same fixture must produce a stable JSON snapshot across runs.
- Run the analyzer on the SecInterp corpus (or a reduced copy) and assert:
  - no alias/loop false positives (including the 3 `dem_page` + 1 `section_page`
    tuple pairs and the 6 `preview_task_orchestrator` aliases);
  - the 16 real `SymbologyTab` sites are **all `unmatched`** before the code fix
    (11 currently + 4 hidden by R4 + the reset button);
  - 0 unmatched after SecInterp P0;
  - the child-lifetime entries (10 side-panel + 4 symbology rows + 2 selector +
    6 panel) are classified as `benign`.

---

## 8. Acceptance criteria

**Delivered in 1.19.0**

- [x] `SIGNAL_LEAK` docstring/catalog describe per-connection analysis, not the
      old `initGui`/`unload` literal diff.
- [x] Single-name loop-variable disconnects produce 0 false positives.
- [x] Single-name loop-variable connects produce per-connection entries.
- [x] Partial-slot disconnects report the remaining slot.
- [x] Duplicate connections are counted, not collapsed.
- [x] `deleteLater` / parented / `destroyed` hints are attached.
- [x] Every item has `file`, `line`, `scope`, `sender`, `receiver`, `slot`,
      `status`, `confidence`, `lifetime`, `connection_type`.
- [x] Summary is informational and `--signals` is opt-in.
- [x] `signal_leaks` remains available (deprecated).
- [x] `emit=true` is available; the default does not change any gate.

**Delivered in 1.19.1**

- [x] **R1**: slot-less disconnect matches only the same sender; verified with
      the `slotless_disconnect_same_class` fixture and SecInterp.
- [x] Tuple/list loop targets are recognized by `_target_names`/`loop_bindings`.
- [x] `deleteLater` propagation for row/lambda/selector connections.
- [x] Explicit parent (`SidePanel(self)`) is classified as `parent_child`.

**Required for 1.19.2**

- [ ] **R4**: `self.tr(...)` is not a parent; `QRadioButton(self.tr("A"))` must
      not become `parent_child`. The 4 hidden `changed.emit` + reset button must
      be `unmatched`.
- [ ] **R5**: unresolved `for task in list(...)` bindings are `confidence="low"`
      or resolved; the 6 `preview_task_orchestrator` false positives disappear.
- [ ] **R6**: tuple-loop `sender`/`slot` bindings are zipped; the 3 `dem_page` +
      1 `section_page` false positives disappear.
- [ ] **R3 residual**: the 6 `main_dialog` panel connections are `parent_child`.
- [ ] Tests and fixtures pass in CI; JSON snapshots are stable.
- [ ] CHANGELOG documents the 1.19.2 fixes and the new fixtures.

---

## 9. Compatibility and migration

- **Minor version** (`1.19.0`): add `signal_connections`, keep `signal_leaks`,
  add `--signals`, add config. No breaking change.
- **Next major**: remove `signal_leaks` or make it an alias of the unmatched
  sender list; change the default summary to hidden.
- Consumers that read `qgis_context.signal_leaks` (SecInterp reads it only in the
  summary output, not in `agent_metrics.json`) keep working.
- Do not change CC, i18n, security or module-size semantics.

---

## 10. Non-goals

- Full dataflow analysis, SSA, type inference or runtime instrumentation.
- Cross-repository/plugin signal buses resolved across modules by default.
- Proving that a `disconnect` is reachable at runtime.
- Replacing Qt's own object-lifetime model.
- Turning `SIGNAL_LEAK` into a release gate for every plugin.

---

## 11. Implementation checklist / PR breakdown

**PR 1 — honest contract (✅ 1.19.0)**

1. [x] Rename the summary label to "Unmatched signal paths" (informational).
2. [x] Make the detailed list opt-in (`--signals`); no `🚨` banner.
3. [x] Fix the visitor/catalog docstrings.
4. [x] Add `signal_connections` with per-connection fields.
5. [x] Keep `signal_leaks` for compatibility.
6. [x] Tests for the JSON shape and the opt-in flag.

**PR 2 — resolution (✅ 1.19.0, ⚠️ R1/R2)**

7. [x] Per-scope symbol table (alias assignments + single-name `for` loops).
8. [x] Collect `SignalEvent`s with `scope`, `sender`, `receiver`, `slot`.
9. [x] Slot-aware matching and duplicate counting.
10. [x] Add `scope` config (`function`/`class`/`file`).
11. [x] Fixtures for D1, D2, D3, D5, D7.
12. [x] **R1**: sender equality in `signal_resolver.py` + fixture (1.19.1).
13. [x] **R2**: `ast.Tuple`/`ast.List` targets recognized (1.19.1).
14. [ ] **R6**: zip `sender`/`slot` bindings element-wise (1.19.2).

**PR 3 — lifetime (✅ partial, ⚠️ R3/R4)**

15. [x] Detect `deleteLater`, parented constructors and `destroyed.connect`.
16. [x] Add `include_benign` and `confidence` config.
17. [x] Fixtures for the basic D6 cases.
18. [x] **R3**: propagate child-widget/lambda lifetime (1.19.1; panel remains).
19. [ ] **R4**: reject `self.tr(...)` as a parent; add `parent_tr_call.py`.
20. [ ] **R5**: unresolved loop bindings → `confidence="low"`; add
       `loop_list_alias.py`.
21. [ ] **R3 residual**: panel is `parent_child` in `main_dialog`.
22. [ ] Run the SecInterp corpus and publish the before/after report.

**PR 4 — optional cross-module**

23. [ ] Detect a sender connected in module A and disconnected in module B;
       report `confidence="low"` and a reason.
24. [ ] Do not resolve it by default; document the limitation.

---

## 12. SecInterp expected outcome

| State | `unmatched` | `benign` | Notes |
| :--- | ---: | ---: | :--- |
| 1.18.0 + current code | 47 unique strings (16 real sites, 13 hidden) | not modelled | Misleading `🚨` banner |
| 1.19.0 (measured) | 18 | 10 | 15 real hidden by R1 |
| **1.19.1 (measured)** | **27** | **22** | 11 real + 5 real-benign (R4) + 6 R5 + 4 R6 + 6 R3 |
| 1.19.2 (R4) | 32 | 17 | 16 real visible |
| 1.19.2 (R4+R5+R6) | 22 | 17 | 16 real + 6 panel (R3) |
| 1.19.2 (R4+R5+R6+R3) | 16 | 23 | all 16 real sites visible |
| + SecInterp P0 | 0 | 23 | duplication fixed |

The 16 are 15 `source → self.changed.emit` connections in
`symbology_tab.py:326-343` plus `btn_reset_units.clicked` in
`symbology_units.py:127`.

The **benign** column counts connection sites, not unique sender strings: the
22 sites in `preview_side_panel.py`, `main_dialog.py`, `section_feature_selector.py`
and `symbology_units.py` collapse to 15 unique strings in 1.18.0. Per-site
counting is one of the fixes.

---

## 13. References

**1.18.0 (original heuristic)**

- `analyzer/visitors/safety_visitor.py:13-14, 31-32, 72-83, 124-135`.
- `analyzer/rules/catalog_core.py:44-53`.
- `analyzer/aggregators.py:116, 147, 167`.
- `analyzer/reporters/summary_reporter.py:122-126`.
- `analyzer/visitors/composite_visitor.py:128-137`.

**1.19.0 (implemented)**

- `analyzer/signal_analysis.py:31-53` (`SignalEvent`), `:239-369` (collector).
- `analyzer/signal_resolver.py:18-88` (resolver), `:68-79` (R1), `:163-191`
  (scope/receiver/slot matching), `:194-254` (record/report).
- `analyzer/engine.py:378-424` (project-scope resolution and optional emission).
- `analyzer/reporters/summary_reporter.py:127-166` (`--signals` output).
- `analyzer/rules/catalog_core.py:44-56` (informational rule).

**1.19.1 (R1 fixed, R4–R6 found)**

- `analyzer/signal_resolver.py:73` — sender equality (R1 fixed).
- `analyzer/signal_analysis.py:82-96` (`_target_names`), `:218-231`
  (`visit_For` tuple bindings).
- `analyzer/signal_scope.py:71-93` (`loop_values`/`loop_bindings`).
- `analyzer/signal_analysis.py:155-164` — R4 (`self.tr(...)` parent bug).
- `analyzer/signal_scope.py:131-144` — R5 (unknown bindings stay `high`).
- `analyzer/signal_analysis.py:259-320` — R6 (slot canonicalization).

**SecInterp**

- Fix plan:
  [implementation_plan_v3.12.1_signal_idempotency.md](implementation_plan_v3.12.1_signal_idempotency.md).
- Minimal repros and SecInterp classification: conversation of 2026-11-01.

---

## 14. Issue-ready report (copy/paste)

> Ready-to-file body:
> [upstream_issue_signal_leak_1.19.0.md](upstream_issue_signal_leak_1.19.0.md)
> (`gh issue create --repo geociencio/qgis-plugin-analyzer --title "..." --body-file ... --label bug`).

**Title:** `SIGNAL_LEAK: a slot-less disconnect resolves connections from other senders (1.19.0 false negative)`

**Body:**

````markdown
## Summary

`SIGNAL_LEAK` in 1.19.0 reports per-connection records, but a slot-less
`sender.disconnect()` resolves **every pending connect in the same class**,
regardless of sender. A real duplicate-connection bug is therefore reported as
`matched`.

## Reproduction

```python
class Widget(QWidget):
    changed = pyqtSignal()

    def connect_signals(self):
        for signal in (self.a.toggled, self.b.toggled):
            signal.connect(self.changed.emit)          # 2 connects
        self.changed.disconnect()                       # slot-less disconnect

    def disconnect_signals(self):
        self.changed.disconnect()
```

`self.changed.disconnect()` is recorded with `sender="self.changed"`,
`receiver=None`, `slot=None`. `analyzer/signal_resolver.py:68-79` filters
candidates by group, receiver and slot only; `_slot_matches` treats `None` as a
wildcard (`:187-191`). Both `self.a.toggled → self.changed.emit` and
`self.b.toggled → self.changed.emit` are marked `matched`, although Qt only
disconnects slots of `self.changed`.

On the SecInterp corpus, 1.19.0 reports 148 matched / 18 unmatched, and marks
the real 15 `source → self.changed.emit` duplication links as `matched`.

## Expected

A slot-less disconnect resolves **all slots of the same sender only**. The 15
links must be `unmatched` (or `benign` after the lifetime fix), not `matched`.

## Suggested fix

Add sender equality to the candidate filter:

```python
if (
    _same_group(record, disconnect, scope)
    and record.get("sender") == disconnect.get("sender")
    and _receiver_matches(record, disconnect)
    and _slot_matches(record, disconnect)
)
```

## Regression tests

- `slotless_disconnect_same_class.py`: sender A is connected; sender B is
  slot-less disconnected; A must remain unmatched.
- The `symbology_tab` shape: 15 connects to `self.changed.emit` plus
  `self.changed.disconnect()`; expect 15 unmatched.
- `loop_tuple_disconnect.py`: `for signal, slot in (...): signal.disconnect(slot)`
  must resolve the tuple loop (R2).
- `child_widget_lambda.py`: a widget child of a `deleteLater()` row with lambda
  connections must be `benign` (R3).
````

---

## 15. 1.19.1 verification comment (post to issue #1)

```markdown
## Update after 1.19.1 — R1 fixed; R2/R3 partial; new R4–R6

Verified 1.19.1 on the SecInterp corpus (176 connect sites): **127 matched, 27
unmatched, 22 benign**.

R1 is fixed: `self.changed.disconnect()` no longer marks the 15
`SymbologyTab` links as matched; 11 of the 15 are now `unmatched`. However,
the rule is still not trustworthy for duplicate connections:

- **R4 (critical false negative):** 4 of the 15 real `changed.emit` links and
  the reset button are classified `benign` / `parent_child`. `_record_parented_assignment`
  (`signal_analysis.py:155-164`) treats `QRadioButton(self.tr("A"))` as if
  `self.tr(...)` were a parent because `first_arg.startswith("self.")`. A
  parent-child relation prevents a dangling reference, not a duplicate
  connection when `connect_signals()` is re-invoked. Suggested fix: require the
  first argument to be an `ast.Name`/`ast.Attribute` parent expression and reject
  `Call` nodes such as `self.tr(...)`.
- **R5 (false positive):** `for task in list(self._active_tasks): task.finished_with_results.disconnect()`
  is correct, but `loop_values` only expands literal tuples/lists
  (`signal_scope.py:71-78`). `task` stays unresolved and `expr_confidence` returns
  `high` (`signal_scope.py:131-144`), producing 6 unmatched entries in
  `preview_task_orchestrator.py`. Mark unresolved loop bindings `low`, or resolve
  `list(<receiver>)`.
- **R6 (false positive):** tuple targets are now recognized, but
  `_call_parts` canonicalizes the slot to the first element
  (`signal_analysis.py:288-320`). In a 3-pair loop, all disconnect events use the
  first slot; 2 pairs remain unmatched. Zip the expanded `sender`/`slot` bindings
  element-wise.
- **R3 residual:** the 6 `main_dialog` panel connections are still unmatched.

### Minimal repro (7 connects)

```python
class Tab:
    def __init__(self):
        self.a = QRadioButton(self.tr("A"))
        self.b = QRadioButton(self.tr("B"))
        self.reset = QPushButton(self.tr("Reset"))

    def connect_signals(self):
        self.a.toggled.connect(self.changed.emit)
        self.b.toggled.connect(self.changed.emit)
        self.reset.clicked.connect(self.reset_units)

    def disconnect_signals(self):
        self.changed.disconnect()


class Dem:
    def connect_signals(self):
        self.raster.layerChanged.connect(self.band.setLayer)
        self.raster.layerChanged.connect(self.update_stats)
        self.band.bandChanged.connect(self.update_stats)

    def disconnect_signals(self):
        for signal, slot in (
            (self.raster.layerChanged, self.band.setLayer),
            (self.raster.layerChanged, self.update_stats),
            (self.band.bandChanged, self.update_stats),
        ):
            signal.disconnect(slot)


class Tasks:
    def __init__(self):
        self.task = None

    def start(self):
        self.task.finished.connect(self.on_finished)

    def cancel(self):
        for task in list([self.task]):
            task.finished.disconnect()
```

Actual 1.19.1: `matched=1, unmatched=3, benign=3`.

- `Tab`: 3/3 `benign` (`parent_child`) — should be `unmatched` (R4).
- `Dem`: only the first pair matched; 2 `unmatched` (R6).
- `Tasks`: `self.task.finished -> on_finished` `unmatched` — should be matched
  or low confidence (R5).

Expected after 1.19.2: `Tab` 3 `unmatched` (not benign), `Dem` 0 `unmatched`,
`Tasks` 0 `unmatched` (matched or low confidence). The 3 `Tab` entries must not
be benign until the duplicate connection is actually removed.
```
