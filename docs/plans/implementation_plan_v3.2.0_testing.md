# Plan de Expansión de Cobertura de Tests (v3.2.0)

Este plan detalla la estrategia para eliminar las "áreas ciegas" de testing identificadas, elevando la suite de pruebas de 368 a aproximadamente 450+ tests, con especial énfasis en la lógica asíncrona y componentes visuales.

## Proposed Changes

### 1. Pruebas de Lógica Asíncrona (GUI Tasks)
Creación de infraestructura para probar `QgsTask` en entorno controlado.
#### [NEW] [test_drillhole_task.py](file:///home/jmbernales/qgispluginsdev/sec_interp/tests/gui/tasks/test_drillhole_task.py)
#### [NEW] [test_geology_task.py](file:///home/jmbernales/qgispluginsdev/sec_interp/tests/gui/tasks/test_geology_task.py)
- Pruebas de ciclo de vida (Start, Cancel, Error, Finish).
- Validación de transferencia de datos entre hilos mediante señales.

### 2. Servicios de Core y Seguridad
#### [NEW] [test_access_control.py](file:///home/jmbernales/qgispluginsdev/sec_interp/tests/core/services/test_access_control.py)
- Pruebas de permisos de usuario y disponibilidad de herramientas según perfil.
#### [NEW] [test_drillhole_processors.py](file:///home/jmbernales/qgispluginsdev/sec_interp/tests/core/services/drillhole/test_processors.py)
- Tests unitarios aislados para `CollarProcessor`, `SurveyProcessor` e `IntervalProcessor`.

### 3. Pruebas de Renderizado (State-Based)
Dado que el renderizado visual es difícil de automatizar sin capturas de pantalla, usaremos validación de estado del `QPainter`.
#### [NEW] [test_renderers.py](file:///home/jmbernales/qgispluginsdev/sec_interp/tests/gui/renderers/test_renderers.py)
- Verificar que `topo_renderer` y `drillhole_renderer` llaman a los métodos de dibujo correctos con coordenadas proyectadas válidas.

### 4. Utilidades de Performance y UX
#### [NEW] [test_lod_calculator.py](file:///home/jmbernales/qgispluginsdev/sec_interp/tests/gui/test_lod_calculator.py)
- Validar el cálculo de niveles de detalle (LOD) según niveles de zoom.
#### [NEW] [test_preview_reporter.py](file:///home/jmbernales/qgispluginsdev/sec_interp/tests/gui/test_preview_reporter.py)
- Validar la generación de cadenas de texto y reportes HTML.

## Verification Plan

### Automated Tests
- `make docker-test`: Verificación global de la suite. El objetivo es alcanzar ~450 tests OK.
- `uv run ai-ctx analyze`: Verificar que el *Quality Score* mejora tras añadir los tests (meta > 75.0).
