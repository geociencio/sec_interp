---
tags:
  - secinterp
  - code-walkthrough
  - core
  - services
aliases:
  - trajectory_engine.py
  - TrajectoryEngine
cssclass: secinterp-note
---

# `core/services/drillhole/trajectory_engine.py`

> [!abstract] Resumen en una línea
> Orquestador **puro** por sondaje: calcula la trayectoria 3D, la proyecta sobre la sección, interpola los tramos litológicos y empaqueta el resultado en un `DrillholeProjection` con `SpatialMeta` y `GeologySegment`.

**Ruta**: `core/services/drillhole/trajectory_engine.py` (111 líneas)
**Clase/Función principal**: `TrajectoryEngine`
**Capa**: Core (QGIS-agnóstico)
**Tags**: #secinterp #core #services

---

## 🎯 ¿Por qué existe este archivo?

Un sondaje requiere **cuatro transformaciones coordinadas** (profundidad final,
trayectoria, proyección e interpolación de intervalos). Hacerlas por separado deja
al consumidor (`DrillholeService`) con un puzzle de llamadas; concentrarlas aquí da
una única entrada por sondaje:

| Problema | Solución |
|----------|----------|
| Coordinar survey → trayectoria → proyección → intervalos | `process_single_hole` encadena las 4 fases |
| Decidir la profundidad real del sondaje | `SurveyProcessor.determine_final_depth` (delegado) |
| Construir el DTO final con metadatos espaciales | `create_drillhole_result` monta `SpatialMeta` + `segments` |

> [!important] Nota arquitectónica
> **QGIS-agnóstico** y sin estado global (solo compone dos procesadores inyectables en
> `__init__`). Es el **corazón del dominio de sondajes**: recibe datos puros
> (`collar_point`, `survey_data`, `intervals`, `line_points`) y devuelve DTOs puros
> (`GeologySegment`, `DrillholeProjection`). Nunca toca `qgis.core`.

---

## 🧬 Diagrama de relaciones

```mermaid
graph TD
    TE["TrajectoryEngine"]
    SP["SurveyProcessor"]
    IP["IntervalProcessor"]
    SCU["core.utils.drillhole"]
    DP["DrillholeProjection"]
    SM["SpatialMeta"]
    GS["GeologySegment"]
    DS["DrillholeService.process_context"]

    TE --> SP
    TE --> IP
    TE --> SCU
    TE --> DP
    TE --> SM
    TE --> GS
    DS -->|process_single_hole| TE
    TE -.->|(hole_geol, hole_proj)| DS
```

> [!tip] Cómo leer
> Flecha sólida = importa/delega; punteada = resultado devuelto al orquestador.
> `TrajectoryEngine` compone `SurveyProcessor` + `IntervalProcessor` (patrón
> **mediator** ligero) y delega la trigonometría a `core.utils.drillhole`.

---

## 📦 Imports — lectura arquitectónica

```python
# trajectory_engine.py
from __future__ import annotations

from typing import Any

from sec_interp.core import utils as scu
from sec_interp.core.domain import DrillholeProjection, GeologySegment, SpatialMeta
from sec_interp.core.services.drillhole.interval_processor import IntervalProcessor
from sec_interp.core.services.drillhole.survey_processor import SurveyProcessor
```

| # | Observación |
|---|-------------|
| ① | `utils as scu` — acceso a las tres funciones puras de trayectoria (`calculate_drillhole_trajectory`, `project_trajectory_to_section`). |
| ② | Importa **tres** DTOs del dominio: `DrillholeProjection` (salida), `GeologySegment` (segmentos) y `SpatialMeta` (puntos 3D). |
| ③ | Compone dos procesadores del **mismo paquete** (`IntervalProcessor`, `SurveyProcessor`) — dependencia intra-servicio, no cruzada a QGIS. |
| ④ | `Any` solo en `hole_id` y `collar_proj` (parámetro opcional por duck-typing). |

> [!note] Sin `math` propio
> A diferencia de `core/utils/drillhole.py`, aquí no hay trigonometría directa: toda la
> matemática se delega. `TrajectoryEngine` es **orquestación pura**.

