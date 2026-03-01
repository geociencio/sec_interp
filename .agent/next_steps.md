# Próximos Pasos - 2026-02-28

## Estado Actual
Finalizada la **Fase 3** de optimización de performance y UX. Se implementó `LayerResolver` con caché, se unificaron las validaciones en `PreviewParams` y se mejoró el feedback de progreso en la UI. La suite de pruebas es estable con 229 tests OK.

## Tareas Pendientes
- [ ] **Auditoría de Señales**: Retomar el plan de `implementation_plan_v3.0.1.md` para cerrar las 22 fugas detectadas por `qgis-analyzer`.
- [ ] **Fase 4: Consolidación de Configuración**: Unificar `ConfigService`, `ConfigManager` y `DialogConfig` (Pendiente de la Fase 3 original).
- [ ] **Refactorización de Herramientas**: Revisar `InterpretationTool` y `MeasureTool` para asegurar que aprovechan `LayerResolver`.
- [ ] **Modernización QGIS 4**: Iniciar revisión de compatibilidad siguiendo la skill `qgis-migration-4x`.

## Comandos para Retomar
```bash
/inicia-sesion
/audit-plugin
make docker-test
```

## Notas Técnicas
- El sistema de mocks ahora es más estricto; cualquier cambio en validadores de capa debe reflejarse en `tests/mocks/qgis_layers.py` (WKB types y Fields).
- Se recomienda mantener `LayerResolver.clear_cache()` en el `setUp` de los tests para evitar efectos secundarios.
