# Recomendaciones para Eliminación Progresiva de Facades

**Fecha:** 15 de Febrero de 2026
**Propósito:** Reducir la complejidad de SecInterpDialog eliminando facades innecesarios

---

## Resumen Ejecutivo

El diálogo principal (`SecInterpDialog`) actualmente tiene **12 managers** que actúan como facades, creando una cadena de indirección innecesaria. Este documento propone una eliminación progresiva para lograr código más directo y mantenible.

**Estado actual:** 12 managers
**Estado objetivo:** 6 managers
**Reducción:** 50%

---

## 1. Análisis de Facades Actuales

### Lista completa de managers en `SecInterpDialog`:

| # | Manager | Líneas aprox. | Propósito |
|---|---------|---------------|-----------|
| 1 | `MessageManager` | ~50 | Mensajes UI |
| 2 | `ValidationManager` | ~80 | Validación de inputs |
| 3 | `PreviewManager` | ~400 | Generación preview |
| 4 | `ExportManager` | ~150 | Exportación |
| 5 | `CacheHandler` | ~40 | Limpieza de cache |
| 6 | `DataAggregator` | ~100 | Agregar datos de páginas |
| 7 | `SettingsManager` | ~120 | Persistencia settings |
| 8 | `StatusManager` | ~60 | Indicadores UI |
| 9 | `InterpretationManager` | ~200 | Gestión interpretaciones |
| 10 | `ToolManager` | ~150 | Herramientas QGIS |
| 11 | `NavigationManager` | ~80 | Zoom/Pan canvas |
| 12 | `LayerFactory` | ~100 | Creación de layers |

### Clasificación:

| Tipo | Managers |
|------|---------|
| **NECESARIOS** (lógica compleja) | PreviewManager, ExportManager, InterpretationManager, ToolManager, LayerFactory |
| **FUSIONABLES** (relacionados) | StatusManager + SettingsManager, DataAggregator + ValidationManager, ToolManager + NavigationManager |
| **ELIMINABLES** (thin wrappers) | MessageManager, CacheHandler |

---

## 2. Fase 1: Eliminar Facades Inmediatamente (Bajo Riesgo)

Estos managers son wrappers puros sin lógica - eliminar directamente.

### 2.1 MessageManager

**Ubicación:** `gui/main_dialog_messages.py`

```python
# ANTES - facade innecesario
class MessageManager:
    def __init__(self, dialog):
        self.dialog = dialog

    def show_error(self, msg):
        self.dialog.messagebar.pushMessage(msg, Qgis.Critical)

    def show_warning(self, msg):
        self.dialog.messagebar.pushMessage(msg, Qgis.Warning)

# DESPUÉS - método directo en SecInterpDialog
class SecInterpDialog:
    def _show_message(self, msg: str, level: Qgis.MessageLevel = Qgis.Warning):
        """Show message in message bar."""
        self.messagebar.pushMessage(msg, level)

    def show_error(self, msg: str):
        self._show_message(msg, Qgis.Critical)

    def show_warning(self, msg: str):
        self._show_message(msg, Qgis.Warning)
```

### 2.2 CacheHandler

**Ubicación:** `gui/main_dialog_cache_handler.py`

```python
# ANTES
class CacheHandler:
    def __init__(self, dialog):
        self.dialog = dialog

    def clear_cache_handler(self):
        self.dialog.data_cache.clear()
        self.dialog.preview_manager.clear_cache()

# DESPUÉS - atributo directo
class SecInterpDialog:
    def __init__(self, ...):
        self.data_cache = DataCache()  # Directo
        ...

    def clear_cache_handler(self):
        self.data_cache.clear()
        self.preview_manager.clear_cache()
```

### 2.3 DialogEntityManager

**Ubicación:** `gui/main_dialog_utils.py` (parte)

```python
# ANTES
class DialogEntityManager:
    def __init__(self, dialog):
        self.dialog = dialog

    def get_selected_layers(self):
        return self.dialog.layer_factory.get_layers()

# DESPUÉS - eliminar clase, usar directamente
# Donde antes: self.entity_manager.get_selected_layers()
# Ahora: self.layer_factory.get_layers()
```

---