---

## 🏗️ Inventario de estructura

**Clases:** `class TrajectoryEngine` — 3 métodos (2 públicos + `__init__`)

**Atributos de instancia:**
- `self.survey_processor: SurveyProcessor`
- `self.interval_processor: IntervalProcessor`

**Funciones/Métodos:**
- `__init__() -> None` — construye los dos procesadores colaboradores
- `process_single_hole(hole_id, collar_point, collar_z, given_depth, survey_data, intervals, line_points, buffer_width, section_azimuth) -> tuple[list[GeologySegment], DrillholeProjection]`
- `create_drillhole_result(hole_id, projected_traj, hole_geol_data, collar_proj=None) -> DrillholeProjection`

---

## 📁 Archivos del paquete

| Archivo | Nota |
|---------|------|
| `trajectory_engine.py` | esta nota |
| `survey_processor.py` | [[core_services_drillhole]] — `determine_final_depth` |
| `interval_processor.py` | [[interval_processor]] — interpolación de tramos |
| `collar_processor.py` | [[collar_processor]] — proyección del collar |
| `projection_engine.py` | [[core_services_drillhole]] — proyección punto-línea |

---

## 📖 Recorrido método por método

### `__init__`

```python
def __init__(self) -> None:
    self.survey_processor = SurveyProcessor()
    self.interval_processor = IntervalProcessor()
```

Inicializa los dos colaboradores. Son **instancias por defecto** (no inyectables por
constructor), a diferencia de `DrillholeService`, que sí admite inyectarlos. Si un
test quiere sustituir `IntervalProcessor`, debe hacer monkeypatch del atributo.

> [!note] Composición sobre herencia
> `TrajectoryEngine` no hereda de nada; **usa** dos procesadores. Es el estilo del
> paquete: clases pequeñas y componibles en vez de jerarquías profundas.

### `process_single_hole`

```python
def process_single_hole(
    self,
    hole_id: Any,
    collar_point: tuple[float, float],
    collar_z: float,
    given_depth: float,
    survey_data: list[tuple[float, float, float]],
    intervals: list[tuple[float, float, str]],
    line_points: list[tuple[float, float]],
    buffer_width: float,
    section_azimuth: float,
) -> tuple[list[GeologySegment], DrillholeProjection]:
```

Punto de entrada. Encadena cuatro fases con comentarios explícitos:

```python
# 1. Determine Final Depth
final_depth = self.survey_processor.determine_final_depth(
    given_depth, survey_data, intervals
)

# 2. Trajectory and Projection
trajectory = scu.calculate_drillhole_trajectory(
    collar_point,
    collar_z,
    survey_data,
    section_azimuth,
    total_depth=final_depth,
)
projected_traj = [
    p
    for p in scu.project_trajectory_to_section(trajectory, line_points)
    if p[5] <= buffer_width
]

# 3. Interpolate Intervals
hole_geol_data = self.interval_processor.interpolate_hole_intervals(
    projected_traj, intervals, buffer_width
)

# 4. Generate results
hole_proj = self.create_drillhole_result(hole_id, projected_traj, hole_geol_data)

return hole_geol_data, hole_proj
```

1. **Profundidad final**: `determine_final_depth` devuelve el `max(given_depth,
   max_survey_depth, max_interval_depth)` — el sondaje llega tan hondo como indique la
   fuente más profunda.
2. **Trayectoria y proyección**: `calculate_drillhole_trajectory` genera la 6-tupla
   `(depth, x, y, z, 0, 0)`; `project_trajectory_to_section` la convierte en 8-tupla y
   la comprensión de lista **filtra** los puntos con `p[5] > buffer_width`.
3. **Interpolación de intervalos**: delega en `IntervalProcessor`, que devuelve
   `list[GeologySegment]`.
4. **Resultado**: `create_drillhole_result` monta el `DrillholeProjection`.

