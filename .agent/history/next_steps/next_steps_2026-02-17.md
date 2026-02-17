# Próximos Pasos - SecInterp

## Estado Final de la Sesión
- **Versión**: 3.0.1 (Expert Stability & Global Reach)
- **Fugas de Señales**: 0 (Resuelto)
- **Calidad**: 71.0/100
- **Seguridad**: 100/100
- **Tests**: 386 tests pasando en Docker.

## Tareas Pendientes (Deuda Técnica)
1. **Internacionalización (i18n)**:
   - Abordar los 872 strings detectados por `qgis-analyzer` que faltan por traducir (usar `self.tr()`).
   - Principalmente en diálogos, mensajes de log y exporters.
2. **Type Hints**:
   - Mejorar la cobertura de retorno (actualmente 45.3%).
   - Estandarizar el uso de `| None` para opcionales en el core.
3. **Docstrings**:
   - Completar las 246 docstrings faltantes (principalmente en métodos privados y clases GUI).

## Comando para retomar
```bash
/inicia-sesion
```

## Notas de Contexto
Se ha migrado el sistema de i18n a Master Data JSON. Para actualizar traducciones, usar `scripts/i18n/master_data/*.json`.
La resolución de fugas de señales requirió el desenrollado de bucles en `SignalManager` y la desconexión explícita en el `tearDown` de los tests.
