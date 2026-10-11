# Next Steps (Updated 2026-10-11)

## ✅ Session 2026-10-11 — Release Train Unblock & v3.10.0 (COMPLETADO)

- **Qué se hizo**: el tren programado estaba **bloqueado**; se arregló y se **publicó v3.10.0**.
  - **Dos desajustes main↔rama** (ramas cortadas el 27-sep, antes de cambios del 4/8-oct):
    (1) `.agent` es **submódulo** en `main` y **carpeta** en las ramas → `git checkout` abortaba
    (`d9b13ebe`: `git submodule deinit -f .agent && rm -rf .agent` antes del checkout);
    (2) la ayuda offline necesita `conf.py` (modo help) + `help_index.rst` de `main`, no solo
    `build_docs.sh` (`f202a083`: cachear y restaurar los tres).
  - **v3.10.0 publicada**: tag `v3.10.0` en `release/v3.10.0`, release `2026-10-11T15:37Z`,
    `sec_interp.3.10.0.zip` (**2.27 MiB**, ayuda 14 idiomas), *Latest*. Contenido: leyenda
    interactiva en panel lateral (Goal 1.1 core), sondeos en leyenda, editor por unidad, + Qt6 `QgsRasterBandStats`.
  - El selector ahora reporta `nothing_due` (v3.11.0 el **18-oct**); el mismo arreglo la cubre.
