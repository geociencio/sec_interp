# Recomendaciones para el Desarrollador de ai-context-core

> **Fecha**: 2026-09-18
> **Versión analizada**: `ai-context-core` v3.4.0 (CLI `ai-ctx`)
> **Proyecto de referencia**: `sec_interp` (plugin QGIS)

Este documento consolida las deficiencias detectadas en `ai-ctx` a lo largo del uso en el proyecto y propone recomendaciones técnicas para su mejora. Sustituye y unifica los reportes dispersos: [`dev_feedback.md`](dev_feedback.md), [`v250_fix_report.md`](v250_fix_report.md), [`bug_report_v320.md`](bug_report_v320.md) y [`bug_report_v321_aggregation.md`](bug_report_v321_aggregation.md).

---

## 1. Robustez / Manejo de Errores

**Problema recurrente:** el generador de reportes accede a claves de diccionarios con `occ['class']` y `occ['module']` de forma directa. Cuando una heurística devuelve una estructura incompleta (patrones a nivel de módulo, decoradores como `@functools.wraps`), se lanza `KeyError: 'class'` y se aborta la generación completa de `AI_CONTEXT.md` y `PROJECT_SUMMARY.md`.

- **Historial**: v2.1.1, v2.5.0 (y reapareció tras la corrección).
- **Localización**: `ai_context_core/analyzer/reporting.py` (`SummaryGenerator._build_patterns`, `AICtxGenerator._add_patterns`) y `ai_context_core/cli.py` (`show_specific`).

**Recomendación:**

```python
class_name = occ.get("class", occ.get("name", "N/A"))
module_path = occ.get("module", "N/A")
confidence = occ.get("confidence", 0)
```

> Aplicar acceso seguro `.get()` con fallbacks en **todos** los puntos que interpongan patrones detectados, no solo en los ya corregidos.

---

## 2. Corrección de Métricas (Agregación)

**Problema:** en v3.2.1, `AI_CONTEXT.md` y `PROJECT_SUMMARY.md` reportaban `0` en *Functions*, *Classes* y *Maintenance Index*, aunque el cache de análisis por módulo era correcto.

**Causa raíz:** desajuste de claves entre el productor y el consumidor de métricas.

| Capa | Archivo | Clave esperada | Clave real |
| :--- | :--- | :--- | :--- |
| Productor | `analyzer/builders/calculator.py` | `total_functions` | ❌ omitida |
| Productor | `analyzer/builders/calculator.py` | `total_classes` | ❌ omitida |
| Productor | `analyzer/builders/calculator.py` | `average_maintenance_index` | `avg_maintainability` |
| Consumidor | `analyzer/builders/formatter.py` | `average_complexity` | `avg_complexity` |

**Recomendación:**

1. Unificar el nombre de las claves en un único contrato (constantes compartidas o un `TypedDict`) para evitar desajustes silenciosos.
2. Devolver siempre el conjunto completo de claves desde `calculate_project_metrics`.
3. Añadir una validación explícita que avise si una clave esperada no está presente, en lugar de caer en el `0` por defecto.

---

## 3. Configuración i18n (Scope)

**Problema:** la funcionalidad de segmentación `i18n scope` introducida en v3.2.0 presentaba tres fallos encadenados:

1. **`ResultsAggregator`** no propagaba `i18n_config` al llamar a `aggregate_qgis_compliance`, ignorando siempre el scope (`gui_only`).
2. **`_match_path`** usaba `fnmatch` y no interpretaba correctamente los globs recursivos `**/*.py`, por lo que ningún archivo se incluía en `gui_only`.
3. **El CLI** no exponía la opción `--i18n-scope` en `ai-ctx qgis`.

**Recomendación:**

- Pasar `i18n_config` como tercer argumento en `_run_qgis_aggregation`:
  ```python
  i18n_config = self.config.get("patterns", {}).get("i18n", {})
  return aggregate_qgis_compliance(m_data, metadata, i18n_config)
  ```
- Migrar `_match_path` a `pathlib.Path.match` o a una regex que soporte `**` nativamente:
  ```python
  from pathlib import Path
  p = Path(path)
  return p.match(pattern) or p.match(f"**/{pattern}")
  ```
- Exponer `--i18n-scope` (tipo `click.Choice(["all", "gui_only"])`) en el comando `qgis`.

---

## 4. Heurísticas Específicas de QGIS

**Problema:** la herramienta está orientada a Python genérico y pierde detalle arquitectónico en plugins QGIS.

1. **Entry points**: solo se detecta `if __name__ == "__main__"`, ignorando `classFactory`, el entry point real de un plugin QGIS.
2. **Patrón Observer (PyQt)**: no se detectan señales/slots, que son el mecanismo de comunicación dominante en QGIS.

