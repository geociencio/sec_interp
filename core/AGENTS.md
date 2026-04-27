# Core Layer — Agent Instructions

> **Scope**: All Python modules under `sec_interp/core/`.
> This file takes precedence over the root `AGENTS.md` for work done in this directory.
> **Reference**: [Root AGENTS.md](../../.agent/AGENTS.md) | [coding-standards](../../.agent/skills/coding-standards/SKILL.md)

---

## ⚠️ Absolute Constraints (NEVER violate)

```
❌  from qgis.core import *          → FORBIDDEN in /core
❌  from qgis.gui import *           → FORBIDDEN in /core
❌  QgsProject.instance()            → FORBIDDEN in /core
❌  iface.mapCanvas()                → FORBIDDEN in /core
❌  import PyQt5 / PyQt6             → FORBIDDEN in /core (use standard library only)
```

The `core/` layer must be **100% QGIS-agnostic** and **100% thread-safe**.
It must be testable with `uv run pytest tests/core/` — no QGIS installation required.

---

## ✅ Required Patterns

### Extract-then-Compute (mandatory)
All data entering `core/` from the GUI must arrive as primitive types or DTOs:

```python
# ✅ CORRECT — receives WKT, returns DTO
def process_geology(geometry_wkt: str, attributes: dict) -> GeologySegment:
    ...

# ❌ FORBIDDEN — direct QGIS dependency
def process_geology(layer: QgsVectorLayer) -> GeologySegment:
    ...
```

### Type Annotations (mandatory on all public functions)
```python
from __future__ import annotations
from typing import Optional

def calculate_intersection(
    line_wkt: str,
    polygon_wkt: str,
    tolerance: float = 0.001,
) -> Optional[GeologySegment]:
```

### Error Handling
- Use the custom exception hierarchy: `SecInterpError → ValidationError / ProcessingError`
- Never swallow exceptions silently
- Always log before re-raising

---

## 📁 Directory Structure

```
core/
├── services/       # Business logic orchestrators (one service per domain)
├── utils/          # Pure utility functions (no state)
├── types.py        # Domain DTOs and type aliases
├── exceptions.py   # Custom exception hierarchy
├── interfaces/     # ABCs / service contracts
└── validation/     # Input validation (QGIS-agnostic)
```

---

## ⛔ Stop Conditions for Core Work

| Condition | Action |
|---|---|
| A core function needs a `QgsGeometry` parameter | Stop. Use WKT string instead. Escalate if WKT is insufficient. |
| A new `core/service` needs to emit a Qt signal | Stop. Signals belong in `gui/tasks/`. Redesign using callback or DTO return. |
| Cyclomatic complexity > 10 on any function | Stop. Decompose into `_stepN_` private methods before proceeding. |
| A unit test in `tests/core/` requires QGIS to be installed | Stop. The test is misplaced or the implementation violates the layer boundary. |

---

## 🔗 Skills to Load for Core Work

| Task | Skill |
|---|---|
| Writing algorithms | [coding-standards](../../.agent/skills/coding-standards/SKILL.md) |
| Geological logic | [geological-logic](../../.agent/skills/geological-logic/SKILL.md) |
| Writing tests | [qa-docker](../../.agent/skills/qa-docker/SKILL.md) |
| QGIS API gotchas | [qgis-core](../../.agent/skills/qgis-core/SKILL.md) |

---

*Antigravity Framework — Gen 5 | Nested AGENTS.md for `core/`*