- **Calidad**: dry-run `38151593980` **success** · publish `38151877186` **success** (tests Docker OK, help + package OK).
- **Referencia**: `docs/maintenance/session_2026-10-11_release_train_v3.10.0.md`.
- **Pendiente / cómo reanudar**:
  1. **v3.10.0 en el portal de QGIS**: ✅ **subido** — pendiente de **aprobación** del repositorio (verificar en https://plugins.qgis.org/plugins/sec_interp/).
  2. **v3.11.0 (18-oct)**: el cron debería publicarla; si no dispara, `gh workflow run scheduled-release.yml -f version=3.11.0`.
  3. **Merge final del tren → `main`** (tras v3.11.0): NO es `--ff-only` (main-only=65, train-only=26) →
     merge real; el diff de `.agent` (submódulo vs carpeta) y las versiones de `metadata/CHANGELOG` darán conflicto.
  4. **Plan de interop estereonet/3D**: alcance **confirmado y guardado para implementación futura** — `docs/plans/implementation_plan_interop_stereonet_3d.md` (§9 checklist). B2 = acción GUI; empezar por **B1 (estilos 3D de sondeo)**.
  5. **Plan del parser de notaciones estructurales** (cobertura de todas las variantes, planos; convención `strike_dip` por defecto): `docs/plans/implementation_plan_structural_parser.md` (guardado, sin implementar).

## ✅ Session 2026-10-11 — QGIS MCP Integration (Fork + `qgis_driver`) (COMPLETADO)

- **Qué se hizo**: se cerró la exploración `docs/plans/exploration_qgis4_qa_mcp.md`
  **adoptando + forkeando + extendiendo** `nkarasiak/qgis-mcp` (publicado como "QGIS MCP")
  en lugar de construir un MCP propio: ya existe, es QGIS 4-ready y soporta `opencode`.
  Ahora SecInterp se **smoke-testea en vivo por MCP**.
  - **Fork**: `tools/qgis_mcp/` = `nkarasiak/qgis-mcp` **v0.15.1** (`55519eb`); puerto por
    defecto **9877**; `PROVENANCE.md` (commit upstream, cambios, install, sync).
  - **Extensión SecInterp** (sin `execute_code`): handler `handlers/secinterp.py` + 6 tools
    `secinterp_*` en `src/qgis_mcp/server.py` + grupo compound `secinterp`. `open` replica
    `run()` **sin `exec()`** (evita el loop Qt anidado que congelaría el server).
  - **opencode**: `mcp.secinterp_qgis` (compound, puerto 9877) **deshabilitado globalmente**
    + subagente nuevo **`qgis_driver`** que lo habilita.
  - **Scope**: `tools/` es `DEV_DIRECTORY` de `qgis-manage` → nunca entra al ZIP;
    `.analyzerignore`/`ruff exclude` += `tools`; workflow `.agent-state/workflows/smoke-qgis4.md`
    (+ fila en `AGENTS.md`).
- **Calidad**: suite del fork **429 passed / 2 skipped** · ruff limpio (fork + root) ·
  handshake stdio **131** (granular) / **28** (compound) · `validate_agent_system` **14/14** ·
  **smoke en vivo QGIS 4.2.1** verde (`ping`→`open`→`preview`→`ready`→`results`→`export`,
  PNG 2286×900).
- **Referencia**: `docs/maintenance/session_2026-10-11_qgis_mcp_integration.md`.
- **Pendiente / cómo reanudar**:
  1. **Mantener el fork sincronizado** con upstream (procedimiento en `PROVENANCE.md`);
     correr `diagnose` tras cada update (server ↔ plugin deben casar versión).
  2. **Instalar el plugin del fork** en cada perfil QGIS que se use (symlink a
     `.../QGIS4/profiles/default/python/plugins/qgis_mcp_plugin`) si no está ya.
  3. Opcional: contribuir el grupo `secinterp` upstream, o recortar el fork al subconjunto usado.
  4. El resto de pendientes (tren v3.10.0/v3.11.0, `legend_widget.py`, bóveda, Goal 1.1/1.5)
     siguen abajo sin cambios.

## ✅ Session 2026-10-11 — Type-Check Gate (mypy wired) (COMPLETADO)

- **Qué se hizo**: se cableó **`mypy`** como gate **bloqueante** sobre las capas estrictas
  (`core` + `exporters`) y se dejaron en **0 errores** (32 → 0). Sin cambios de comportamiento
  (anotaciones, guards de `None`, `cast`/tipos precisos).
  - **Invocación**: mypy debe correr desde el **directorio padre** (base del paquete) para
    resolver `sec_interp.*` sin la ambigüedad `core` vs `sec_interp.core`. Nuevo target
    **`make mypy`** (corre desde `$(CURDIR)/..` con `--explicit-package-bases
    sec_interp/core sec_interp/exporters`); añadido a `pre-release`.
  - **CI**: nuevo job **`typecheck`** en `.github/workflows/test.yml` (`UV_FROZEN=1 make mypy`).
  - **Arreglos**: anotaciones faltantes (`validation_helpers`, `io.create_shapefile_writer`,
    `interpretation_3d_exporter`, `orchestrator.topo_handler`, `svg_exporter`); guards
    (`io.create_vector_writer`, `path_resolver.get_profile_name`, provider 3D); tipos
    precisos (`layer_validator`, `parsing`, `drillhole`); quirks de qgis-stubs (enums como
    `Any`, iteración de `QgsFields` por índice, `cast`); contrato de `BaseExporter.export`
    alineado; atributos de `ExportServiceCompatMixin`.
- **Calidad**: **`make mypy` → Success: no issues found in 89 source files** · ruff/format
  limpios · `unittest discover tests` **763 OK** (Docker).
- **Referencia**: `docs/DEVELOPMENT_LOG.md` (session 2026-10-11 Type-Check Gate).
- **Pendiente / cómo reanudar**:
  1. **Extender el gate**: `gui` tiene 338 hallazgos (fuera de alcance) — futura fase módulo a
     módulo, opcionalmente con un ratchet basado en `mypy-baseline`.
  2. **Pendiente (bloqueado)**: `uv` 0.12.10 → 0.13.0 — está vía **pacman** (Manjaro stable
     aún sirve 0.12.10; `uv self update` no aplica). `pacman` lo subirá cuando se promueva;
     comprobar con `pacman -Si uv`.
  3. El resto de pendientes (deuda por la cobertura 1.16.0, tren v3.10.0/v3.11.0,
     `legend_widget.py`, bóveda, Goal 1.1/1.5) siguen abajo sin cambios.

## ✅ Session 2026-10-11 — Toolchain Modernization (ruff 0.17 + mypy 2.4, drop black) (COMPLETADO)

- **Qué se hizo**: se completó la mitad "lint/type" del refresco de toolchain, con las
  dos actualizaciones que se habían retenido a propósito. **Sin impacto en el runtime**.
  - **ruff** 0.15.2 → **0.17.0**: `pyproject.toml` `ruff>=0.17.0`; `.pre-commit-config.yaml`
    `ruff-pre-commit` `v0.8.4` → `v0.17.0` (estaban divergentes). Reglas nuevas:
    `ISC004` (concatenación implícita en colección) — paréntesis explícitos en los 3
    mensajes de `core/validation/validation_helpers.py`; `PLR0917` (demasiados
    posicionales) — `# noqa` ampliado en `gui/adapters/drillhole_extractor.py`.
  - **Markdown**: ruff 0.17 formatea los bloques Python **dentro de Markdown** (quería
    reescribir 381 `.md`). Se añadió `**/*.md` al `exclude` de `[tool.ruff]` para no
    tocar docs ni romper los gates de bóveda/mirrors.
  - **mypy** 1.19.1 → **2.4.0** (`mypy>=2.4.0`): mismo baseline (15 hallazgos, todos en
    `scripts/`/`tests/`/`docs/`; **0 nuevos en el plugin**).
  - **black** eliminado (no se usa; `ruff format` es canónico).
- **Calidad**: `ruff check`/`format --check` limpios · `uv run --frozen ruff check .`
  (paridad CI) PASS · `pre-commit run ruff/ruff-format --all-files` PASS · `unittest
  discover tests` **763 OK** (Docker).
- **Referencia**: `docs/DEVELOPMENT_LOG.md` (session 2026-10-11 Toolchain Modernization).
- **Pendiente / cómo reanudar**:
  1. **Opcional**: cablear `mypy` a un target acotado (`mypy core exporters`) si debe
     ser gate — hoy `mypy .` revisa scripts/tests/docs y aborta pronto.
  2. **Pendiente (bloqueado)**: `uv` 0.12.10 → 0.13.0 — está vía **pacman** (Manjaro stable
     aún sirve 0.12.10; `uv self update` no aplica). `pacman` lo subirá cuando se promueva;
     comprobar con `pacman -Si uv`.
  3. El resto de pendientes (deuda por la cobertura 1.16.0, tren v3.10.0/v3.11.0,
     `legend_widget.py`, bóveda, Goal 1.1/1.5) siguen abajo sin cambios.

## ✅ Session 2026-10-11 — Dependency Refresh (uv "safe batch") (COMPLETADO)

- **Qué se hizo**: se actualizó la cadena de herramientas gestionada por `uv` con un
  **lote de bajo riesgo**, dejando fuera a propósito las actualizaciones breaking.
  **Sin impacto en el runtime del plugin**.
  - **Ecosistema**: `qgis-manage` 0.9.0 → **0.9.2** (la usan `make compile/deploy/package`
    y el CI de release); `qgis-stubs` 0.2.0.post1 → 0.5.0.
  - **Dev tools**: `bandit` 1.9.4 · `flake8` 7.4.1 · `pre-commit` 4.6.2 · `pytest` 9.1.1 ·
    `pytest-mock` 3.16.0 · `networkx` 3.7 · `setuptools` 84.0.0 · `sphinx-intl` 2.4.0 ·
    `sphinxcontrib-mermaid` 2.1.1 · `myst-parser` 5.1.0 · `linkify-it-py` 2.2.0
    (+ transitivas; baja `uc-micro-py`).
  - **Método**: `uv lock --upgrade-package … --no-cache --refresh` + `uv sync`.
    `agent_metrics.json` intacto (sin cambio de métricas).
  - **Retenidas a propósito (HECHO después, misma fecha)**: `ruff` 0.15.2 → 0.17.0 y
    `mypy` 1.19.1 → 2.4.0, y `black` eliminado → ver la sesión "Toolchain Modernization"
    más arriba.
- **Calidad**: ruff/format limpios · `unittest discover tests` **763 OK** (Docker) ·
  **empaquetado smoke-test** con `qgis-manage 0.9.2` (`sec_interp.3.9.1.zip` a `/tmp`, exit 0) ·
  `forge metrics validate` PASS.
- **Pendiente / cómo reanudar**:
  1. **Opcional**: `uv self update` (0.12.10 → 0.13.0).
  2. ~~**Opcional (fase propia)**: subir `ruff` 0.17 y `mypy` 2.x sincronizando
     pre-commit/CI y arreglando el fallout; decidir si se elimina `black`.~~ ✅ **HECHO
     (2026-10-11)**: sesión "Toolchain Modernization" (ruff 0.17.0 + mypy 2.4.0, `black`
     eliminado).
  3. El resto de pendientes (deuda por la cobertura 1.16.0, tren v3.10.0/v3.11.0,
     `legend_widget.py`, bóveda, Goal 1.1/1.5) siguen abajo sin cambios.

## ✅ Session 2026-10-11 — qgis-plugin-analyzer 1.16.0 (Module-Coverage Fix + Triage) (COMPLETADO)

- **Qué se hizo**: se adoptó `qgis-plugin-analyzer` **1.16.0** y se descubrió que **1.15.2
  infrarreportaba la cobertura**: analizaba **135** módulos en proyecto-completo
  cuando el plugin tiene **171** (`.py` reales − 2 scripts ignorados). 1.16.0 arregla
  el bug de descubrimiento; el código antes sin gate (`core/validation/*`,
  `exporters/*`, `gui/adapters/*`, `gui/ui/pages/*`) ahora se analiza. Se triajearon
  los hallazgos para dejar los gates verdes.
  - **Dependency**: `>=1.15.2` → `>=1.16.0` (`pyproject.toml` deps+dev; `uv.lock`
    vía `uv lock --upgrade-package qgis-plugin-analyzer --no-cache --refresh`).
  - **Cobertura 135 → 171**. Prueba de que era bug de 1.15.2: analizando
    `core/validation` por separado veía los 12 módulos; en proyecto-completo solo 5.
  - **i18n**: 1.16.0 emitió **167 `MISSING_I18N`** (todas en los 36 módulos nuevos;
    0 en los ya cubiertos → la regla no cambió). Triaje a **0** =
    `extra_ignore_calls` (`_stats_edit`, `_check_field`, ya traducidas) + **129
    `# no-i18n`** (core es Qt-free; los mensajes de core son inglés por diseño →
    deuda: traducir inyectando el traductor de la GUI).
  - **CC**: refactorizadas las **3 funciones** >10 → `implausible_crs_reason`
    (14→7), `export_topography` (12→5), `export_structures` (11→7). `cc_gate` PASS.
  - **Metrics**: quality 57.9 → **56.2** · maintainability 99.9 · security 100.0 ·
    issues 35 · i18n 0 · cc_gate PASS · `module_size_gate` FAIL (4 módulos).
- **Calidad**: ruff/format limpios · `unittest discover tests` **763 OK** (Docker) ·
  `forge metrics validate` PASS · `sync_metrics --validate` PASS · `make context`
  fresco (**2.650/8.000 tokens**, 171 módulos).
- **Referencia**: `docs/maintenance/session_2026-10-11_qgis_analyzer_1_16_0.md`.
- **Pendiente / cómo reanudar**:
  1. **Deuda SecInterp (aflorada por el fix de cobertura)**: `module_size_gate` FAIL
     **4** módulos (`core/controller.py` 428, `exporters/interpretation_3d_exporter.py`
     466, `gui/adapters/geometry.py` 598, `gui/preview_layer_factory.py` 511);
     `GOD_OBJECT` 18 (la regla ahora también marca clases con >20 métodos);
     i18n de core (mensajes user-facing en inglés).
  2. **Upstream opcional (analyzer)**: la regla `MISSING_I18N` marca cadenas YA
     traducidas vía helper (`_stats_edit`, `_check_field`) y docstrings atributo
     (no solo el primero del módulo) → candidato a mejorar upstream.
  3. El resto de pendientes (tren v3.10.0/v3.11.0, `legend_widget.py`, bóveda, Goal
     1.1/1.5) siguen abajo sin cambios.

## ✅ Session 2026-10-11 — qgis-plugin-analyzer 1.15.2 (B102 fix) (COMPLETADO)

- **Qué se hizo**: se adoptó `qgis-plugin-analyzer` **v1.15.2**, el fix upstream de los
  falsos positivos `B102`/`B307` detectados en la adopción de 1.15.1 (sobre `QDialog.exec()`).
  Cierra el bucle: en la misma sesión se arregló y publicó el analyzer 1.15.2.
  - **Dependency**: `>=1.15.1` → `>=1.15.2` (`pyproject.toml` deps+dev; `uv.lock` vía
    `uv lock --upgrade-package qgis-plugin-analyzer --no-cache --refresh` — el `--refresh`
    solo no bastó por la caché del índice).
  - **Re-análisis**: `analyze . --max-cc 10` (175 ficheros / 135 módulos). **Security
    80.0 → 100.0**; issues 34 → 32 (`SECURITY:B102` eliminado); `security.findings` vacío.
  - **Upstream (misma sesión)**: release **1.15.2** del analyzer — `check_exec_eval` ignora
    llamadas de atributo/método; fix del CI `release.yml` para que PyPI se publique solo en
    eventos `release`. GitHub release + PyPI (`qgis_plugin_analyzer-1.15.2`) vivos.
- **Calidad**: ruff/format limpios · `unittest discover tests` **714 OK** ·
  `forge metrics validate` PASS · `sync_metrics --validate` PASS · `make context` fresco.
- **Referencia**: `docs/maintenance/session_2026-10-11_qgis_analyzer_1_15_2.md`.
- **Pendiente / cómo reanudar**:
  1. **Deuda SecInterp**: `module_size_gate` FAIL (`core/controller.py` 428 > 400), 15
     `GOD_OBJECT`, 1 `SPAGHETTI_CODE`, 10 `MISSING_DOCSTRING`, 4 `NON_PYTHONIC_LOOP`, 2
     `POTENTIAL_MISSING_SLOT`.
  2. **Upstream opcional (analyzer)**: `B602` marca cualquier `.run(..., shell=True)` y
     `B608` cualquier `.execute(...)` sin validar el receptor.
  3. El resto de pendientes (tren v3.10.0/v3.11.0, `legend_widget.py`, bóveda, Goal
     1.1/1.5) siguen abajo sin cambios.

## ✅ Session 2026-10-11 — qgis-plugin-analyzer 1.15.1 (Security Scanning Restored) (COMPLETADO)

- **Qué se hizo**: se adoptó `qgis-plugin-analyzer` **v1.15.1**, el fix upstream del
  registro de seguridad desconectado reportado en el análisis profundo. El escaneo de
  seguridad vuelve a ejecutarse (analyzer + `qgis-plugin-manager`, que delega en él) y
  llega el hardening recomendado: `rules/scopes.py` compartido, borrado de código muerto
  (`models/`, `modernization_rules`, `get_all_handlers`, `setup_output_dir`, helpers de
  `validators`) y menor complejidad (`ProjectAnalyzer.run` 16→1, `visit_For` 18→1,
  `visit_Constant` 17→8).
  - **Dependency**: `>=1.15.0` → `>=1.15.1` (`pyproject.toml` deps+dev; `uv.lock`).
  - **Re-análisis**: `analyze . --max-cc 10` (175 ficheros / 135 módulos). **Security
    Score 100.0 → 80.0** (el scanner ahora corre); issues 32 → 34 (+2 `SECURITY:B102`).
  - **Triage**: los 2 `B102` son **falsos positivos** sobre `QDialog.exec()`
    (`gui/dialog_interpretation_manager.py:83`, `plugin/lifecycle.py:105`); la regla casa
    llamadas de atributo y `# noqa: B102` no las suprime → **fix upstream pendiente**.
  - **Fix parser**: `scripts/sync_metrics.py` divide por el **último** `:` → ya no pierde
    `SECURITY:B102` (subcontaba `total_issues` como 32).
- **Calidad**: ruff/format limpios · `unittest discover tests` **714 OK** ·
  `forge metrics validate` PASS · `sync_metrics --validate` PASS · `make context` fresco.
- **Referencia**: `docs/maintenance/session_2026-10-11_qgis_analyzer_1_15_1.md`.
- **Pendiente / cómo reanudar**:
  1. **Upstream (analyzer)**: restringir B102/B307 a `ast.Name` (builtins) para no marcar
     `.exec()`/`.eval()` de Qt; hacer efectivo `# noqa: <RULE>` en findings de seguridad.
  2. El resto de pendientes (tren v3.10.0/v3.11.0, `legend_widget.py`, bóveda, Goal
     1.1/1.5, `module_size_gate`) siguen abajo sin cambios.

## ✅ Session 2026-10-11 — qgis-plugin-analyzer 1.15.0 Adoption (COMPLETADO)

- **Qué se hizo**: se adoptó `qgis-plugin-analyzer` **v1.15.0** ("Repo Hygiene &
  Hardening"), cambio **solo de tooling** (sin tocar el runtime del plugin). La release
  añade detección de anti-patrones (`GOD_OBJECT`, `SPAGHETTI_CODE`), métricas Halstead,
  sugerencias de optimización, `# noqa` transversal, `--workers N` y auditoría ruff fiable.
  - **Dependency**: `>=1.14.0` → `>=1.15.0` (`pyproject.toml` deps+dev; `uv.lock` vía
    `uv lock --upgrade-package qgis-plugin-analyzer --refresh`).
  - **Re-análisis**: `analyze . --max-cc 10` (175 ficheros / 135 módulos). Scores
    **sin cambios** (Stability 57.9 · Maintainability 99.9 · Security 100.0 · type-hints
    95.2/99.5% · docstrings 98.5%); **issues 16 → 32** por las reglas nuevas (+15
    `GOD_OBJECT`, +1 `SPAGHETTI_CODE`).
  - **Metrics**: `sync_metrics.py` refrescó `agent_metrics.json` (`issue_breakdown`,
    `ground_truth_sources`); `meta.tools.qgis-plugin-analyzer` → 1.15.0.
- **Calidad**: ruff/format limpios · `unittest discover tests` **714 OK** ·
  `forge metrics validate` PASS · `sync_metrics --validate` PASS · `make context` fresco.
- **Referencia**: `docs/maintenance/session_2026-10-11_qgis_analyzer_1_15_0.md`.
- **Pendiente / cómo reanudar**: backlog nuevo no bloqueante (15 `GOD_OBJECT` en
  orquestadores GUI, 1 `SPAGHETTI_CODE`); `module_size_gate` sigue FAIL
  (`core/controller.py` 428 > 400). El resto de pendientes (tren v3.10.0/v3.11.0,
  `legend_widget.py`, bóveda, Goal 1.1/1.5) siguen abajo sin cambios.

## ✅ Session 2026-10-10 — ai-context-core v5.1.0 Adoption (COMPLETADO)

- **Qué se hizo**: se adoptó `ai-context-core` **v5.1.0** ("Context Alignment &
  Hardening"), release **backward-compatible** (no quita comandos ni contratos).
  Diagrama Mermaid compacto por defecto (`mermaid_style=false`), presupuesto de
  tokens por defecto, dominios retirados (`security`/`qgis_compliance`/`patterns`/
  `antipatterns`) fuera de `project_context.json`, y el detector de imports no usados
  ahora honra `# noqa`.
  - **Dependency**: `ai-context-core>=5.0.1` → `>=5.1.0` (`pyproject.toml` deps+dev, `uv.lock`).
  - **Config**: `.ai-context/config.toml` `max_tokens` 6000 → 8000 + `mermaid_style=false`.
  - **Metrics**: `agent_metrics.json` tool → 5.1.0; `context_tokens` 619 → 2639 (estaba stale).
- **Calidad**: ruff/format limpios · `forge metrics validate` PASS · `unittest discover tests`
  **714 OK** · `make context` fresco (**2.639/8.000 tokens, 33%**).
- **Commit**: `ff6f5cfe`. **Referencia**: `docs/maintenance/session_2026-10-10_ai_context_core_v510.md`.
- **Pendiente / cómo reanudar**: sin cambios respecto a abajo → backlog
  (`module_size_gate` FAIL, docstrings, signal leaks) y **tren de release** v3.10.0 (11 oct) /
  v3.11.0 (18 oct) + divergencia `legend_widget.py`.

## ✅ Session 2026-10-10 — ai-context-core Value Leverage (COMPLETADO)

- **Qué se hizo**: `ai-context-core` pasó de artefacto stale a entrada de sesión
  fresca y curada. La clave fue arreglar `.analyzerignore`, que scopeaba **tanto**
  ai-ctx como `qgis-plugin-analyzer` solo a `gui/` → `core/` y `exporters/` quedaban
  sin gate. Ahora **71 → 135 módulos**; contexto y gates ven la lógica de negocio.
  - **Scope** `.analyzerignore`; **config v5** `.ai-context/config.toml`;
    **notas curadas** `.ai-context/architecture_notes.md` (+ `context_docs`).
  - **Frescura**: `make context` + `context-{deps,git,roadmap,graph,health}`;
    sección "Context & Architecture Tooling" en `AGENTS.md`.
  - **Higiene**: `README_DEV.md` y doc v500 corregidos; 44 ficheros legacy
    `.ai-context/` eliminados; `antigravity-framerepo/` borrado.
- **Calidad**: ruff/format limpios · `forge metrics validate` PASS · `check_docs`
  PASS · CC/i18n PASS · `AI_CONTEXT.md` 2.639/6.000 tokens, 135 módulos.
- **Plan**: `docs/plans/implementation_plan_ai_context_core_value.md`.
- **Referencia**: `docs/maintenance/session_2026-10-10_ai_context_core_value.md`.
- **Pendiente / cómo reanudar**:
  1. **Backlog (tras los releases)**: `module_size_gate=FAIL` (`core/controller.py`
     428 > 400), 10 `MISSING_DOCSTRING`, 4 `NON_PYTHONIC_LOOP`, 2
     `POTENTIAL_MISSING_SLOT`, +6 signal leaks (preexistentes, aflorados por el scope).
  2. **Release train**: v3.10.0 (11 oct) / v3.11.0 (18 oct) publican solos; al mergear
     a `main` vigilar conflictos en `.ai-context/` y refs de docs; luego bóveda v3.11.0.
  3. Deuda funcional: Goal 1.1 (symbology preview), selector multi-línea, Goal 1.5.

## ✅ Session 2026-10-08 — Unify Agentic Systems on agentic-forge (COMPLETADO)

- **Qué se hizo**: se unificaron los sistemas agénticos de los tres proyectos hermanos
  (`qgis-plugin-analyzer`, `ai-context-core`, `qgis-plugin-manager`) sobre **`agentic-forge`**
  `v1.2.0` (Codeberg). Sin cambios en el código de SecInterp; fue una sesión de coordinación
  entre repos. Plan: `docs/plans/implementation_plan_unify_agentic_systems.md`.
  - **Upstream (agentic-forge)**: núcleo genericizado (9 skills + 14 workflows), dominio QGIS a
    `scaffold/qgis/`, añadidas `testing-standards` + `release-package`/`audit-package`, tag `v1.2.0`.
  - **analyzer** / **ai-context-core** / **manager**: submódulo `.agent/` + `forge.toml` +
    `.agent-state/` + overlay skills; limpieza de sistemas legacy (`.ai-context/`, `skill_sync.py`).
- **Commits**: `agentic-forge` `2de22cf` · analyzer `4b10b11`+`fb080db` · ai-context-core `fb70feb`
  · manager `73586a2` (todos pusheados).
- **Calidad**: `forge validate` verde en los tres; `pytest` 126 / 299 / 190 OK.
- **Referencia**: `docs/maintenance/session_2026-10-08_unify_agentic_systems.md`.
- **Pendiente / cómo reanudar**:
  1. ~~Gate cross-repo que confirme que los tres pinnean la misma versión del framework.~~ ✅ **HECHO (2026-10-10)**: SecInterp subió el submódulo `a77548b` → `2de22cf` (`v1.2.0`); los tres repos alineados. Domain pack QGIS montado en `.agent-state/{skills,workflows}`.
  2. Promover `geological-logic` a `scaffold/geology` en agentic-forge.
  3. Los pendientes propios de SecInterp (tren v3.10.0/v3.11.0, `legend_widget.py`, bóveda)
     siguen abajo sin cambios.

## ✅ Session 2026-10-04 — Offline Help (User Guide only) + graphify (COMPLETADO)

- **Qué se hizo**: el botón **Help** del plugin ahora muestra un manual offline con **solo la
  User Guide** (navegación limpia, sin enlaces muertos) en 14 idiomas, **sin tocar el código del
  plugin** y **sin afectar al sitio publicado**. Se evaluó **graphify** (grafo de código local,
  ignorado en git).
  - **Help**: `docs/source/help_index.rst` (master doc solo `USER_GUIDE`); `conf.py` excluye el
    resto de docs con `SECINTERP_DOCS_HELP=1` y oculta `help_index.rst` del build web;
    `build_docs.sh` separa builds **web**/**help** (`root_doc=help_index`) y renombra
    `help_index.html` → `index.html` (parcheando enlaces) para no tocar `open_help()`.
  - **Higiene**: `.gitignore` ignora `graphify-out/`.
  - **graphify** (dev): 192 ficheros / 2929 nodos / 5216 aristas; `benchmark` 13.7× menos tokens.
- **Commits**: `92e5eabd`, `81d1f39d`.
- **Calidad**: ruff/format limpios · pre-commit PASS · `unittest discover tests` **714 OK** ·
  build help 14 locales verificado (`index.html` + `USER_GUIDE.html`) · build web intacto.
- **Referencia**: `docs/maintenance/session_2026-10-04_help_userguide_only.md`.
- **Pendiente / cómo reanudar**:
  1. **Opcional**: `make docs-i18n-update` para traducir el título “SecInterp Help”. Para añadir
     una página al manual offline, listarla en `help_index.rst`.
  2. El resto de pendientes (tren v3.10.0/v3.11.0, `legend_widget.py`, bóveda, Goal 1.1/1.5)
     siguen abajo sin cambios.

## ✅ Session 2026-10-04 — Agentic Forge Extraction (F1–F5) (COMPLETADO)

- **Qué se hizo**: se extrajo el framework agéntico reutilizable (skills/workflows/tooling) del
  estado del proyecto y se publicó en **Codeberg** como **`agentic-forge`** (MIT), consumido
  como **submódulo** en `.agent/`. Plan: `docs/plans/implementation_plan_agentic_forge_extraction.md`.
  - **F1**: estado → `.agent-state/` + `forge.toml` + `scripts/forge_paths.py` (tooling path-aware).
  - **F2**: overlay de skills de proyecto; docs genéricos; **MIT**; `export_agentic_forge.sh`;
    publicado en Codeberg (export sin historial, público).
  - **F3**: `.agent/` → submódulo; CI con `submodules: recursive`.
  - **F4**: gobernanza — tag `v1.0.0`, `update_agentic_forge.sh`, guía de sync reescrita.
  - **F5**: CLI `forge` + tools genéricos en `.agent/tools/`; `sync_metrics` partido en core
    genérico (`forge_metrics.py`) + colector de proyecto; umbrales a `forge.toml`.
  - **Fix**: `AGENTS.md` del framework (era un puntero roto) → config propia.
- **Commits**: `be5baa9f`, `a0241127`, `1a0290e4`, `a5a6a281`, `43a4aa64`, `2e7940c7`, `3ee51a5c`.
- **Framework**: https://codeberg.org/geociencio/agentic-forge (`main` `a77548b`, tags `v1.0.0`/`v1.1.0`).
- **Calidad**: Docker verde (23/237/40/323/76) · `forge validate` · `sync_metrics --validate` ·
  `check_docs` · pre-commit.
- **Pendiente / cómo reanudar**:
  1. **Codeberg**: poner **description + topics** al repo `agentic-forge` (UI).
  2. **Opcional**: genericizar menciones residuales a `SecInterp` en skills; promover
     `geological-logic` a `scaffold/geology`.
  3. **Plugin (sin cambios)**: `legend_widget.py` (divergencia al mergear el tren), bóveda
     v3.11.0 y deuda funcional (Goal 1.1/1.5, selector multi-línea).

## ✅ Session 2026-10-04 — v3.9.1 Released · Docs/Vault v2-First · ZIP & CI Fixes (COMPLETADO)

- **Qué se hizo**: se publicó **v3.9.1** y se cerró una sesión de saneamiento de docs, release
  y empaquetado.
  - **v3.9.1 publicado**: el cron de las 15:00 UTC **no disparó** (tampoco lo había hecho nunca);
    se publicó por **`workflow_dispatch`** (tag + GitHub release + ZIP). Merge
    `release/v3.9.1 → main` (`11806511`): `main` ya tiene el **perfil suavizado**.
  - **Docs v2-first**: `README` + `ARCHITECTURE_EN` / `MONOLITHIC_VS_CLEAN` / `PLUGIN_REPORT`
    actualizados a **v3.9.1** (módulos 177, tests 745→**763** tras el merge, features v3.9);
    **v1 congelado** (excluido de `sync_vault_mirrors.sh`); espejos v2 regenerados; bóveda a
    v3.9.1 (footers 356 notas + Index) y structure docs con `vertical_exaggeration_service` /
    `crs_plausibility`.
  - **Quick wins `.agent/`**: `black`→`ruff format`, refs fantasma
    (`prune_consolidated.py`, `COMMIT_GUIDELINES`), conteos (745/763, 15 workflows), Gen 8
    marcado implementado, `qgis-migration-4x` referenciado, contador del validador.
  - **Versión**: `metadata.txt`/`pyproject.toml` → **3.9.1**; `make docs-version` (7 docs);
    CHANGELOG [3.9.1].
  - **Ayuda/ZIP**: el CI empaquetaba **sin `help/`** (0.4 vs 3.9 MiB). Arreglado el workflow
    (`mkdir -p help` + build de docs) y `build_docs.sh`. **Optimización**: dedup de `_static`
    (22 assets) + PNG lossless (`pyoxipng`) → ayuda 8.5→**3.7 MiB**; ZIP 3.76→**2.38 MiB**.
    Excluido `.release-queue.json` del paquete. Asset del release v3.9.1 **reemplazado**.
- **Commits**: `314a4f34`, `654ead62`, `cd6838ab`, `11806511`, `3c31e322`, `fb7918e5`,
  `48a73ca6`, `b7c52db3`.
- **Calidad**: suite Docker verde (23/237/40/323/76) · ruff PASS · gates docs/vault/agentes PASS ·
  analyzer 0 issues.
- **Pendiente / cómo reanudar**:
  1. **Portal QGIS**: ~~subir `dist/sec_interp.3.9.1.zip`~~ ✅ **HECHO** — v3.9.1
     (2.38 MiB, con ayuda en 14 idiomas) ya está en el repositorio de plugins de QGIS.
  2. **Tren**: v3.10.0 (11 oct) / v3.11.0 (18 oct) publican solos; el workflow ahora usa el
     `build_docs.sh` optimizado de `main` → incluirán la ayuda optimizada. Verificar cada uno.
  3. **⚠️ Divergencia `legend_widget.py`**: las ramas del tren **eliminaron**
     `gui/legend_widget.py` (commit `1d82db0f`, panel lateral de leyenda); `main` lo
     **conserva**. Al mergear el tren en `main` (v3.11.0): eliminar las refs a
     `legend_widget.py` en `docs/ARCHITECTURE_EN.md`, `docs/structure/project_structure*.md`
     y resolver el conflicto (por esto el backport directo a las ramas quedó bloqueado por el
     doc-gate).
  4. **Bóveda completa v3.11.0**: refresco completo cuando `main` consolide el tren.
  5. **Deuda funcional**: Goal 1.1 Fase 4 (presets), selector multi-línea, Goal 1.5.

## ✅ Session 2026-09-27 — Release Train, CI Hardening & Vault Refresh (COMPLETADO)

- **Qué se hizo**: se liberó **v3.9.0** y se preparó el **tren incremental** v3.9.1 /
  v3.10.0 / v3.11.0 con publicación **programada** (domingos 4 / 11 / 18 oct). Se reparó el
  **CI** (llevaba rojo en cada push) y se refrescó la **bóveda v2** a v3.9.0.
  - **v3.9.0**: merge boundary `76908843` en `main`, versión, CHANGELOG, notas de release,
    dev-log; **bug bloqueante** de aislamiento de mocks en `tests/gui` corregido; gates
    (696 locales / 681 Docker, analyzer 0, security PASS); ZIP auditado; tag + **GitHub
    release publicado**. Commits `e00604e`, `664d775`. **Portal: manual, omitido por decisión.**
  - **Tren v3.9.1/3.10.0/3.11.0**: ramas `release/v3.9.1|v3.10.0|v3.11.0` (acumulativas) con
    merge + versión + notas (714 / 729 / 743 tests). Workflow programado
    `.github/workflows/scheduled-release.yml` + `.release-queue.json`; validado con
    `dry_run` de v3.9.1 (checkout + Docker tests + build, sin publicar).
  - **CI**: lint fijado al ruff del lock (`ISC004`/`PLR0917` de ruff 0.16); detección real
    de hallazgos Qt6; job de tests migrado al **Docker** del proyecto; deploy de docs
    omitido si falta `DOCS_DEPLOY_TOKEN`; eliminado `release.yml` legado. `main` **en verde**.
  - **Qt6/QGIS4**: `QgsRasterBandStats.All` → `.Stats.All` y `Qgis.RasterBandStatistic.All`
    (con fallback 3.28–3.39) en `dem_page.py`; aplicado a `main` + las 3 ramas.
  - **Bóveda v2 → v3.9.0**: notas `preview_param_hasher`/`ui_status_manager` a tier A,
    nuevas `crs_plausibility`/`layer_metadata`/`topo_renderer`, footers a v3.9.0 (346),
    Index/hubs/mapa actualizados. `check_notes --strict` PASS (308).
- **Referencia**: `docs/maintenance/session_2026-09-27_release_train_and_vault_refresh.md`.
- **Pendiente / cómo reanudar**:
  1. **Portal QGIS**: ~~subir el ZIP del release que se publique (v3.9.1 el 4 oct)~~ ✅
     **HECHO** — v3.9.1 ya está en el repositorio de plugins de QGIS.
  2. **v3.9.0**: no se sube al portal (decisión); v3.9.1+ ya traen los fixes de Qt6.
  3. **Tren**: los domingos 4/11/18 oct el workflow publica solo; sincronizar `main`
     manualmente al final (`git merge --ff-only release/v3.11.0`).
  4. **Bóveda completa v3.11.0**: refresco completo cuando `main` consolide el tren.
  5. **Deuda funcional**: Goal 1.1 Fase 4 (presets), selector multi-línea, Goal 1.5.

## ✅ Session 2026-09-23 — Optional Smoothed Topography Profile (COMPLETADO)

- **Qué se hizo**: perfil suavizado opcional — checkbox **Smooth** + ventana (m)
  en Controls que superpone una línea roja suave y exporta `*_smoothed.csv` +
  `profile_line_smoothed.<ext>`; filtro de media móvil por distancia (core, puro).
- **Commits**: `3094a1f1`, `76fc6206`.
- **Calidad**: suite verde · ruff/format limpios · analyzer 0 issues · gates
  CC/Module Size/i18n PASS · smoke QGIS 4 OK.
- **Referencia**: `docs/maintenance/session_2026-09-23_smoothed_profile.md`.
- **Sin bugs abiertos**. Diferidos: remuestreo bilineal, Savitzky-Golay,
  selector multi-línea, editor por unidad (Goal 1.1), leyenda.

## ✅ Session 2026-09-23 — DEM/Section v3.9.0 Phases (1.5, 1.6, 2, 3) (COMPLETADO)

- **Qué se hizo**: se completó el plan v3.9.0 — resolver central de la sección
  (Fase 1.5, neutro), stats de banda del DEM + combo ancho/unidades abreviadas
  (Fase 1.6), modo de color del perfil gradiente/simple (Fase 2) y stats
  perfil-vs-DEM (Fase 3).
- **Commits**: `2a14767b`, `2352f031`, `008b18ad`, `b978e4ee`, `6d342189` (5) +
  cierre.
- **Calidad**: suite verde · ruff/format limpios · analyzer 0 issues · smoke QGIS 4
  OK (stats DEM, colores, stats de perfil, export).
- **Referencia**: `docs/maintenance/session_2026-09-23_dem_section_v390_phases.md`.
- **Sin bugs abiertos**. Queda deuda: **selector multi-línea** (infra lista),
  remuestreo bilineal, editor por unidad (Goal 1.1), leyenda, y reimportar el CSV
  de geología como UTF-8.

## ✅ Session 2026-09-23 — CRS Sampling Hardening + Structure/Section Fixes (COMPLETADO)

- **Qué se hizo**: se corrigió un cuelgue del sistema al muestrear un DEM
  geográfico (EPSG:4326, mal nombrado `..._3857.tif`) con línea proyectada
  (32614, OTF). También elevaciones 0 en estructuras/collares por CRS, se añadió
  detección **bloqueante** de CRS mal etiquetado, y se arreglaron los combos de
  campo estructurales. Se commitó el gating S0/S1/S2 previo.
- **Commits**: `baf11d8c`, `98758e92`, `02d9cd65`, `1e44c658`, `ef88acf7`,
  `eb9ffa20` (6).
- **Calidad**: suite verde (unittest discover 666; tooling ground truth 715) ·
  ruff/format limpios · smoke manual QGIS 4 completo
  (sin cuelgue; 430 pts/6109 m = 14.24 m; estructuras sobre el perfil; collar Z
  correcto; interpretaciones heredadas + persistencia; export GPKG/PNG OK).
- **Referencia**: `docs/maintenance/session_2026-09-23_crs_sampling_hardening.md`.
- **Sin bugs abiertos**. Diferidos: leyenda (tamaño/jerarquía), remuestreo
  bilineal, selector multi-línea (Fase 1.5), y reimportar el CSV de geología como
  UTF-8 (acentos se perdieron en el origen).

## 🚧 Session 2026-09-22 — Code Walkthrough Vault v2 (COMPLETO)

**Handover de la bóveda v2** (docs-only; sin cambios en Python):

- **Qué se hizo**: nueva bóveda completa bilingüe v2 (`docs/code_walkthrough_v2/` ES +
  `docs/code_walkthrough_en_v2/` EN); la v1 queda intacta.
  - Tooling: `scripts/generate_vault_v2.py` (AST, tiering A/B/C, slugs sin colisión,
    enumeración de archivos de paquete, `HIGH_IMPORTANCE` → `note_lines: 700`),
    `scripts/check_notes.py` (gate 400–500, mínimos por tier A/C=400 B=300, tope 700,
    placeholders, paridad ES↔EN). `check_docs.py` + `sync_vault_mirrors.sh` actualizados.
  - `docs/structure/project_structure_table.md` (vista tabular Depth 1–5).
- **Estado**: Bóveda v2 **COMPLETA y commiteada** — Core 56/56 + GUI 73/73 + Fase 3 22/22 +
  Fase 4 (23 hubs `layer_*` + Index final ES/EN) + mapa archivo→nota
  (`project_structure_links.md`, 178 ficheros → 151 notas, script regenerable).
  `check_notes.py --strict` PASS (302 notas, 0 placeholders, 0 enlaces rotos).
  Commits: `1d4af77d` `d5e8a82b` `b7d221f7` `dab9d27e` `26ada077` (+ cierre).
  Tooling: `resolve_group_slugs` + 23 hubs + `project_structure_links` en SKIP_STEMS.
- **Cómo reanudar**: `uv run python scripts/generate_vault_v2.py --layer <capa> --write`
  para generar esqueletos; enriquecer cada nota leyendo el fuente hasta 400–500 líneas;
  validar con `uv run python scripts/check_notes.py` (y `--strict` al finalizar).
- **Convenciones clave**: notas de paquete → tabla `Archivos del paquete` con self-anchors
  `[[#Sección\|archivo.py]]`; archivos con nota individual se enlazan en `layer_*`; tope
  500 por defecto, `note_lines` (máx 700) solo para la lista `HIGH_IMPORTANCE`.

### Pendiente bóveda v2
- [x] Enriquecer ~49 esqueletos de Core restantes — COMPLETO ✅ (49/49, `check_notes.py --strict` PASS).
- [x] Fase 2 GUI — COMPLETO ✅ (73/73: 63 individuales + 10 grupos, `check_notes.py --strict` PASS).
- [x] Fase 3 Exporters/Plugin/Raíz — COMPLETO ✅ (22/22: 19 individuales + 3 grupos, `--strict` PASS).
- [x] Fase 4 `layer_*` + Index final — COMPLETO ✅ (23 hubs + Index ES/EN, 0 enlaces rotos, `--strict` PASS).
- [ ] Referencia: `docs/maintenance/session_2026-09-22_code_walkthrough_v2.md`.

## ✅ Session 2026-09-21 — Adaptive Vertical Exaggeration + Preview fixes (COMPLETADO)

- Adaptive VE end-to-end (Goal 1.2), VE visible, fix scratch layers. 643 tests.
- Referencia: `docs/maintenance/session_2026-09-21_adaptive_ve_and_preview_fixes.md`.

## 🎯 Goals pendientes (post v3.8.0)

### Goal 1: 3D Interpretation & Symbology Enhancements
- [ ] **1.1** Live symbology/legend styling preview bajo el sidebar de Settings.
- [x] **1.2** Adaptive VE — COMPLETO 2026-09-21 ✅
- [ ] **1.5** Expandir tests de integración de proyección vertical cartesiana.

## 🧾 Deuda restante (documentada, no bloqueante)

- **6 áreas grises** (integración QGIS genuina): `i18n.py`, `config.py`, `data_cache.py`,
  `access_control_service.py`, `export/map_settings_factory.py`, `export/orchestrator.py`, `io.py`.
- **Analyzer**: 0 issues.
- **Docs i18n opcional**: traducir `USER_GUIDE` fr (28%) / de (18%); `make docs` para publicar.
- **QA MCP QGIS 4 (exploración)**: propuesta de un MCP de QA acotado para automatizar el
  smoke en QGIS 4 → `docs/plans/exploration_qgis4_qa_mcp.md` (no implementado; opción B).

## 🚀 How to Resume
1. Run `/start-session`.
2. `docs/plans/implementation_plan_dem_section_v3.9.0.md`: **completo** (Fase 0 ✅,
   1 ✅, 1.5 ✅, 1.6 ✅, 2 ✅, 3 ✅) + **perfil suavizado** ✅ (extra). Opciones:
   - **Geología sobre el perfil suavizado (v3.9.1)** → plan aprobado (Opción A),
     pendiente: `docs/plans/implementation_plan_smoothed_geology_v3.9.1.md`.
   - **Selector multi-línea** (deuda; resolver + `section_feature_id` ya listos).
   - **Goal 1.1** (symbology/legend preview) o **Goal 1.5** (tests proyección).
   - Preparar **release v3.9.0/v3.9.1** (`/release-plugin`).
