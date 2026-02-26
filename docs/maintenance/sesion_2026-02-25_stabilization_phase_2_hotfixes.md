# Sesión Mantenimiento: Hotfixes de Estabilización Fase 2.1 (2026-02-25)

## Resumen Ejecutivo
Sesión de emergencia para corregir regresiones críticas introducidas durante la optimización de la Fase 2. Se resolvieron fallos de inyección de dependencias y errores de acceso por índice que causaban el colapso del plugin al procesar sondajes proyectados.

## Problemas Identificados y Resueltos

### 1. Desajuste de Inyección de Dependencias (TypeError)
- **Síntoma**: `TypeError: 'NoneType' object has no attribute 'prepare_task_input'` en `ProfileController`.
- **Causa**: Discrepancia en el nombre del argumento (`drillhole_service` vs `service`) en la inyección perezosa de `DrillholeTaskOrchestrator`.
- **Solución**: Mapeado el argumento correcto en `ProfileController`. Añadida guarda defensiva en `PreviewTaskOrchestrator`.

### 2. Error de Índice en Sondajes Fuera de Sección (IndexError)
- **Síntoma**: `IndexError: list index out of range` en `TrajectoryEngine`.
- **Causa**: Intento de acceder al primer punto de una trayectoria que resultaba vacía por estar fuera del plano de sección.
- **Solución**: Implementada validación de longitud antes de acceder a `spatial_points[0]`.

### 3. Error de Subscripción en Renderizado (TypeError)
- **Síntoma**: `TypeError: 'DrillholeProjection' object is not subscriptable` en `PreviewLayerFactory`.
- **Causa**: El renderizador esperaba tuplas legacy pero recibió objetos `DrillholeProjection` tras la refactorización parcial.
- **Solución**: Refactorizado `PreviewLayerFactory` para soportar polimorfismo (objetos de dominio y tuplas legacy).

## Verificación Técnica
- **Tests Core**: Suite de 145+ tests verificada (Local).
- **Regresión**: Creado `tests/core/services/test_drillhole_engine_crash.py` para validar el fix de sondajes vacíos.
- **QA UI**: Validación visual del renderizado de sondajes en el Preview.

## Impacto en Arquitectura
- El sistema es ahora más resiliente a datos inconsistentes o asincrónicos.
- Se ha reforzado el desacoplamiento entre el Motor de Trayectorias y el Renderizador de UI.

**Estado**: 🟢 Estable y listo para Fase 3 (UX & Performance).
