# Tareas Activas - SecInterp

## 🔄 Sesión Actual: Limpieza de Deuda Técnica y Preparación QGIS 4.0
- [x] **Sincronización Inicial**
    - [x] Análisis de contexto (`ai-ctx`)
    - [x] Lectura de `next_steps.md` y `AGENT_LESSONS.md`
    - [x] Validación de integridad (Tests)
- [ ] **Migración PyQt (Hacia QGIS 4.0)**
    - [ ] (POSPUESTO) Identificar todos los `from PyQt5...` restantes
- [x] **Estabilidad de Señales (Fase 2)**
    - [x] Implementar `disconnect_all` en `DialogSignalManager`
    - [x] Limpieza en `PreviewManager` (timer y canvas)
    - [x] Gestión de señales en `PreviewTaskOrchestrator`
    - [x] Implementación de `disconnect_signals` en todas las páginas de configuración
    - [x] Validación de reducción de fugas con `qgis-analyzer` (Reducción de 65 a 29)
- [x] **Mejora del Quality Score (Fase 3)**
    - [x] Analizar reporte de `qgis-analyzer`
    - [x] Crear plan de implementación
    - [x] Incrementar cobertura de Type Hints (Returns) al >80% (Completo en Core, GUI, Exporters y Plugin)
    - [x] Resolver incidencias críticas de i18n en `controller.py`
    - [x] Eliminar importaciones directas de PyQt5 en utilidades de geometría
    - [x] Validar incremento de score
