# Informe de Mejora y Fixes — ai-context-core v4.1.0

> **Fecha**: 2026-10-08
> **Versión analizada**: `ai-context-core` v4.1.0 (CLI `ai-ctx`, commit release `ada494c`)
> **Fuentes**: wheel instalado en `.venv/lib/python3.12/site-packages/` + clon `~/qgispluginsdev/ai-context-core`
> **Proyecto de referencia**: `sec_interp` (plugin QGIS)
> **Alcance**: análisis estático de la herramienta; este documento propone fixes, no los aplica.
> **Relación**: continúa la serie [`improvement_report_v3.4.0.md`](improvement_report_v3.4.0.md)
> y los `bug_report_*` previos.

---

## 1. Resumen ejecutivo

`ai-context-core` v4.1.0 está en buen estado arquitectónico (capas `providers/`,
`visitors/`, `builders/`; 148 módulos, ~9.4k LOC; 65 archivos de test). La mayoría de los
bugs históricos ya están corregidos: los falsos positivos de `__future__` y la resolución
del grafo de imports **sí funcionan en 4.1.0** (ver §2), pero quedan **cinco defectos
activos** que degradan la calidad de los reportes.

El más grave no es de código sino de **ciclo de vida del caché**: al actualizar la
herramienta, el cache no se invalida, por lo que el primer `full-scan` tras el bump
reproduce resultados de la versión anterior. Esto ya provocó una salida incorrecta durante
la adopción de 4.1.0 en SecInterp.

Prioridad global: **F1 (correctitud del caché) → F2/F3 (correctitud de reportes) → F4/F5 (ruido)**.

---

## 2. Estado: ya resuelto en v4.1.0 (verificado)

| Fix del CHANGELOG 4.1.0 | Estado | Evidencia |
| :--- | :--- | :--- |
| `__future__` ya no se marca como unused | ✅ | `visitors/imports_visitor.py:76-77`; tras `ai-ctx clean` desaparecen los falsos positivos |
| Resolución de import graph (prefijo de paquete + relativos) | ✅ | Edges pasan de **5 → 60** (densidad 0.001 → 0.011) tras limpiar caché |
| Churn realista con `--find-renames` | ⚠️ parcial | Coincide con git, pero **no se acota al código** (ver F4) |
| Secciones configurables + `context`-only | ✅ | `ai-ctx context` disponible; salida sin score |

> **Conclusión de §2**: los fixes anunciados están en el binario, pero **no se manifiestan
> hasta limpiar el caché** por el defecto F1. Ese es el hallazgo más importante de este informe.

---

## 3. Hallazgos y fixes propuestos

### F1 — El caché no se invalida al cambiar la versión del analizador (ALTO)

**Evidencia**
- `providers/fs_cache.py:34-51`: `load_cache`/`save_cache` sólo serializan el dict de
  módulos; no guardan versión ni schema.
- `providers/worker.py:49-68`: la validez de una entrada se decide **sólo** por
  `mtime`/`size`/`hash` del archivo fuente.
- `analyzer/engine.py:64,116`: lee y guarda el cache sin comprobar versión.

**Impacto**
Al actualizar `ai-ctx`, los `.py` no cambian (mismo `mtime`/`hash`), por lo que se
reutiliza el resultado AST de la versión anterior. En SecInterp esto produjo un
`AI_CONTEXT.md` con **5 edges** y falsos `__future__.annotations`, contradiciendo el
CHANGELOG de 4.1.0, hasta ejecutar `ai-ctx clean`.

**Fix propuesto** — versionar el caché con `_meta`:

