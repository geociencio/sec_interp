# Tareas Activas - SecInterp

## [/] Sesión Actual: Mejoras de Infraestructura (qgis-manage) [/]
- [x] **Sintonización de Contexto**
    - [x] Ejecutar `ai-ctx analyze`
    - [x] Revisar `next_steps.md` y `AGENT_LESSONS.md`
    - [x] Validar reporte de `qgis-analyzer summary`
    - [x] Sincronizar entorno (`uv sync`) y ejecutar tests (`make docker-test`)

- [-] **Soporte para `.pluginignore`**
    - [x] Investigar implementación actual de exclusiones en `qgis_manager`
    - [-] Implementar lectura de `.pluginignore` (Redundante: usar `.qgisignore` o `.toml`)
    - [-] Validar con tests unitarios

- [x] **RCC Patching Automatizado**
    - [x] Identificar punto de inyección en el comando de compilación
    - [x] Implementar reemplazo de `PyQt5` por `qgis.PyQt` vía `sed` o Python
    - [x] Verificar compilación de recursos

- [x] **Validación Estructural**
    - [x] Añadir chequeos para iconos y `classFactory`
    - [x] Integrar nuevos chequeos en `qgis-manage validate`

## 🔜 Siguientes Pasos
- [x] Mantenimiento de tipado en `core/tasks`
- [ ] Cierre de sesión y actualización de memoria
