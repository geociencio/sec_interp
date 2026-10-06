# Informe de Mejora y Refactorización — ai-context-core v3.4.0

> **Fecha**: 2026-10-06
> **Versión analizada**: `ai-context-core` v3.4.0 (CLI `ai-ctx`, commit `b8520a5`)
> **Fuentes**: wheel instalado en `.venv` + clon fuente `~/qgispluginsdev/ai-context-core`
> **Proyecto de referencia**: `sec_interp` (plugin QGIS)
> **Alcance**: análisis estático del código de la herramienta; sin modificaciones.
> **Relación**: complementa y actualiza [`developer_recommendations.md`](developer_recommendations.md).

---

## 1. Resumen ejecutivo

`ai-context-core` está en buen estado arquitectónico (modularización en `visitors/`,
`builders/`, `providers/`; 58 archivos de test; score propio 97.3). La mayoría de los bugs
históricos documentados en `docs/maintenance/ai-context-core/` **ya están corregidos en
v3.4.0**.

Sin embargo, quedan **dos bugs funcionales que corrompen los reportes generados** (la sección
ENTRY POINTS siempre vacía y el conteo de tests acoplado al `.analyzerignore`, que deprime
artificialmente el Quality Score), **una ruta interna que ignora la config i18n**, y **deuda
arquitectónica clara**: paquetes completos muertos/duplicados (`context_builders/`,
`patterns_detectors/`, `commands/`).

Prioridad global: **corregir correctitud primero**, luego explicabilidad del score, y después
limpieza estructural.

---

## 2. Estado: ya resuelto en v3.4.0

| Recomendación histórica | Estado | Evidencia |
| :--- | :--- | :--- |
| `KeyError: 'class'` en reportes | ✅ | acceso seguro con `.get()` |
| Contrato de claves de métricas | ✅ | `builders/metric_keys.py`, `missing_metric_keys()` |
| i18n scope (`--i18n-scope`, globs `**`) | ✅ | `cli/commands/specialized.py:30`, `aggregator_qgis.py:10` |
| Entry point QGIS `classFactory` | ✅ | `visitors/ast_qgis.py:8` |
| Patrón Observer (pyqtSignal exacto) | ✅ | `visitors/observer.py:33` |
| Compatibilidad Python 3.14 (`ast.Str`) | ✅ | `visitors/sloc_helpers.py:29` |
| Opt-out `# no-i18n` + heurística de puntuación | ✅ | `visitors/i18n_components.py:42,68` |
| Renombrado de labels de métricas + doc | ✅ | `README.md:272-281`, `CHANGELOG.md` |

---

## 3. Hallazgos y recomendaciones

### A. Correctitud (bugs activos)

#### A1 — Sección `ENTRY POINTS` siempre vacía (CRÍTICO)
- **Evidencia:** `builders/structure.py:15` lee `analyses["entry_points"]`, pero **nada escribe
  esa clave**: `aggregator.py:64` calcula la lista `entry_points` y no la persiste en el
  resultado de `aggregate()`. Confirmado con `grep`: la única aparición de `"entry_points"` en
  todo `src/` es esa lectura.
- **Impacto:** `AI_CONTEXT.md` (raíz y por módulo) muestra `## 🎯 ENTRY POINTS` vacío incluso en
  plugins con `classFactory`. El dato se calcula y se descarta.
- **Recomendación:** añadir `"entry_points": entry_points` al dict devuelto por
  `ResultsAggregator.aggregate()` y exponer también el tipo (`qgis_plugin`, `main_guard`,
  `flask`, etc.). Añadir test de regresión que verifique que un módulo con `classFactory`
  aparece listado.

#### A2 — Conteo de tests acoplado al scope de análisis → penalización falsa (ALTO)
- **Evidencia:** `aggregator.py:68` recalcula los tests sobre `valid_modules`
  (`"test" in path.lower()`), en lugar de usar el `test_files_count` que ya produce
  `fs_scanner.py:101`. Como `sec_interp/.analyzerignore` excluye `tests/`, el resultado es `0`,
  y `calculator.py:126-127` resta **-20** al score.