> [!warning] Dos parámetros se pasan sin usarse aquí
> `section_azimuth` se reenvía a `calculate_drillhole_trajectory` (donde hoy es un
> parámetro **muerto**, ver [[drillhole]]) y `densify_step` **no se pasa**, por lo que
> `calculate_drillhole_trajectory` usa su valor por defecto `1.0`. La densidad de
> vértices de la trayectoria queda fija en 1 m sin exponerse.

### `create_drillhole_result`

```python
def create_drillhole_result(
    self,
    hole_id: Any,
    projected_traj: list[tuple],
    hole_geol_data: list[GeologySegment],
    collar_proj: Any = None,
) -> DrillholeProjection:
```

Construye el DTO final. Primero mapea cada punto proyectado a un `SpatialMeta`:

```python
spatial_points = []
for p in projected_traj:
    spatial_points.append(
        SpatialMeta(
            hole_id=str(hole_id),
            dist_along=p[4],
            offset=p[5],
            z=p[3],
            x_3d=p[1],
            y_3d=p[2],
            x_proj=p[6],
            y_proj=p[7],
        )
    )
```

Luego decide las coordenadas de cabecera del `DrillholeProjection` con tres fuentes
en cascada:

| Orden | Fuente | Valores |
|:---:|---|---|
| 1 | `collar_proj` (si se inyectó) | `distance`, `elevation`, `offset`, `total_depth` |
| 2 | `spatial_points[0]` (primer punto) | `dist_along`, `z`, `offset`, `depth=0.0` |
| 3 | nada | todos `0.0` |

Finalmente:

```python
return DrillholeProjection(
    hole_id=str(hole_id),
    distance=dist,
    elevation=elev,
    offset=offset,
    total_depth=depth,
    points_3d=spatial_points,
    segments=hole_geol_data,
)
```

> [!important] `collar_proj` es opcional y por duck-typing
> El parámetro `collar_proj: Any = None` permite inyectar la proyección del collar
> (un `DrillholeProjection` ligero creado por [[collar_processor]]) para copiar sus
> campos de cabecera. Si no llega, se deriva del primer punto de la trayectoria. En el
> flujo real, `DrillholeService` **no** lo pasa (queda `None`), así que la cabecera se
> obtiene de `spatial_points[0]` con `total_depth = 0.0`.

---

## 🔄 Flujo de datos

| Fase | Entrada | Transformación | Salida |
|------|---------|----------------|--------|
| Profundidad final | `given_depth`, `survey_data`, `intervals` | `max(...)` en `SurveyProcessor` | `final_depth` |
| Trayectoria | `collar_point`, `collar_z`, `survey_data` | `calculate_drillhole_trajectory` | 6-tupla `(depth,x,y,z,0,0)` |
| Proyección + filtro | 6-tupla + `line_points` | `project_trajectory_to_section` + `p[5] <= buffer_width` | 8-tupla filtrada |
| Intervalos | 8-tupla + `intervals` | `IntervalProcessor` | `list[GeologySegment]` |
| Resultado | 8-tupla + segmentos | `create_drillhole_result` | `DrillholeProjection` |

> [!tip] Encadenamiento canónico
> `DrillholeService.process_context` → `process_single_hole` → `create_drillhole_result`.
> El retorno `(hole_geol_data, hole_proj)` alimenta `geol_data_all` y
> `drillhole_data_all` del servicio, y esos son los dos arrays que el `PreviewResult`
> consolida (ver [[drillhole_service]] y [[dtos]]).

---

## 📐 Esquema de las tuplas de trayectoria

`create_drillhole_result` **sí** reinterpreta los índices de la 8-tupla proyectada
(producida por `scu.project_trajectory_to_section`):

| Índice | Campo | Mapeado a |
|:---:|---|---|
| 1 | `x` | `SpatialMeta.x_3d` |
| 2 | `y` | `SpatialMeta.y_3d` |
| 3 | `z` | `SpatialMeta.z` |
| 4 | `dist_along` | `SpatialMeta.dist_along` |
| 5 | `offset` | `SpatialMeta.offset` |
| 6 | `proj_x` | `SpatialMeta.x_proj` |
| 7 | `proj_y` | `SpatialMeta.y_proj` |

