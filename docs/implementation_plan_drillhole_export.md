# Refactorización: Extracción de DrillholeService

## Goal Description
El objetivo es extraer la lógica de procesamiento de datos de sondajes (collares, surveys, intervalos) que actualmente reside de forma monolítica en [drillsec/drillsec.py](file:///home/jmbernales/qgispluginsdev/sec_interp/drillsec/drillsec.py) hacia un servicio dedicado [core/services/drillhole_service.py](file:///home/jmbernales/qgispluginsdev/sec_interp/core/services/drillhole_service.py). Esto alineará el manejo de sondajes con la nueva arquitectura del plugin (Controller/Services) implementada en la versión 1.2.0.

## User Review Required
> [!IMPORTANT]
> Esta refactorización moverá lógica crítica. Se requiere confirmar que los datos de prueba ([drillsec/Drilldata/](file:///home/jmbernales/qgispluginsdev/sec_interp/drillsec/Drilldata)) son suficientes para verificar que la extracción no altera los cálculos.

## Proposed Changes

### Core Services
Se creará un nuevo servicio que encapsule las reglas de negocio de los sondajes.

#### [NEW] [drillhole_service.py](file:///home/jmbernales/qgispluginsdev/sec_interp/core/services/drillhole_service.py)
*   **Clase [DrillholeService](file:///home/jmbernales/qgispluginsdev/sec_interp/core/services/drillhole_service.py#24-309)**:
    *   Método [project_collars](file:///home/jmbernales/qgispluginsdev/sec_interp/core/services/drillhole_service.py#27-147): Migrado desde `DrillSecPlugin._project_collars`.
    *   Método [process_intervals](file:///home/jmbernales/qgispluginsdev/sec_interp/core/services/drillhole_service.py#148-309): Migrado desde `DrillSecPlugin._process_intervals`.
    *   Validaciones propias usando [core/validation.py](file:///home/jmbernales/qgispluginsdev/sec_interp/core/validation.py).

#### [NEW] [drillhole.py](file:///home/jmbernales/qgispluginsdev/sec_interp/core/utils/drillhole.py)

## Fase 2: Integración de Interfaz de Usuario (UI)

### GUI
#### [NEW] [drillhole_page.py](file:///home/jmbernales/qgispluginsdev/sec_interp/gui/ui/pages/drillhole_page.py)
 - Nueva clase [DrillholePage](file:///home/jmbernales/qgispluginsdev/sec_interp/gui/ui/pages/drillhole_page.py#20-300) que hereda de `BasePage`.
 - Implementa selección de capas:
   - **Collares**: Capa, ID, X, Y, Z (Opcional - Empty), Depth.
     - *Nota*: Si el campo Z está vacío, se obtendrá la elevación del DEM seleccionado.
     - Checkbox para usar geometría vs campos X/Y.
   - **Survey**: Capa, ID, Depth, Azimuth, Inclination.
   - **Intervalos**: Capa, ID, From, To, Lithology.
 - Validación de campos obligatorios ([is_complete](file:///home/jmbernales/qgispluginsdev/sec_interp/gui/ui/pages/drillhole_page.py#264-300)).

#### [MODIFY] [main_window.py](file:///home/jmbernales/qgispluginsdev/sec_interp/gui/ui/main_window.py)
 - Instanciar `self.page_drillhole = DrillholePage()`.
 - Agregar a `sidebar` ("Drillholes", icon="mActionDataSourceManager.svg" o similar).
 - Agregar a `stacked_widget`.

#### [MODIFY] [main_dialog.py](file:///home/jmbernales/qgispluginsdev/sec_interp/gui/main_dialog.py)
 - Actualizar [get_selected_values](file:///home/jmbernales/qgispluginsdev/sec_interp/gui/main_dialog.py#338-396) para incluir datos de `page_drillhole`.
 - Actualizar [update_button_state](file:///home/jmbernales/qgispluginsdev/sec_interp/gui/main_dialog.py#306-337) y [update_preview_checkbox_states](file:///home/jmbernales/qgispluginsdev/sec_interp/gui/main_dialog.py#262-305): La visualización de sondajes requiere capas de collar, survey e intervalos (o al menos collar).

## Verification Plan

### Test Data (Drillsec)
- **Collar**: [DrillCollar.csv](file:///home/jmbernales/qgispluginsdev/sec_interp/drillsec/Drilldata/DrillCollar.csv)
- **Survey**: [DrillsurveySummary.csv](file:///home/jmbernales/qgispluginsdev/sec_interp/drillsec/Drilldata/DrillsurveySummary.csv)
- **Intervals**: `DillLith.csv` (Lithology), [DrillOx.csv](file:///home/jmbernales/qgispluginsdev/sec_interp/drillsec/Drilldata/DrillOx.csv) (Oxidation)
#### [MODIFY] [controller.py](file:///home/jmbernales/qgispluginsdev/sec_interp/core/controller.py)
*   Integrar [DrillholeService](file:///home/jmbernales/qgispluginsdev/sec_interp/core/services/drillhole_service.py#24-309) en `ProfileController.__init__`.
*   Agregar llamadas al servicio en [generate_profile_data](file:///home/jmbernales/qgispluginsdev/sec_interp/core/controller.py#41-191).

### Plugin Entry Point
#### [MODIFY] [drillsec.py](file:///home/jmbernales/qgispluginsdev/sec_interp/drillsec/drillsec.py)
*   Eliminar métodos privados gigantes `_project_collars` y `_process_intervals`.
*   Delegar la ejecución al [ProfileController](file:///home/jmbernales/qgispluginsdev/sec_interp/core/controller.py#19-295).


## Fase 4: Auto-cálculo de Profundidad
El usuario solicita que si el campo "Total Depth" se deja en blanco, se calcule automáticamente a partir de los datos de survey o intervalos.

### [MODIFY] [core/utils/drillhole.py](file:///home/jmbernales/qgispluginsdev/sec_interp/core/utils/drillhole.py)
*   Actualizar [calculate_drillhole_trajectory](file:///home/jmbernales/qgispluginsdev/sec_interp/core/utils/drillhole.py#12-140):
    *   Agregar argumento opcional `total_depth`.
    *   Si `total_depth` > `last_survey_depth`: Extrapolar (línea recta usando último azimut/inclinación) hasta `total_depth`.

### [MODIFY] [core/services/drillhole_service.py](file:///home/jmbernales/qgispluginsdev/sec_interp/core/services/drillhole_service.py)
*   Actualizar [process_intervals](file:///home/jmbernales/qgispluginsdev/sec_interp/core/services/drillhole_service.py#148-309):
    *   Recuperar el valor de `collar_depth` (actualmente ignorado con `_`).
    *   Calcular `max_survey_depth` de `survey_data`.
    *   Calcular `max_interval_depth` de [intervals](file:///home/jmbernales/qgispluginsdev/sec_interp/core/services/drillhole_service.py#148-309).
    *   Determinar `final_depth`:
        *   Si `collar_depth` > 0: Usar `collar_depth`.
        *   Si no: Usar `max(max_survey_depth, max_interval_depth)`.
    *   Pasar `final_depth` a [calculate_drillhole_trajectory](file:///home/jmbernales/qgispluginsdev/sec_interp/core/utils/drillhole.py#12-140).

## Verification Plan

### Automated Tests
Dado que los tests actuales requieren QGIS y el entorno es limitado, nos enfocaremos en **tests unitarios con mocking** para el nuevo servicio.
1.  Crear `tests/test_drillhole_service_mock.py` para probar la lógica de proyección sin depender de capas reales de QGIS (mocking de `QgsVectorLayer`).

### Manual Verification
1.  Cargar los datos de ejemplo del directorio [drillsec/Drilldata/](file:///home/jmbernales/qgispluginsdev/sec_interp/drillsec/Drilldata).
    *   Collar: [DrillCollar.csv](file:///home/jmbernales/qgispluginsdev/sec_interp/drillsec/Drilldata/DrillCollar.csv)
    *   Interval: [DrillAltn.csv](file:///home/jmbernales/qgispluginsdev/sec_interp/drillsec/Drilldata/DrillAltn.csv)
2.  Generar un perfil y comparar visualmente con la versión anterior (capturando screenshot antes de aplicar cambios si es posible).
3.    *   Verificar que los logs (ahora centralizados) muestren la misma información de conteo de puntos.

## Fase 5: Exportación de Datos de Sondajes

### Goal Description
Implementar la exportación de datos de sondajes (trazas e intervalos) a archivos Shapefile (.shp), permitiendo al usuario guardar el perfil generado para su uso posterior en otros softwares GIS.

### Proposed Changes

#### Exporters
Crear un nuevo exportador especializado para datos de sondajes.

##### [NEW] [sec_interp/exporters/drillhole_exporters.py](file:///home/jmbernales/qgispluginsdev/sec_interp/exporters/drillhole_exporters.py)
*   **Clase `DrillholeTraceShpExporter`**:
    *   Exporta las trazas de los sondajes (geometría de líneas 3D proyectadas al plano 2D).
    *   Campos: `hole_id` (String).
*   **Clase `DrillholeIntervalShpExporter`**:
    *   Exporta los intervalos geológicos a lo largo de la traza.
    *   Campos: `hole_id`, [from](file:///home/jmbernales/qgispluginsdev/sec_interp/gui/main_dialog_preview.py#205-257), [to](file:///home/jmbernales/qgispluginsdev/sec_interp/__init__.py#26-35), `lith/unit`.

#### Controller
##### [MODIFY] [core/controller.py](file:///home/jmbernales/qgispluginsdev/sec_interp/core/controller.py)
*   Importar los nuevos exportadores.
*   Actualizar método [export_data](file:///home/jmbernales/qgispluginsdev/sec_interp/core/controller.py#192-295):
    *   Recibir `drillhole_data` (asegurar que se pasa correctamente).
    *   Llamar a `DrillholeTraceShpExporter` para guardar `drillhole_traces.shp`.
    *   Llamar a `DrillholeIntervalShpExporter` para guardar `drillhole_intervals.shp`.

### Verification Plan
1.  Generar un perfil con sondajes visibles.
2.  Hacer clic en el botón "Save/Guardar".
3.  Verificar que se generen los archivos:
    *   `drillhole_traces.shp`
    *   `drillhole_intervals.shp`
4.  Cargar estos archivos en QGIS y verificar que se alinean con la visualización del plugin.