- **Impacto:** `PROJECT_SUMMARY.md` reporta "Test Coverage: 0 test files" y un Quality Score
  (36.2) artificialmente bajo. La etiqueta "Test Coverage" es engañosa: mide **presencia de
  archivos**, no cobertura %.
- **Recomendación:**
  1. Desacoplar *scope de análisis* de *scope de métricas*: contar tests independientemente del
     `IgnoreFilter`.
  2. Unificar el conteo (usar solo `fs_scanner.test_files_count`, eliminar el recálculo de
     `aggregator.py:68`).
  3. Renombrar la métrica a "Test Files" (o integrar cobertura real si existe).
  4. Distinguir `no evaluado` de `0` en el reporte.

#### A3 — Ruta interna que ignora `i18n_config` (MEDIO)
- **Evidencia:** `aggregator.py:175-181` (`_aggregate_qgis_compliance`, wrapper legacy) llama a
  `aggregate_qgis_compliance(m_data, metadata)` **sin** `i18n_config`, mientras
  `_run_qgis_aggregation` sí lo propaga (`aggregator.py:131`).
- **Impacto:** si se invoca la ruta legacy, el `--i18n-scope` se pierde silenciosamente.
- **Recomendación:** eliminar el wrapper legacy o hacerlo delegar en `_run_qgis_aggregation`.
  Prohibir dos rutas para la misma operación.

#### A4 — Parámetro muerto en `is_translatable_string` (BAJO)
- **Evidencia:** `i18n_components.py:16` define `in_dict_key=False`, pero el llamador
  `i18n.py:68` nunca lo pasa; el contexto de dict se gestiona por estado externo
  (`qgis_visitor.py:95-101`).
- **Recomendación:** eliminar el parámetro (o cablearlo); mantener una sola fuente de verdad
  para el contexto de dict.

#### A5 — `except` silencioso en `_match_path` (BAJO)
- **Evidencia:** `aggregator_qgis.py:44-46` captura `Exception` y devuelve `False`.
- **Recomendación:** registrar `warning` con el patrón problemático; no silenciar.

---

### B. Métricas y scoring (explicabilidad)

- **Fórmula opaca con números mágicos:** `calculator.py:114-129` (umbrales `15`, `65`, `-20`,
  `+2`).
- **`max_complexity` calculado y no usado:** `calculator.py:106` lo computa, pero el score solo
  usa el promedio. Los outliers (el valor que realmente importa para gates CC ≤ 10) se ignoran.
- **Sin desglose en el reporte:** el score aparece como un único número sin justificación.

**Recomendaciones:**
1. Añadir sección **"Score Breakdown"** en `PROJECT_SUMMARY.md` (penalización por complejidad /
   MI / tests, con valores).
2. Incorporar `max_complexity` al score (penalizar máximos, no solo promedio).
3. Externalizar umbrales y pesos a config/perfil (`config_loader.py:62` ya define pesos de
   `has_main`).
4. Mantener la nota de "no canónico" **dentro del reporte generado** (hoy solo está en README).

---

### C. Precisión i18n

- **Denylist hardcodeada y frágil:** `i18n.py:23-42` (`_ignored_functions`); cada setter nuevo
  de Qt/QGIS no listado genera falsos positivos.
- **Palabras sueltas en minúscula siempre traducibles:** `i18n_components.py:63-65`.
- **Sin detección de idioma/entropía ni allowlist de APIs de UI**; sin tratamiento específico de
  kwargs técnicos.

**Recomendaciones:**
1. Cambiar de *denylist* a **allowlist de APIs de UI** (contar solo strings que son argumentos
   de `setText`, `setTitle`, `QAction`, `addAction`, `tr` en UI, etc.).
2. Hacer configurables las listas ignore/allow.
3. Añadir heurística de entropía/idioma para separar tokens técnicos de lenguaje humano.
4. Evaluar aislar el clasificador en un componente testeable (ya está parcialmente en
   `i18n_components.py`).

---

### D. Contexto cualitativo (recomendación histórica #5, abierta)