## 3. Fase 2: Fusionar Managers Relacionados (Riesgo Medio)

Managers que comparten dominio pueden fusionarse en uno solo.

### 3.1 StatusManager + SettingsManager → DialogStateManager

**Ubicación:** `gui/main_dialog_status.py` + `gui/main_dialog_settings.py`

```python
# NUEVO ARCHIVO: gui/dialog_state_manager.py
from __future__ import annotations
from typing import Any

class DialogStateManager:
    """Maneja settings Y estado UI de forma unificada."""

    def __init__(self, dialog: Any) -> None:
        self.dialog = dialog
        self._settings = {}

    # --- Settings Methods (antes en SettingsManager) ---
    def load_settings(self) -> None:
        """Cargar settings desde QSettings."""
        from qgis.PyQt.QtCore import QSettings
        qset = QSettings()
        # Cargar settings...
        self._settings = {...}

    def save_settings(self) -> None:
        """Guardar settings en QSettings."""
        from qgis.PyQt.QtCore import QSettings
        qset = QSettings()
        # Guardar settings...

    # --- Status Methods (antes en StatusManager) ---
    def setup_indicators(self) -> None:
        """Configurar indicadores visuales."""
        # Configurar status indicators...
        pass

    def update_all(self) -> None:
        """Actualizar todos los indicadores."""
        self._update_status_indicators()

    def _update_status_indicators(self) -> None:
        """Actualizar estado de indicadores."""
        pass
```

### 3.2 DataAggregator + ValidationManager → InputManager

**Ubicación:** `gui/main_dialog_data.py` + `gui/main_dialog_validation_manager.py`

```python
# NUEVO ARCHIVO: gui/input_manager.py
from __future__ import annotations
from typing import Any

class InputManager:
    """Maneja recolección y validación de datos de entrada."""

    def __init__(self, dialog: Any) -> None:
        self.dialog = dialog

    # --- Collection Methods (antes en DataAggregator) ---
    def collect_all_page_data(self) -> dict[str, Any]:
        """Recolectar datos de todas las páginas."""
        data = {}
        data.update(self._get_section_data())
        data.update(self._get_dem_data())
        data.update(self._get_geology_data())
        return data

    def _get_section_data(self) -> dict:
        return self.dialog.section_page.get_data()

    # --- Validation Methods (antes en ValidationManager) ---
    def validate_all(self) -> tuple[bool, str]:
        """Validar todos los inputs."""
        errors = []
        if not self._validate_section():
            errors.append("Sección inválida")
        if not self._validate_dem():
            errors.append("DEM inválido")

        if errors:
            return False, "; ".join(errors)
        return True, ""

    def _validate_section(self) -> bool:
        return self.dialog.section_page.line_combo.currentLayer() is not None
```

### 3.3 ToolManager + NavigationManager → CanvasToolsManager

**Ubicación:** `gui/main_dialog_tools.py`

```python
# REORGANIZAR: gui/main_dialog_tools.py
class CanvasToolsManager:
    """Maneja herramientas interactivas y navegación del canvas."""

    def __init__(self, dialog: Any) -> None:
        self.dialog = dialog
        self._measure_tool = None
        self._interpretation_tool = None

    # --- Tool Management ---
    def initialize_tools(self) -> None:
        """Inicializar todas las herramientas."""
        self._init_measure_tool()
        self._init_interpretation_tool()

    def toggle_measure_tool(self, checked: bool) -> None:
        """Activar/desactivar herramienta de medición."""
        ...

    def toggle_interpretation_tool(self, checked: bool) -> None:
        """Activar/desactivar herramienta de interpretación."""
        ...

    # --- Navigation (antes en NavigationManager) ---
    def handle_wheel_event(self, event: Any) -> bool:
        """Manejar evento de rueda de mouse."""
        ...

    def zoom_to_extent(self) -> None:
        """Zoom a extensión del preview."""
        ...
```

---

## 4. Fase 3: Simplificar API de Managers Complejos

### 4.1 PreviewManager

El manager más complejo. NO eliminar, pero sí simplificar su API:

