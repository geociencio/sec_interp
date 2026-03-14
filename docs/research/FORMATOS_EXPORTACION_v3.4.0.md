# Investigación de Formatos de Exportación para SecInterp

Este reporte evalúa los formatos óptimos para el intercambio de datos geológicos entre SecInterp (QGIS) y software industrial como Leapfrog, MineSight y Vulcan.

## 1. Formatos Recomendados

### 🟢 GeoPackage (.gpkg) - El Estándar Moderno
- **Uso**: Formato por defecto para todos los datos vectoriales (secciones, proyecciones).
- **Ventajas**:
    - Soporte nativo y optimizado en QGIS.
    - Soporta geometrías 3D (Z) de forma real.
    - Sin límites de nombres de atributos (a diferencia de Shapefile/DBF).
    - Un solo archivo (SQLite) en lugar de múltiples archivos auxiliares.
- **Implementación**: Prioridad Alta. Reemplazar Shapefile como formato primario.

### 🟡 DXF (AutoCAD) - Interoperabilidad Industrial
- **Uso**: Exportación de interpretaciones para software CAD y minería (MineSight, Vulcan).
- **Ventajas**:
    - Estándar "de facto" en ingeniería y minería.
    - Compatible con casi todos los modeladores geológicos.
    - Soporta políneas y caras 3D (3DFace).
- **Estatus**: Se puede implementar nativamente usando `QgsDxfExport` de QGIS.

### 🔵 OMF (Open Mining Format) - El "Gold Standard"
- **Uso**: Intercambio de modelos 3D complejos con Leapfrog.
- **Ventajas**:
    - Específicamente diseñado para geología.
    - Preserva la estructura de "Proyectos" (superficies, mallas, bloques).
- **Estatus**: Requiere la librería Python `omf`. Recomendado como característica opcional/premium para la v3.5.0.

---

## 2. Matriz de Compatibilidad

| Formato | QGIS | Leapfrog | MineSight/Vulcan | Web/Vis |
| :--- | :---: | :---: | :---: | :---: |
| **GeoPackage** | ⭐⭐⭐ | 🟢 (GIS) | 🟡 (Import) | 🟢 |
| **Shapefile** | 🟡 (Legacy) | 🟢 | 🟢 | 🟡 |
| **DXF** | 🟢 | 🟢 | ⭐⭐⭐ | 🟡 |
| **OMF** | 🟡 (Plugin) | ⭐⭐⭐ | 🟢 | 🟢 |

---

## 3. Propuesta Técnica para v3.4.0

1. **Nuevo GpkgfileExporter**:
    - Crear `GpkgfileExporter` como clase independiente para manejo exclusivo de GeoPackage.
    - Mantener `ShapefileExporter` como opción legacy.
2. **Interfaz de Exportación Flexible**:
    - Implementar selector de formato (GPKG, DXF, SHP) en el diálogo de exportación.
    - Añadir campo para definir el nombre del archivo de salida (anteriormente automático).
3. **Nuevo DXFExporter**:
    - Implementar exportador dedicado para DXF 3D usando `QgsDxfExport`.
4. **Reducción de Complejidad**:
    - Refactorizar `MainDialog` y `ExportManager` para manejar la lógica de selección de formato de forma desacoplada.

## 4. Próximos Pasos

He iniciado la **Fase v3.4.0** siguiendo este esquema.
