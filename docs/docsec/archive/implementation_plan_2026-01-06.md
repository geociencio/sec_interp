# Plan de Refactorización de Exportadores (v2.6.0)

Este plan detalla las acciones para mejorar la calidad del código en los exportadores de SecInterp, basándose en los resultados de `qgis-analyzer`.

## Objetivos
- Reducir la complejidad ciclomática de los métodos de exportación principales.
- Eliminar advertencias de falta de documentación (Docstrings).
- Completar la cobertura de anotaciones de tipo (Type Hints).

## Cambios Propuestos

### [MODIFY] [shp_exporter.py](file:///home/jmbernales/qgispluginsdev/sec_interp/exporters/shp_exporter.py)
- **Refactorizar `export`**:
    - Extraer `_prepare_fields` para la lógica de creación de campos.
    - Extraer `_create_writer` para la configuración del writer.
    - Simplificar el bucle de escritura de features.

### [MODIFY] [drillhole_exporters.py](file:///home/jmbernales/qgispluginsdev/sec_interp/exporters/drillhole_exporters.py)
- **Refactorizar `DrillholeIntervalShpExporter.export`**:
    - Extraer la lógica de procesamiento de segmentos a un método privado `_process_segment`.
- **Documentación**:
    - Añadir docstrings a `get_supported_extensions`.

### [MODIFY] [profile_exporters.py](file:///home/jmbernales/qgispluginsdev/sec_interp/exporters/profile_exporters.py)
- **Documentación**:
    - Añadir docstrings a `get_supported_extensions` en todas las clases.

### [MODIFY] [interpretation_3d_exporter.py](file:///home/jmbernales/qgispluginsdev/sec_interp/exporters/interpretation_3d_exporter.py)
- **Anotaciones de Tipo**:
    - Añadir tipos a los métodos recientemente extraídos (`_make_fields_obj`, `_prepare_fields`, `_collect_projected_features`, etc.).

### [MODIFY] [interpretation_exporters.py](file:///home/jmbernales/qgispluginsdev/sec_interp/exporters/interpretation_exporters.py)
- **Refactorizar `export`**:
    - Extraer la lógica de creación de geometría y feature a métodos privados.

## Plan de Verificación

### Tests Automatizados
- Ejecutar la suite de tests de exportadores completa:
  ```bash
  PYTHONPATH=.. uv run python3 -m unittest discover tests/exporters/
  ```
- Re-ejecutar `qgis-analyzer` para verificar la mejora en las métricas.

### Verificación Manual
- Validar que los Shapefiles generados siguen siendo válidos en QGIS.
