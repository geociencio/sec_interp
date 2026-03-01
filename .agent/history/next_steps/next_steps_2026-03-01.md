# Próximos Pasos - 2026-03-01

## Estado Actual
Finalizada la **Fase 3.0.1** de Estabilización y Seguridad.
- Implementada protección contra Path Traversal en `BaseExporter`.
- Resueltas fugas de señales y `QgsRubberBand`.
- Corregido el manejo de excepciones críticas (`KeyboardInterrupt`, etc.).
- Eliminado código muerto en `PreviewRenderer`.
- Suite de pruebas estable con **124 tests OK** en Docker.
- Plugin desplegado localmente para pruebas de QGIS.

## Tareas Pendientes
- [ ] **Fase 4: Consolidación de Configuración**: Unificar `ConfigService`, `ConfigManager` y `DialogConfig`.
- [ ] **Auditoría de Señales (Final)**: Cerrar las fugas remanentes detectadas por `qgis-analyzer` (ahora que las desconexiones base son robustas).
- [ ] **Refactorización de Herramientas**: Revisar `InterpretationTool` y `MeasureTool` para asegurar el uso óptimo de `LayerResolver`.
- [ ] **Integración de Drill Logs**: Iniciar investigación sobre la integración de logs de perforación detallados.

## Comandos para Retomar
```bash
/inicia-sesion
make docker-test
uv run qgis-manage deploy --no-compile
```

## Notas Técnicas
- El entorno local `uv run` presenta inconsistencias al resolver `sec_interp` como paquete si no se instala en modo editable (`-e .`). Se recomienda usar el contenedor Docker para validación formal.
- La protección Path Traversal usa `path.resolve()` y comprobación de prefijo; cualquier nuevo exportador debe heredar de `BaseExporter` y llamar a `validate_export_path`.