```python
# providers/fs_cache.py
from ai_context_core import __version__

CACHE_SCHEMA = 1

def load_cache(project_path: pathlib.Path) -> Dict[str, Any]:
    cache_file = project_path / ".ai_context_cache.json"
    if not cache_file.exists():
        return {}
    try:
        with open(cache_file, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return {}
    meta = data.get("_meta", {})
    if meta.get("schema") != CACHE_SCHEMA or meta.get("version") != __version__:
        return {}  # cache de otra versión del analizador → ignorar
    return {k: v for k, v in data.items() if k != "_meta"}

def save_cache(project_path: pathlib.Path, cache_data: Dict[str, Any]) -> None:
    cache_file = project_path / ".ai_context_cache.json"
    payload = {"_meta": {"schema": CACHE_SCHEMA, "version": __version__}}
    payload.update({k: v for k, v in cache_data.items() if k != "_meta"})
    try:
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)
    except Exception:
        pass
```

**Test de regresión**: escribir un cache con `_meta.version` distinta y verificar que
`load_cache` devuelve `{}`; con la misma versión, que preserva los módulos.

**Alternativa mínima (hotfix)**: en `engine.py:64`, forzar `ignore_cache=True` cuando
`__version__` no coincida con la del último cache (mismo efecto, menos limpio).

---

### F2 — La severidad de seguridad del resumen está *hardcodeada* a HIGH (MEDIO)

