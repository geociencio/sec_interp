# Auditoría del repositorio — SecInterp v3.11.0

> Análisis integral de código, arquitectura, tests, i18n, documentación, CI/CD y empaquetado.
> **Fecha:** 2026-10-18 · **Rama:** `main` · **HEAD:** `4ff74ba8` (`chore(docs): close session deps refresh, packaging and local deploy`)
> **Alcance:** árbol de trabajo completo (`core/`, `gui/`, `exporters/`, `plugin/`, `tests/`, `docs/`, `.github/`).
> **Estado del árbol:** limpio (`git status` sin cambios pendientes).

---

## Resumen ejecutivo

| Dimensión | Valoración | Hallazgo clave |
|---|---|---|
| Lógica y arquitectura | 🟢 Buena | Extract-then-Compute real, adaptadores GUI, DI y tareas asíncronas bien resueltas |
| Tests | 🟢 Muy buena | **743 tests OK** en 20,3 s, mock-first, sin skips |
| Lint / tipos / seguridad | 🟢 Buena | `ruff` limpio, `mypy` 89 archivos sin errores, `bandit` 0 hallazgos |
| Empaquetado | 🟢 Muy bueno | ZIP 3.11.0: 311 entradas, 2,28 MB, 14 idiomas de ayuda, sin artefactos de desarrollo |
| Arquitectura `core/` | 🟡 Media | 7 archivos aún acoplados a QGIS (allowlist), aunque la documentación dice 6 |
| Calidad estructural | 🟡 Media | 37 hallazgos del analizador; 20 objetos dios; 5 módulos >400 líneas |
| i18n | 🔴 Débil | Catálogos desincronizados: cadenas de v3.9–v3.11 ausentes; 7–21 `unfinished` por idioma |
| Coherencia documental | 🔴 Débil | README en v3.9.1 y afirma 85/100 y “0 issues”; el analizador dice 16/100 y 37 hallazgos |
| Gobernanza de release | 🟡 Media | El workflow de publicación solo ejecuta tests, no lint/tipos/seguridad/i18n/analizador |
| Compatibilidad declarada | 🟡 Media | QGIS 3.28 declarado, pero el código usa constructos de Python ≥3.10 y `pyproject` exige 3.12 |

**Valoración global:** código y tests notables; gobernanza de release, i18n y coherencia de métricas mejorables. Aproximadamente **8/10 en ingeniería de código** y **5/10 en consistencia de release/documentación**.

---

## 1. Composición del proyecto

**SecInterp** es un plugin QGIS para interpretación geológica de secciones: muestrea un DEM, proyecta polígonos geológicos, estructuras y sondajes sobre una línea de sección, permite interpretaciones 2D/3D y exporta a SHP, GPKG, DXF, CSV, PDF, SVG y PNG.

| Componente | Archivos `.py` | Líneas |
|---|---:|---:|
| `core/` — lógica pura, QGIS-agnóstica | 76 | 7.795 |
| `gui/` — QGIS/PyQt, extracción y presentación | 82 | 13.243 |
| `exporters/` — formatos de salida | 13 | 2.235 |
| `plugin/` + módulos raíz | 8 | ~1.000 |
| **Total código del plugin** | **175** | **~23.700** |
| `tests/` | 140 | 18.275 |

- Versión: **3.11.0** (`metadata.txt` y `pyproject.toml` sincronizados).
- Compatibilidad declarada: QGIS **3.28 – 4.99**; Python del proyecto: **≥3.12**; 14 idiomas.
- Repositorio: **1.965 archivos versionados** (~37 MB); árbol de trabajo ~700 MB por `docs/build`, `.git` y artefactos locales.

---

## 2. Metodología y verificaciones ejecutadas

Se leyó el código y la documentación, se inspeccionaron los informes del analizador y se ejecutaron las puertas de calidad con el entorno local (`.venv`). `uv run` no pudo operar en este entorno porque su caché está en solo lectura; por eso se usaron los binarios de `.venv` y una copia local de `ruff`.

