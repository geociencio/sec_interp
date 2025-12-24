# Propuesta: Organización de utils.py en Submódulos Específicos

## Análisis Actual

El archivo `utils.py` tiene **792 líneas** con funciones muy diversas que pueden agruparse por funcionalidad:

| Categoría | Funciones | Líneas Aprox. |
|-----------|-----------|---------------|
| **Geometría Espacial** | `create_buffer_geometry`, `filter_features_by_buffer`, `densify_line_by_interval` | ~250 |
| **Cálculos Geométricos** | `calculate_line_azimuth`, `calculate_step_size`, `get_line_start_point`, `create_distance_area` | ~150 |
| **Muestreo y Perfiles** | `sample_elevation_along_line`, `prepare_profile_context`, `interpolate_elevation` | ~120 |
| **Parsing Estructural** | `parse_strike`, `parse_dip`, `cardinal_to_azimuth` | ~120 |
| **Renderizado/Visualización** | `calculate_bounds`, `create_coordinate_transform`, `calculate_interval` | ~80 |
| **I/O y Utilidades** | `create_shapefile_writer`, `show_user_message` | ~50 |
| **Cálculos Geológicos** | `calculate_apparent_dip` | ~30 |

## Propuesta de Reorganización

### Estructura Propuesta

```
core/
├── __init__.py
├── algorithms.py
├── data_cache.py
├── validation.py
├── utils/                    # NUEVO: Directorio de utilidades
│   ├── __init__.py          # Exports principales
│   ├── geometry.py          # Operaciones geométricas espaciales
│   ├── spatial.py           # Cálculos espaciales y distancias
│   ├── sampling.py          # Muestreo de elevación y perfiles
│   ├── parsing.py           # Parsing de datos estructurales
│   ├── rendering.py         # Utilidades de renderizado/visualización
│   ├── io.py                # I/O y mensajes de usuario
│   └── geology.py           # Cálculos geológicos específicos
└── services/
    ├── __init__.py
    ├── profile_service.py
    ├── geology_service.py
    └── structure_service.py
```

---

## Detalle de Submódulos

### 1. [geometry.py](file:///home/jmbernales/qgispluginsdev/sec_interp/core/utils/geometry.py) - Operaciones Geométricas Espaciales

**Responsabilidad**: Operaciones geométricas complejas usando algoritmos nativos de QGIS.

**Funciones**:
- `create_buffer_geometry()` - Crear buffer usando native:buffer
- `filter_features_by_buffer()` - Filtrado espacial con índice R-tree
- `densify_line_by_interval()` - Densificación de líneas

**Líneas**: ~250

---

### 2. [spatial.py](file:///home/jmbernales/qgispluginsdev/sec_interp/core/utils/spatial.py) - Cálculos Espaciales y Distancias

**Responsabilidad**: Cálculos de distancias, azimuts y geometría básica.

**Funciones**:
- `calculate_line_azimuth()` - Calcular azimut de línea
- `calculate_step_size()` - Calcular tamaño de paso (deprecated)
- `get_line_start_point()` - Obtener punto inicial
- `create_distance_area()` - Crear objeto QgsDistanceArea

**Líneas**: ~150

---

### 3. [sampling.py](file:///home/jmbernales/qgispluginsdev/sec_interp/core/utils/sampling.py) - Muestreo y Perfiles

**Responsabilidad**: Muestreo de elevación y preparación de contexto para perfiles.

**Funciones**:
- `sample_elevation_along_line()` - Muestrear elevación a lo largo de línea
- `prepare_profile_context()` - Preparar contexto común para perfiles
- `interpolate_elevation()` - Interpolar elevación en distancia dada

**Líneas**: ~120

---

### 4. [parsing.py](file:///home/jmbernales/qgispluginsdev/sec_interp/core/utils/parsing.py) - Parsing de Datos Estructurales

**Responsabilidad**: Parsing de mediciones estructurales (strike/dip) en múltiples formatos.

**Funciones**:
- `parse_strike()` - Parsear strike (numérico o notación de campo)
- `parse_dip()` - Parsear dip (numérico o notación de campo)
- `cardinal_to_azimuth()` - Convertir direcciones cardinales a azimut

**Líneas**: ~120

---

### 5. [rendering.py](file:///home/jmbernales/qgispluginsdev/sec_interp/core/utils/rendering.py) - Utilidades de Renderizado

**Responsabilidad**: Cálculos para visualización y renderizado de perfiles.

**Funciones**:
- `calculate_bounds()` - Calcular límites min/max con padding
- `create_coordinate_transform()` - Crear función de transformación de coordenadas
- `calculate_interval()` - Calcular intervalo para etiquetas de ejes

**Líneas**: ~80

---

### 6. [io.py](file:///home/jmbernales/qgispluginsdev/sec_interp/core/utils/io.py) - I/O y Mensajes

**Responsabilidad**: Entrada/salida de archivos y mensajes de usuario.

**Funciones**:
- `create_shapefile_writer()` - Crear writer de shapefile
- `show_user_message()` - Mostrar mensajes al usuario con logging

**Líneas**: ~50

---

