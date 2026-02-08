# Bug Report: ai-context-core v3.2.0

Este documento detalla los fallos críticos encontrados en la versión 3.2.0 relacionados con la nueva funcionalidad de segmentación de i18n (`i18n scope`).

## Bug 1: Omisión de Configuración en el Agregador

### Descripción
El `ResultsAggregator` no pasa la configuración de `i18n` al llamar a la función de cumplimiento de QGIS. Esto causa que cualquier configuración de `scope` (ej. `gui_only`) sea ignorada, regresando siempre al valor por defecto (`all`).

### Localización
Archivo: `ai_context_core/analyzer/builders/aggregator.py`
Método: `_run_qgis_aggregation`

### Código Afectado
```python
def _run_qgis_aggregation(
    self, m_data: List[Dict[str, Any]], metadata: Dict[str, Any]
) -> Dict[str, Any]:
    # ... (omisión de carga de i18n_config)
    from .aggregator_qgis import aggregate_qgis_compliance
    return aggregate_qgis_compliance(m_data, metadata) # Falla: falta tercer argumento
```

### Solución Propuesta
```python
def _run_qgis_aggregation(self, m_data, metadata):
    # ...
    i18n_config = self.config.get("patterns", {}).get("i18n", {})
    return aggregate_qgis_compliance(m_data, metadata, i18n_config)
```

---

## Bug 2: Fallo en el Matching de Rutas Recursivas

### Descripción
La función interna `_match_path` utiliza `fnmatch` de una manera que no interpreta correctamente los patrones de glob recursivo (`**/*.py`). Esto provoca que, incluso si se pasa la configuración, ningún archivo sea incluido en el scope `gui_only`.

### Localización
Archivo: `ai_context_core/analyzer/builders/aggregator_qgis.py`
Función: `_match_path`

### Comportamiento Erróneo
Cuando el patrón es `gui/**/*.py` y la ruta es `gui/main_dialog.py`:
- La lógica intenta dividir por `**/`.
- El sufijo resultante `.py` se compara con `fnmatch.fnmatch(path, "*.py")`.
- Sin embargo, la implementación actual de la partición y el reemplazo de prefijos no es lo suficientemente robusta para manejar subdirectorios anidados de forma consistente en todos los sistemas operativos.

### Solución Propuesta
Migrar a `pathlib.Path.match` o mejorar la expresión regular generada para soportar `**` nativamente:

```python
def _match_path(path: str, pattern: str) -> bool:
    from pathlib import Path
    try:
        p = Path(path)
        # pathlib.Path.match soporta ** a partir de Python 3.13+
        # Para versiones anteriores, se requiere una regex más compleja
        return p.match(pattern) or p.match(f"**/{pattern}")
    except Exception:
        return False
```

---

## Bug 3: Opción faltante en CLI

### Descripción
El comando `ai-ctx qgis` no expone la opción `--i18n-scope` a pesar de que el método `validate_qgis` en el backend ya está preparado para recibirla.

### Localización
Archivo: `ai_context_core/cli/commands/specialized.py`

### Cambio Sugerido
```python
@click.command(name="qgis")
@click.option("--path", default=".", help="Project path")
@click.option("--i18n-scope", type=click.Choice(["all", "gui_only"]), help="Limit i18n analysis scope")
def qgis_cmd(path: str, i18n_scope: str):
    qgis.validate_qgis(path, i18n_scope)
```

---

## Resolución

Todos los errores detallados anteriormente han sido corregidos en la versión **3.2.1** de `ai-context-core`.

### Verificación de la Solución
- **Bug 1 & 2**: Verificados mediante el script `scripts/verify_v321_fixes.py`. El scope `gui_only` ahora filtra correctamente los módulos técnicos, reduciendo el conteo de strings de 882 (`all`) a 399 (`gui_only`) en el proyecto `sec_interp`.
- **Bug 3**: Verificado mediante `ai-ctx qgis --help`, confirmando la presencia de la opción `--i18n-scope`.

Se ha actualizado la dependencia en `pyproject.toml` a `>=3.2.1`.