| Comprobación | Comando | Resultado |
|---|---|---|
| Suite completa | `PYTHONPATH=.. .venv/bin/python -m unittest discover tests` | **743 tests OK**, 20,3 s |
| Lint | `ruff check .` (ruff 0.14.10 de caché; el proyecto fija 0.17.1) | **All checks passed** |
| Tipos | `mypy` 2.4.0 sobre `core/` + `exporters/` | **89 archivos, 0 errores** |
| Seguridad | `bandit -q -c .bandit -r core gui exporters plugin ...` | **0 hallazgos** |
| Flake8 | `flake8 core gui exporters plugin sec_interp_plugin.py` | Solo 4 `E402` en `symbology_tab.py` |
| ZIP de release | Inspección de `dist/sec_interp.3.11.0.zip` | **311 entradas**, 2,28 MB, 14 idiomas, 0 tests/scripts/`.agent`/`.pyc` |
| Cobertura | — | **No medida**: `coverage` no está instalado y CI no la ejecuta |

**Limitaciones:** no se ejecutó la suite dentro de QGIS real (Docker) ni el checker Qt6 (requiere Docker); no se midió cobertura. Las cifras de tests y lint corresponden al entorno local y al árbol actual.

---

## 3. Arquitectura

### 3.1 Fortalezas

El patrón **Extract-then-Compute** está implementado de forma real:

1. `gui/adapters/` extrae datos de QGIS a WKT/DTOs (`geometry.py`, `geology_extractor.py`, `drillhole_extractor.py`, `structure_extractor.py`, `profile_extractor.py`).
2. `core/services/` calcula con tipos primitivos (`GeologyService`, `StructureService`, `DrillholeService`, `VerticalExaggerationService`).
3. `exporters/` materializa los resultados.

Otros puntos fuertes:

- **DI explícita** en `ProfileController` y cadenas de procesadores para sondajes (`collar`, `survey`, `interval`, `trajectory`).
- **Tareas asíncronas** con contextos “detached” (`GeologyContext`, `DrillholeContext`): no hay objetos QGIS vivos en hilos secundarios.
- **Seguridad de CRS**: `build_sampling_transform`, `raster_resolution_in_crs` y validación de CRS mal etiquetados.
- **Validación en 3 niveles**, jerarquía de excepciones (`SecInterpError` y derivadas) y `path_validator` con protección contra *path traversal*.
- **Caché con TTL y metadatos**, invalidación por señales `dataChanged` de capas.
- **Cumplimiento Qt6/QGIS 4**: sin imports directos de PyQt5/PyQt6 y sin enums planos detectables.

### 3.2 Deuda arquitectónica

