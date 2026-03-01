# Tareas Activas - SecInterp

## [x] Sesión Actual: Inicia Fase 3 (UX & Performance & Code Quality) [x]
- [x] **Sintonización de Contexto**
    - [x] Ejecutar `ai-ctx analyze`
    - [x] Revisar `next_steps.md` y `AGENT_LESSONS.md`
    - [x] Validar reporte de `qgis-analyzer summary`
    - [x] Sincronizar entorno (`uv sync`) y ejecutar tests (`make docker-test`)

## [x] Fase 3: UX & Performance & Code Quality (Refactor) [x]
- [x] **Fixes Críticos**: `first_start` en plugin, manejo de caché inconsistente para geol/drillhole, doble `debounce` en zoom de canvas.
- [x] **Optimización de Performance**: Evitar `import` en runtime en methods, corrección simple de pipeline validator.
- [x] **Limpieza y Centralización**: Consolidar LayerResolver para evitar redundancia de obtención de capas, unificar validación de params.
- [x] **Feedback de UI**: Mejorar la transpiración visual del progreso de renderizado de sondajes (señal de progreso).
- [x] Revisión de cobertura de tests tras aplicar las refactorizaciones (229 tests OK).

## [/] Siguiente Objetivo: Consolidación de Configuración & Auditoría de Señales [/]
- [ ] Auditoría de Señales (implementation_plan_v3.0.1.md)
- [ ] Consolidación de ConfigService/Manager/Dialog