> [!warning] Acoplamiento posicional
> Este es el punto donde el esquema posicional de `core/utils/drillhole.py` se
> "fija" en un DTO nombrado (`SpatialMeta`). Un cambio de orden en la tupla rompería
> silenciosamente la correspondencia. Ver "Preguntas abiertas".

---

## 🔢 Ejemplo numérico — sondaje vertical

`hole_id="DH01"`, `collar_point=(100, 200)`, `collar_z=50`, `given_depth=0`,
`survey_data=[(10, 0, -90)]`, `intervals=[(0, 5, "LithA")]`,
`line_points=[(0,0),(300,0)]`, `buffer_width=50`, `section_azimuth=0`:

1. `final_depth = max(0, 10, 5) = 10`.
2. `trajectory = calculate_drillhole_trajectory((100,200), 50, [(10,0,-90)], 0, total_depth=10)`
   → puntos desde `(0,100,200,50,0,0)` hasta `(10,100,200,40,0,0)` (vertical: solo baja `z`).
3. `project_trajectory_to_section` proyecta cada `(x,y)` sobre `[(0,0),(300,0)]` →
   `dist_along` creciente, `offset ≈ 0` (el collar está a `y=200`, lejos… pero el
   offset real dependerá de la línea).
4. `interpolate_hole_intervals` devuelve un `GeologySegment` `"LithA"`.
5. `create_drillhole_result` monta el `DrillholeProjection` con los `SpatialMeta`.

> [!note] El filtro `p[5] <= buffer_width` es la clave
> Si todo el sondaje quedara a `offset > buffer_width`, `projected_traj` sería `[]` y
> el `DrillholeProjection` resultante tendría `points_3d=[]` y `segments=[]` (caso
> cubierto por `test_process_empty_traj`).

---

## 🏛️ Patrones de diseño presentes

| Patrón | Dónde | Propósito |
|--------|-------|-----------|
| **Pipeline** | `process_single_hole` (4 fases) | Encadenar transformaciones independientes |
| **Composition root** | `__init__` | Construir colaboradores en un único punto |
| **Facade** | la clase completa | Una API simple sobre un pipeline complejo |
| **Mapper** | `create_drillhole_result` | 8-tupla → `SpatialMeta` → `DrillholeProjection` |
| **Cascading default** | selección `collar_proj`/`spatial_points[0]`/`0.0` | Resolver cabecera con fallback |

---

## 🧾 Resumen de la API

| Símbolo | Firma / Hereda | Uso típico |
|---------|----------------|------------|
| `process_single_hole` | `(hole_id, collar_point, collar_z, given_depth, survey_data, intervals, line_points, buffer_width, section_azimuth) -> tuple[list[GeologySegment], DrillholeProjection]` | Procesar un sondaje completo |
| `create_drillhole_result` | `(hole_id, projected_traj, hole_geol_data, collar_proj=None) -> DrillholeProjection` | Construir el DTO final |
| `__init__` | `() -> None` | Instanciar `SurveyProcessor` + `IntervalProcessor` |

---

## 🛡️ Manejo de errores

`TrajectoryEngine` **no captura** excepciones: deja que suban al `DrillholeService`,
que sí las maneja:

| Caso | Comportamiento |
|------|----------------|
| `projected_traj` vacío | `create_drillhole_result` devuelve DTO con `points_3d=[]` y cabecera `0.0` (sin `IndexError`) |
| Survey desordenado | `calculate_drillhole_trajectory` lo ignora (guard en `_process_survey_segment`) |
| `ValueError`/`TypeError`/`KeyError`/`SecInterpError` | se capturan en `DrillholeService.process_context` y se registran con `logger.exception` |

> [!note] Por qué no captura aquí
> El engine no conoce el `feedback` ni el contexto de logging; su contrato es "o
> devuelvo un DTO válido, o propago la excepción". La capa superior decide si un
> fallo de un sondaje aborta todo o se salta (hoy: se salta y sigue con el siguiente).

---

## 🧪 Tests asociados

Mapeo a los tests reales bajo `tests/core/`:

- `tests/core/services/test_drillhole_engine_crash.py::test_create_result_with_empty_traj` —
  `create_drillhole_result` con `projected_traj=[]` no lanza `IndexError`.
