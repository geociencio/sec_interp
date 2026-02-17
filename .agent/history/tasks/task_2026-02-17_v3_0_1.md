# Tareas de la Sesión

- [x] Sintonización de Contexto
    - [x] Ejecutar análisis de contexto con `ai-ctx`
    - [x] Revisar `next_steps.md` y `AGENT_LESSONS.md`
    - [x] Validar tareas activas y estado de `task.md`
    - [x] Revisar `AI_CONTEXT.md` y `project_context.json`
- [x] Escaneo de Calidad (Quick Quality Scan)
- [x] Validación de Integridad
    - [x] Sincronizar dependencias (`uv sync`)
    - [x] Ejecutar pruebas de regresión (`make docker-test`)

# Tareas Actuales: Corrección de Fugas de Señales
- [x] Análisis inicial de fugas de señales (`qgis-analyzer`) <!-- id: 0 -->
- [x] Corrección de fugas en archivos principales <!-- id: 1 -->
    - [x] `sec_interp_plugin.py` (unload/disconnect) <!-- id: 5 -->
    - [x] `SettingsPage.py` (unroll loops) <!-- id: 6 -->
    - [x] `GeologyPage.py` y `DrillholePage.py` (explicit disconnects) <!-- id: 7 -->
- [x] Refactorización de `SignalManager` <!-- id: 2 -->
    - [x] Unificación de identificadores y eliminación de alias <!-- id: 8 -->
    - [x] Eliminación de conexiones duplicadas en `MainDialog` <!-- id: 9 -->
- [x] Verificación y validación <!-- id: 3 -->
    - [x] Análisis final con `qgis-analyzer` (0 fugas) <!-- id: 10 -->
    - [x] Limpieza en archivos de tests <!-- id: 11 -->
- [x] Documentación final (Walkthrough) <!-- id: 4 -->
- [x] Implementar `disconnect_signals` en `SecInterp` (Plugin)
- [x] Implementar `disconnect_signals` en `SignalManager`
- [x] Validar desconexiones en páginas de datos
- [x] Verificación
    - [x] Ejecutar `qgis-analyzer summary` para validar 0 fugas
    - [x] Ejecutar `make docker-test`

# Liberación de Versión 3.0.1
- [x] Fase 1: Calidad y Preparación <!-- id: 12 -->
    - [x] Análisis de Calidad y Seguridad Deep <!-- id: 13 -->
    - [x] Actualizar Badges en README.md <!-- id: 14 -->
- [x] Fase 2: Versionamiento y Documentación <!-- id: 15 -->
    - [x] Actualizar `metadata.txt` (v3.0.1 + Changelog) <!-- id: 16 -->
    - [x] Actualizar `pyproject.toml` <!-- id: 17 -->
    - [x] Generar Release Notes <!-- id: 18 -->
- [x] Fase 3: Verificación Técnica <!-- id: 19 -->
    - [x] Validar 361+ tests en Docker <!-- id: 20 -->
- [x] Fase 4: Git y Tagging <!-- id: 21 -->
    - [x] Commit `chore(release): prepare v3.0.1` <!-- id: 22 -->
    - [x] Crear Tag `v3.0.1` <!-- id: 23 -->
- [x] Fase 5: Empaquetado y Distribución <!-- id: 24 -->
    - [x] Build ZIP Optimizado <!-- id: 25 -->
    - [x] Crear Draft Release en GitHub <!-- id: 26 -->
