# Next Steps - SecInterp

## Contexto Final de la Sesión (2026-02-15)
Se ha completado la limpieza masiva de Type Hints (Returns) y la estabilización de señales en la GUI. El código de producción (`core`, `gui`, `exporters`) está ahora libre de incidencias de tipado según las reglas de `qgis-analyzer`.

## Tareas Pendientes
1. **Refactorización: Eliminación de Facades**: Implementar Inyección de Dependencias en `DrillholeService` y `GeologyService` según el [plan](file:///home/jmbernales/qgispluginsdev/sec_interp/docs/plans/implementation_plan_facade_removal.md).
2. **Migración PyQt5 -> qgis.PyQt**: Quedan 3 incidencias reportadas en el punto de entrada o utilidades menores.
3. **i18n de Tests**: Muchos strings en la carpeta `tests/` no usan `self.tr()`.
4. **Mypy Integration**: Iniciar la validación estática estricta con Mypy.

## Comando para retomar
```bash
/inicia-sesion
```
