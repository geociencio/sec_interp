# Sample Data

This folder contains sample data files for testing the SecInterp plugin.

## Study Area

**Location**: LOMA ALTA F14A59 topographic sheet (INEGI, Mexico)

## Files

| File | Type | Description |
|------|------|-------------|
| `mdearea.tif` | GeoTIFF | Digital Elevation Model (DEM) of the study area |
| `secc1.shp` | Shapefile | Cross-section line for profile generation |
| `geologia.shp` | Shapefile | Geological unit polygons (fictitious) |
| `pts.shp` | Shapefile | Structural measurement points with dip/strike (fictitious) |
| `area.shp` | Shapefile | Study area boundary polygon |

## Data Sources

### DEM (mdearea.tif)
- **Source**: INEGI Continental Relief
- **URL**: https://www.inegi.org.mx/temas/relieve/continental/
- **Sheet**: F14A59 (Loma Alta)
- **Format**: GeoTIFF

### Cross-Section Line (secc1.shp)
- Line layer defining the cross-section profile path
- Use this layer as the "Section Line" input in the plugin

### Geological Polygons (geologia.shp)
> ⚠️ **FICTITIOUS DATA** - For demonstration purposes only

Sample geological unit polygons to test the geological profile functionality.

### Structural Points (pts.shp)
> ⚠️ **FICTITIOUS DATA** - For demonstration purposes only

Sample structural measurement points (dip/strike) to test the structural projection functionality.

### Area Boundary (area.shp)
Polygon defining the study area extent.

## How to Use

1. Open QGIS and add the layers from this folder
2. Open the SecInterp plugin
3. Configure inputs:
   - **DEM/Raster Layer**: `mdearea.tif`
   - **Section Line**: `secc1.shp`
   - **Geological Outcrops** (optional): `geologia.shp`
   - **Structural Layer** (optional): `pts.shp`
4. Click "Generate Preview" to visualize the profile
5. Click "Save Profile" to export the results

## License

DEM data is provided by INEGI under their open data license.
Geological and structural data are fictitious and provided for testing only.
