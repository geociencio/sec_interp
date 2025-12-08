# Refactorización de algorithms.py en Clases de Servicio

## Objetivo

Refactorizar el archivo `algorithms.py` (1263 líneas) dividiéndolo en clases de servicio más pequeñas y enfocadas para mejorar la mantenibilidad, testabilidad y organización del código.

## Análisis de la Estructura Actual

El archivo `algorithms.py` contiene actualmente:

1. **DataCache** (líneas 60-127): Gestión de caché para datos procesados
2. **SecInterp** (líneas 130-1263): Clase principal del plugin con múltiples responsabilidades:
   - Gestión de UI y ciclo de vida del plugin
   - Procesamiento de perfiles topográficos
   - Procesamiento de perfiles geológicos
   - Proyección de estructuras geológicas
   - Exportación de datos
   - Renderizado de previsualizaciones

### Responsabilidades Identificadas

| Responsabilidad | Métodos Actuales | Líneas Aprox. |
|----------------|------------------|---------------|
| **Plugin Lifecycle** | `__init__`, `initGui`, `unload`, `run`, `add_action` | ~150 |
| **Data Processing Orchestration** | `process_data`, `_process_profile_data`, `_get_and_validate_inputs` | ~300 |
| **Topographic Profile** | `topographic_profile` | ~40 |
| **Geological Profile** | `geol_profile` | ~170 |
| **Structural Projection** | `project_structures` | ~220 |
| **Export** | `save_profile_line` | ~140 |
| **Preview** | `draw_preview` | ~65 |

## Propuesta de Refactorización

### Estructura de Archivos Propuesta

```
core/
├── __init__.py
├── algorithms.py          # SecInterp (orquestador principal)
├── data_cache.py          # DataCache (movido)
├── services/
│   ├── __init__.py
│   ├── profile_service.py    # ProfileService (NUEVO)
│   ├── geology_service.py    # GeologyService (NUEVO)
│   └── structure_service.py  # StructureService (NUEVO)
├── utils.py
└── validation.py
```

### Clases de Servicio

#### 1. ProfileService

**Responsabilidad**: Generación de perfiles topográficos

**Métodos**:
- `generate_topographic_profile(line_layer, raster_layer, band_number)` → Lista de (dist, elev)

**Dependencias**:
- `utils.py`: `sample_elevation_along_line`, `create_distance_area`

---

#### 2. GeologyService

**Responsabilidad**: Generación de perfiles geológicos mediante intersección con outcrops

**Métodos**:
- `generate_geological_profile(line_layer, raster_layer, outcrop_layer, geology_field, band_number)` → Lista de (dist, elev, geology)

**Dependencias**:
- `qgis.processing`: algoritmo `native:intersection`
- `utils.py`: `calculate_step_size`, `create_distance_area`

---

#### 3. StructureService

**Responsabilidad**: Proyección de mediciones estructurales al plano de sección

**Métodos**:
- `project_structures(line_layer, structural_layer, buffer_distance, line_azimuth, dip_field, strike_field)` → Lista de (dist, apparent_dip)

**Dependencias**:
- `utils.py`: `create_buffer_geometry`, `filter_features_by_buffer`, `parse_strike`, `parse_dip`, `calculate_apparent_dip`, `create_distance_area`
- `validation.py`: `validate_angle_range`

---

## Cambios Propuestos

### Core Services

#### [NEW] [profile_service.py](file:///home/jmbernales/qgispluginsdev/sec_interp/core/services/profile_service.py)

Nueva clase de servicio para perfiles topográficos. Encapsula la lógica de muestreo de elevación a lo largo de una línea de sección.

**Contenido**:
- Clase `ProfileService` con método `generate_topographic_profile`
- Manejo de errores específico para validación de geometría
- Logging detallado del proceso

---

#### [NEW] [geology_service.py](file:///home/jmbernales/qgispluginsdev/sec_interp/core/services/geology_service.py)

Nueva clase de servicio para perfiles geológicos. Gestiona la intersección de líneas de sección con polígonos de afloramientos.

**Contenido**:
- Clase `GeologyService` con método `generate_geological_profile`
- Lógica de intersección usando `native:intersection`
- Procesamiento de geometrías MultiLineString
- Interpolación y muestreo de elevación

---

#### [NEW] [structure_service.py](file:///home/jmbernales/qgispluginsdev/sec_interp/core/services/structure_service.py)

Nueva clase de servicio para proyección de estructuras. Maneja el filtrado espacial y cálculo de buzamiento aparente.

**Contenido**:
- Clase `StructureService` con método `project_structures`
- Filtrado espacial por buffer
- Parsing y validación de ángulos (dip/strike)
- Cálculo de buzamiento aparente
- Logging detallado con contadores de éxito/fallo

---

#### [NEW] [data_cache.py](file:///home/jmbernales/qgispluginsdev/sec_interp/core/data_cache.py)

Mover la clase `DataCache` a su propio archivo para mejor organización.

**Contenido**:
- Clase `DataCache` (movida desde `algorithms.py`)
- Sin cambios en funcionalidad

---

#### [MODIFY] [algorithms.py](file:///home/jmbernales/qgispluginsdev/sec_interp/core/algorithms.py)

Refactorizar para usar servicios en lugar de métodos internos.

