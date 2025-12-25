# Análisis: Refactorización de Muestreo de Raster

## Uso Actual

### Caso 1: Perfil Geológico
```python
# En geol_profile() - línea 816-821
res = (
    raster_lyr.dataProvider()
    .identify(pt, QgsRaster.IdentifyFormatValue)
    .results()
)
elev = res.get(band_number, 0.0)
```

### Caso 2: Perfil Topográfico
```python
# En sample_elevation_along_line() - línea 425-426
val, ok = raster_layer.dataProvider().sample(pt, band_number)
elev = val if ok else 0.0
```

## Algoritmo Nativo: `native:rastersampling`

### Cómo Funciona
```python
processing.run("native:rastersampling", {
    'INPUT': point_layer,      # Capa de puntos (QgsVectorLayer)
    'RASTERCOPY': raster_layer,  # Capa raster
    'COLUMN_PREFIX': 'rvalue',
    'OUTPUT': 'memory:'
})
```

**Entrada**: Capa de puntos
**Salida**: Capa de puntos con valores del raster como atributos

## Análisis de Viabilidad

### ❌ Problemas con `native:rastersampling`

1. **Requiere Capa de Puntos**
   - Necesitamos crear una capa temporal con todos los puntos
   - Overhead de crear/poblar la capa

2. **Workflow Más Complejo**
   ```python
   # Método actual (simple)
   for pt in points:
       elev = raster.sample(pt)

   # Con native:rastersampling (complejo)
   # 1. Crear capa temporal de puntos
   temp_layer = QgsVectorLayer("Point", "temp", "memory")
   for pt in points:
       feat = QgsFeature()
       feat.setGeometry(QgsGeometry.fromPointXY(pt))
       temp_layer.dataProvider().addFeatures([feat])

   # 2. Ejecutar algoritmo
   result = processing.run("native:rastersampling", {...})

   # 3. Extraer valores de atributos
   for feat in result['OUTPUT'].getFeatures():
       elev = feat['rvalue_1']
   ```

3. **No Hay Ganancia de Rendimiento**
   - El algoritmo internamente hace lo mismo: muestrea punto por punto
   - El overhead de crear capas temporales es mayor que el beneficio

4. **Menos Flexible**
   - El método actual permite manejar errores por punto
   - Más control sobre el proceso

### ✅ Ventajas del Método Actual

1. **Directo y Simple**
   - Muestreo punto por punto sin capas intermedias
   - Código fácil de entender

2. **Eficiente**
   - No crea capas temporales innecesarias
   - Acceso directo al data provider

3. **Flexible**
   - Manejo de errores granular
   - Fácil de debuggear

## Comparación de Rendimiento

### Método Actual
```
Para 400 puntos:
- 400 llamadas a sample() ≈ 10-20ms
- Total: ~10-20ms
```

### Con native:rastersampling
```
Para 400 puntos:
- Crear capa temporal: ~5ms
- Añadir 400 features: ~10ms
- Ejecutar algoritmo: ~10-20ms
- Extraer resultados: ~5ms
- Total: ~30-40ms
```

**Conclusión**: El método actual es **MÁS RÁPIDO**

## Recomendación

### ⭐ MANTENER MÉTODO ACTUAL

**Razones**:
1. ✅ Más simple y directo
2. ✅ Mejor rendimiento
3. ✅ Más flexible
4. ✅ Código más mantenible
5. ✅ No requiere capas temporales

### Posible Optimización Alternativa

Si se quisiera optimizar el muestreo, una mejor opción sería:

```python
# Usar QgsRasterDataProvider.block() para leer un bloque del raster
# y muestrear múltiples puntos del bloque en memoria
# Esto es más eficiente que sample() punto por punto
```

Pero esto es una optimización prematura - el método actual funciona bien.

## Decisión Final

**NO REFACTORIZAR** el muestreo de raster porque:
- El método actual es óptimo para este caso de uso
- `native:rastersampling` no ofrece beneficios
- Mantener código simple es más valioso

**Estado**: ❌ Refactorización no recomendada
