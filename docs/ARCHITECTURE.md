# Arquitectura del Plugin SecInterp

## Visión General

SecInterp es un plugin de QGIS para generar perfiles geológicos de sección transversal. La arquitectura ha sido refactorizada para seguir principios de diseño modular con separación clara de responsabilidades.

---

## Estructura de Directorios

```
sec_interp/
├── __init__.py                 # Punto de entrada del plugin
├── metadata.txt                # Metadatos del plugin
├── icon.png                    # Icono del plugin
├── logger_config.py            # Configuración de logging
│
├── core/                       # Lógica de negocio principal
│   ├── __init__.py
│   ├── algorithms.py           # Orquestador principal (778 líneas)
│   ├── data_cache.py           # Cache de datos para performance
│   ├── validation.py           # Validación de inputs
│   │
│   ├── services/               # Servicios especializados
│   │   ├── __init__.py
│   │   ├── profile_service.py      # Generación de perfiles topográficos
│   │   ├── geology_service.py      # Procesamiento geológico
│   │   └── structure_service.py    # Proyección de estructuras
│   │
│   └── utils/                  # Utilidades organizadas por función
│       ├── __init__.py
│       ├── geometry.py         # Operaciones geométricas espaciales
│       ├── spatial.py          # Cálculos de distancias y azimuts
│       ├── sampling.py         # Muestreo de elevación
│       ├── parsing.py          # Parsing de datos estructurales
│       ├── rendering.py        # Utilidades de visualización
│       ├── io.py               # I/O y mensajes de usuario
│       └── geology.py          # Cálculos geológicos
│
├── gui/                        # Interfaz de usuario
│   ├── __init__.py
│   ├── main_dialog.py          # Diálogo principal
│   ├── preview_renderer.py     # Renderizado de previsualizaciones
│   ├── legend_widget.py        # Widget de leyenda
│   └── ui/                     # Archivos UI generados
│
├── exporters/                  # Exportadores de datos
│   ├── __init__.py
│   ├── base_exporter.py        # Clase base abstracta
│   ├── csv_exporter.py         # Exportación a CSV
│   ├── shp_exporter.py         # Exportación a Shapefile
│   ├── image_exporter.py       # Exportación a imágenes
│   ├── svg_exporter.py         # Exportación a SVG
│   └── pdf_exporter.py         # Exportación a PDF
│
├── resources/                  # Recursos del plugin
├── i18n/                       # Traducciones
├── docs/                       # Documentación
├── tests/                      # Tests unitarios
└── scripts/                    # Scripts de utilidad
```

---

## Componentes Principales

### 1. Core - Lógica de Negocio

#### `algorithms.py` - Orquestador Principal
**Responsabilidad:** Coordinar el flujo de trabajo principal del plugin

**Clase Principal:** `SecInterp`
- Inicializa servicios y componentes
- Maneja eventos de UI
- Coordina procesamiento de datos
- Gestiona exportación de resultados

**Dependencias:**
- `ProfileService` - Generación de perfiles
- `GeologyService` - Procesamiento geológico
- `StructureService` - Proyección de estructuras
- `DataCache` - Cache de datos
- `PreviewRenderer` - Renderizado de previsualizaciones

#### `data_cache.py` - Cache de Datos
**Responsabilidad:** Cachear datos procesados para mejorar performance

**Funcionalidad:**
- Cache de perfiles topográficos
- Cache de datos geológicos
- Cache de datos estructurales
- Invalidación de cache cuando cambian inputs

---

### 2. Services - Servicios Especializados

#### `ProfileService` - Perfiles Topográficos
**Responsabilidad:** Generar perfiles de elevación a lo largo de líneas de sección

**Método Principal:**
```python
generate_topographic_profile(
    line_layer: QgsVectorLayer,
    raster_layer: QgsRasterLayer,
    band_number: int
) -> list[tuple[float, float]]
```

**Funcionalidad:**
- Densificación de líneas a resolución del raster
- Muestreo de elevación en puntos densificados
- Cálculo de distancias a lo largo de la línea

#### `GeologyService` - Procesamiento Geológico
**Responsabilidad:** Calcular intersecciones entre línea de sección y polígonos de afloramientos

**Método Principal:**
```python
generate_geological_profile(
    line_layer: QgsVectorLayer,
    raster_layer: QgsRasterLayer,
    outcrop_layer: QgsVectorLayer,
    outcrop_name_field: str,
    band_number: int
) -> list[tuple[float, float, str]]
```

**Funcionalidad:**
- Intersección de línea con polígonos de afloramientos
- Muestreo de elevación en puntos de intersección
- Asociación de nombres de formaciones geológicas

