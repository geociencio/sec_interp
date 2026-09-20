---
tags:
  - secinterp
  - code-walkthrough
  - gui
  - qgstask
  - background
aliases:
  - gui/tasks
  - QgsTask
  - PreviewTaskOrchestrator
cssclass: secinterp-note
---

# 24 — `gui/tasks/` + `preview_task_orchestrator.py`

> [!abstract] Resumen en una línea
> Ejecuta geología y sondajes en **segundo plano** con `QgsTask` (datos desacoplados + señales diferidas).

**Ruta**: `gui/tasks/` (2 tasks) + `gui/preview_task_orchestrator.py` (158 l.)
**Clases**: `GeologyGenerationTask`, `DrillholeGenerationTask`, `PreviewTaskOrchestrator`
**Capa**: GUI · Tasks
**Tags**: #secinterp #gui #qgstask #background

---

## 🎯 ¿Por qué existe este paquete?

La generación de geología/sondajes puede tardar segundos. Las reglas:

| Regla | Solución |
|-------|----------|
| Nunca bloquear la UI | `QgsTask` en `QgsTaskManager` |
| Nunca pasar `QgsVectorLayer` a `QgsTask` | DTOs desacoplados (`GeologyContext`, `DrillholeContext`) |
| No crashear por GC en QGIS 4/Qt6 | Anchoring en `_active_tasks` |
| No emitir señales desde el hilo worker | `QTimer.singleShot(0, ...)` |

---

## 🧱 `GeologyGenerationTask`

```python
class GeologyGenerationTask(QgsTask):
    finished_with_results = pyqtSignal(object)
    error_occurred = pyqtSignal(str)

    def __init__(self, description, context: GeologyContext, service: GeologyService, params):
        super().__init__(description, QgsTask.Flag.CanCancel)
        self.context = context
        self.service = service

    def run(self) -> bool:   # hilo worker
        self.result = self.service.build_segments(self.context, feedback=self)
        return True

    def finished(self, is_successful: bool):   # hilo principal
        if is_successful:
            # deferred emit para evitar señales desde worker
            QTimer.singleShot(0, lambda: self.finished_with_results.emit(self.result))
```

| Método | Hilo | Qué hace |
|--------|------|----------|
| `run()` | worker | Llama `GeologyService.build_segments` con `feedback=self` |
| `finished()` | main | Emite resultado si `is_successful`, loguea si `self.exception` |

> [!important] `feedback=self`
> El propio `QgsTask` implementa `isCanceled()`/`setProgress()`; el servicio lo usa sin saber que es un task.

## 🧱 `DrillholeGenerationTask`

Idéntico patrón con `DrillholeContext` + `DrillholeService.process_context`.

## 🧱 `PreviewTaskOrchestrator`

```python
class PreviewTaskOrchestrator:
    def __init__(self, manager: PreviewManager):
        self.manager = manager
        self.geology_task = None
        self.drillhole_task = None
        self._active_tasks = []   # anchor

    def start_geology_task(self, params, service):
        if self.geology_task: self.geology_task.cancel()
        ctx = GeologyExtractor(...).extract_context(...)
        self.geology_task = GeologyGenerationTask(..., ctx, service, params)
        self._active_tasks.append(self.geology_task)
        self.geology_task.finished_with_results.connect(manager._on_geology_finished)
        QgsApplication.taskManager().addTask(self.geology_task)

    def cancel_active_tasks(self):
        for task in list(self._active_tasks):
            task.cancel()
            task.finished_with_results.disconnect()
        self._active_tasks.clear()
```

| Método | Rol |
|--------|-----|
| `start_geology/drillhole_task` | Construye contexto (Extract) + task + señales + enqueue |
| `cancel_active_tasks` | Cancela y desconecta, limpia anchors |
| `remove_task` | Quita task terminado de `_active_tasks` |

> [!tip] Anchoring
> Mantiene referencias en `self._active_tasks` para evitar que Python/QGIS limpie el `QgsTask` prematuramente (segfaults en Qt6).

---

## 🏛️ Patrones

| Patrón | Dónde |
|--------|-------|
| **Worker / Background Task** | `QgsTask` |
| **Anchor / Retention** | `_active_tasks` |
| **Deferred signal** | `QTimer.singleShot` |

---

## 🔗 Notas relacionadas

- [[10 - controller]] — core puro que consumen los tasks
- [[11 - domain]] — contexts DTOs
- [[21 - dialog_preview_manager]] — orquestado por el manager

---

*Nota 24 de la bóveda SecInterp Code Walkthrough — v3.8.0*
