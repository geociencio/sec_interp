# Investigación de Tags para metadata.txt - SecInterp

Tras analizar el desarrollo actual del plugin (v2.7.0) y las funcionalidades implementadas hasta la fecha, se propone una actualización de los tags en `metadata.txt` para mejorar la visibilidad y el posicionamiento en el repositorio oficial de QGIS.

## Clasificación de Tags Propuestos

### 1. Dominio y Disciplina (Geociencias)
- **Actuales**: `geology`, `mining`, `exploration`, `structural geology`.
- **Recomendados**: `geoscience`, `earth science`.

### 2. Funcionalidades de Perfil y Sección
- **Actuales**: `cross-section`, `topography`, `profile`, `dem`.
- **Recomendados**: `section`, `lithology`, `apparent dip`.

### 3. Manejo de Datos de Sondajes (Drillholes)
- **Actuales**: `borehole`, `drillhole`.
- **Recomendados**: `sondajes`, `drilling`.

### 4. Capacidades 3D y Geometría
- **Actuales**: `subsurface`, `visualization`.
- **Recomendados**: `3d`, `z-values`, `projection`.

### 5. Edición e Interpretación
- **Actuales**: `interpretation`, `digitizing`, `snapping`, `interpolation`.
- **Recomendados**: `drawing`, `vectorization`.

### 6. Interoperabilidad y Formatos
- **Recomendados**: `export`, `dxf`, `cad`, `shp`, `csv`, `pdf`, `svg`.

### 7. Internacionalización e Interfaz
- **Recomendados**: `i18n`, `multilingual`.

---

## Propuesta Final para metadata.txt

```ini
tags=geology, mining, geoscience, cross-section, section, borehole, drillhole, 3d, exploration, topography, profile, interpretation, dem, interpolation, digitizing, snapping, structural geology, subsurface, visualization, export, dxf, cad, lithology, apparent dip, i18n, multilingual, sondajes
```