#### `StructureService` - Proyección de Estructuras
**Responsabilidad:** Proyectar mediciones estructurales (rumbo/buzamiento) en el plano de sección

**Método Principal:**
```python
project_structures(
    line_layer: QgsVectorLayer,
    structural_layer: QgsVectorLayer,
    buffer_distance: float,
    line_azimuth: float,
    dip_field: str,
    strike_field: str
) -> list[tuple[float, float, float, float]]
```

**Funcionalidad:**
- Filtrado espacial con buffer
- Parsing de mediciones estructurales
- Cálculo de buzamiento aparente
- Proyección en plano de sección

---

### 3. Utils - Utilidades Organizadas

#### `geometry.py` - Operaciones Geométricas
**Funciones Helper:**
- `create_memory_layer()` - Crear capas temporales
- `get_line_vertices()` - Extraer vértices de líneas
- `run_processing_algorithm()` - Ejecutar algoritmos QGIS

**Funciones Principales:**
- `create_buffer_geometry()` - Crear buffers usando algoritmos nativos
- `filter_features_by_buffer()` - Filtrado espacial con índice R-tree
- `densify_line_by_interval()` - Densificar líneas a intervalos regulares

#### `spatial.py` - Cálculos Espaciales
- `calculate_line_azimuth()` - Calcular azimut de línea
- `get_line_start_point()` - Obtener punto inicial
- `create_distance_area()` - Crear objeto de medición de distancias

#### `sampling.py` - Muestreo de Elevación
- `sample_elevation_along_line()` - Muestrear elevación a lo largo de línea
- `prepare_profile_context()` - Preparar contexto para perfiles
- `interpolate_elevation()` - Interpolar elevación en punto dado

#### `parsing.py` - Parsing de Datos Estructurales
- `parse_strike()` - Parsear rumbo (numérico o notación de campo)
- `parse_dip()` - Parsear buzamiento (numérico o notación de campo)
- `cardinal_to_azimuth()` - Convertir direcciones cardinales a azimut

#### `rendering.py` - Utilidades de Visualización
- `calculate_bounds()` - Calcular límites de datos
- `create_coordinate_transform()` - Crear transformación de coordenadas
- `calculate_interval()` - Calcular intervalos para ejes

#### `io.py` - I/O y Mensajes
- `create_shapefile_writer()` - Crear writer de shapefile
- `show_user_message()` - Mostrar mensajes al usuario con logging

#### `geology.py` - Cálculos Geológicos
- `calculate_apparent_dip()` - Calcular buzamiento aparente

---

### 4. GUI - Interfaz de Usuario

#### `main_dialog.py` - Diálogo Principal
**Responsabilidad:** Interfaz principal del usuario

**Funcionalidad:**
- Selección de capas y parámetros
- Validación de inputs
- Generación de previsualizaciones
- Exportación de resultados

#### `preview_renderer.py` - Renderizado de Previsualizaciones
**Responsabilidad:** Renderizar previsualizaciones interactivas

**Funcionalidad:**
- Renderizado de perfil topográfico
- Renderizado de datos geológicos
- Renderizado de estructuras proyectadas
- Manejo de exageración vertical

---

### 5. Exporters - Exportadores de Datos

#### Arquitectura de Exportadores
**Patrón:** Factory + Strategy

**Clase Base:** `BaseExporter` (abstracta)
- Define interfaz común para todos los exportadores
- Manejo de errores consistente

**Exportadores Concretos:**
- `CSVExporter` - Exportación a CSV
- `ShapefileExporter` - Exportación a Shapefile
- `ImageExporter` - Exportación a PNG/JPG
- `SVGExporter` - Exportación a SVG
- `PDFExporter` - Exportación a PDF

**Factory:** `get_exporter(extension, settings)`
- Selecciona exportador apropiado según extensión
- Configura exportador con settings

---

## Flujo de Datos

### Generación de Perfil

```
Usuario selecciona capas → Validación de inputs
                              ↓
                    SecInterp.process_profile_data()
                              ↓
                    ┌─────────┴─────────┐
                    ↓                   ↓
          ProfileService        GeologyService
          (topografía)          (geología)
                    ↓                   ↓
                    └─────────┬─────────┘
                              ↓
                    StructureService
                    (estructuras)
                              ↓
                    PreviewRenderer
                    (visualización)
```

### Exportación de Datos

```
Usuario solicita exportación → Validación de ruta
                                      ↓
                              Generación de datos
                              (ProfileService, etc.)
                                      ↓
                              Factory selecciona
                              exportador apropiado
                                      ↓
                              Exportador escribe
                              archivos de salida
```

---

## Patrones de Diseño Utilizados

### 1. Service Layer Pattern
**Ubicación:** `core/services/`

**Propósito:** Separar lógica de negocio en servicios especializados

