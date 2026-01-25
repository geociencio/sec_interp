# Sesión: 2026-01-24 - Estabilización de Tests Docker

## Resumen Técnico
Esta sesión se centró en resolver los fallos críticos detectados al ejecutar los tests en el entorno Docker (`make docker-test`). El problema principal era doble: una discrepancia en la definición de los DTOs tras el desacoplamiento de arquitectura y una contaminación del estado global de Python que impedía cargar la API real de QGIS en los tests de integración.

## Cambios Clave

### 1. Sincronización de DTOs (`GeologySegment`)
- El campo `geometry` fue renombrado a `geometry_wkt` en `core/types.py` para desacoplar el core de los objetos `QgsGeometry`.
- Se actualizaron todos los puntos de instanciación en los tests y en `GeologyService`.
- Se implementó la conversión automática `asWkt()` en el servicio para mantener la compatibilidad.

### 2. Aislamiento de Entornos (Mocks vs Real)
- Refactorización de `tests/base_test.py`: Se crearon funciones `apply_mock_patches()` y `remove_mock_patches()` para permitir el control granular de cuándo se interceptan los módulos de QGIS.
- Mejora en `tests/integration/base_integration.py`: Ahora se limpia explícitamente `sys.modules` antes de inicializar `QgsApplication`.
- Actualización de `Dockerfile`: Se dividió la ejecución de los tests en 4 sub-procesos independientes para evitar colisiones de memoria y estado entre los tests mockeados y los reales.

### 3. Fortalecimiento de la Suite de Mocks
- Se añadieron métodos de compatibilidad a los Mocks:
    - `MockQgsGeometry`: `pointN()`, `is3D()`, `wkbType()`.
    - `MockQgsPointXY`: `compare()`.

## Resultados de Verificación
- **Ejecución Docker**: `make docker-test` exitosa.
- **Total Tests**: 359 tests OK.
- **Integración**: Los 14 tests de la carpeta `tests/integration/` cargan satisfactoriamente la API real de QGIS dentro del contenedor.

## Archivos Afectados
- `Dockerfile`
- `core/services/geology_service.py`
- `tests/base_test.py`
- `tests/integration/base_integration.py`
- `tests/integration/test_3d_integration.py`
- `tests/exporters/test_drillhole_3d_exporter.py`
- `tests/gui/test_attribute_inheritance.py`
- `tests/gui/test_preview_components.py`