La allowlist del test de frontera sigue teniendo **7 archivos** de `core/` acoplados a QGIS
([`tests/core/test_architecture_boundary.py:46`](../../tests/core/test_architecture_boundary.py#L46)):

| Archivo | Acoplamiento |
|---|---|
| `core/config.py` | `QgsSettings`, `QCoreApplication` |
| `core/data_cache.py` | `QCoreApplication` |
| `core/services/access_control_service.py` | `QgsSettings` |
| `core/services/export/map_settings_factory.py` | `QgsMapSettings`, `QgsRectangle` |
| `core/services/export/orchestrator.py` | `QCoreApplication` |
| `core/utils/i18n.py` | `QCoreApplication` |
| `core/utils/io.py` | `QgsVectorFileWriter`, `QgsProject.instance()` |

La documentación sigue afirmando “allowlist 36 → 6” (`docs/DEVELOPMENT_LOG.md`, `docs/docsec/CHANGELOG.md`); el valor real es **7**. Además:

- `map_settings_factory.py` y `utils/io.py` son responsabilidad de **exportación/renderizado**, no de dominio; deberían vivir en `exporters/` o en un adaptador.
- `ProfileController` (en `core/`) recibe extractores de la capa GUI y los conserva; es un *composition root* con dependencias invertidas hacia `gui/`. Es defendible, pero conviene documentarlo como “application service” y no como dominio puro.
- `DrillholeService` conserva un parámetro `data_fetcher` que ya no se usa (`core/services/drillhole_service.py:34`).
- `gui/adapters/geometry.py` (597 líneas) y `gui/preview_layer_factory.py` (534) concentran demasiada responsabilidad.

---

## 4. Calidad estática y deuda estructural

El informe vigente del propio analizador ([`analysis_results/PROJECT_SUMMARY.md`](../../analysis_results/PROJECT_SUMMARY.md), generado a las 17:10 del 2026-10-18, alineado con HEAD) contradice las insignias del README:

| Métrica | Valor |
|---|---:|
| Overall score | **35,9 / 100** |
| QGIS Compliance | **16,0 / 100** |
| Module Stability | 55,7 / 100 |
| Maintainability | 99,9 / 100 |
| Security | 100,0 / 100 |
| Type hints (params / returns) | 97,2 % / 99,7 % |
| Docstrings | 99,0 % (estilo Google) |
| Hallazgos | **37** (25 `low`, 12 `medium`) |

Desglose de los 37 hallazgos:

| Tipo | Cantidad |
|---|---:|
| `GOD_OBJECT` | 20 |
| `MISSING_DOCSTRING` | 9 |
| `NON_PYTHONIC_LOOP` | 4 |
| `POTENTIAL_MISSING_SLOT` | 2 |
| `SPAGHETTI_CODE` | 1 |
| `UNPRECISE_LAYER` | 1 |

Ejemplos concretos:

- **Objetos dios:** `SecInterpDialog` 40 atributos, `PreviewWidget` 41, `SymbologyTab` 37, `PreviewSidePanel` 28, `SettingsPage` 26.
- **Tamaño de módulo:** 5 módulos superan 400 líneas; 2 superan 500:
  [`gui/adapters/geometry.py`](../../gui/adapters/geometry.py) (597) y
  [`gui/preview_layer_factory.py`](../../gui/preview_layer_factory.py) (534).
- **Funciones largas:** 28 funciones de ≥60 líneas; las mayores son
  `_orchestrate_exports` (110), `extract_context` (108) y `_load_from_qgs_settings` (108).
- **Docstrings de módulo:** **22 `__init__.py`** no tienen docstring reconocido porque el texto va después de `from __future__ import annotations` (p. ej. [`__init__.py:1`](../../__init__.py#L1)). Esto explica 6–7 de los 9 `MISSING_DOCSTRING`.
- **Manejo de errores:** 49 `except Exception` y 29 `# type: ignore`; aceptable en la frontera GUI, pero conviene revisar los de `core/`.
- **Sin `TODO`/`FIXME`** en el código del plugin.
- **`flake8`:** solo 4 `E402` en [`gui/ui/pages/settings/symbology_tab.py`](../../gui/ui/pages/settings/symbology_tab.py) (imports después de código), ignorados por `ruff`.

**Desajuste de métricas:** el README afirma “QGIS Compliance 85/100”, “docstring 100 %” y “`qgis-analyzer` reports 0 issues” ([`README.md:8`](../../README.md#L8), [`README.md:35`](../../README.md#L35)). El analizador actual dice 16/100 y 37 hallazgos. Hay que regenerar las insignias desde una única fuente de verdad.

---

## 5. Tests

**Fortaleza principal del repositorio.**

- **743 tests OK**, 20,3 s, **177 clases**, **0 skips**.
- Enfoque *mock-first* real: `tests/base_test.py` inyecta QGIS/PyQt simulados; `tests/integration/` usa `QgsApplication` real en Docker.
- Cobertura funcional de las features nuevas: `test_symbology_tab`, `test_preview_side_panel`, `test_preview_legend_renderer`, `test_color_manager`, `test_cache_fix` y `test_architecture_boundary`.
- Benchmarks en `tests/benchmarks/` y tests de integración para exportación, preview, mediciones y 3D.

**Carencias:**

- **No hay puerta de cobertura** en CI, aunque `pyproject.toml` tiene configuración de `coverage`.
- Las cifras de tests de la documentación no cuadran: las sesiones hablan de **728 ejecutados / 792 descubiertos**, mientras que el árbol actual descubre **743**. Son cifras copiadas a mano.
- La suite Docker usa `qgis/qgis:latest`, por lo que el entorno de integración no es reproducible.

---

## 6. i18n

**Hallazgo claro:** los catálogos están desincronizados respecto a las fuentes.

| Evidencia | Valor |
|---|---|
| Mensajes por `.ts` | 282 |
| `type="unfinished"` | 7–21 según idioma (FI/HI/JA/NL/PL: 21; DE/FR/ID/IT/PT_BR/RU/ZH_CN: 7) |
| “Smooth” en `.ts` / `.qm` | 0 apariciones |
| “Symbology” en `.ts` / `.qm` | 0 apariciones |
| “Reset unit styles” en `.ts` / `.qm` | 0 apariciones |
| “Legend layout” / “Drillhole traces” | 0 apariciones |
| `i18n/SecInterp_es.ts` | 11-may (anterior a v3.9–v3.11) |
| Archivos `gui/*.py` más nuevos que `.ts` | 75 |
| Archivos `gui/*.py` más nuevos que `.qm` | 31 |

Consecuencia: las cadenas nuevas de **v3.9.0, v3.10.0 y v3.11.0** (topografía suavizada, Symbology, editor de unidades, layout de leyenda) se muestran en inglés en todos los idiomas. La afirmación histórica de “100 % de cobertura en 13 idiomas” ya no se sostiene.

La regla `MISSING_I18N` del analizador **no detecta** esto: valida que las cadenas usen `tr()`, no que el catálogo esté actualizado.

**Acción:** regenerar catálogos (`lupdate`/`qgis-manage compile --type translations`), traducir las pendientes y añadir un gate que falle si hay `unfinished` o si el `.ts` es más antiguo que las fuentes.

---

## 7. Documentación

**Volumen y estado:**

- **1.354 documentos versionados**, 1.024 Markdown, 365 imágenes.
- **4 vaults de code walkthrough**: `code_walkthrough` (98 notas), `code_walkthrough_en` (97), `code_walkthrough_v2` (188), `code_walkthrough_en_v2` (188) = **571 notas** para 175 módulos.
- 201 notas de mantenimiento, 39 planes, 9 ADR, 14 notas de release.
- `docs/build/` ocupa **170 MB** en el árbol de trabajo (ignorado por git).
- El `DEVELOPMENT_LOG` y `docs/maintenance/` **sí están al día**: hay sesiones del 2026-10-18 para la fusión de v3.11.0 y el refresco de dependencias.

**Problemas:**

- **README obsoleto**: insignia 3.9.1, “What’s New in v3.9.1”, descarga de `sec_interp.3.9.1.zip` ([`README.md:5`](../../README.md#L5), [`README.md:22`](../../README.md#L22), [`README.md:89`](../../README.md#L89)).
- **Imagen principal rota** para cualquiera que no sea el autor: usa `file:///home/jmbernales/.gemini/...` ([`README.md:17`](../../README.md#L17)).
- **Métricas contradictorias** con el analizador (ver §4).
- **Licencia inconsistente**: README dice GPL v3; `LICENSE` dice GPL-2.0 **o** v3; `pyproject.toml` declara `GPL-2.0-or-later`.
- **Duplicación de vaults**: el `DOCS_INDEX` solo menciona dos, pero los `_v2` son los realmente refrescados en v3.11. Hay que elegir un vault canónico y archivar el resto.

---

## 8. CI/CD y empaquetado

### 8.1 Lo que funciona

- CI (`.github/workflows/test.yml`) con `ruff`, `mypy`, `check_docs`, Qt6 checker y tests en Docker QGIS.
- Workflow de release programado (`.github/workflows/scheduled-release.yml`) que selecciona la release debida, construye la ayuda offline, empaqueta y publica.
- ZIP de release **limpio**: 311 entradas, 2,28 MB, 14 idiomas de ayuda, sin `.ts`, tests, scripts, `.agent`, `.pyc` ni metadatos de análisis.
- `.bandit` y `.qgisignore` corregidos para excluir tooling de desarrollo.

### 8.2 Riesgos

1. **El workflow de release no ejecuta las puertas de calidad.** Solo corre tests Docker, empaqueta y publica ([`.github/workflows/scheduled-release.yml:80`](../../.github/workflows/scheduled-release.yml#L80)). No ejecuta `ruff`, `mypy`, `bandit`, analizador ni i18n. Ya se materializó: la sesión del 18-oct documenta que `PreviewLegendRenderer` llegó con CC 14 porque “el CI del tren no ejecutaba el analyzer”.
2. **Dockerfile usa `FROM qgis/qgis:latest`** ([`Dockerfile:2`](../../Dockerfile#L2)): builds no reproducibles.
3. **Dependencias de desarrollo declaradas como runtime** en `[project].dependencies`: `ai-context-core`, `qgis-plugin-analyzer`, `sphinx-intl` ([`pyproject.toml:12`](../../pyproject.toml#L12)).
4. **Configuración pip incompleta**: `[tool.setuptools] packages` omite `plugin/` y los módulos raíz ([`pyproject.toml:24`](../../pyproject.toml#L24)). No afecta al ZIP de QGIS, pero sí a un `pip install`/editable install.
5. **El analizador marca el repo como no conforme por tamaño** (`package_size_mb: 65,28 > 20 MB`), aunque el ZIP real pesa 2,28 MB. Es un problema de alcance de la medición, pero invalida la métrica de conformidad.

---

## 9. Hallazgos accionables priorizados

### P0 — corregir antes de la próxima release

#### 9.1 Claves de caché incompletas en la ruta de exportación

En [`core/controller.py:199`](../../core/controller.py#L199) la topografía cachea solo `[band_num, max_points]`; en [`core/controller.py:243`](../../core/controller.py#L243) la geología omite `smooth`/`smooth_window`; en [`core/controller.py:296`](../../core/controller.py#L296) las estructuras omiten la línea; en [`core/controller.py:367`](../../core/controller.py#L367) los sondajes omiten los mapeos de campos, la banda y el ráster.

El preview no usa este caché, pero **sí la exportación**: [`gui/dialog_export_manager.py:172`](../../gui/dialog_export_manager.py#L172) llama a `controller.generate_profile_data(params)`.

**Reproducción:**

1. Exportar con **Smooth** desactivado → se cachea la geología cruda con la clave K.
2. Activar **Smooth** y exportar de nuevo → la topografía se suaviza en el exportador, pero `_process_geology` reutiliza K y devuelve la geología cruda.
3. Resultado: topografía suavizada + geología sin suavizar, incoherente con la feature documentada.

**Solución:** hashear el `PreviewParams` completo (o añadir línea, ráster, `smooth`, `smooth_window`, banda y mapeos de campos a cada subclave) e invalidar al cambiar de capa en los combos.

#### 9.2 Compatibilidad declarada incoherente

`metadata.txt` declara QGIS **3.28** ([`metadata.txt:3`](../../metadata.txt#L3)), que en Windows suele traer **Python 3.9**, pero el código usa:

- `isinstance(x, int | float)` — 14 casos, requiere Python **3.10+**.
- `zip(..., strict=...)` — 2 casos, requiere Python **3.10+**.

Además, `pyproject.toml` exige Python **≥3.12** ([`pyproject.toml:6`](../../pyproject.toml#L6)) y el README dice 3.10. El CI instala 3.10 pero `requires-python >=3.12` hace que no se use; **nadie prueba 3.10/3.11**.

**Solución:** o subir `qgisMinimumVersion` a una versión con Python ≥3.10/3.12 y probarla, o eliminar esos constructos y soportar 3.9 de verdad.

### P1 — coherencia de release

3. **Regenerar y completar los catálogos i18n** y añadir un gate de frescura/`unfinished`.
4. **Añadir las puertas de calidad al workflow de release** (ruff, mypy, bandit, i18n, analizador/CC) o reutilizar el job `quality` de CI.
5. **Una sola fuente de verdad para las métricas**: regenerar README/insignias desde `metadata.txt` + `analysis_results` y eliminar afirmaciones manuales.

### P2 — mantenibilidad

6. **Reducir objetos dios y tamaño de módulos**, empezando por `SecInterpDialog`, `PreviewWidget`, `SymbologyTab`, `gui/adapters/geometry.py` y `gui/preview_layer_factory.py`.
7. **Arreglar los 22 `__init__.py`**: mover el docstring a la línea 1 (antes de `from __future__`).
8. **Consolidar documentación**: elegir un vault canónico, archivar los duplicados, sacar `docs/build` del árbol de trabajo y actualizar `DOCS_INDEX`.
9. **Higiene del árbol**: hay 37 archivos ignorados dentro de `core/`, `gui/` y `exporters/` (`AI_CONTEXT.md`, `PROJECT_SUMMARY.md`, `project_context.json`, `__pycache__`) y un `core/services/geology/__pycache__` de módulos eliminados. No llegan al ZIP, pero ensucian el repo.
10. **Código muerto/legado**: `core/algorithms.py` es un placeholder vacío; `IRenderer3D` no se usa; `data_fetcher` en `DrillholeService` no se usa; `gui/ui/main_window.py` es una base heredada de 167 líneas.
11. **Empaquetado**: mover herramientas de desarrollo a `[dependency-groups]`, incluir `plugin/` en `packages` si se quiere soportar pip, y fijar la imagen Docker.

---

## 10. Plan recomendado

| Fase | Trabajo | Criterio de aceptación |
|---|---|---|
| **Ahora** | Corregir claves de caché y añadir test de regresión (exportar con/sin Smooth y con campos distintos) | El export refleja siempre los parámetros actuales |
| **Ahora** | Decidir política de compatibilidad QGIS/Python y alinear `metadata.txt`, `pyproject.toml`, README y CI | Una sola versión mínima declarada y probada |
| **Próxima release** | Regenerar i18n y añadir gate de catálogo | 0 `unfinished` y `.ts` más nuevo que las fuentes |
| **Próxima release** | Meter lint/tipos/seguridad/i18n/analizador en el workflow de release | Un fallo de calidad bloquea la publicación |
| **Próxima release** | Regenerar README e insignias desde la fuente de verdad | README = 3.11.0, métricas = informe del analizador |
| **Ciclo de deuda** | Reducir 3–5 objetos dios y 2 módulos >500 líneas | `module_size_gate` PASS y menos `GOD_OBJECT` |
| **Ciclo de deuda** | Arreglar docstrings de `__init__.py`, limpiar artefactos y consolidar vaults | 0 `MISSING_DOCSTRING` evitable y un solo vault canónico |

---

## 11. Conclusión

El proyecto está **por encima de la media** de los plugins QGIS: separación de capas real, tests rápidos y numerosos, seguridad y CRS bien tratados, y un ZIP de release profesional. Lo que le resta puntos es la **disciplina de release y la coherencia de sus propios números**: el README dice 85/100 y 0 issues mientras el analizador dice 16/100 y 37 hallazgos; las traducciones de las features nuevas no están en los catálogos; y el workflow que publica no ejecuta los gates que el proyecto exhibe.

Si solo se abordan tres cosas, que sean: **(1)** las claves de caché de exportación, **(2)** la compatibilidad QGIS 3.28/Python y **(3)** meter los gates de calidad e i18n en el workflow de publicación. Con eso, el resto es deuda de mantenibilidad manejable.