```python
# ANTES: Múltiples métodos
class PreviewManager:
    def run_preview(self): ...
    def update_preview(self): ...
    def clear_preview(self): ...
    def refresh_preview(self): ...
    def regenerate_preview(self): ...

# DESPUÉS: API unificada
class PreviewManager:
    def execute(self, force: bool = False) -> None:
        """Ejecutar preview. Detecta automáticamente qué hacer.

        Args:
            force: Si True, ignora cache y regenera.
        """
        if force or self._needs_regeneration():
            self._generate_full()
        else:
            self._update_existing()

    def _needs_regeneration(self) -> bool:
        """Determina si necesita regenerar o actualizar."""
        # Lógica existente...
        pass
```

### 4.2 ExportManager

```python
# ANTES: Múltiples métodos de exportación
class ExportManager:
    def export_to_png(self): ...
    def export_to_pdf(self): ...
    def export_to_svg(self): ...
    def export_to_csv(self): ...

# DESPUÉS: Método genérico
class ExportManager:
    def execute(self, format: str, output_path: str) -> bool:
        """Exportar al formato especificado."""
        exporters = {
            'png': self._export_image,
            'pdf': self._export_pdf,
            'svg': self._export_svg,
            'csv': self._export_csv,
        }
        exporter = exporters.get(format)
        if exporter:
            return exporter(output_path)
        return False
```

---

## 5. Estructura Final Objetivo

### Antes:
```
SecInterpDialog (12 managers)
├── message_manager
├── validation_manager
├── preview_manager
├── export_manager
├── cache_handler
├── data_aggregator
├── settings_manager
├── status_manager
├── interpretation_manager
├── tool_manager
├── navigation_manager
└── layer_factory
```

### Después:
```
SecInterpDialog (6 managers)
├── state_manager          # settings + status
├── input_manager         # data + validation
├── preview_manager       # COMPLEJO - mantener
├── export_manager        # COMPLEJO - mantener
├── interpretation_manager # COMPLEJO - mantener
└── canvas_tools          # tools + navigation
```

**Eliminados:** MessageManager, CacheHandler, EntityManager, NavigationManager
**Fusionados:** StatusManager→state, SettingsManager→state, DataAggregator→input, ValidationManager→input, ToolManager→canvas_tools
**Mantenidos:** PreviewManager, ExportManager, InterpretationManager, LayerFactory

---

## 6. Plan de Ejecución

### Semana 1: Fase 1 (Eliminar thin wrappers)
- [ ] Eliminar MessageManager, convertir a métodos directos
- [ ] Eliminar CacheHandler, usar DataCache directamente
- [ ] Eliminar EntityManager (si existe)

### Semana 2-3: Fase 2 (Fusionar relacionados)
- [ ] Crear DialogStateManager (fusionar status + settings)
- [ ] Crear InputManager (fusionar data + validation)
- [ ] Reorganizar CanvasToolsManager (fusionar tools + navigation)

### Semana 4: Fase 3 (Simplificar APIs)
- [ ] Simplificar PreviewManager.execute()
- [ ] Simplificar ExportManager.execute()
- [ ] Limpiar imports obsoletos

---

## 7. Regla de Decisión para Facades

**Eliminar el facade si:**
- ❌ Solo pasa llamadas a `self.dialog`
- ❌ No tiene estado propio
- ❌ No tiene lógica de negocio (<60 líneas)
- ❌ Métodos son 1:1 con otros objetos

**Mantener el facade si:**
- ✅ Tiene lógica de negocio compleja
- ✅ Gestiona múltiples sub-componentes
- ✅ Coordina flujos de trabajo
- ✅ 150+ líneas con lógica real

---

## 8. Riesgos y Mitigaciones

| Riesgo | Impacto | Mitigación |
|--------|---------|------------|
| Romper funcionalidad existente | Alto | Tests exhaustivos después de cada fase |
| Introducir imports circulares | Medio | Usar TYPE_CHECKING para imports lambat |
| Perder flexibilidad | Bajo | Mantener inyección de dependencias |

---

## 9. Verificación Post-Refactor

После каждой фазы ejecutar:

```bash
# Verificar que el diálogo still works
make test

# Verificar imports
uv run ruff check gui/

# Verificar tipos
uv run mypy gui/main_dialog.py
```

---

*Documento generado: 2026-02-15*