- **Evidencia:** `engine.py:210` solo lee `.ai-context/project_brain.md`. No existe
  `--include-md`.
- **Impacto:** la herramienta descarta documentación de arquitectura escrita por humanos/agentes
  (`ARCHITECTURE.md`, `AGENTS.md`, `docs/`), perdiendo contexto que es precisamente su propuesta
  de valor.
- **Recomendación:** flag `--include-md PATTERN` (repetible) y/o config `context_docs`; volcar en
  la sección "MANUAL ARCHITECTURE NOTES" ya existente (`builders/structure.py:22-24`).

---

### E. Refactorización arquitectónica (deuda estructural)

#### E1 — Paquetes muertos/duplicados (ALTO para mantenibilidad)
Evidencia del `grep` de imports:

| Paquete | Estado | Acción |
| :--- | :--- | :--- |
| `analyzer/context_builders/` (`structure.py`, `dependencies.py`, `patterns.py`) | **Sin ningún import externo** → muerto | Eliminar o convertir en la implementación única y borrar `builders/*` duplicado |
| `analyzer/patterns_detectors/` | Solo referenciado en un docstring-facade (`visitors/patterns.py:4`); los detectores reales viven en `visitors/` | Eliminar tras confirmar con tests |
| `commands/` (top-level `clean.py`, `report.py`) | Duplica `cli/commands/` | Consolidar en `cli/commands/` |

**Impacto:** ~dos árboles paralelos para las mismas responsabilidades
(structure/dependencies/patterns) invitan a divergencia y a mantener código que nadie ejecuta.

#### E2 — Capas de compatibilidad y aliases
- Aliases tipo `ContextAggregator = ResultsAggregator` (`aggregator.py:185`),
  `QGISComplianceVisitor = GenericQGISComplianceVisitor` (`ast_qgis.py:26`), facades en
  `visitors/patterns.py`.
- **Recomendación:** marcar deprecations con fecha, medir uso, y retirarlas en una versión mayor.
  Documentar contrato público vs. interno.

#### E3 — Duplicación de conteo de tests
- Ya descrito en A2: `fs_scanner` y `aggregator` cuentan tests de forma distinta. **Una sola
  fuente de verdad.**

#### E4 — Complejidad de `aggregate_qgis_compliance`
- `aggregator_qgis.py:52-197` mezcla filtrado por scope, recolección de API issues, agregación y
  scoring en una función. **Recomendación:** dividir en `_collect_api_issues`, `_aggregate_i18n`,
  `_compute_compliance_score` (bajo CC ≤ 10).

---

### F. Robustez, CI y tests

- **Historial de regresiones recurrentes** (KeyError, agregación, globs). Existen tests de
  regresión (`tests/test_regression_patterns.py`, `tests/test_metric_keys.py`,
  `test_i18n_scoping.py`), pero el reporte de salida no tiene *golden files*.
- **Muchos tests de "cantidad"** (`test_coverage_boost.py`, `test_final_gaps*.py`,
  `test_final_100_percent.py`) con riesgo de medir cobertura, no comportamiento.
- **Recomendaciones:**
  1. **CI smoke test** ejecutando `ai-ctx analyze` contra un plugin QGIS real (`sec_interp`) y
     comparando `AI_CONTEXT.md`/`PROJECT_SUMMARY.md` contra golden files.
  2. Tests de regresión explícitos para A1 (entry points no vacío) y A2 (conteo de tests
     desacoplado).
  3. Revisar/consolidar los tests "final gaps"; priorizar aserciones de comportamiento.

---

### G. UX y configuración

- `.analyzerignore` confunde **excluir de análisis** con **excluir de scoring** (raíz de A2).
- `config.toml` en `.ai-context/` parece legado (`context_cheatsheet.md` aún menciona
  `analyze_project_optfixed.py`).
- **Recomendaciones:** documentar semántica de `.analyzerignore`; introducir secciones de config
  por dominio (métricas, i18n, qgis) con umbrales explícitos; limpiar/actualizar artefactos
  legados.

---

## 4. Matriz de priorización

