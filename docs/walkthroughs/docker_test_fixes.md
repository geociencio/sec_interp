# Walkthrough: Reparación de Tests en Docker

Se han corregido los fallos en la ejecución de tests dentro del entorno Docker, resolviendo problemas de arquitectura y contaminación de estado entre Mocks y la API real de QGIS.

## Cambios Realizados

### 1. Corrección de Incompatibilidad en `GeologySegment`
El reciente desacoplamiento de la arquitectura introdujo cambios en `core/types.py`, renombrando el atributo `geometry` a `geometry_wkt`.
- **Acción**: Se actualizaron todos los archivos de test (`tests/integration/test_3d_integration.py`, `tests/exporters/test_drillhole_3d_exporter.py`, etc.) para usar el nuevo nombre de argumento.
- **Servicios**: Se ajustó `GeologyService` para convertir objetos `QgsGeometry` a WKT antes de instanciar `GeologySegment`.

### 2. Aislamiento de Mocks vs. API Real
Se detectó que los tests de integración (que inicializan `QgsApplication`) fallaban debido a que el sistema de Mocks de `base_test.py` ya había parcheado `sys.modules`, impidiendo la carga de la API real de QGIS.
- **Acción**:
    - Se refactorizó `tests/base_test.py` para incluir funciones `apply_mock_patches()` and `remove_mock_patches()`.
    - Se modificó `tests/integration/base_integration.py` para limpiar explícitamente los parches de Mocks antes de importar QGIS.
    - Se actualizó el `Dockerfile` para ejecutar los tests en procesos separados por categorías (`core`, `exporters`, `gui`, y finalmente `integration` con `FORCE_MOCKS=0`).

### 3. Mejora de Cobertura de Mocks
Se añadieron métodos faltantes a los objetos Mock para dar soporte a los tests de exportación 3D cuando el entorno no tiene QGIS instalado (aunque en Docker sí lo tiene, esto mejora la robustez local).
- **Añadidos**: `pointN()`, `is3D()`, `wkbType()` en `MockQgsGeometry` y `compare()` en `MockQgsPointXY`.

## Verificación Resultante

Se ejecutó el comando completo de validación en Docker:

```bash
make docker-test
```

**Resultado:**
- **Tests Ejecutados**: 359
- **Estado**: ✅ OK
- **Cobertura**: Incluye los 14 tests de integración que utilizan la API real de QGIS en modo headless.

---
*Este walkthrough marca el cierre de la incidencia de tests en Docker.*
