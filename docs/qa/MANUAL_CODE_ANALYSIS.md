# 🕵️ Análisis Manual del Repositorio SecInterp

He realizado una revisión manual de la arquitectura, estructura de carpetas y los archivos clave del repositorio (principalmente en `/core` y `/gui`). A continuación te presento los hallazgos relacionados con código redundante, "code smells", "spaghetti code" y recomendaciones de mejora.

> [!WARNING]
> He detectado una violación **crítica** a los principios arquitectónicos definidos en tu `AGENTS.md` respecto a la separación estricta entre **Core y GUI**.

---

## 1. 🍝 Spaghetti Code y "God Objects" (Capa GUI)

El archivo [`gui/main_dialog.py`](file:///home/jmbernales/qgispluginsdev/sec_interp/gui/main_dialog.py) sufre del anti-patrón **"God Object"** (Objeto Dios).

*   **Problema:** Aunque la lógica parece haberse extraído a múltiples manejadores (`InputManager`, `PreviewManager`, `ExportManager`, `StateManager`, `InterpretationManager`, `ToolManager`, etc.), `SecInterpDialog` los inicializa y mantiene referencias a todos ellos.
*   **Acoplamiento Fuerte:** Se pasa la instancia completa del diálogo (`self`) a cada manejador (ej. `self.input_manager = InputManager(self)`). Esto significa que cada manejador tiene acceso irrestricto y depende de toda la vista principal, lo que crea un acoplamiento circular masivo. Modificar un componente de la UI probablemente rompa pruebas o la lógica en estos manejadores.

## 2. 👃 Code Smells y Violaciones de Arquitectura (Capa Core)

Tu documento `AGENTS.md` especifica claramente el patrón **Extract-then-Compute**:
> *"NEVER do this in `/core`: Direct QGIS dependencies in core... Processes using QGIS-agnostic types (WKT, dicts, primitives)"*

Sin embargo, el análisis revela que la capa `/core` está **altamente acoplada a QGIS**.

*   **Importaciones de `qgis.core` generalizadas:** Se encontraron docenas de importaciones directas de QGIS en `/core` (`QgsVectorLayer`, `QgsRasterLayer`, `QgsFeature`, `QgsProject`). Por ejemplo, en [`core/utils/spatial.py`](file:///home/jmbernales/qgispluginsdev/sec_interp/core/utils/spatial.py) y en validadores.
*   **[`core/controller.py`](file:///home/jmbernales/qgispluginsdev/sec_interp/core/controller.py):** El método `connect_layer_notifications` recibe objetos `QgsMapLayer` y se conecta directamente a sus señales Qt (`layer.dataChanged.connect(callback)`). Esto acopla la lógica de negocio puramente a eventos de la interfaz gráfica y del mapa de QGIS.
*   **[`core/services/drillhole/data_fetcher.py`](file:///home/jmbernales/qgispluginsdev/sec_interp/core/services/drillhole/data_fetcher.py):** Extrae características directamente usando `QgsFeatureRequest` sobre un `QgsVectorLayer`. Esto rompe el principio de que el Core solo procesa, no extrae de QGIS.

## 3. ♻️ Código Redundante / Sobreingeniería

*   **Generación de Previsualización:** El proceso de preview involucra a [`dialog_preview_manager.py`](file:///home/jmbernales/qgispluginsdev/sec_interp/gui/dialog_preview_manager.py) (~500 líneas), un `PreviewTaskOrchestrator`, un `PreviewLayerFactory`, y múltiples "Renderers" individuales (`TopoRenderer`, `GeologyRenderer`, etc.).
*   **Problema:** Aunque el patrón "Factory + Strategy (Renderers)" es teóricamente correcto, la complejidad de mantener el estado, hacer "debouncing" del zoom y sincronizar la UI se ha vuelto enorme. Hay una mezcla de responsabilidades donde el `PreviewManager` calcula LODs (Level of Detail), maneja "hashes" para cache, maneja UI, y orquesta tareas en segundo plano. Esto lo hace redundante y muy difícil de mantener.

---

## 💡 Recomendaciones de Mejora

### 1. Aplicar el patrón DTO (Data Transfer Object) Realmente
Para solucionar la violación arquitectónica de `/core`:
*   Crea una capa `data_access` o mantenlo estrictamente en `/gui/services/`.
*   Extrae los datos de `QgsVectorLayer` (geometrías a WKT, atributos a diccionarios) **antes** de llamar a cualquier método de `/core`.
*   Las clases en `/core` no deben importar nada de `qgis.core` ni `qgis.gui`. Solo deben aceptar y devolver clases de datos estándar (`DataClasses`) o tipos primitivos.

### 2. Desacoplar la UI usando un "Event Bus" o Patrón Observador
Para solucionar el God Object en `main_dialog.py`:
*   En lugar de pasar `self` (el diálogo) a cada manejador, inyecta solo las dependencias específicas (ej. solo el componente de configuración a `StateManager`).
*   Usa un sistema de señales (Event Bus de Qt) interno para que los componentes se comuniquen. Por ejemplo, en lugar de que `InputManager` llame directamente a métodos del `PreviewManager`, `InputManager` debería emitir una señal `inputs_changed`, y `PreviewManager` se suscribe a ella independientemente.

### 3. Extraer el Manejo de Eventos Qt del Core
*   Mueve la lógica `connect_layer_notifications` de `core/controller.py` hacia un coordinador en la carpeta `/gui`.
*   La lógica de invalidar caché (ej. `self.data_cache.invalidate()`) sí debe estar en el Core, pero debe ser invocada manualmente desde la capa GUI mediante llamadas a métodos cuando la GUI detecte un cambio en QGIS, evitando que el Core se suscriba a eventos de QGIS.

### 4. Simplificar la Gestión de Estado (State Management)
*   El estado actual de la UI parece muy fragmentado (dividido entre managers). Considera centralizar el estado (capas seleccionadas, progreso de tareas, parámetros) en un único objeto de estado "inmutable". La interfaz de usuario (`main_dialog.py` y sus widgets) simplemente debería "reaccionar" (Redux-like) a los cambios en este objeto central.