| Prioridad | Hallazgo | Impacto | Esfuerzo | Riesgo si no se corrige |
| :--- | :--- | :--- | :--- | :--- |
| 🔥 CRÍTICA | A1 `entry_points` nunca persistido | Reporte incompleto (sección vacía) | Muy bajo | Alto (información perdida) |
| 🔥 CRÍTICA | A2 tests acoplados a ignore | Score -20 artificial, métrica engañosa | Bajo | Alto (decisiones erróneas) |
| 🔥 ALTA | E1 paquetes muertos/duplicados | Mantenibilidad, divergencia | Medio | Medio |
| ⚡ MEDIA | A3 ruta legacy ignora i18n | Scope inoperante | Muy bajo | Medio |
| ⚡ MEDIA | B scoring opaco + `max_complexity` sin uso | Explicabilidad y detección de outliers | Medio | Medio |
| ⚡ MEDIA | C precisión i18n | Falsos positivos | Medio/Alto | Medio |
| ⚡ MEDIA | F CI/golden files | Regresiones silenciosas | Medio | Medio |
| 🔵 BAJA | D `--include-md` | Pérdida de contexto cualitativo | Medio | Bajo |
| 🔵 BAJA | A4/A5 limpieza (param muerto, except) | Higiene | Muy bajo | Bajo |
| 🔵 BAJA | G config/UX legada | Confusión | Bajo | Bajo |

---

## 5. Roadmap sugerido

- **Fase 1 — Correctitud (patch/minor):** A1, A2, A3, A4, A5 + tests de regresión.
- **Fase 2 — Explicabilidad (minor):** B1–B4 (Score Breakdown, `max_complexity`, umbrales
  configurables).
- **Fase 3 — Refactor estructural (mayor):** E1–E4 (eliminar paquetes muertos, consolidar
  facades, dividir `aggregate_qgis_compliance`).
- **Fase 4 — Valor diferencial:** C (i18n allowlist/entropía), D (`--include-md`), F (CI con
  golden files).

---

## 6. Evidencia (referencias de código)

- `ai_context_core/analyzer/builders/structure.py:15` — lee `entry_points` inexistente.
- `ai_context_core/analyzer/builders/aggregator.py:64,68,131,175-181,185` — cálculo de entry
  points no persistido; recálculo de tests; ruta i18n inconsistente; alias.
- `ai_context_core/analyzer/builders/calculator.py:106,114-129,147` — `max_complexity` sin uso y
  umbrales mágicos.
- `ai_context_core/analyzer/builders/aggregator_qgis.py:10-49,52-197` — `_match_path` y función
  monolítica.
- `ai_context_core/analyzer/visitors/i18n.py:23-42,68` y `i18n_components.py:16,42,52-65` —
  denylist y parámetro muerto.
- `ai_context_core/analyzer/providers/fs_scanner.py:101`, `fs_helpers.py:33` — conteo real de
  tests no usado.
- `ai_context_core/analyzer/engine.py:210` — único doc cualitativo leído.
- Paquetes sin imports: `analyzer/context_builders/`, `analyzer/patterns_detectors/`,
  `commands/`.

---

## 7. Addendum — Verificación en v3.5.0 (2026-10-06)

> **Contexto**: `ai-context-core` v3.5.0 ("Explainable Scoring & Context Enrichment") ya está
> publicado en PyPI y se adoptó en `sec_interp` (`pyproject.toml`, `uv.lock`). Esta sección
> verifica cada hallazgo contra el wheel instalado en `.venv` y contra los artefactos
> regenerados (`AI_CONTEXT.md`, `PROJECT_SUMMARY.md`, `project_context.json`).

### 7.1. Estado de los hallazgos

