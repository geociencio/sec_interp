# Tareas Activas - SecInterp

## [x] Sesión Actual: Inicialización y Validación [x]
- [x] Sintonización de Contexto (`ai-ctx`, `next_steps.md`, `AGENT_LESSONS.md`)
- [x] Validación de Calidad (`qgis-analyzer summary`)
- [x] Sincronización de Entorno (`uv sync`)
- [x] Verificación de Estabilidad (`make docker-test` - **ALL PASS**)

## [x] Objetivo Completado: Fase 3.0.1 - Estabilización y Refactorización [x]
- [x] **Limpieza Crítica**: Eliminar código muerto en `preview_renderer.py`.
- [x] **Manejo de Errores**: Corregir captura de excepciones en `sec_interp_plugin.py` (Propagar KeyboardInterrupt).
- [x] **Auditoría de Señales**: Implementar desconexiones según `implementation_plan_v3.0.1.md`.
- [x] **Validación y Seguridad**: Centralizar validación de capas y añadir protección contra Path Traversal en exportadores.
- [x] **Consolidación de Configuración**: Unificar `ConfigService`, `ConfigManager` y `DialogConfig`.
- [x] **Memoria**: Robustecer `_cleanup_layers` para liberación de `QgsRubberBand`.

## Fase 3.2.0 - Expansión de Cobertura de Tests [x]
- [x] Implementar infraestructura de tests para `gui/tasks/`
- [x] Añadir tests unitarios para `access_control_service.py`
- [x] Implementar tests unitarios para procesadores de `drillhole/`
- [x] Implementar tests de estado para `gui/renderers/`
- [x] Validar utilidades de performance (`lod_calculator.py`)
- [x] Alcanzar meta de >400 tests OK en Docker

## Fase 3.2.1 - Automatización de la Documentación de Tests [x]
- [x] Diseñar estrategia de actualización dinámica para `TESTING_STATUS.md`
- [x] Implementar script `scripts/update_testing_status.py`
- [x] Integrar actualización en el flujo de `make docker-test`