**Evidencia**
- `builders/aggregator.py:197`: `"max_severity": "high",  # Default for AST issues for now`.
- `builders/issues.py:9-18`: imprime `(Max: {severity})` usando ese valor.
- `ai-ctx security` real: SecInterp sólo reporta hallazgos **LOW** ("Too broad exception
  handler"), pero `PROJECT_SUMMARY.md` muestra `Max: HIGH`.

**Impacto**
Falsa alarma de seguridad de nivel alto en todos los módulos con cualquier hallazgo AST,
minando la confianza en el reporte.

**Fix propuesto** — calcular la severidad real del conjunto:

```python
# builders/aggregator.py
_SEV_RANK = {"low": 0, "medium": 1, "high": 2}

def _max_severity(issues: list[dict]) -> str:
    return max(
        (i.get("severity", "low") for i in issues),
        key=lambda s: _SEV_RANK.get(s, 0),
        default="low",
    )

# dentro de _aggregate_security(), al construir la entrada nueva:
{
    "module": mod["path"],
    "issues": ast_issues,
    "total_issues": len(ast_issues),
    "max_severity": _max_severity(ast_issues),
}
```

**Además**: `builders/issues.py:14` limita a `sec[:3]`; conviene documentar el top-3 o
añadir `… (+N modules)` para no parecer que sólo hay 3 archivos afectados.

---

### F3 — Re-exports intencionales marcados como "unused imports" (MEDIO)

**Evidencia**
- `visitors/imports_visitor.py:112-122`: `detect_unused_imports` sólo compara contra
  `used_names`; **no entiende `__all__` ni el rol de re-export de un `__init__.py`**.
- Salida en SecInterp (`ai-ctx deps`):
  - `gui/__init__.py`: `main_dialog.SecInterpDialog`, `preview_renderer.PreviewRenderer`
  - `plugin/__init__.py`: `input_validator.InputValidationMixin`, …

**Impacto**
Falsos positivos en cada paquete que re-exporta su API pública vía `__init__.py`, que es
el patrón dominante en SecInterp.

**Fix propuesto** — capturar `__all__` y añadir una opción de config:

```python
# visitors/imports_visitor.py
class ImportVisitor(ast.NodeVisitor):
    def __init__(self, package=None):
        ...
        self.exported_names = set()

    def visit_Assign(self, node):
        # __all__ = ["X", "Y"]
        targets = [t.id for t in node.targets if isinstance(t, ast.Name)]
        if "__all__" in targets and isinstance(node.value, (ast.List, ast.Tuple)):
            for elt in node.value.elts:
                if isinstance(elt, ast.Constant) and isinstance(elt.value, str):
                    self.exported_names.add(elt.value)
        self.generic_visit(node)

def detect_unused_imports(tree, *, ignore_package_reexports: bool = True):
    visitor = ImportVisitor()
    visitor.visit(tree)
    for name_in_scope, full_import in visitor.imported_names.items():
        if name_in_scope in visitor.exported_names:
            continue
        if name_in_scope not in visitor.used_names:
            unused.append(full_import)
    return unused
```

Exponer además `[patterns.unused_imports].ignore_package_reexports = true` (por defecto)
y aplicar `ignore_package_reexports` en `builders/dependencies.py` según si el módulo es un
`__init__.py`.

**Nota**: `dependencies.py` ya filtra algunos módulos; conviene revisar qué módulos
`__init__.py` llegan hoy a `detect_unused_imports_in_project` (`builders/dependencies.py:160`).

---

### F4 — El churn no se acota a `.analyzerignore` (BAJO)

**Evidencia**
- `providers/git_analysis.py`: usa `git log --numstat` sin filtrar por `IgnoreFilter`.
- SecInterp: **512,693** líneas/30d (+251,498 / −261,195), dominado por `docs/` y `dist/`,
  no por código (el proyecto sólo tiene ~7k SLOC).

**Impacto**
La métrica de deuda/hotspots queda dominada por documentación y artefactos; como señal de
salud del código es ruidosa.

**Fix propuesto**: pasar `exclusion_patterns`/`IgnoreFilter` a `analyze_git_evolution` y
filtrar los paths del `--numstat`. Reportar dos números:

```python
"code_churn": {...},   # sólo rutas incluidas en el scope de análisis
"raw_churn": {...},    # total git (para contexto)
```

---

### F5 — Recomendación genérica "No Processing Algorithms found" (BAJO)

**Evidencia**
- `builders/qgis_summarizer.py:29`: emite el aviso siempre que no encuentra un
  `QgsProcessingAlgorithm`.

**Impacto**
Falso consejo para plugins que usan `QgsTask`/render propio (como SecInterp). Genera ruido
en las recomendaciones.

**Fix propuesto**: emitir el aviso sólo si el plugin declara un procesamiento (p. ej. import
`processing`, `QgsProcessingProvider` o un grupo de algoritmos en `metadata.txt`); en caso
contrario, omitirlo o sustituirlo por una nota neutral.

---

## 4. Guía operativa para SecInterp (mientras F1 no se corrija)

Tras **cada** actualización de `ai-context-core`, limpiar el caché antes de regenerar:

```bash
uv run ai-ctx clean          # invalida .ai_context_cache.json + artefactos
uv run ai-ctx full-scan      # regeneración correcta con la nueva versión
```

Añadir esta secuencia al procedimiento de adopción evita el incidente visto en 4.1.0
(`session_2026-10-08_ai_context_core_v410.md`). Alternativamente, borrar
`.ai_context_cache.json` manualmente antes del `full-scan`.

---

## 5. Priorización

| ID | Defecto | Severidad | Coste del fix | Recomendación |
| :--- | :--- | :--- | :--- | :--- |
| F1 | Cache no versionado | Alto | Bajo | Aplicar ya |
| F2 | Severidad de seguridad hardcodeada | Medio | Bajo | Aplicar ya |
| F3 | Falsos positivos de re-exports | Medio | Medio | Aplicar ya |
| F4 | Churn no acotado | Bajo | Medio | Planificar |
| F5 | Recomendación Processing genérica | Bajo | Bajo | Planificar |

---

## 6. Entorno de verificación

- **Tool**: ai-context-core `4.1.0` (`uv run ai-ctx --version`).
- **Reproducción**: `uv run ai-ctx full-scan` en `sec_interp` con y sin `ai-ctx clean`.
- **Evidencia F1**: Edges `5 → 60`, densidad `0.001 → 0.011`; falsos `__future__` presentes
  antes del `clean`, ausentes después.
- **Evidencia F2**: `PROJECT_SUMMARY.md` (`Max: HIGH`) vs `ai-ctx security` (todos `LOW`).
- **Evidencia F3**: sección `⚠️ UNUSED IMPORTS` en `AI_CONTEXT.md`.
