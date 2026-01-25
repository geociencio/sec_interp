# Análisis de Refactorizaciones - Fase v2.8.0

Este documento detalla las refactorizaciones realizadas desde el cierre de la v2.7.0 (2026-01-18) hasta el hito actual (2026-01-25).

## 1. Core Services: Desacoplamiento y Seguridad de Hilos

### GeologyService
- **Fragmentación granular**: Métodos que antes excedían las 50 líneas fueron descompuestos en utilidades privadas especializadas (`_validate_inputs`, `_extract_outcrop_data`, `_extract_geometries`).
- **Patrón Extract-then-Compute**: Se implementó una separación estricta en `prepare_task_input` (Main Thread, acceso a QGIS) y `process_task_data` (Thread asíncrono, cálculo puro).
- **Inmutabilidad de Datos**: Migración de objetos `QgsGeometry` y atributos dinámicos a estructuras planas de Python (WKT strings y dicts de tipos primitivos) para evitar segfaults en hilos de fondo.

### DrillholeService
- **Modularización Crítica**: Reducción de la complejidad ciclomática en el cálculo de trayectorias e interpolación de intervalos.
- **Centralización de Lógica**: Movido el cálculo de azimut de sección y el mapeo de campos desde el `PreviewManager` al servicio. Esto asegura que la lógica de negocio resida en el Core y no en la UI.

---

## 2. Arquitectura Agnóstica (Core-QGIS Decoupling)

Se ha completado la visión de un "Core Puro":
- Los servicios ya no requieren objetos vivos de la API de QGIS (como `QgsFeature` o `QgsVectorLayer`) para realizar cálculos espaciales pesados.
- El uso de **Well-Known Text (WKT)** como estándar de intercambio de geometrías entre la UI y el Core garantiza la portabilidad y facilita el testing.

---

## 3. Simplificación de la Capa de Interfaz (UI Logic)

- **PreviewManager**: Se eliminaron ~100 líneas de código procedimental que gestionaban la recolección de parámetros. Ahora, el manager actúa como un orquestador simple que llama a los métodos `prepare_task_input` de los servicios.
- **Reactividad Mejorada**: La UI se ha vuelto más ligera al delegar validaciones y preparaciones complejas a la capa de servicios.

---

## 4. Infraestructura de Calidad y Testing

- **Mocks Geométricos**: Se implementó el método `azimuth` en `MockQgsPointXY` y se mejoró `MockQgsFields` para soportar búsqueda de índices por nombre.
- **Aislamiento en Docker**: El entorno de pruebas se optimizó para ejecutar suites en procesos aislados, eliminando por completo la contaminación de mocks entre tests.
- **Cobertura**: Todos los nuevos cambios están cubiertos por tests unitarios y de integración, manteniendo la suite estable en 359 tests exitosos.

---

## 5. Conclusión del Análisis
La Fase v2.8.0 ha transformado el Core de SecInterp de un sistema estrechamente acoplado a la API de QGIS a una arquitectura modular, robusta y preparada para hilos asíncronos. La deuda técnica de "métodos largos" ha sido eliminada casi en su totalidad en los servicios principales.
