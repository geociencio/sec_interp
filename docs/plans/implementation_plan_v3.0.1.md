# Plan de Corrección de Fugas de Señales

Corregir las 22 fugas de señales detectadas por `qgis-analyzer` para mejorar la estabilidad de QGIS y evitar comportamientos erráticos tras cerrar diálogos o cambiar herramientas.

## Cambios Propuestos

### [SecInterp Plugin] [sec_interp_plugin.py](file:///home/jmbernales/qgispluginsdev/sec_interp/sec_interp_plugin.py)
- Implementar `disconnect_signals()` para desconectar `action.triggered` y `dlg.accepted`.
- Llamar a `disconnect_signals()` en `unload()`.

### [Signal Manager] [dialog_signal_manager.py](file:///home/jmbernales/qgispluginsdev/sec_interp/gui/dialog_signal_manager.py)
- Añadir desconexión para `reset_defaults_btn.clicked`.
- Añadir desconexión para `btn_finalize.clicked` (conectado al slot de `measure_tool`).
- Asegurar que `disconnect_all()` sea infalible ante objetos ya destruidos.

### [Data Pages]
- **[MODIFY] [drillhole_page.py](file:///home/jmbernales/qgispluginsdev/sec_interp/gui/ui/pages/drillhole_page.py)**: Asegurar desconexión de `chk_use_geom`.
- **[MODIFY] [geology_page.py](file:///home/jmbernales/qgispluginsdev/sec_interp/gui/ui/pages/geology_page.py)**: Validar desconexión de `fieldChanged`.
- **[MODIFY] [structure_page.py](file:///home/jmbernales/qgispluginsdev/sec_interp/gui/ui/pages/structure_page.py)**: Validar desconexión de `dip_combo` y `strike_combo`.

## Plan de Verificación

### Pruebas Automatizadas
- Ejecutar `/audit-plugin` para verificar que el número de fugas de señales detectadas por `qgis-analyzer` se reduzca a 0.
- Ejecutar `make docker-test` para asegurar que las desconexiones no rompan la lógica funcional de la UI (especialmente en integración).

### Verificación Manual
- Validar visualmente en QGIS (si fuera posible) que el cambio de herramientas de mapa no deje rastros o logs de errores de señales ya muertas.
