# Upstreaming Plan: SecInterp scripts → qgis-plugin-analyzer

> **Estado**: ✅ UPSTREAMING COMPLETO en qgis-plugin-analyzer **1.14.0**.
> Este documento se ha reconciliado con la versión 1.14.0 (instalada en
> `.venv/.../site-packages/analyzer/`). Solo queda la **migración del lado
> SecInterp** (sección 6), ya ejecutada el 2026-09-17.

## 1. Premisa

SecInterp y qgis-plugin-analyzer comparten autor. El analizador es la
herramienta reutilizable de análisis estático para plugins QGIS; SecInterp
acumuló lógica más madura en dos áreas — i18n por AST y gate de complejidad —
que vivían como scripts ad-hoc (`scripts/verify_i18n_hygiene.py`,
`scripts/check_cc.py`).

Esa madurez **ya se trasladó al analizador** en la versión 1.14.0, por lo que
cualquier plugin QGIS se beneficia. Los scripts duplicados de SecInterp se han
retirado.

## 2. Implementado en 1.14.0 (verificado contra el código instalado)

| Ítem | Ubicación en 1.14.0 | Estado |
| :--- | :--- | :--- |
| Regla i18n por AST (`MISSING_I18N`) | `visitors/i18n_visitor.py` (port de `scripts/upstream/i18n_ast_rule.py`) | ✅ DONE |
| Config por proyecto | `[tool.qgis-analyzer.profiles.<p>.rules.MISSING_I18N]` con `extra_ignore_calls` / `extra_exact_ignores` | ✅ DONE |
| Exclusión inline `# no-i18n` / `# noqa` | `i18n_visitor.py` (`visit_Constant`) | ✅ DONE |
| Gate de complejidad `--max-cc N` | `analyzer/cli/commands/analyze.py` + `commands.py::_enforce_max_cc` (expone `cc_gate`/`cc_violations`) | ✅ DONE |
| `--json` (stdout machine-readable) | `analyzer/cli/commands/analyze.py` | ✅ DONE |
| `--include-content` (off por defecto) | `analyzer/cli/commands/analyze.py` | ✅ DONE |
| `schema_version` + `analyzer_version` en salida | `project_context.json` (`schema_version: 1`, `analyzer_version: 1.14.0`) | ✅ DONE |
| Warning de directorio de salida legacy | `commands.py::_warn_legacy_output_dir` | ✅ DONE |
| Warning de caché obsoleta | `commands.py::_detect_stale_cache` | ✅ DONE |

### Decisión de diseño (antes abierta)

La regla se expone con id **`MISSING_I18N`** (no `UNTRANSLATED_STRING`, sin
flag `--ast-precise`). La heurística antigua fue **reemplazada** por el enfoque
AST; no se mantiene fallback heurístico.

## 3. Falsos positivos residuales (resueltos)

El port generalizó la regla y retiró entradas específicas de SecInterp
(`PerformanceTimer`, `track` de `SAFE_CALL_SUFFIXES`; strings de preview de
`SAFE_EXACT_STRINGS`). Resultado: 2 `MISSING_I18N` en los labels de
`PerformanceTimer` (`Total Preview Generation`, `Total Preview Export Time`).

Solución (config, no código): en `pyproject.toml`,

```toml
[tool.qgis-analyzer.profiles.default.rules.MISSING_I18N]
extra_ignore_calls = ["PerformanceTimer"]
```

Con esto `MISSING_I18N` → **0** en el corpus SecInterp.

## 4. Gap analysis (histórico)

- El enfoque AST portado añade `_collect_docstring_lines()` (excluye docstrings
  multilínea vía `end_lineno`), 19 patrones `TECHNICAL_PATTERNS`, call-stack de
  `SAFE_CALL_SUFFIXES` y el gate "parece user-facing".
- `scanner.py` ya calcula `functions[].complexity` y `functions[].line`; solo
  hacía falta exponerlo como gate, hecho en 1.14.0.

## 5. Riesgos y tradeoffs

- **Deriva de versiones**: SecInterp depende de `>=1.14.0` (`pyproject.toml`).
- **Falsos positivos en terceros**: mitigado con configuración por proyecto y
  `.analyzerignore`.
- **Pérdida de precisión específica**: mitigada con `extra_exact_ignores` /
  `extra_ignore_calls` configurables.

## 6. Migración de SecInterp (ejecutada 2026-09-17)

1. ✅ Retirar `scripts/check_cc.py` → `qgis-analyzer analyze --max-cc 10`.
2. ✅ Retirar `scripts/verify_i18n_hygiene.py` → regla `MISSING_I18N` del analyzer.
3. ✅ Retirar `scripts/upstream/i18n_ast_rule.py` (referencia ya fusionada).
4. ✅ `scripts/sync_metrics.py`: derivar CC gate del `--max-cc` returncode y
   i18n gate de `MISSING_I18N == 0`; eliminar `run_check_cc`/`run_verify_i18n`.
5. ✅ Arreglar pre-push hook: `--output json` (CLI legacy) → `--max-cc 10`.
6. ✅ `pyproject.toml`: `extra_ignore_calls = ["PerformanceTimer"]`.
7. ✅ Actualizar `agent_metrics.json`, `scripts/README.md`, workflows y skills.

## 7. Estrategia de pruebas (aplicada)

- Corpus SecInterp → `MISSING_I18N` 2 → 0 (sin cambios de código, solo config).
- `qgis-analyzer analyze . --max-cc 10` → exit 0 (CC ≤ 10).
- `sync_metrics.py --validate` → PASS (consistencia interna).
