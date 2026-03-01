# Análisis de Código - SecInterp Plugin QGIS

**Fecha de análisis:** 28 de febrero 2026
**Alcance:** Revisión exhaustiva de código completo del plugin
**Propósito:** Identificar errores, redundancias y áreas de mejora

---

## Resumen Ejecutivo

Plugin QGIS para interpretación de secciones geológicas con arquitectura basada en managers, controllers y servicios. El código presenta buena separación de responsabilidades pero suffers de duplicación significativa y algunos bugs críticos de flujo.

---

## 1. ERRORES CRÍTICOS

### 1.1 Bug: `first_start` Inicializado Incorrectamente

**Ubicación:** `sec_interp_plugin.py:102, 114`

```python
# Línea 102
self.first_start = True

# Línea 114 - OVERRIDE!
self.first_start = None
```

**Impacto:** La verificación en línea 231 (`if self.first_start:`) nunca será `True` porque siempre será `None`.

**Fix:** Eliminar línea 114 o corregir la lógica de inicialización.

---

### 1.2 Validación Duplicada en Múltiples Capas

**Capas afectadas:**
- `core/domain/dtos.py:95-161` - `PreviewParams.validate()`
- `core/validation/project_validator.py:60-87` - `ProjectValidator.validate_all()`
- `gui/dialog_input_manager.py:157-164` - `InputManager.validate_inputs()`

**Problema:** La misma validación se ejecuta 2-3 veces en flujos típicos:
1. Preview genera → `PreviewParams.validate()`
2. Aceptar diálogo → `InputManager.validate_inputs()` → `ProjectValidator.validate_all()`

**Fix sugerido:** Unificar en un solo punto de validación con паттерн Strategy.

---

### 1.3 Estado de Caché Inconsistente

**Ubicación:** `gui/dialog_preview_manager.py:164-173`

```python
def _update_cache_and_metrics(self, result: PreviewResult) -> None:
    self.cached_data.update({
        "topo": result.topo,
        "struct": result.struct,
    })
    # FALTA: geol y drillhole que se actualizan async
```

**Problema:** `geol` y `drillhole` se actualizan en callbacks asíncronos pero el cache local puede quedar desincronizado con el controller.

---

### 1.4 Imports en Posiciones Inconsistentes

**Ubicación:** `gui/main_dialog.py:31-43`

```python
from .legend_widget import LegendWidget  # import en medio

logger = get_logger(__name__)           # uso de logger

from .dialog_export_manager import ExportManager  # import después
```

**Fix:** Consolidar todos los imports al inicio del archivo.

---

## 2. REDUNDANCIAS IDENTIFICADAS

### 2.1 Obtención de Capas (resolve_layer)

| Archivo | Líneas | Código |
|---------|--------|--------|
| `core/controller.py` | 228-229 | `resolve_layer(params.line_layer)` |
| `core/services/preview_service.py` | 121-122 | Duplicado |
| `core/services/preview_service.py` | 192-194 | Duplicado |
| `gui/dialog_preview_manager.py` | 125, 190 | Duplicado |

**Fix sugerido:** Crear `LayerResolver` centralizado con caché.

---

### 2.2 Múltiples Definiciones de Configuración

| Componente | Archivo |
|------------|---------|
| `ConfigService` | `core/config.py` |
| `PluginSettings` | `core/models/settings_model.py` |
| `DialogSettingsPersistence` | `gui/dialog_settings_persistence.py` |

**Fix sugerido:** Consolidar en una sola clase de configuración.

---

### 2.3 Métodos Similares para Obtener Valores

**Ubicación:** `gui/dialog_input_manager.py`

```python
# Líneas 70-114
def get_all_values(self) -> dict[str, Any]:
    # Obtiene datos de pages

# Líneas 116-153
def get_validation_params(self) -> ValidationParams:
    # Obtiene LOS MISMOS datos de pages pero en otro formato
```

**Fix sugerido:** Unificar en un solo método con mapper.

---

### 2.4 Cálculo de LOD Repetido

| Ubicación | Líneas |
|-----------|--------|
| `gui/lod_calculator.py` | Clase completa |
| `core/services/preview_service.py` | 64-94 |
| `gui/dialog_preview_manager.py` | 227-231 |

---

### 2.5 Hash de Parámetros

| Ubicación | Líneas |
|-----------|--------|
| `core/data_cache.py` | 50-70 |
| `gui/preview_param_hasher.py` | Módulo completo |

---

## 3. PROBLEMAS DE ARQUITECTURA

### 3.1 Acoplamiento Controller-Servicios

**Ubicación:** `core/controller.py:31-96`

El ProfileController carga ~10 servicios con `SafeLoader.lazy_load()`. Si un servicio falla, puede afectar todo el flujo.

**Recomendación:** Implementar Circuit Breaker pattern para manejo de errores de servicios.

---

### 3.2 Gestión de Estado Distribuida

**Managers con estado:**
- `dialog_state_manager.py` - UI state
- `dialog_input_manager.py` - Input state
- `dialog_signal_manager.py` - Signal state
- `dialog_preview_manager.py` - Preview state
- `controller` - Cache state

