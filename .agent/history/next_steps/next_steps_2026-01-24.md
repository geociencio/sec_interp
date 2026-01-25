# Siguiente Paso: Integración de UI Asíncrona y Refactorización Final v2.8.0

## Estado Actual
- **Core**: 100% desacoplado de QGIS. Los servicios operan con WKT y DTOs agnósticos.
- **Validación**: 100% tests OK (359/359 tests en Docker exitosos).
- **Infraestructura**: Entorno Docker estabilizado con aislamiento entre Mocks y API Real.
- **Mocks**: Mejorados con soporte para métodos de geometría 3D (`pointN`, `is3D`) y comparación.

## Tareas Pendientes
- [ ] Integrar el nuevo `GeologyGenerationTask` y `DrillholeGenerationTask` en el `PreviewManager` para procesamiento background.
- [ ] Refactorizar la extracción de datos en el hilo principal (Main Thread) antes de lanzar las tareas (preparar DTOs planos).
- [ ] Verificar la coherencia de la visualización estructural con los nuevos DTOs de dominio.
- [ ] Revisar el impacto del cambio `geometry` -> `geometry_wkt` en scripts externos de automatización.

## Comando para Retomar
```bash
/inicia-sesion
```
O validar el estado completo:
```bash
make docker-test
```

## Notas Técnicas
- El entorno Docker es ahora la fuente de verdad definitiva para la estabilidad del plugin.
- Se ha corregido la contaminación de `sys.modules` en tests de integración usando `remove_mock_patches()`.
- `GeologySegment.geometry_wkt` es ahora el estándar para intercambio de geometrías entre Core y GUI.