**Beneficios:**
- Separación de responsabilidades
- Facilita testing
- Código más mantenible

### 2. Factory Pattern
**Ubicación:** `exporters/__init__.py`

**Propósito:** Crear exportadores apropiados según tipo de archivo

**Beneficios:**
- Extensibilidad
- Desacoplamiento
- Configuración centralizada

### 3. Strategy Pattern
**Ubicación:** `exporters/`

**Propósito:** Diferentes estrategias de exportación intercambiables

**Beneficios:**
- Flexibilidad
- Facilita agregar nuevos formatos
- Código limpio

### 4. Helper Functions Pattern
**Ubicación:** `core/utils/geometry.py`

**Propósito:** Funciones reusables para eliminar duplicación

**Beneficios:**
- DRY (Don't Repeat Yourself)
- Consistencia
- Facilita mantenimiento

---

## Principios de Diseño

### SOLID Principles

#### Single Responsibility Principle (SRP)
- Cada servicio tiene una responsabilidad única
- Cada módulo utils tiene una función específica

#### Open/Closed Principle (OCP)
- Exportadores extensibles sin modificar código existente
- Servicios pueden extenderse mediante herencia

#### Dependency Inversion Principle (DIP)
- `SecInterp` depende de abstracciones (servicios)
- Servicios se inyectan en constructor

### DRY (Don't Repeat Yourself)
- Funciones helper eliminan código duplicado
- Utilidades compartidas en módulos utils

### Separation of Concerns
- GUI separado de lógica de negocio
- Servicios separados por dominio
- Utils organizados por función

---

## Dependencias Externas

### QGIS API
- `qgis.core` - Clases core de QGIS
- `qgis.PyQt` - Bindings de Qt
- `qgis.processing` - Algoritmos de procesamiento

### Python Standard Library
- `pathlib` - Manejo de rutas
- `math` - Cálculos matemáticos
- `re` - Expresiones regulares
- `tempfile` - Archivos temporales

---

## Testing

### Estructura de Tests
```
tests/
├── test_services/
│   ├── test_profile_service.py
│   ├── test_geology_service.py
│   └── test_structure_service.py
├── test_utils/
│   ├── test_geometry.py
│   ├── test_spatial.py
│   └── test_parsing.py
└── test_exporters/
    └── test_exporters.py
```

### Estrategia de Testing
- **Unit Tests:** Servicios y utilidades individuales
- **Integration Tests:** Flujo completo de procesamiento
- **UI Tests:** Validación de interfaz (manual)

---

## Performance

### Optimizaciones Implementadas

#### 1. Data Caching
- Cache de perfiles topográficos
- Cache de datos geológicos
- Invalidación inteligente

#### 2. Spatial Indexing
- Uso de `QgsSpatialIndex` para filtrado espacial
- R-tree para búsquedas eficientes

#### 3. Native Algorithms
- Uso de algoritmos nativos de QGIS
- Mejor performance que implementaciones manuales

---

## Deployment

### Script de Deployment
**Ubicación:** `scripts/deploy.sh`

**Funcionalidad:**
- Copia archivos al directorio de plugins de QGIS
- Crea backup de instalación anterior
- Compila traducciones
- Copia estructura de directorios completa

### Comando
```bash
make deploy
```

---

## Extensibilidad

### Agregar Nuevo Servicio

1. Crear archivo en `core/services/`
2. Implementar lógica del servicio
3. Agregar a `core/services/__init__.py`
4. Inicializar en `SecInterp.__init__()`
5. Usar en `SecInterp._process_profile_data()`

### Agregar Nuevo Exportador

1. Crear clase que herede de `BaseExporter`
2. Implementar método `export()`
3. Agregar a factory en `exporters/__init__.py`
4. Actualizar mapeo de extensiones

### Agregar Nueva Utilidad

1. Determinar módulo apropiado en `core/utils/`
2. Implementar función con docstring
3. Agregar a exports en `core/utils/__init__.py`
4. Usar en código donde sea necesario

---

## Mantenimiento

### Guías de Código
- Seguir PEP 8 para estilo de Python
- Usar type hints donde sea posible
- Documentar con docstrings de Google style
- Commits siguiendo Conventional Commits

### Refactorizaciones Futuras
- [ ] Tests unitarios completos
- [ ] Documentación de API
- [ ] Optimización adicional de performance
- [ ] Internacionalización completa

---

## Conclusión

La arquitectura refactorizada del plugin SecInterp sigue principios de diseño sólidos, está bien organizada y es fácil de mantener y extender. La separación en servicios, utilidades modulares y funciones helper proporciona una base sólida para futuro desarrollo.

**Versión:** Post-refactorización 2025-12-07  
**Estado:** ✅ Estable y en producción