**Problema:** Comunicación dispersa entre managers.

**Recomendación:** Implementar Event Bus o Pub/Sub centralizado.

---

### 3.3 Type Hints Inconsistentes

```python
# Malo
controller: Any

# Bueno
controller: ProfileController
```

**Archivos con `Any` excesivo:**
- `core/services/preview_service.py:34`
- `gui/dialog_preview_manager.py:51`
- Múltiples signatures en managers

---

## 4. ISSUES DE PERFORMANCE

### 4.1 Import Dentro de Método

**Ubicación:** `core/controller.py:205`

```python
def _get_cache_sub_key(self, param_values: list[Any]) -> str:
    import hashlib  # COSTOSO - se ejecuta en cada llamada
```

**Fix:** Mover import al nivel del módulo.

---

### 4.2 Debounce Timer Inicializado Dos Veces

**Ubicación:** `dialog_preview_manager.py:314-322`

```python
def _on_extents_changed(self) -> None:
    self.debounce_timer.start(DialogConfig.ZOOM_DEBOUNCE_MS)
    # ...
    self.debounce_timer.start(200)  # Sobreescribe el anterior!
```

---

### 4.3 Validación en Pipeline Sin Short-Circuit

**Ubicación:** `validation/pipeline.py`

Cada validator crea nuevos contextos en lugar de short-circuit en primer error.

---

## 5. MANEJO DE ERRORES

### 5.1 Excepciones No Capturadas

**Ubicación:** `sec_interp_plugin.py:297-302`

```python
except SecInterpError as e:
    # maneja
except (ValueError, TypeError, KeyError, AttributeError) as e:
    # maneja
# Faltan: KeyboardInterrupt, MemoryError, SystemError
```

---

### 5.2 Null Checks Inconsistentes

```python
# Forma correcta
if hasattr(self, "dlg") and self.dlg:

# Forma arriesgada
if self.dlg:  # Puede lanzar AttributeError
```

---

## 6. CODE SMELLS

### 6.1 Comentario Engañoso

**Ubicación:** `sec_interp_plugin.py:33`

```python
# DataCache has been moved to core/data_cache.py
```

Comentario sin propósito aparente.

---

### 6.2 Magic Numbers

- `dialog_preview_manager.py:316` - `DialogConfig.ZOOM_DEBOUNCE_MS` (bien)
- Otros valores hardcodeados sin constantes

---

### 6.3 Método con Nombre Incorrecto

**Ubicación:** `gui/main_dialog.py:31-43`

Clase `_NoOpMessageBar` con leading underscore pero usada como implementación real.

---

## 7. RECOMENDACIONES DE REFACTORIZACIÓN

### Prioridad Alta

1. **Corregir bug `first_start`** - Eliminar línea 114 en `sec_interp_plugin.py`

2. **Unificar validación** - Eliminar duplicación entre PreviewParams, ProjectValidator, InputManager

3. **Centralizar resolución de capas** - Crear `LayerResolver` service

4. **Consolidar configuración** - Unificar ConfigService, PluginSettings, DialogSettingsPersistence

### Prioridad Media

5. **Mejorar type hints** - Reemplazar `Any` con tipos específicos

6. **Event Bus** - Implementar pub/sub para comunicación entre managers

7. **Mover imports** - Consolidar al inicio de cada archivo

8. **Circuit Breaker** - Para manejo de errores de servicios

### Prioridad Baja

9. **Tests** - La arquitectura actual dificulta testing; considerar inyección de dependencias

10. **Documentación** - Agregar docstrings faltantes en managers

---

## 8. ESTRUCTURA ACTUAL

```
sec_interp/
├── core/
│   ├── controller.py          # Orchestrator principal
│   ├── config.py              # Configuración
│   ├── data_cache.py          # Caché
│   ├── domain/                # DTOs y entidades
│   ├── services/              # Servicios de negocio
│   │   ├── drillhole/
│   │   ├── geology/
│   │   └── ...
│   └── validation/            # Pipelines de validación
├── gui/
│   ├── main_dialog.py         # Dialog principal
│   ├── dialog_*.py            # Managers (~8)
│   ├── renderers/             # Renderers
│   ├── tools/                 # Herramientas (measure, interpretation)
│   ├── ui/pages/              # Páginas del UI
│   └── tasks/                 # Tareas asíncronas
├── exporters/                 # Exportadores (PDF, SVG, etc.)
└── sec_interp_plugin.py       # Entry point
```

---

## 9. MÉTRICAS

| Métrica | Valor |
|---------|-------|
| Archivos Python | ~60 |
| Líneas de código | ~15,000 |
| Managers | 8 |
| Servicios | 15+ |
| Patrones | Manager, Service, Factory, Pipeline, Observer |
| Complejidad | Media-Alta |

---

## 10. PRÓXIMOS PASOS SUGERIDOS

1. Crear issue para bug `first_start`
2. Planificar refactor de validación (impacto medio)
3. Implementar `LayerResolver` service
4. Agregar type hints faltantes
5. Implementar Event Bus para comunicación

---

*Documento generado automáticamente - Revisión manual de código*
