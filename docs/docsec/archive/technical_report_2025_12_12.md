# Informe Técnico: Refactorización de Rendimiento y Procesamiento Paralelo

**Fecha:** 12 de Diciembre, 2025
**Proyecto:** SecInterp QGIS Plugin
**Versión de Cambios:** `feat/parallel-processing`

## 1. Resumen Ejecutivo

Este documento detalla las mejoras técnicas implementadas en el plugin SecInterp con el objetivo de optimizar la experiencia de usuario durante la generación de perfiles geológicos complejos. Se han introducido dos subsistemas principales: un **Monitor de Rendimiento** para diagnóstico y un **Servicio de Procesamiento Paralelo Asíncrono** para evitar el bloqueo de la interfaz gráfica de QGIS.

## 2. Sistema de Monitoreo de Rendimiento

Se implementó un sistema ligero para medir y registrar métricas de ejecución.

### 2.1 Componentes (`core/performance_metrics.py`)
- **Clase `PerformanceMonitor`**: Utiliza `time.perf_counter()` para precisión en microsegundos y el módulo `tracemalloc` para rastrear el uso de memoria RAM.
- **Decorador `@performance_monitor`**: Permite instrumentar cualquier función o método con una sola línea de código, generando logs automáticos en `performance.log`.

### 2.2 Aplicación
Se aplicó el monitoreo al método crítico `GeologyService.generate_geological_profile` en `core/services/geology_service.py`, proporcionando visibilidad inmediata sobre cuellos de botella en operaciones de intersección espacial.

## 3. Servicio de Procesamiento Paralelo

Se desarrolló una arquitectura basada en `QThread` para descargar tareas pesadas del hilo principal (GUI Thread).

### 3.1 Arquitectura (`core/services/parallel_geology.py`)
- **`ParallelGeologyService`**: Clase orquestadora que gestiona un pool de hilos.
  - Hereda de `QObject` para integración completa con el sistema de señales de Qt.
  - Implementa lógica de "Chunking" para dividir listas de tareas entre los núcleos disponibles (máx. 8 para estabilidad).
  - Gestiona el ciclo de vida de los hilos, emitiendo una señal `all_finished` solo cuando todas las subtareas han concluido.

- **`GeologyProcessingThread`**: Clase trabajadora (`worker`) que hereda de `QThread`.
  - Recibe un lote (`chunk`) de datos y una función de procesamiento.
  - Emite señales de progreso (`progress_updated`) y finalización (`processing_finished`).
  - Captura excepciones para evitar caídas silenciosas de hilos (`error_occurred`).

### 3.2 Patrón de Diseño "Command"
Para maximizar la flexibilidad y reutilización, se implementó el Patrón Comando en el método de procesamiento:
- El servicio acepta tuplas en el formato `(Callable, *args)`.
- El método interno `_process_profile_chunk` detecta automáticamente estas tuplas y ejecuta la función contenida con sus argumentos.
- **Beneficio**: Permite ejecutar cualquier método de cualquier servicio existente sin escribir clases `worker` específicas para cada caso.

## 4. Integración en Interfaz Gráfica (`GUI`)

La integración se realizó en `gui/main_dialog_preview.py` dentro de la clase `PreviewManager`.

### 4.1 Flujo Asíncrono
Se replanteó el método `generate_preview` para soportar una ejecución mixta (Síncrona/Asíncrona):
1. **Fase Síncrona**: Generación inmediata de Topografía y Estructuras (procesos rápidos).
2. **Fase Asíncrona**: Si se requiere Geología, se delega al `ParallelGeologyService` y se devuelve el control a la UI inmediatamente.
3. **Callback (`_on_geology_finished`)**: Al finalizar el cálculo en segundo plano:
   - Se recolectan y aplanan los resultados.
   - Se actualiza la caché local.
   - Se dispara una actualización del Canvas para mostrar las nuevas capas geológicas.

## 5. Correcciones Críticas

Durante la implementación se resolvieron dos desafíos técnicos importantes:
1. **Acumulación de Resultados**: Se corrigió un error en el bucle del hilo donde los valores de retorno de la función procesadora eran ignorados. Ahora se acumulan en una lista.
2. **Aplanamiento de Datos**: Debido a la arquitectura de "Chunks", los resultados llegaban con triple anidamiento (`Result -> Chunks -> Items -> Data`). Se implementó una lógica robusta en `_on_geology_finished` para aplanar esta estructura correctamente antes de enviarla al renderizador.

## 6. Conclusión

La refactorización ha transformado la generación de perfiles de un proceso bloqueante y monolítico a uno responsivo y modular. La infraestructura creada permite escalar fácilmente a futuras funcionalidades, como la exportación masiva de perfiles, utilizando el mismo patrón de servicio paralelo.