- `tests/core/services/test_drillhole_engine_crash.py::test_process_empty_traj` —
  sondaje lejano (`offset > buffer`) → `points_3d` vacío.
- `tests/core/services/drillhole/test_processors.py::TestSurveyProcessor` — cubre
  `determine_final_depth` (delegado de la fase 1).
- `tests/core/services/drillhole/test_processors.py::TestIntervalProcessor` — cubre la
  interpolación (delegado de la fase 3).
- `tests/core/test_drillhole_service.py::test_process_context_projects_collar` —
  integración del pipeline completo.

> [!tip] El test de crash es una regresión documentada
> `test_drillhole_engine_crash.py` existe precisamente porque una trayectoria vacía
> llegó a provocar `IndexError`. La cascada `collar_proj → spatial_points[0] → 0.0`
> en `create_drillhole_result` es la defensa.

---

## ⚡ Rendimiento y complejidad

| Aspecto | Análisis |
|---------|----------|
| **Complejidad** | dominada por `calculate_drillhole_trajectory` `O(n)` (densificación) y `project_trajectory_to_section` `O(n·m)` |
| **Densificación** | `densify_step` queda en el default `1.0` (no expuesto) → hasta ~1 vértice por metro |
| **Filtro temprano** | `p[5] <= buffer_width` descarta puntos antes de interpolar, ahorrando trabajo |
| **Instancias** | `SurveyProcessor`/`IntervalProcessor` se crean **una vez** por engine; `TrajectoryEngine` se comparte entre sondajes |

> [!tip] Un engine, muchos sondajes
> `DrillholeService.__init__` crea un único `TrajectoryEngine` y lo reutiliza en el
> bucle `for collar in collar_data`. Como los métodos no mutan estado de instancia
> (más allá de los colaboradores), es seguro en `QgsTask`.

---

## 🌐 i18n y notas de migración

- **Sin cadenas de usuario**: el módulo no hereda `TranslatableMixin`; no emite
  mensajes. Cualquier texto de error se produce arriba, en `DrillholeService`.
- **Thread-safety**: sin estado mutable por llamada ⇒ reentrante y apto para `QgsTask`.
- **Migración v3.x**: el paso de `section_azimuth` a `calculate_drillhole_trajectory`
  es hoy un no-op (parámetro muerto); y `densify_step` no se propaga. Son candidatos a
  limpiar en un refactor.

---

## 👀 Observaciones y notas

> [!success] Fortalezas
> - Orquestación clara con comentarios de fase (`# 1. … # 4.`) que hacen legible el flujo.
> - Composición limpia de dos colaboradores especializados.
> - Defensa ante trayectoria vacía (sin `IndexError`) en `create_drillhole_result`.

> [!warning] Puntos de atención
> - `section_azimuth` se propaga a un parámetro muerto (ver [[drillhole]]).
> - `densify_step` no se expone: la densidad queda fija en 1 m.
> - El mapeo posicional 8-tupla → `SpatialMeta` es frágil a cambios de orden.

> [!question] Preguntas abiertas
> - ¿Exponer `densify_step` como parámetro del engine/servicio?
> - ¿Inyectar `SurveyProcessor`/`IntervalProcessor` por constructor (como `DrillholeService`)?
> - ¿Migrar las tuplas a `NamedTuple` para eliminar el acoplamiento posicional?

---

## 🔗 Notas relacionadas

- [[Index]] — índice de la bóveda
- [[drillhole_service]] — consumidor principal de `process_single_hole`
- [[collar_processor]] — produce el `collar_proj` que alimenta la cabecera
- [[interval_processor]] — colaborador de la fase de interpolación
- [[core_services_drillhole]] — `SurveyProcessor` y `ProjectionEngine` (delegados)
- [[drillhole]] — `calculate_drillhole_trajectory` / `project_trajectory_to_section`
- [[dtos]] — `DrillholeProjection`, `SpatialMeta`, `GeologySegment`

---

*Nota de la bóveda SecInterp Code Walkthrough v2 — v3.9.0*
