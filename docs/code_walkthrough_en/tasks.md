---
tags:
  - secinterp
  - code-walkthrough
  - gui
  - qgstask
aliases:
  - gui/tasks
  - PreviewTaskOrchestrator
cssclass: secinterp-note
---

# 24 — `gui/tasks/` + `preview_task_orchestrator.py`

> [!abstract] One-line summary
> Runs geology and drillholes in the **background** with `QgsTask` (detached data + deferred signals).

**Path**: `gui/tasks/` (2 tasks) + `gui/preview_task_orchestrator.py` (158 l.)
**Classes**: `GeologyGenerationTask`, `DrillholeGenerationTask`, `PreviewTaskOrchestrator`
**Layer**: GUI · Tasks
**Tags**: #secinterp #gui #qgstask

---

## 🎯 Why does this package exist?

Geology/drillhole generation can take seconds. Rules:

| Rule | Solution |
|------|----------|
| Never block the UI | `QgsTask` in `QgsTaskManager` |
| Never pass `QgsVectorLayer` to `QgsTask` | Detached DTOs (`GeologyContext`, `DrillholeContext`) |
| Don't crash from GC in QGIS 4/Qt6 | Anchoring in `_active_tasks` |
| Don't emit signals from the worker thread | `QTimer.singleShot(0, ...)` |

---

## 🧱 `GeologyGenerationTask`

```python
class GeologyGenerationTask(QgsTask):
    finished_with_results = pyqtSignal(object)
    error_occurred = pyqtSignal(str)
    def run(self) -> bool:   # worker thread
        self.result = self.service.build_segments(self.context, feedback=self)
        return True
    def finished(self, is_successful: bool):   # main thread
        QTimer.singleShot(0, lambda: self.finished_with_results.emit(self.result))
```

| Method | Thread | What it does |
|--------|--------|--------------|
| `run()` | worker | Calls `GeologyService.build_segments` |
| `finished()` | main | Emits result if successful |

> [!important] `feedback=self`
> The task itself implements `isCanceled()`/`setProgress()`.

## 🧱 `PreviewTaskOrchestrator`

```python
class PreviewTaskOrchestrator:
    def start_geology_task(self, params, service):
        ctx = GeologyExtractor(...).extract_context(...)
        self.geology_task = GeologyGenerationTask(..., ctx, service, params)
        self._active_tasks.append(self.geology_task)
        self.geology_task.finished_with_results.connect(manager._on_geology_finished)
        QgsApplication.taskManager().addTask(self.geology_task)
    def cancel_active_tasks(self): ...  # cancel + disconnect + clear anchors
```

| Method | Role |
|--------|------|
| `start_geology/drillhole_task` | Build context (Extract) + task + signals + enqueue |
| `cancel_active_tasks` | Cancel and disconnect, clear anchors |
| `remove_task` | Remove finished task from `_active_tasks` |

> [!tip] Anchoring
> Keeps references in `_active_tasks` to prevent Python/QGIS from GC'ing the `QgsTask` early (Qt6 segfaults).

---

## 🏛️ Patterns

| Pattern | Where |
|---------|-------|
| **Worker / Background Task** | `QgsTask` |
| **Anchor / Retention** | `_active_tasks` |
| **Deferred signal** | `QTimer.singleShot` |

---

## 🔗 Related notes

- [[controller]] — pure core consumed by tasks
- [[domain]] — context DTOs
- [[dialog_preview_manager]] — orchestrated by the manager

---

*Note 24 of the SecInterp Code Walkthrough vault — v3.8.0*
