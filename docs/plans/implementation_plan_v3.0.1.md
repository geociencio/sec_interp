# Plan de Estabilización y Refactorización v3.0.1

Este plan aborda tanto la auditoría de señales como los hallazgos críticos del análisis de código exhaustivo (`CODE_ANALYSIS2.md`) para garantizar una base de código limpia y segura.

## User Review Required

> [!IMPORTANT]
> Se eliminará código inalcanzable en el renderizador y se ajustará el manejo de excepciones globales. Esto puede cambiar ligeramente cómo se reportan errores críticos del sistema (ahora se propagarán en lugar de silenciarse).

## Proposed Changes

### 1. Eliminación de Código Muerto y Limpieza de Memoria
#### [MODIFY] [preview_renderer.py](file:///home/jmbernales/qgispluginsdev/sec_interp/gui/preview_renderer.py)
- **Eliminar** el bloque de código duplicado e inalcanzable (Líneas 191-211).
- **Robustecer** `_cleanup_layers()`: Asegurar que los `QgsRubberBand` se eliminen explícitamente de la escena del canvas antes de limpiar la lista.
- **Logging**: Reemplazar supresiones ciegas de excepciones con logs de advertencia.

### 2. Manejo de Excepciones y Señales
#### [MODIFY] [sec_interp_plugin.py](file:///home/jmbernales/qgispluginsdev/sec_interp/sec_interp_plugin.py)
- **Corregir** bloques `except`: Dejar de capturar `KeyboardInterrupt`, `SystemError` y `MemoryError` globalmente para permitir que el sistema responda correctamente a interrupciones.
- **Mejorar** `disconnect_signals()`: Implementar desconexiones más granulares y seguras.

### 3. Validación Centralizada y Seguridad de Paths
#### [MODIFY] [dtos.py](file:///home/jmbernales/qgispluginsdev/sec_interp/core/domain/dtos.py)
- Mover importaciones de validación al nivel de módulo (usando `TYPE_CHECKING`).
- Agregar validaciones de tipo y rango para parámetros numéricos en `PreviewParams.validate()`.
#### [MODIFY] [base_exporter.py](file:///home/jmbernales/qgispluginsdev/sec_interp/exporters/base_exporter.py)
- Implementar verificación de **Path Traversal** en `validate_export_path` para prevenir fugas de datos fuera del directorio permitido.

### 4. Auditoría de Señales (Original)
- Implementar desconexiones faltantes en `sec_interp_plugin.py`, `dialog_signal_manager.py` y páginas de datos (`drillhole_page.py`, etc.) según el reporte de `qgis-analyzer`.

## Verification Plan

### Automated Tests
- **QGIS Analyzer**: Ejecutar `/audit-plugin` para confirmar que las fugas de señales bajan a 0 y que el código muerto desaparece.
- **Docker Tests**: `make docker-test` para verificar regresiones en el flujo de renderizado y exportación.
- **Nuevos Tests**: Crear un test unitario en `tests/core/test_security.py` para validar la protección contra Path Traversal.

### Manual Verification
- Validar que al cerrar el diálogo repetidamente no se incremente el uso de memoria (fuga de RubberBands).
- Forzar un error de validación de path para confirmar que el sistema bloquea directorios prohibidos.
