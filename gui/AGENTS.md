# GUI Layer — Agent Instructions

> **Scope**: All Python modules under `sec_interp/gui/`.
> This file takes precedence over the root `AGENTS.md` for work done in this directory.
> **Reference**: [Root AGENTS.md](../../.agent/AGENTS.md) | [ui-framework](../../.agent/skills/ui-framework/SKILL.md)

---

## ⚠️ Absolute Constraints (NEVER violate)

```
❌  Business logic in GUI classes         → FORBIDDEN
❌  Direct file I/O in GUI classes        → FORBIDDEN
❌  QgsTask running with live QGIS objects → FORBIDDEN (use WKT/DTO in threads)
❌  GUI classes in tests/core/            → FORBIDDEN
❌  iface.messageBar() outside gui/       → FORBIDDEN
```

The `gui/` layer is responsible **only** for:
1. Extracting data from QGIS objects into DTOs (the "Extract" phase)
2. Calling `core/` services with those DTOs (the "Compute" phase)
3. Converting results back to QGIS objects for display (the "Present" phase)

---

## ✅ Required Patterns

### Extract-then-Compute (mandatory)
```python
# ✅ CORRECT — GUI extracts, core computes
def _on_run_clicked(self):
    # Extract phase (GUI responsibility)
    line_wkt = self._section_layer.geometry().asWkt()
    tolerance = self.tolerance_spin.value()

    # Compute phase (delegate to core)
    result = self._geology_service.calculate_intersection(line_wkt, tolerance)

    # Present phase (GUI responsibility)
    self._render_result(result)
```

### Background Processing (QgsTask)
- All operations expected to take > 100ms **must** use `QgsTask`
- **Never** pass live QGIS objects (`QgsVectorLayer`, `QgsFeature`) into a `QgsTask`
- Extract to WKT/dict before launching the task; convert back in `finished()`

```python
# ✅ CORRECT — task receives serialized data
class ProcessTask(QgsTask):
    def __init__(self, wkt_data: list[str], tolerance: float):
        ...
```

### Manager Pattern (for complex dialogs)
Decompose complex dialogs into specialized managers:
- `SignalManager` — connects/disconnects all signals
- `PreviewManager` — canvas and preview rendering
- `ExportManager` — orchestrates export pipelines
- `InputManager` — validates and reads user inputs

---

## 📁 Directory Structure

```
gui/
├── tasks/          # QgsTask subclasses for background processing
├── tools/          # Interactive map tools (QgsMapTool subclasses)
├── ui/
│   ├── pages/      # Individual dialog pages / tabs
│   └── widgets/    # Reusable custom widgets
└── services/       # GUI-specific orchestration services
```

---

## ⛔ Stop Conditions for GUI Work

| Condition | Action |
|---|---|
| A GUI class imports from `core/` AND from `qgis.gui` and tries to mix both | Stop. Separate into an Extractor class and a Presenter class. |
| A `QgsTask.run()` method references `iface` or any Qt widget | Stop. Move all display logic to `QgsTask.finished()`. |
| A dialog class exceeds 300 lines | Stop. Extract into Manager classes before adding more features. |
| A signal is connected but has no corresponding `disconnect_signals()` | Stop. Add explicit disconnection before continuing. |

---

## 🔗 Skills to Load for GUI Work

| Task | Skill |
|---|---|
| Widget creation | [ui-framework](../../.agent/skills/ui-framework/SKILL.md) |
| QGIS API usage | [qgis-core](../../.agent/skills/qgis-core/SKILL.md) |
| Background tasks | [qgis-core](../../.agent/skills/qgis-core/SKILL.md) |
| Writing GUI tests | [qa-docker](../../.agent/skills/qa-docker/SKILL.md) |
| i18n in UI strings | [i18n-standards](../../.agent/skills/i18n-standards/SKILL.md) |

---

*Antigravity Framework — Gen 5 | Nested AGENTS.md for `gui/`*
