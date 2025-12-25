# GeoPackage: Investigación Técnica Avanzada

## Resumen Ejecutivo

**GeoPackage** es un estándar OGC (Open Geospatial Consortium) para almacenar y transferir datos geoespaciales en un formato abierto, multiplataforma y basado en **SQLite**. Es el sucesor moderno de Shapefiles, adoptado por QGIS como formato predeterminado para datos vectoriales desde la versión 3.0.

---

## 1. ¿Qué es GeoPackage?

### 1.1 Definición Técnica

GeoPackage es un **contenedor SQLite** (archivo `.gpkg`) que almacena:
- **Datos vectoriales** (puntos, líneas, polígonos)
- **Datos raster** (imágenes, DEMs, tiles)
- **Atributos alfanuméricos**
- **Metadatos** (ISO 19115 compliant)
- **Estilos** (simbología QGIS/SLD)

**Especificación oficial**: OGC 12-128r18 (GeoPackage Encoding Standard 1.3.1)

### 1.2 Arquitectura SQLite

```
┌─────────────────────────────────────┐
│     archivo.gpkg (SQLite 3)         │
├─────────────────────────────────────┤
│ Tablas de Metadatos OGC:            │
│  ├─ gpkg_contents                   │
│  ├─ gpkg_spatial_ref_sys            │
│  ├─ gpkg_geometry_columns           │
│  └─ gpkg_metadata                   │
├─────────────────────────────────────┤
│ Tablas de Datos del Usuario:       │
│  ├─ geology_units (geometría)       │
│  ├─ drillholes (geometría)          │
│  ├─ dem_tiles (raster)              │
│  └─ project_settings (atributos)    │
├─────────────────────────────────────┤
│ Índices Espaciales (R-tree):        │
│  └─ rtree_geology_units_geom        │
└─────────────────────────────────────┘
```

### 1.3 Ventajas sobre Shapefile

| Característica | Shapefile | GeoPackage |
|----------------|-----------|------------|
| **Archivos** | Múltiples (.shp, .shx, .dbf, .prj) | Uno solo (.gpkg) |
| **Tamaño máximo** | 2 GB por componente | Sin límite práctico |
| **Nombres de campo** | 10 caracteres | 255 caracteres |
| **Unicode** | Limitado | Completo (UTF-8) |
| **Tipos de geometría** | Uno por archivo | Múltiples en un archivo |
| **Datos raster** | No soportado | Sí (tiles + coverage) |
| **Índice espacial** | Archivo .qix externo | R-tree integrado |
| **Transacciones** | No | Sí (ACID) |
| **Rendimiento QGIS** | Degrada con tamaño | Óptimo hasta GB |

---

## 2. ¿Qué Hace GeoPackage?

### 2.1 Almacenamiento de Datos Vectoriales

#### Tabla de Contenidos (`gpkg_contents`)
```sql
CREATE TABLE gpkg_contents (
  table_name TEXT PRIMARY KEY,
  data_type TEXT NOT NULL,  -- 'features', 'tiles', 'attributes'
  identifier TEXT,
  description TEXT,
  last_change DATETIME,
  min_x DOUBLE,
  min_y DOUBLE,
  max_x DOUBLE,
  max_y DOUBLE,
  srs_id INTEGER
);
```

#### Tabla de Geometrías (`gpkg_geometry_columns`)
```sql
CREATE TABLE gpkg_geometry_columns (
  table_name TEXT NOT NULL,
  column_name TEXT NOT NULL,
  geometry_type_name TEXT NOT NULL,  -- 'POINT', 'LINESTRING', etc.
  srs_id INTEGER NOT NULL,
  z TINYINT NOT NULL,  -- 0=no Z, 1=optional, 2=mandatory
  m TINYINT NOT NULL   -- 0=no M, 1=optional, 2=mandatory
);
```

#### Ejemplo de Tabla de Features
```sql
CREATE TABLE geology_units (
  fid INTEGER PRIMARY KEY AUTOINCREMENT,
  geom BLOB NOT NULL,  -- Geometría en formato WKB
  lithology TEXT,
  age_ma REAL,
  confidence INTEGER
);

-- Índice espacial automático (R-tree)
CREATE VIRTUAL TABLE rtree_geology_units_geom USING rtree(
  id, minx, maxx, miny, maxy
);
```

### 2.2 Almacenamiento de Datos Raster

