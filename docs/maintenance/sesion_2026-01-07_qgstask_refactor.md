# Walkthrough - Native QgsTask Refactor

## Objetivo
Resolver crashes intermitentes causados por el acceso inseguro a capas de QGIS desde hilos secundarios, migrando a una arquitectura 100% nativa de QGIS.

## Cambios Realizados

### 1. Data Transfer Object (DTO)
Se introdujo `GeologyTaskInput` en `core/types.py` para encapsular todos los datos necesarios para el procesamiento geológico en estructuras de memoria puras (sin dependencias a `QgsVectorLayer`).

### 2. Refactorización GeologyService
Se dividió la lógica en dos métodos claros en `core/services/geology_service.py`:
*   `prepare_task_input(...)`: Ejecuta consultas a la API de QGIS (Spatial Index, lecturas de atributos) **síncronamente** en el hilo principal y devuelve un DTO.
*   `process_task_data(...)`: Recibe el DTO y ejecuta la matemática geométrica pura. Este método es 100% thread-safe.

### 3. Implementación QgsTask
Se creó `gui/tasks/geology_task.py` conteniendo `GeologyGenerationTask`, una subclase de `QgsTask` que:
*   Maneja la ejecución en background.
*   Reporta logs de forma segura usando `QgsMessageLog`.
*   Permite cancelación graciosa.

### 4. Integración GUI
Se actualizó `gui/main_dialog_preview.py` para usar `QgsApplication.taskManager()`.
*   Eliminado: `ParallelGeologyService` (Legacy custom thread).
*   Implementado: Flujo de preparación sincrona -> Ejecución asíncrona gestionada por QGIS.

## Validación
*   **Unit Tests**: Se creó `tests/gui/test_geology_task.py` validando el ciclo de vida de la tarea y el manejo de errores.
*   **Thread Safety**: El diseño garantiza por construcción que no hay acceso concurrente a la API de QGIS.

## Resultado
El plugin ahora utiliza el mecanismo estándar de QGIS para tareas pesadas, eliminando la causa raíz de los crashes y mejorando la estabilidad a largo plazo.
