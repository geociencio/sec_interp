# Next Steps - SecInterp

## Contexto Final de la Sesión (2026-02-15)
Se ha completado la limpieza masiva de Type Hints (Returns) y la estabilización de señales en la GUI. El código de producción (`core`, `gui`, `exporters`) está ahora libre de incidencias de tipado según las reglas de `qgis-analyzer`.

## Tareas Pendientes
1. **Migración PyQt5 -> qgis.PyQt**: Quedan 3 incidencias reportadas en el punto de entrada o utilidades menores.
2. **i18n de Tests**: Muchos strings en la carpeta `tests/` no usan `self.tr()`. Aunque no es crítico para producción, afecta al score global.
3. **Mypy Integration**: Iniciar la validación estática estricta con Mypy ahora que hay tipos base.
4. **Optimización de Tests**: Reducir el tiempo de ejecución en Docker.

## Comando para retomar
```bash
/inicia-sesion
```