**Cambios**:
1. Importar servicios: `ProfileService`, `GeologyService`, `StructureService`, `DataCache`
2. Inicializar servicios en `__init__`:
   ```python
   self.profile_service = ProfileService()
   self.geology_service = GeologyService()
   self.structure_service = StructureService()
   ```
3. Eliminar métodos movidos a servicios:
   - `topographic_profile` → `self.profile_service.generate_topographic_profile`
   - `geol_profile` → `self.geology_service.generate_geological_profile`
   - `project_structures` → `self.structure_service.project_structures`
4. Actualizar llamadas en `_process_profile_data` y `save_profile_line`
5. Mantener métodos de orquestación: `process_data`, `_process_profile_data`, `save_profile_line`, `draw_preview`

**Reducción esperada**: ~430 líneas → archivo más manejable de ~830 líneas

---

#### [NEW] [\_\_init\_\_.py](file:///home/jmbernales/qgispluginsdev/sec_interp/core/services/__init__.py)

Archivo de inicialización para el paquete de servicios.

**Contenido**:
```python
from .profile_service import ProfileService
from .geology_service import GeologyService
from .structure_service import StructureService

__all__ = ['ProfileService', 'GeologyService', 'StructureService']
```

---

## Beneficios de la Refactorización

### Mantenibilidad
- **Separación de responsabilidades**: Cada servicio tiene una única responsabilidad bien definida
- **Archivos más pequeños**: Más fáciles de navegar y entender (~200-250 líneas por servicio)
- **Cohesión mejorada**: Código relacionado agrupado lógicamente

### Testabilidad
- **Servicios independientes**: Pueden ser testeados en aislamiento
- **Mocking simplificado**: Fácil inyectar mocks de servicios en tests
- **Cobertura granular**: Tests específicos para cada tipo de procesamiento

### Extensibilidad
- **Nuevas funcionalidades**: Agregar nuevos servicios sin modificar existentes
- **Reusabilidad**: Servicios pueden ser usados por otros componentes
- **Configuración**: Servicios pueden recibir configuración en constructor

### Organización del Código
- **Estructura clara**: Jerarquía de directorios refleja arquitectura
- **Imports explícitos**: Dependencias claras entre módulos
- **Navegación mejorada**: Encontrar código específico es más rápido

---

## Plan de Migración

### Fase 1: Crear Infraestructura
1. Crear directorio `core/services/`
2. Crear `core/services/__init__.py`
3. Crear `core/data_cache.py` y mover clase `DataCache`

### Fase 2: Crear Servicios
1. Crear `ProfileService` en `profile_service.py`
2. Crear `GeologyService` en `geology_service.py`
3. Crear `StructureService` en `structure_service.py`

### Fase 3: Refactorizar SecInterp
1. Actualizar imports en `algorithms.py`
2. Inicializar servicios en `__init__`
3. Reemplazar llamadas a métodos por llamadas a servicios
4. Eliminar métodos movidos

### Fase 4: Actualizar Tests
1. Actualizar imports en tests
2. Verificar que tests existentes pasan
3. Agregar tests específicos para servicios (opcional)

---

## Verificación

### Tests Automatizados
```bash
# Ejecutar suite de tests existente
pytest tests/

# Verificar imports
python -c "from sec_interp.core.services import ProfileService, GeologyService, StructureService"
```

### Verificación Manual
1. **Cargar plugin en QGIS**: Verificar que no hay errores de importación
2. **Generar perfil topográfico**: Validar funcionalidad básica
3. **Generar perfil geológico**: Validar intersección con outcrops
4. **Proyectar estructuras**: Validar cálculo de buzamiento aparente
5. **Exportar datos**: Validar que CSV y Shapefiles se generan correctamente
6. **Verificar caché**: Validar que el caché funciona con nueva arquitectura

---

## Consideraciones de Diseño

### Inyección de Dependencias
Los servicios se inicializan en el constructor de `SecInterp` y se mantienen como atributos de instancia. Esto permite:
- Fácil reemplazo con mocks en tests
- Configuración centralizada
- Reutilización de instancias

### Manejo de Errores
Cada servicio mantiene su propio manejo de errores y logging, pero propaga excepciones al orquestador (`SecInterp`) para decisiones de UI.

### Logging
Los servicios usan el mismo sistema de logging (`logger_config.py`) para mantener consistencia en los logs.

### Compatibilidad
La refactorización es **interna** - la API pública del plugin (`SecInterp`) no cambia, por lo que no hay breaking changes para usuarios o código externo.

---

## Riesgos y Mitigaciones

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|--------------|---------|------------|
| Errores de importación circular | Baja | Alto | Servicios no se importan entre sí, solo usan `utils` y `validation` |
| Regresión en funcionalidad | Media | Alto | Tests exhaustivos antes y después de refactorización |
| Pérdida de contexto en logs | Baja | Medio | Mantener logging detallado en servicios |
| Complejidad adicional | Baja | Bajo | Estructura clara compensa complejidad inicial |

---

## Próximos Pasos

Una vez aprobado este plan:

1. Crear estructura de directorios y archivos base
2. Implementar servicios uno por uno
3. Actualizar `SecInterp` para usar servicios
4. Ejecutar tests y verificación manual
5. Documentar cambios en walkthrough
