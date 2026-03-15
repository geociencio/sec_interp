# Plan: Reducción de Complejidad en [ExportService](file:///home/jmbernales/qgispluginsdev/sec_interp/core/services/export_service.py#22-446)

**Objetivo**: Reducir la CC de [ExportService](file:///home/jmbernales/qgispluginsdev/sec_interp/core/services/export_service.py#22-446) de ~44 a menos de 20, manteniendo al 100% la cobertura de tests existente.

## Diagnóstico

### Fuentes de Complejidad

| Método | Líneas | CC Estimada | Problema |
|---|---|---|---|
| [_export_drillholes_3d](file:///home/jmbernales/qgispluginsdev/sec_interp/core/services/export_service.py#306-354) | 306–353 | ~16 | 4 bloques `if` anidados (traces/intervals × original/projected) con código duplicado |
| [_orchestrate_exports](file:///home/jmbernales/qgispluginsdev/sec_interp/core/services/export_service.py#98-166) | 98–165 | ~12 | Mezcla resolución de layers con despacho de handlers |
| [_export_drillholes](file:///home/jmbernales/qgispluginsdev/sec_interp/core/services/export_service.py#268-305) | 268–304 | ~8 | `if options:` llama a [_export_drillholes_3d](file:///home/jmbernales/qgispluginsdev/sec_interp/core/services/export_service.py#306-354) — sin impacto real, es overhead lógico |
| Resto | — | ~8 | Distribuido correctamente |

---

## Cambios Propuestos

### [MODIFY] [core/services/export_service.py](file:///home/jmbernales/qgispluginsdev/sec_interp/core/services/export_service.py)

#### Refactor 1: Extraer `_resolve_layers()`
Mover la resolución de [line_layer](file:///home/jmbernales/qgispluginsdev/sec_interp/tests/core/test_export_service.py#181-195) y `raster_layer` desde [_orchestrate_exports](file:///home/jmbernales/qgispluginsdev/sec_interp/core/services/export_service.py#98-166) a un método privado especializado. Reduce la carga cognitiva de [_orchestrate_exports](file:///home/jmbernales/qgispluginsdev/sec_interp/core/services/export_service.py#98-166) y aísla el código que toca `QgsProject`.

```python
def _resolve_layers(self, params: PreviewParams) -> tuple[Any, Any]:
    """Resolve layer IDs to QgsMapLayer objects. Returns (line_layer, raster_layer)."""
```

#### Refactor 2: Aplanar [_export_drillholes_3d()](file:///home/jmbernales/qgispluginsdev/sec_interp/core/services/export_service.py#306-354) — Task-List Pattern
Eliminar los 4 bloques `if/if` anidados reemplazándolos por una lista declarativa de tareas:

**Antes (CC ~16):**
```python
if options.get("drill_3d_traces", False):
    if options.get("drill_3d_original", True):
        ... DrillholeTrace3DExporter ...
    if options.get("drill_3d_projected", False):
        ... DrillholeTrace3DExporter ...
if options.get("drill_3d_intervals", False):
    if options.get("drill_3d_original", True):
        ... DrillholeInterval3DExporter ...
    if options.get("drill_3d_projected", False):
        ... DrillholeInterval3DExporter ...
```

**Después (CC ~5):**
```python
tasks = [
    ("drill_3d_traces", "drill_3d_original", DrillholeTrace3DExporter,
     "drillhole_traces_3d_real.shp", False, "3D Real"),
    ("drill_3d_traces", "drill_3d_projected", DrillholeTrace3DExporter,
     "drillhole_traces_3d_projected.shp", True, "3D Proj"),
    ("drill_3d_intervals", "drill_3d_original", DrillholeInterval3DExporter,
     "drillhole_intervals_3d_real.shp", False, "3D Real"),
    ("drill_3d_intervals", "drill_3d_projected", DrillholeInterval3DExporter,
     "drillhole_intervals_3d_projected.shp", True, "3D Proj"),
]
for type_opt, proj_opt, ExporterClass, filename, use_proj, label in tasks:
    if options.get(type_opt) and options.get(proj_opt):
        path = folder / filename
        ExporterClass({}).export(path, {...})
        msg.append(f"  - {path.name} ({label})")
```

#### Refactor 3: Consolidar importaciones tardías en [_orchestrate_exports](file:///home/jmbernales/qgispluginsdev/sec_interp/core/services/export_service.py#98-166)
Mover `from sec_interp.exporters import CSVExporter` al bloque de imports del módulo (ya es un patrón mixto — algunos métodos importan localmente, el método raíz también). Esto no afecta CC pero limpia el código.

> [!NOTE]
> Los imports tardíos de los métodos `_export_*` se **conservan** para mantener el *lazy loading* que previene fallos de inicialización del plugin.

---

## Plan de Verificación

### Tests Automáticos (sin cambios a los tests)
Los tests existentes en [test_export_service.py](file:///home/jmbernales/qgispluginsdev/sec_interp/tests/core/test_export_service.py) ya cubren todos los handlers y son suficientes para validar el refactor:

```bash
# Ejecutar solo los tests del ExportService en Docker
make docker-test

# Alternativa local (requiere QGIS mock)
uv run python -m unittest tests.core.test_export_service -v
```

### Métricas de Calidad Post-Refactor
```bash
# Verificar que la CC bajó
uv run qgis-analyzer summary
```

**Objetivo**: CC de [export_service.py](file:///home/jmbernales/qgispluginsdev/sec_interp/core/services/export_service.py) < 20 (actualmente 44).
