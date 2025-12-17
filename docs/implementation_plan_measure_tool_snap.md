# Eliminar Advertencia de Capas Temporales y Usar QgsPointLocator

Este plan aborda la eliminación de la advertencia de "capas temporales" en QGIS al usar la herramienta de medición, implementando un sistema de snapping directo que no requiere que las capas estén en el proyecto principal.

## User Review Required
> [!NOTE]
> Este cambio eliminará las capas "invisibles" del proyecto principal, mejorando la limpieza y eliminando diálogos molestos al cerrar QGIS.

## Proposed Changes

### Preview Renderer
#### [MODIFY] [preview_renderer.py](file:///home/jmbernales/qgispluginsdev/sec_interp/gui/preview_renderer.py)
- Revertir la adición de capas a `QgsProject.instance()`.
- Eliminar la configuración de `QgsSnappingConfig` en el canvas (ya no será necesaria para el snapping del proyecto).

### GUI Tools
#### [MODIFY] [measure_tool.py](file:///home/jmbernales/qgispluginsdev/sec_interp/gui/tools/measure_tool.py)
- Importar `QgsPointLocator`.
- Rediseñar `_snap_point` para iterar sobre las capas activas del canvas y usar `QgsPointLocator` directamente en cada una.
- Esto permite snapping a los vértices de las capas de preview sin que estas pertenezcan al proyecto.

## Verification Plan

### Automated Tests
- Validar mediante scripts que las capas de preview no aparecen en `QgsProject.instance().mapLayers()`.

### Manual Verification
1. Abrir el perfil y herramienta de medición.
2. Verificar que el snapping sigue funcionando (el cursor se imanta a los puntos).
3. Cerrar el plugin o QGIS y verificar que ya no aparece el mensaje de "capas temporales scratch".
