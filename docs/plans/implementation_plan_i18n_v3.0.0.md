# Plan de Actualización de Documentación

Este plan detalla los cambios necesarios para alinear la documentación del plugin con la versión 3.0.0.

## User Review Required
> [!NOTE]
> Se requiere regenerar la documentación HTML con `make docs` tras los cambios.

## Proposed Changes

### Documentation Source
#### [MODIFY] [USER_GUIDE.md](file:///home/jmbernales/qgispluginsdev/sec_interp/docs/source/USER_GUIDE.md)
*   Actualizar sección de i18n para reflejar soporte de 10 idiomas (incluyendo Hindi y Japonés).
*   Refinar descripción de 3D Export.

#### [MODIFY] [DEVELOPMENT_GUIDE.md](file:///home/jmbernales/qgispluginsdev/sec_interp/docs/source/DEVELOPMENT_GUIDE.md)
*   Actualizar instrucciones de i18n para mencionar `apply_full.py` y el nuevo flujo automatizado.

#### [MODIFY] [ARCHITECTURE.mmd](file:///home/jmbernales/qgispluginsdev/sec_interp/ARCHITECTURE.mmd)
*   Actualizar diagrama para incluir `AccessControlService` y la descomposición de `DrillholeService`.

#### [MODIFY] [docs/source/ARCHITECTURE.md](file:///home/jmbernales/qgispluginsdev/sec_interp/docs/source/ARCHITECTURE.md)
*   Reflejar cambios en la capa de servicios (Access Control, Drillhole decomposition).

#### [MODIFY] [docs/ARCHITECTURE_EN.md](file:///home/jmbernales/qgispluginsdev/sec_interp/docs/ARCHITECTURE_EN.md)
*   Eliminar menciones obsoletas al patrón "Facade" en `DrillholeService`.
*   Actualizar diagramas Mermaid si es necesario.

#### [MODIFY] [docs/source/TECHNICAL_COMPENDIUM.md](file:///home/jmbernales/qgispluginsdev/sec_interp/docs/source/TECHNICAL_COMPENDIUM.md)
*   Verificar y actualizar definiciones técnicas si están desactualizadas.

#### [MODIFY] [docs/source/MAINTENANCE_LOG.md](file:///home/jmbernales/qgispluginsdev/sec_interp/docs/source/MAINTENANCE_LOG.md)
*   Asegurar que las entradas recientes reflejen los cambios arquitectónicos (Drillholes, i18n).




## Verification Plan
### Automated Verification
*   Ejecutar `make docs` y verificar que no hay errores de Sphinx.
*   Abrir `help/html/index.html` (si es posible verificar existencia) para confirmar generación.
