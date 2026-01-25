# Siguiente Paso: Integración de UI Asíncrona

## Estado Actual
- **Core**: 100% desacoplado de QGIS. Los servicios operan con WKT y DTOs agnósticos.
- **Validación**: 100% tests OK (204 tests core pasando).
- **Mocks**: Estabilizados y con soporte WKT.

## Tareas Pendientes
- [ ] Integrar el nuevo `GeologyGenerationTask` y `DrillholeGenerationTask` en el `PreviewManager`.
- [ ] Refactorizar la extracción de datos en el hilo principal (Main Thread) antes de lanzar las tareas.
- [ ] Verificar la coherencia de la visualización estructural con los nuevos DTOs de dominio.

## Comando para Retomar
```bash
/inicia-sesion
```
O simplemente ejecutar los tests para validar el estado:
```bash
PYTHONPATH=.. uv run python3 -m unittest discover tests/core
```

## Notas Técnicas
- El `DrillholeService` ahora espera diccionarios con llaves `attributes` y `wkt`.
- `GeologySegment` ya no tiene el campo `geometry`, ahora es `geometry_wkt`.
