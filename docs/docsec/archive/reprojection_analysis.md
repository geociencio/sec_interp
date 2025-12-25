# Análisis: Reproyección de Coordenadas

## Estado Actual

Actualmente, el plugin **NO realiza reproyección de coordenadas**.

### Lógica Existente
- Verifica si las capas tienen el mismo CRS.
- Si los CRS son diferentes, advierte al usuario o falla.
- Confía en que el usuario prepare los datos en el CRS correcto.

Ejemplo en `algorithms.py`:
```python
# Línea 1047
# "Check that line and structural layers use the same CRS"
```

## Propuesta: Usar `native:reprojectlayer`

Esto no sería una refactorización (cambiar cómo se hace algo), sino una **NUEVA CARACTERÍSTICA** (hacer algo que antes no se hacía).

### Implementación Hipotética

Para cada capa de entrada (geología, estructuras), verificaríamos el CRS contra la capa de línea:

```python
def ensure_crs_match(layer, target_crs):
    if layer.crs() != target_crs:
        logger.info(f"Reprojecting layer from {layer.crs().authid()} to {target_crs.authid()}")
        result = processing.run("native:reprojectlayer", {
            'INPUT': layer,
            'TARGET_CRS': target_crs,
            'OUTPUT': 'memory:'
        })
        return result['OUTPUT']
    return layer
```

### Ventajas
1. **Mejor Experiencia de Usuario**: No requiere que el usuario reproyecte manualmente.
2. **Menos Errores**: Evita problemas sutiles si el usuario ignora las advertencias.

### Desventajas / Riesgos
1. **Rendimiento**: Reproyectar capas grandes puede ser lento.
2. **Complejidad**: Añade pasos extra al flujo de procesamiento.
3. **Manejo de Rasters**: Reproyectar rasters (`gdal:warp`) es mucho más complejo y costoso que vectores.

## Conclusión

**NO HAY CÓDIGO PARA REFACTORIZAR**.

Implementar reproyección automática sería una mejora valiosa, pero cae fuera del alcance de "refactorización de código existente con algoritmos nativos".

## Recomendación

**POSPONER** para una fase de "Nuevas Características".

**Razón**:
- No estamos reemplazando código ineficiente con nativo.
- Estamos añadiendo lógica nueva compleja.
- El plugin funciona correctamente tal como está (con advertencias).

**Estado**: ⏸️ No aplicable como refactorización