### 7. [geology.py](file:///home/jmbernales/qgispluginsdev/sec_interp/core/utils/geology.py) - Cálculos Geológicos

**Responsabilidad**: Cálculos específicos de geología estructural.

**Funciones**:
- `calculate_apparent_dip()` - Calcular buzamiento aparente

**Líneas**: ~30

---

## Archivo [\_\_init\_\_.py](file:///home/jmbernales/qgispluginsdev/sec_interp/core/utils/__init__.py)

Para mantener compatibilidad hacia atrás, exportar todas las funciones:

```python
"""
Core utilities package.

Organized by functionality:
- geometry: Spatial geometry operations
- spatial: Distance and azimuth calculations
- sampling: Elevation sampling and profiling
- parsing: Structural data parsing
- rendering: Visualization utilities
- io: File I/O and user messages
- geology: Geological calculations
"""

# Geometry operations
from .geometry import (
    create_buffer_geometry,
    filter_features_by_buffer,
    densify_line_by_interval,
)

# Spatial calculations
from .spatial import (
    calculate_line_azimuth,
    calculate_step_size,
    get_line_start_point,
    create_distance_area,
)

# Sampling and profiling
from .sampling import (
    sample_elevation_along_line,
    prepare_profile_context,
    interpolate_elevation,
)

# Structural data parsing
from .parsing import (
    parse_strike,
    parse_dip,
    cardinal_to_azimuth,
)

# Rendering utilities
from .rendering import (
    calculate_bounds,
    create_coordinate_transform,
    calculate_interval,
)

# I/O utilities
from .io import (
    create_shapefile_writer,
    show_user_message,
)

# Geological calculations
from .geology import (
    calculate_apparent_dip,
)

__all__ = [
    # Geometry
    'create_buffer_geometry',
    'filter_features_by_buffer',
    'densify_line_by_interval',
    # Spatial
    'calculate_line_azimuth',
    'calculate_step_size',
    'get_line_start_point',
    'create_distance_area',
    # Sampling
    'sample_elevation_along_line',
    'prepare_profile_context',
    'interpolate_elevation',
    # Parsing
    'parse_strike',
    'parse_dip',
    'cardinal_to_azimuth',
    # Rendering
    'calculate_bounds',
    'create_coordinate_transform',
    'calculate_interval',
    # I/O
    'create_shapefile_writer',
    'show_user_message',
    # Geology
    'calculate_apparent_dip',
]
```

---

## Beneficios

### 1. Organización Clara
- **Fácil navegación**: Encontrar funciones por categoría
- **Archivos más pequeños**: ~50-250 líneas por archivo vs 792 líneas
- **Responsabilidades claras**: Cada módulo tiene un propósito específico

### 2. Mantenibilidad
- **Cambios localizados**: Modificar parsing no afecta geometría
- **Tests específicos**: Test por módulo de funcionalidad
- **Documentación enfocada**: Cada módulo documenta su dominio

### 3. Reusabilidad
- **Imports selectivos**: `from core.utils.parsing import parse_strike`
- **Dependencias claras**: Ver qué módulos dependen de qué
- **Extensibilidad**: Agregar nuevas utilidades en módulo apropiado

### 4. Compatibilidad
- **Sin breaking changes**: `from core import utils as scu` sigue funcionando
- **Imports existentes**: `scu.parse_strike()` funciona igual
- **Migración gradual**: Código existente no necesita cambios

---

## Plan de Implementación

### Fase 1: Crear Estructura
1. Crear directorio `core/utils/`
2. Crear archivos vacíos para cada submódulo
3. Crear `__init__.py` con exports

### Fase 2: Migrar Funciones
1. Copiar funciones a submódulos apropiados
2. Actualizar imports dentro de cada submódulo
3. Verificar que `__init__.py` exporta todo

### Fase 3: Actualizar Imports (Opcional)
1. Actualizar servicios para usar imports específicos
2. Mantener `utils.py` como alias deprecado (opcional)

### Fase 4: Verificación
1. Ejecutar tests
2. Verificar que plugin carga
3. Probar funcionalidad completa

---

## Compatibilidad hacia Atrás

### Opción 1: Mantener utils.py como Alias (Recomendado)

Convertir `utils.py` en un archivo que re-exporta todo:

```python
# core/utils.py
"""
Legacy utils module - imports from new utils package.
Maintained for backward compatibility.
"""
from .utils import *  # noqa: F401, F403

import warnings
warnings.warn(
    "Importing from core.utils is deprecated. "
    "Use core.utils.geometry, core.utils.parsing, etc. instead.",
    DeprecationWarning,
    stacklevel=2
)
```

### Opción 2: Eliminar utils.py

Si todos los imports se actualizan, `utils.py` puede eliminarse completamente.

---

## Estimación

- **Tiempo**: 2-3 horas
- **Riesgo**: Bajo (con tests)
- **Impacto**: Alto (mejor organización)

---

## Recomendación

✅ **Implementar esta refactorización** después de la actual refactorización de servicios para:
1. Consolidar mejoras de organización
2. Establecer patrón claro para futuras utilidades
3. Facilitar mantenimiento a largo plazo

La estructura propuesta es escalable y sigue mejores prácticas de organización de código Python.