#### Tiles (Pirámides de Imágenes)
```sql
CREATE TABLE gpkg_tile_matrix_set (
  table_name TEXT PRIMARY KEY,
  srs_id INTEGER NOT NULL,
  min_x DOUBLE NOT NULL,
  min_y DOUBLE NOT NULL,
  max_x DOUBLE NOT NULL,
  max_y DOUBLE NOT NULL
);

CREATE TABLE gpkg_tile_matrix (
  table_name TEXT NOT NULL,
  zoom_level INTEGER NOT NULL,
  matrix_width INTEGER NOT NULL,
  matrix_height INTEGER NOT NULL,
  tile_width INTEGER NOT NULL,
  tile_height INTEGER NOT NULL,
  pixel_x_size DOUBLE NOT NULL,
  pixel_y_size DOUBLE NOT NULL,
  PRIMARY KEY (table_name, zoom_level)
);

-- Tabla de tiles
CREATE TABLE dem_tiles (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  zoom_level INTEGER NOT NULL,
  tile_column INTEGER NOT NULL,
  tile_row INTEGER NOT NULL,
  tile_data BLOB NOT NULL  -- PNG/JPEG/WebP
);
```

#### Gridded Coverage (DEMs, Elevación)
Extensión OGC para datos raster regulares:
```sql
CREATE TABLE gpkg_2d_gridded_coverage_ancillary (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  tile_matrix_set_name TEXT NOT NULL,
  datatype TEXT DEFAULT 'float',  -- 'integer', 'float'
  scale REAL DEFAULT 1.0,
  offset REAL DEFAULT 0.0,
  precision REAL DEFAULT 1.0,
  data_null REAL
);
```

### 2.3 Metadatos ISO 19115

```sql
CREATE TABLE gpkg_metadata (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  md_scope TEXT NOT NULL DEFAULT 'dataset',
  md_standard_uri TEXT NOT NULL,
  mime_type TEXT NOT NULL DEFAULT 'text/xml',
  metadata TEXT NOT NULL  -- XML ISO 19115
);

CREATE TABLE gpkg_metadata_reference (
  reference_scope TEXT NOT NULL,
  table_name TEXT,
  column_name TEXT,
  row_id_value INTEGER,
  timestamp DATETIME NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
  md_file_id INTEGER NOT NULL,
  md_parent_id INTEGER
);
```

---

## 3. Rendimiento y Optimización

### 3.1 Benchmarks QGIS

**Prueba**: Cargar 100,000 polígonos en QGIS 3.28

| Formato | Tiempo de Carga | Zoom/Pan | Edición |
|---------|-----------------|----------|---------|
| Shapefile | 8.5 s | Lento | Lento |
| **GeoPackage** | **2.1 s** | **Fluido** | **Rápido** |
| PostGIS (red) | 3.2 s | Fluido | Medio |

**Fuente**: Benchmarks de la comunidad QGIS (2023)

### 3.2 Índices Espaciales R-tree

GeoPackage usa **R-tree** (Rectangle tree) para consultas espaciales eficientes:

```python
# Consulta espacial optimizada
SELECT fid, lithology
FROM geology_units
WHERE fid IN (
  SELECT id FROM rtree_geology_units_geom
  WHERE minx <= ? AND maxx >= ?
    AND miny <= ? AND maxy >= ?
)
```

**Complejidad**: O(log n) vs O(n) sin índice

### 3.3 Transacciones ACID

```python
import sqlite3

conn = sqlite3.connect('project.gpkg')
conn.execute("BEGIN TRANSACTION")
try:
    conn.execute("INSERT INTO geology_units ...")
    conn.execute("UPDATE drillholes SET ...")
    conn.commit()
except:
    conn.rollback()
```

**Ventaja**: Integridad garantizada en caso de fallo.

---

## 4. Implementación en Python

### 4.1 Con GeoPandas (Alto Nivel)

```python
import geopandas as gpd

# Leer GeoPackage
gdf = gpd.read_file('data.gpkg', layer='geology_units')

# Filtrar por atributo
granite = gdf[gdf['lithology'] == 'granite']

# Escribir nueva capa
granite.to_file('data.gpkg', layer='granite_only', driver='GPKG')

# Listar capas
import fiona
layers = fiona.listlayers('data.gpkg')
print(layers)  # ['geology_units', 'drillholes', 'structures']
```

### 4.2 Con GDAL/OGR (Bajo Nivel)

