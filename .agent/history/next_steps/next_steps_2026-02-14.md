# Próximos Pasos - SecInterp (2026-02-14)

## Contexto de la Sesión
Se han estabilizado las componentes básicas y corregido bugs críticos de validación. El sistema está listo para la migración mayor a QGIS 4.x.

## Tareas Pendientes para la Siguiente Sesión

### 🚀 Prioridad Alta: Migración QGIS 4.x (v2.11.0 - Obj 1)
- [ ] Ejecutar script de reemplazo global para `PyQt5` -> `qgis.PyQt`.
- [ ] Validar importaciones en `resources.py`.
- [ ] Configurar job de CI/CD para detectar importaciones prohibidas de PyQt5.

### 🏗️ Prioridad Media: Motor 3D Preview (v2.11.0 - Obj 2)
- [ ] Implementar `core/engines/preview_3d_engine.py`.
- [ ] Integrar vista de proyección 3D en la pestaña de Preview.

### 🧪 Verificación Continua
- [ ] Ejecutar `make docker-test` tras la migración de imports para asegurar que nada se rompió.

## Instrucciones para Retomar la Sesión
1. Ejecutar `/inicia-sesion`.
2. Verificar el estado actual con `make test`.
3. Comenzar con la migración de imports en archivos pequeños (`core/utils/path_validator.py`, etc.) antes del reemplazo masivo.