| ID | Hallazgo | Estado v3.5.0 | Evidencia |
| :--- | :--- | :--- | :--- |
| **A1** | `entry_points` nunca persistido | ✅ Resuelto | `project_context.json` incluye `entry_points` (antes ausente); con `__init__.py` en scope se renderiza `- \`__init__.py\` (qgis_plugin)`. |
| **A2** | Conteo de tests acoplado a `.analyzerignore` | ✅ Resuelto | `PROJECT_SUMMARY.md`: **Test Files: 137** (antes "Test Coverage: 0"); breakdown `Tests: +10.0` (se elimina el `-20` artificial). |
| **A3** | Ruta legacy ignora `i18n_config` | ✅ Resuelto | `aggregator.py`: `_aggregate_qgis_compliance` eliminado; única ruta `_run_qgis_aggregation` propaga `i18n_config`. |
| **A4** | Parámetro muerto `in_dict_key` | ✅ Resuelto | `i18n_components.py` ya no lo define; el estado vive en `i18n.py` (`self._in_dict_key`), fuente única de verdad. |
| **A5** | `except` silencioso en `_match_path` | ✅ Resuelto | `_match_path` eliminado en el refactor; globs inválidos ahora se registran (changelog). |
| **B** | Scoring opaco / `max_complexity` sin uso / umbrales mágicos | ✅ Resuelto | `PROJECT_SUMMARY.md` incluye **Score Breakdown** (`Base`, `Complexity (max)`, `Maintainability`, `Tests`); `max_complexity` penaliza outliers; sección `[scoring]` en `config_loader.py`. |
| **C** | Precisión i18n (denylist frágil) | ✅ Mayormente resuelto | Allowlist `DEFAULT_UI_FUNCTIONS` (`i18n.py:35-39`) + override configurable `patterns.i18n.ui_functions`. Entropía/detección de idioma sigue pendiente. |
| **D** | Sin contexto cualitativo (`--include-md`) | ✅ Resuelto | `ai-ctx analyze --include-md GLOB` (repetible) y `context_docs`; volcado en "MANUAL ARCHITECTURE NOTES". |
| **E2** | Facades/aliases sin política de deprecación | ✅ Resuelto | `deprecations.py` emite `DeprecationWarning`; retirada programada para v4.0.0. |
| **E4** | `aggregate_qgis_compliance` monolítico | ✅ Resuelto | Dividido en `_collect_api_issues`, `_aggregate_i18n`, `_compute_compliance_score`. |
| **E1** | Paquetes muertos/duplicados | ❌ Pendiente | Siguen presentes `analyzer/context_builders/`, `analyzer/patterns_detectors/`, `commands/`. |
| **F** | Golden files / CI smoke en `sec_interp` | ⚠️ Parcial | v3.5.0 añade *golden reports* internos; el CI smoke del proyecto (comparar salida contra fixtures) aún no existe. |

### 7.2. Efecto en las métricas del proyecto

| Métrica | v3.4.0 | v3.5.0 | Nota |
| :--- | ---: | ---: | :--- |
| ai-ctx Quality Score | 36.2 | **68.2** | +32.0 por desacople de tests, breakdown explicable y scope con `__init__.py`. |
| Test Files | 0 (artificial) | **137** | Métrica real, ya no penaliza. |
| Maintainability (Avg MI) | 35.8 | **43.8** | Mejora por inclusión de `__init__.py`. |
| Avg Cyclomatic Complexity | 13.2 | 13.2 | Sin cambio. |
| QGIS Compliance Score | 85.0 | **85.0** | Estable. |
| i18n Coverage | — | 303/438 (69.2%) | Scope `all` (76 módulos). |

### 7.3. Ajuste local de configuración

Al verificar **A1** se detectó que `.analyzerignore` excluía el patrón global `__init__.py`
(matando también el entry point `classFactory` de `sec_interp`). Se **eliminó** esa línea para
que el análisis incluya los `__init__.py` de paquete (66 → 76 módulos) y la sección
**ENTRY POINTS** sea significativa. La semántica de `.analyzerignore` (excluir de análisis vs.
excluir de scoring, hallazgo G) sigue documentada como deuda menor en la herramienta.

### 7.4. Pendientes derivados (no bloqueantes)

- **E1** (paquetes muertos) y **D/G** (limpieza de config legada) en la herramienta.
- **F**: añadir al CI de `sec_interp` un smoke test de `ai-ctx full-scan` con fixtures.