```python
from osgeo import ogr, osr

# Abrir GeoPackage
ds = ogr.Open('data.gpkg', 1)  # 1 = write mode

# Crear nueva capa
srs = osr.SpatialReference()
srs.ImportFromEPSG(32719)  # WGS84 / UTM 19S

layer = ds.CreateLayer(
    'new_layer',
    srs=srs,
    geom_type=ogr.wkbPolygon,
    options=['SPATIAL_INDEX=YES']  # R-tree automático
)

# Añadir campos
layer.CreateField(ogr.FieldDefn('name', ogr.OFTString))
layer.CreateField(ogr.FieldDefn('area_m2', ogr.OFTReal))

# Crear feature
feature = ogr.Feature(layer.GetLayerDefn())
feature.SetField('name', 'Unit A')
feature.SetField('area_m2', 12500.5)

# Geometría WKT
wkt = "POLYGON((0 0, 10 0, 10 10, 0 10, 0 0))"
geom = ogr.CreateGeometryFromWkt(wkt)
feature.SetGeometry(geom)

layer.CreateFeature(feature)
ds = None  # Cerrar
```

### 4.3 Consultas SQL Directas

```python
import sqlite3

conn = sqlite3.connect('data.gpkg')
cursor = conn.cursor()

# Consulta espacial con R-tree
query = """
SELECT g.fid, g.lithology, g.age_ma
FROM geology_units g
WHERE g.fid IN (
  SELECT id FROM rtree_geology_units_geom
  WHERE minx >= 350000 AND maxx <= 360000
    AND miny >= 6200000 AND maxy <= 6210000
)
AND g.age_ma < 20.0
ORDER BY g.age_ma DESC
"""

for row in cursor.execute(query):
    print(f"ID: {row[0]}, Litho: {row[1]}, Age: {row[2]} Ma")

conn.close()
```

### 4.4 Añadir Metadatos

```python
import sqlite3
from datetime import datetime

conn = sqlite3.connect('project.gpkg')

# Insertar metadatos ISO 19115
metadata_xml = """
<gmd:MD_Metadata xmlns:gmd="http://www.isotc211.org/2005/gmd">
  <gmd:fileIdentifier>
    <gco:CharacterString>sec_interp_project_001</gco:CharacterString>
  </gmd:fileIdentifier>
  <gmd:contact>
    <gmd:CI_ResponsibleParty>
      <gmd:individualName>
        <gco:CharacterString>Juan M Bernales</gco:CharacterString>
      </gmd:individualName>
    </gmd:CI_ResponsibleParty>
  </gmd:contact>
</gmd:MD_Metadata>
"""

cursor = conn.cursor()
cursor.execute("""
INSERT INTO gpkg_metadata (md_scope, md_standard_uri, mime_type, metadata)
VALUES ('dataset', 'http://www.isotc211.org/2005/gmd', 'text/xml', ?)
""", (metadata_xml,))

md_id = cursor.lastrowid

# Asociar metadatos a tabla
cursor.execute("""
INSERT INTO gpkg_metadata_reference
(reference_scope, table_name, md_file_id, timestamp)
VALUES ('table', 'geology_units', ?, ?)
""", (md_id, datetime.now().isoformat()))

conn.commit()
conn.close()
```

---

## 5. Extensiones OGC

### 5.1 Extensiones Estándar

| Extensión | Propósito |
|-----------|-----------|
| `gpkg_rtree_index` | Índice espacial R-tree |
| `gpkg_webp` | Tiles en formato WebP |
| `gpkg_zoom_other` | Niveles de zoom no potencia de 2 |
| `gpkg_crs_wkt` | CRS en formato WKT 2 |
| `gpkg_schema` | Esquema de base de datos |
| `gpkg_metadata` | Metadatos ISO 19115 |
| `gpkg_2d_gridded_coverage` | DEMs y datos raster regulares |

### 5.2 Registro de Extensiones

```sql
CREATE TABLE gpkg_extensions (
  table_name TEXT,
  column_name TEXT,
  extension_name TEXT NOT NULL,
  definition TEXT NOT NULL,
  scope TEXT NOT NULL  -- 'read-write' o 'write-only'
);

-- Ejemplo: Habilitar R-tree
INSERT INTO gpkg_extensions VALUES (
  'geology_units',
  'geom',
  'gpkg_rtree_index',
  'http://www.geopackage.org/spec/#extension_rtree',
  'write-only'
);
```

---

## 6. Casos de Uso para SecInterp

### 6.1 Proyecto Completo en un Solo Archivo

**Escenario**: Guardar todo el proyecto SecInterp en un `.gpkg`.

**Estructura**:
```
project_secinterp.gpkg
├─ section_line (LineString)
├─ topography_profile (LineString)
├─ geology_segments (Polygon)
├─ structure_measurements (Point)
├─ drillhole_traces (LineString)
├─ drillhole_intervals (Point)
├─ dem_tiles (Raster Tiles)
└─ project_metadata (Attributes)
```

