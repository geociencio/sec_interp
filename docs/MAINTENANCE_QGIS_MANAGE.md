# Guía de Mantenimiento y Evolución de qgis-manage para QGIS 4

Este documento detallaba los cambios necesarios en la herramienta `qgis-manage` para eliminar hardcodes de versión (QGIS 3). A partir de la versión **0.7.0**, estos problemas han sido resueltos oficialmente.

## 1. Estado Actual (Resuelto en v0.7.0)

La versión 0.7.0 de `qgis-manage` (disponible en PyPI) ya soporta nativamente múltiples versiones de QGIS y despliegue interactivo.

### Cambios Implementados:
- **Soporte Multi-Versión**: Se eliminó el hardcode de QGIS 3.
- **Nuevo Argumento**: Se añadió `--qgis-version` (3 o 4) al comando `deploy`.
- **Detección de Rutas**: Ahora detecta automáticamente las rutas estándar para QGIS 4 en Linux, Windows y macOS.
- **Modo Interactivo**: Si el directorio de destino no existe, la herramienta pregunta antes de crearlo.

## 2. Uso Recomendado

Para proyectos que apuntan a QGIS 4, asegúrate de tener `qgis-manage>=0.7.0` en tu `pyproject.toml` y usa el siguiente patrón en el `Makefile`:

```makefile
# Makefile de SecInterp (Actualizado)
QGIS_VERSION ?= 4

deploy:
    uv run qgis-manage deploy --qgis-version $(QGIS_VERSION)
```

## 3. Instrucciones para AI Agents

Al trabajar en la migración a QGIS 4:
1. **Verifica la versión**: Asegúrate de que `qgis-manage` esté en la versión `0.7.0` o superior.
2. **Usa el CLI**: Prefiere `qgis-manage deploy --qgis-version 4` sobre `rsync` manual, ya que `qgis-manage` gestiona backups y compilación automáticamente.
3. **Validación**: Si el despliegue falla por falta de directorios, ejecuta el comando de forma interactiva (`-i`) una vez para establecer las rutas.

---
*Documento actualizado tras el lanzamiento de qgis-manage 0.7.0 (Mayo 2026).*