**Recomendación:**

- Detección de entry point:
  ```python
  def is_qgis_entry_point(node):
      return isinstance(node, ast.FunctionDef) and node.name == "classFactory"
  ```
- Heurística Observer: buscar asignaciones de `pyqtSignal()`; si un módulo declara más de 2 señales, clasificarlo como **Observer** con confianza 0.8.

---

## 5. Integración de Contexto Cualitativo

**Problema:** `ai-ctx` genera un reporte únicamente a partir del análisis estático del código, descartando documentación de arquitectura escrita por humanos/IA (p. ej. `project_brain.md`).

**Recomendación:**

- Permitir que `ai-ctx` incorpore Markdown existente en la sección de arquitectura del reporte final (flag del tipo `--include-md`), para no perder contexto cualitativo.

---

## 6. Precisión en la Detección de Strings i18n

**Problema:** `is_translatable_string` (`string_utils.py`) usa heurísticas básicas (presencia de espacio o puntuación) y genera falsos positivos en diccionarios técnicos, nombres de columnas/atributos, y strings técnicos como `"Single Symbol"`. El chequeo aísla el `ast.Constant` sin conocer su contexto (clave de diccionario, argumento técnico, valor por defecto).

**Recomendación (ver [`i18n_improvement_guide.md`](i18n_improvement_guide.md)):**

- **Contexto AST**: rastrear el contenedor actual (`visit_Dict` → `DICT_LITERAL`, etc.) para ignorar claves técnicas.
- **Naming patterns**: ignorar `snake_case`, `camelCase`, `PascalCase`, `UPPER_CASE`.
- **Opt-out inline**: soportar `# no-i18n` para exclusiones manuales.
- **Entropía/detección de idioma**: distinguir strings técnicos de lenguaje humano.

---

## 7. Testing / Pipeline de Calidad

**Problema:** los bugs descritos (KeyError, agregación, globs recursivos) reaparecieron en varias versiones, lo que sugiere una cobertura de tests insuficiente en el pipeline de reportes.

**Recomendación:**

1. Añadir tests de regresión para cada bug corregido:
   - Patrones sin clave `class` (decoradores, patrones a nivel de módulo).
   - Contrato de claves entre `calculator.py` y `formatter.py`.
   - `_match_path` con `**/*.py` en rutas anidadas y multi-plataforma.
   - Scope `gui_only` vs `all` (conteo de strings).
2. Ejecutar el análisis contra un proyecto QGIS real (como `sec_interp`) en CI para detectar regresiones.
3. Publicar un `CHANGELOG` de API claro cuando cambien nombres de claves internas.

---

## 8. Claridad de Métricas (vs. Otras Herramientas)

**Problema:** el *Quality Score* de `ai-ctx` es una heurística agregada distinta de la que reporta `qgis-analyzer`, generando confusión (CC promedio 13.6 vs gate CC ≤ 10; score 40.8 vs 52.3). En `sec_interp`, `ai-ctx` fue declarado **no canónico** para métricas de proyecto.

**Recomendación:**

- Documentar explícitamente qué mide cada métrica (promedio vs máximo, heurística vs gate) en el propio reporte generado.
- Evitar nombrar el agregado con la misma etiqueta que métricas canónicas externas para no inducir comparaciones inválidas.

---

## 9. Matriz de Priorización

| Prioridad | Problema | Impacto | Esfuerzo |
| :--- | :--- | :--- | :--- |
| 🔥 CRÍTICA | `KeyError: 'class'` (accesos directos a dict) | Rompe el reporte final | Muy bajo |
| 🔥 ALTA | Desajuste de claves en métricas | Reportes con valores `0` | Bajo |
| 🔥 ALTA | Propagación de `i18n_config` + `_match_path` + CLI `--i18n-scope` | Scope i18n inoperante | Bajo |
| ⚡ MEDIA | Entry points QGIS (`classFactory`) | Reporte incompleto en plugins | Bajo |
| ⚡ MEDIA | Patrón Observer (PyQt signals) | Falta detalle arquitectónico | Medio |
| ⚡ MEDIA | Precisión en detección i18n (contexto AST, naming, opt-out) | Falsos positivos | Medio/Alto |
| 🔵 BAJA | Integración de Markdown cualitativo | Pérdida de contexto humano | Medio |
| 🔵 BAJA | Claridad de métricas vs. otras herramientas | Confusión de métricas | Bajo |

---

*Documento de referencia interna para el equipo de `ai-context-core`. Consolidado desde los reportes históricos de `docs/maintenance/ai-context-core/`.*