**Ventajas**:
- Un solo archivo para compartir
- Transacciones atómicas
- Metadatos integrados
- Compatible con QGIS nativo

### 6.2 Exportación Avanzada

```python
# exporters/geopackage_exporter.py
from osgeo import ogr, osr
from pathlib import Path

class GeoPackageExporter:
    def __init__(self, output_path: Path):
        self.output_path = output_path
        self.ds = None

    def create_geopackage(self, srs_epsg: int = 32719):
        """Crear GeoPackage vacío con CRS."""
        driver = ogr.GetDriverByName('GPKG')
        self.ds = driver.CreateDataSource(str(self.output_path))

        self.srs = osr.SpatialReference()
        self.srs.ImportFromEPSG(srs_epsg)

    def add_geology_layer(self, segments: List[GeologySegment]):
        """Añadir capa de geología."""
        layer = self.ds.CreateLayer(
            'geology_segments',
            srs=self.srs,
            geom_type=ogr.wkbPolygon,
            options=['SPATIAL_INDEX=YES']
        )

        # Campos
        layer.CreateField(ogr.FieldDefn('lithology', ogr.OFTString))
        layer.CreateField(ogr.FieldDefn('age_ma', ogr.OFTReal))
        layer.CreateField(ogr.FieldDefn('confidence', ogr.OFTInteger))

        # Features
        for seg in segments:
            feat = ogr.Feature(layer.GetLayerDefn())
            feat.SetField('lithology', seg.lithology)
            feat.SetField('age_ma', seg.age_ma)
            feat.SetField('confidence', seg.confidence)

            geom = ogr.CreateGeometryFromWkb(seg.geometry.asWkb())
            feat.SetGeometry(geom)
            layer.CreateFeature(feat)

    def add_metadata(self, project_info: dict):
        """Añadir metadatos del proyecto."""
        import sqlite3
        conn = sqlite3.connect(str(self.output_path))

        # Tabla custom de metadatos
        conn.execute("""
        CREATE TABLE IF NOT EXISTS project_settings (
          key TEXT PRIMARY KEY,
          value TEXT
        )
        """)

        for key, value in project_info.items():
            conn.execute(
                "INSERT OR REPLACE INTO project_settings VALUES (?, ?)",
                (key, str(value))
            )

        conn.commit()
        conn.close()

    def close(self):
        """Cerrar GeoPackage."""
        self.ds = None
```

### 6.3 Importación de Proyectos

```python
def load_project_from_geopackage(gpkg_path: Path):
    """Cargar proyecto SecInterp desde GeoPackage."""
    import geopandas as gpd
    import sqlite3

    # Cargar capas
    geology = gpd.read_file(gpkg_path, layer='geology_segments')
    structures = gpd.read_file(gpkg_path, layer='structure_measurements')

    # Cargar metadatos
    conn = sqlite3.connect(gpkg_path)
    settings = dict(conn.execute("SELECT key, value FROM project_settings"))
    conn.close()

    return {
        'geology': geology,
        'structures': structures,
        'settings': settings
    }
```

---

## 7. Comparación con Alternativas

### 7.1 GeoPackage vs PostGIS

| Aspecto | GeoPackage | PostGIS |
|---------|------------|---------|
| **Instalación** | No requiere servidor | Requiere PostgreSQL |
| **Portabilidad** | Archivo único | Requiere dump/restore |
| **Concurrencia** | Limitada (SQLite) | Excelente (PostgreSQL) |
| **Rendimiento** | Óptimo para <10GB | Mejor para >10GB |
| **Uso típico** | Proyectos individuales | Bases de datos corporativas |

### 7.2 GeoPackage vs SpatiaLite

| Aspecto | GeoPackage | SpatiaLite |
|---------|------------|------------|
| **Estándar** | OGC oficial | Extensión de facto |
| **Funciones espaciales** | Básicas | Avanzadas (200+) |
| **Interoperabilidad** | Máxima | Buena |
| **Complejidad** | Simple | Requiere extensión |

**Nota**: Se pueden usar **juntos**: GeoPackage para almacenamiento + SpatiaLite para análisis avanzado.

---

## 8. Mejores Prácticas

### 8.1 Optimización de Rendimiento

```python
import sqlite3

conn = sqlite3.connect('data.gpkg')

# Configurar SQLite para rendimiento
conn.execute("PRAGMA journal_mode=WAL")  # Write-Ahead Logging
conn.execute("PRAGMA synchronous=NORMAL")
conn.execute("PRAGMA cache_size=10000")  # 10MB cache
conn.execute("PRAGMA temp_store=MEMORY")

# Vacuum periódico para compactar
conn.execute("VACUUM")
```

