# SecInterp Debug Logs

Este directorio contiene los logs de depuración del plugin SecInterp para análisis de crashes y problemas de estabilidad.

## Archivos de Log

- **`sec_interp_debug.log`**: Log principal con información detallada de ejecución
- **`sec_interp_debug.log.1` - `.5`**: Backups rotativos (máximo 5 archivos de 10MB cada uno)

## Formato de Log

Cada línea de log contiene:
```
YYYY-MM-DD HH:MM:SS | LEVEL    | Module.Name | function:line | Thread-ID | Message
```

### Ejemplo:
```
2025-12-25 22:30:15 | DEBUG    | SecInterp.gui.tools.interpretation_tool | finalize_polygon:264 | Thread-12345 | Interpretation polygon finalized with 5 vertices, ID: abc123
```

## Análisis de Crashes

Cuando QGIS crashea, el último conjunto de mensajes en el log puede indicar:

1. **Última función ejecutada**: Busca la última entrada DEBUG antes del crash
2. **Thread involucrado**: Verifica si el crash ocurrió en el thread principal o en background
3. **Operaciones de Canvas**: Busca mensajes relacionados con `setLayers()`, `refresh()`, o `removeItem()`
4. **Gestión de Memoria**: Busca mensajes de `_cleanup_layers()` o `reset()`

## Niveles de Log

- **DEBUG**: Información detallada de flujo de ejecución (solo en archivos)
- **INFO**: Eventos importantes (archivos + UI de QGIS)
- **WARNING**: Situaciones anormales pero recuperables
- **ERROR**: Errores que requieren atención
- **CRITICAL**: Fallos graves del sistema

## Rotación de Logs

Los logs rotan automáticamente cuando alcanzan 10MB. Se mantienen hasta 5 archivos de respaldo.

## Privacidad

⚠️ **IMPORTANTE**: Estos logs pueden contener rutas de archivos locales. No compartas los logs públicamente sin revisarlos primero.