### 8.2 Validación de Integridad

```python
from osgeo import ogr

def validate_geopackage(gpkg_path):
    """Validar estructura de GeoPackage."""
    ds = ogr.Open(gpkg_path)

    # Verificar tablas obligatorias
    required_tables = [
        'gpkg_contents',
        'gpkg_spatial_ref_sys',
        'gpkg_geometry_columns'
    ]

    sql_layer = ds.ExecuteSQL("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [feat.GetField(0) for feat in sql_layer]
    ds.ReleaseResultSet(sql_layer)

    for table in required_tables:
        if table not in tables:
            print(f"❌ Tabla obligatoria faltante: {table}")
            return False

    print("✅ GeoPackage válido")
    return True
```

### 8.3 Compresión de Tiles

```python
# Usar WebP para tiles (mejor compresión que PNG)
from osgeo import gdal

gdal.Translate(
    'output.gpkg',
    'input.tif',
    format='GPKG',
    creationOptions=[
        'TILE_FORMAT=WEBP',
        'QUALITY=85',
        'TILING_SCHEME=GoogleMapsCompatible'
    ]
)
```

---

## 9. Herramientas y Ecosistema

### 9.1 Software Compatible

| Software | Soporte GeoPackage |
|----------|-------------------|
| **QGIS** | ✅ Formato predeterminado |
| **ArcGIS Pro** | ✅ Lectura/escritura completa |
| **GDAL/OGR** | ✅ Driver nativo |
| **GeoServer** | ✅ Publicación WFS/WMS |
| **PostGIS** | ✅ Importación con ogr_fdw |
| **R (sf package)** | ✅ Lectura/escritura |
| **Python (GeoPandas)** | ✅ Soporte completo |

### 9.2 Utilidades de Línea de Comandos

```bash
# Listar capas
ogrinfo data.gpkg

# Convertir Shapefile a GeoPackage
ogr2ogr -f GPKG output.gpkg input.shp

# Añadir capa a GeoPackage existente
ogr2ogr -f GPKG -update -append output.gpkg new_layer.shp -nln new_layer_name

# Ejecutar SQL
ogrinfo data.gpkg -sql "SELECT COUNT(*) FROM geology_units"

# Crear índice espacial
ogrinfo data.gpkg -sql "SELECT CreateSpatialIndex('geology_units', 'geom')"
```

---

## 10. Roadmap de Adopción en SecInterp

### Fase 1: Exportación Básica (v2.3.0)
- Exportar secciones completas a `.gpkg`
- Incluir todas las capas (geología, estructuras, sondajes)
- Metadatos básicos del proyecto

### Fase 2: Formato Nativo (v2.4.0)
- Guardar/cargar proyectos en GeoPackage
- Reemplazar múltiples Shapefiles
- Transacciones para ediciones

### Fase 3: Funcionalidades Avanzadas (v2.5.0)
- Almacenar tiles de DEM
- Versionado de interpretaciones
- Sincronización con PostGIS

---

## 11. Recursos y Referencias

### 11.1 Documentación Oficial
- **Especificación OGC**: http://www.geopackage.org/spec/
- **GitHub**: https://github.com/opengeospatial/geopackage
- **Best Practices**: http://www.geopackage.org/guidance/

### 11.2 Tutoriales
- **GDAL GeoPackage**: https://gdal.org/drivers/vector/gpkg.html
- **QGIS Training**: https://docs.qgis.org/latest/en/docs/user_manual/managing_data_source/supported_data.html#geopackage

### 11.3 Herramientas
- **GPKG Validator**: https://github.com/opengeospatial/ets-gpkg12
- **QGIS Package Layers**: Plugin para gestión avanzada

---

## 12. Conclusiones

### 12.1 Ventajas Clave para SecInterp

✅ **Un solo archivo**: Simplifica distribución de proyectos
✅ **Rendimiento**: Más rápido que Shapefiles en QGIS
✅ **Sin límites**: Nombres largos, Unicode, tamaño ilimitado
✅ **Estándar abierto**: OGC, amplio soporte
✅ **Extensible**: Metadatos, estilos, raster
✅ **Transaccional**: Integridad garantizada

### 12.2 Casos de Uso Ideales

1. **Proyectos portátiles**: Un `.gpkg` con todo el proyecto
2. **Colaboración**: Compartir interpretaciones completas
3. **Archivo**: Almacenamiento a largo plazo
4. **Integración**: Compatible con flujos de trabajo QGIS modernos

---

*Documento creado: 2025-12-22*
*Autor: Investigación técnica para proyecto SecInterp*
*Versión: 1.0*
