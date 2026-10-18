# Implementation Plan: DEM Stats + Section Line Hardening + Topo Color Modes

**Phase**: v3.9.0 — Goal 1 (UX de perfil topográfico)
**Status**: 📝 PLAN — guardado para próxima sesión (alcance ampliado con gating UI)
**Created**: 2026-09-23 · **Ampliado**: 2026-09-23 (etiquetas Mandatory, gating S0/S1/S2, bloqueo de páginas)
**Referencias**: `dem_page.py:271`, `section_page.py:117`, `topo_renderer.py:32`,
  `preview_layer_factory.py:166`, `geometry.py:156` (`sample_elevation_along_line`),
  `core/utils/spatial.py:8` (`calculate_line_azimuth`), `dialog_input_manager.py:181-196`

---

## 0. Resumen Ejecutivo

Tres mejoras encadenadas sobre las páginas DEM/Raster y Section Line:

1. **Stats del ráster** en `DemPage` (min/max/media/nodata, solo lectura).
2. **Endurecer Section Line**: solo líneas simples de **2 puntos** (validación en page + regla
   core para que el semáforo y el gating la hereden), más **stats perfil-vs-DEM** y
   **modo de color** (gradiente elegible o color simple) con plomería hasta `TopoRenderer`.
3. **Dedupe de muestras** del mismo píxel antes de agregar stats (los DEM públicos de
   30 m/15 m + el `ceil()` del densificado lo hacen frecuente).

**Diferido explícito** (futuro): selector **UI** de feature si la capa trae varias líneas
(la infraestructura —resolutor + plomería— se implementa en **Fase 1.5**);
remuestreo bilineal (hoy `sample()` es vecino más cercano → perfil escalonado aceptado).

**Gating UI incluido**: etiquetas Mandatory en DEM/Section; páginas Geology/Structural/
Drillholes deshabilitadas hasta DEM+Section; botones en 3 estados (S0 todo bloqueado,
S1 solo Preview+OK, S2 resto tras preview vigente verificado por hash). Detalle en Fase 0.

**Objetivo cuantitativo**: 8 sitios `next(getFeatures())` migrados al resolutor (Fase 1.5),
con comportamiento idéntico (`feature_id=None`); 0 imports `qgis` nuevos en `core/`;
`check_notes` y suite verdes.

---

## 1. Contexto técnico verificado

| Hecho | Fuente |
|---|---|
| Stats de ráster no existen (`bandStatistics` sin uso en el repo) | grep `bandStatistics` → 0 hits |
| `TopoRenderer` hardcodea Spectral→RdYlGn, 8 clases fijas, campo `elev` | `topo_renderer.py:21-32` |
| `create_topo_layer` llama `apply_style(layer)` **sin kwargs** aunque el contrato `BasePreviewRenderer.apply_style(layer, **kwargs)` los admite | `preview_layer_factory.py:166`, `base_renderer.py:58` |
| Sin widgets de rampa en el repo (no `QgsColorRampButton/ComboBox`) | grep → 0 hits |
| Muestreo: `sample_elevation_along_line(geom, raster, band, da)`, intervalo = resolución X si `None`, fallback a geometría sin densificar | `geometry.py:156-187` |
| Densificado: `ceil(seg_len/interval)` → espaciamientos < píxel frecuentes; `sample()` vecino más cercano → duplicados idénticos | `geometry.py:89-108,183` |
| Azimut canónico puro: `calculate_line_azimuth` (2 primeros puntos) | `core/utils/spatial.py:8` |
| Semáforo/gating: `ui_status_manager` → `input_manager.is_section_valid("section")` → reglas sobre `ValidationParams` | `ui_status_manager.py:41-80`, `dialog_input_manager.py:181-196` |
| Tests base: `tests/gui/test_dem_page.py` existe; `test_section_page.py` no; renderers en `tests/gui/renderers/test_renderers.py` | glob `tests/gui/` |

---

## Fase 0 — Mandatory + gating de páginas y botones (base UX)

**Status**: ✅ IMPLEMENTADO 2026-09-23 (rama `feature/dem-section-v3.9.0`; 18 tests nuevos
en `tests/gui/test_ui_gating.py`; suite 612 OK). Ajuste post-prueba QGIS 4:
`QListWidgetItem` no tiene `setDisabled` — se usa `flags()` ± `Qt.ItemFlag.ItemIsEnabled`
(helper `UIStatusManager._set_item_enabled`); `MockQListWidgetItem` ahora implementa
`flags()/setFlags()/isEnabled()` con la máscara real de Qt. Además la **VE entra en la
firma de vigencia** (`last_success_ve` + `_compute_vertical_exaggeration` sin log) y los
controles `vertexag_spin.valueChanged` / `auto_ve_check.toggled` refrescan el gating, así
que cambiar la exageración desactiva el trío hasta regenerar.

**Archivos**: `gui/ui/main_window.py` (`:139-145`, `:147-151`), `gui/ui/sidebar.py`
(`add_item` devuelve el item), `gui/ui_status_manager.py` (`update_button_state`,
nuevo `update_page_states` llamado desde `update_all`), `gui/dialog_preview_manager.py`
(`last_success_hash`, `is_preview_current()`), `dem_page.py` + `section_page.py`
(títulos de grupo), `tests/gui/test_main_dialog_validation_manager.py` (extender),
tests de `main_window`/pages para labels.

### 0.1 Etiquetas Mandatory/Obligatorio

- Sidebar `"DEM / Raster"` y `"Section Line"` → sufijo `self.tr("Mandatory")`
  (ES "Obligatorio" vía catálogos i18n; en inglés visible de inmediato).
- Mismo sufijo en los títulos de grupo de `DemPage` y `SectionPage`. Los `*` de campos
  se mantienen.

### 0.2 Páginas bloqueadas hasta DEM+Section

- `Sidebar.add_item` devuelve el `QListWidgetItem`; `main_window` guarda refs
  (`nav_geology`, `nav_struct`, `nav_drillhole` — filas 2/3/4, sin hardcodear índices).
- Nuevo `UIStatusManager.update_page_states()` (desde `update_all`): habilita esas 3
  páginas solo si `dem` y `section` válidos (`is_section_valid`); si la página visible
  queda deshabilitada → `setCurrentRow(0)`. Interpretation/Settings intactas.

### 0.3 Botones S0/S1/S2 por hash de preview

- **S0** (DEM/Section incompletos): Preview, OK, Export, Measure, Interpret bloqueados
  (`btn_save` conserva su regla `can_export()`).
- **S1** (completos, sin preview vigente): solo Preview + OK.
- **S2** (preview vigente): Export/Measure/Interpret (+Finalize al hacerse visible).
- Vigencia sin señales extra: `PreviewManager.last_success_hash` (se fija en
  `_update_ui_state`, éxito incl. caché; se limpia en reset/cleanup) +
  `is_preview_current()` (hash actual vía `_get_and_validate_inputs()` vs guardado).
  Sin modificar la capa origen en ningún caso.

**Criterios**: S0 todo bloqueado + páginas 2-4 deshabilitadas; S1 solo Preview/OK;
cambio de inputs invalida S2 automáticamente; labels Mandatory visibles; suite verde.

## Fase 1 — Invariante 2 puntos (desbloquea el resto)

**Status**: ✅ IMPLEMENTADO 2026-09-23 (rama `feature/dem-section-v3.9.0`; suite 627 OK,
analyzer 0 issues, CC PASS, ruff/format limpios).

**Archivos**: `gui/ui/pages/section_page.py`, `core/validation/project_validator.py`
(+ `ValidationParams`/metadata que porte nº de vértices), `tests/gui/test_section_page.py` (nuevo),
tests de `project_validator` en `tests/core/`.

- `SectionPage.validate()`: exige `LineString` de exactamente 2 vértices (más capa presente).
- Regla core con primitivos (nº vértices, sin QGIS): el semáforo `lbl_section_status`,
  `can_preview()` y `validate_inputs()` la heredan sin tocar managers.
- Longitud > 0 y CRS no geográfico como errores en la misma regla (el buffer en m y la
  escala solo tienen sentido proyectados).
- Con 2 puntos, `calculate_line_azimuth` == azimut de toda la línea: definición única.

**Implementación**:
- `LayerMetadata.crs_is_geographic` (extractor GUI lo puebla vía `crs.isGeographic()`).
- `ValidationParams.line_vertex_count` / `line_length` (primitivos), poblados por
  `extract_section_line_metrics()` (adaptador Extract, `setLimit(1)`, defensivo → `None`).
- `section_line_geometry_error()` en `project_validators.py` (SSoT de la regla), invocada
  por `SectionValidator.validate` y expuesta como `ProjectValidator.section_geometry_error`;
  la usa también la regla `"section"` de `InputManager` (check + mensaje dinámico).
- `SectionPage.validate()` con mensajes explícitos; `is_complete()` delega en `validate()`.
- Refactor CC: `_disconnect_vertical_exaggeration_signals()` en `dialog_signal_manager`.

**Criterios**: línea 2-pt OK; 3-pt/multi/vacía rechazadas en page y core; punto rojo + preview
bloqueado; suite verde. (Pendiente: smoke manual en QGIS 4.)

## Fase 1.5 — Resolutor central de la línea de sección (prep multi-línea)

**Status**: ✅ IMPLEMENTADO 2026-09-23 (rama `feature/dem-section-v3.9.0`; Bloque A + B + C;
10 tests nuevos en `tests/gui/test_section_resolver.py`; suite 681 OK).
**Objetivo**: un único punto de resolución de la feature de sección, parametrizable por
`feature_id`, usado por los 8 sitios actuales con `feature_id=None` (primera feature).
Prepara el selector multi-línea y elimina duplicación (`line_start`, lectura de la 1ª feature).

### Bloque A — Resolutor, migración y firmas

1. `gui/adapters/geometry.py`: `resolve_section_feature(line_lyr, feature_id=None)`,
   `resolve_section_geometry(line_lyr, feature_id=None)`, `section_line_start_point(geom)`.
   `None` → `getFeatures(setLimit(1))`; fid → `getFeatures(setFilterFid(fid))`; defensivo.
2. Migrar los 8 sitios a `feature_id=None` y `line_start` a `section_line_start_point`:
   `profile_extractor:36,70` · `geometry:194,220` · `geology_extractor:133` ·
   `structure_extractor:164` · `drillhole_extractor:158` · `dialog_preview_manager:233`.
3. `extract_section_line_metrics(layer_ref, feature_id=None)` vía resolutor (mantiene el
   `try/except` defensivo); actualizar `build_validation_params`,
   `InputManager.get_validation_params`, `SectionPage.validate`.
4. `feature_id=None` (trailing/keyword) en firmas públicas:
   `ProfileExtractor.calculate_lod_interval` / `.extract_profile`,
   `GeologyExtractor.extract_context`, `StructureExtractor.extract_section_and_structures`,
   `DrillholeExtractor.extract_context`; y privados `_read_line_geometry`/`_extract_line_info`.
   Callers (`controller`, `preview_service`, `preview_task_orchestrator`) siguen sin pasarlo.
5. **Fidelidad de mocks** (lección `setDisabled`): `MockQgsFeatureRequest.setFilterFid/filterFid/
   setLimit/limit`; `MockQgsVectorLayer.getFeatures` honra fid/limit e **ignora** rect/expresión
   (para no romper el test de índice espacial); verificar `MockQgsFeature.id()`.

### Bloque B — Cadena de datos lista (neutra en comportamiento)

`section_feature_id` (primitivo, default `None`) en: `PreviewParams`, `assemble_preview_params`,
`PreviewParamHasher.calculate_hash` (invalidación S2 al cambiar la selección), `ValidationParams`
+ `build_validation_params`, `SectionPage.get_data/dump/load/reset`, y
`InputManager.get_all_values`/`get_validation_params`. El selector futuro solo aporta el widget
+ sus señales; el camino hasta los extractores queda cableado.

### Tests / verificación

`tests/gui/test_section_resolver.py` (default, fid elegido, fid inexistente, capa inválida,
geometría nula, `section_line_start_point` simple/multipart, métricas con fid); suite completa;
`ruff`/`format`; `qgis-analyzer --max-cc 10`; smoke manual QGIS 4 (comportamiento idéntico).

## Fase 1.6 — Stats del ráster DEM (solo lectura)

**Status**: ✅ IMPLEMENTADO 2026-09-23 (rama `feature/dem-section-v3.9.0`; 4 tests nuevos en
`tests/gui/test_dem_page.py`; suite 670 OK).

**Archivos**: `gui/ui/pages/dem_page.py`, `tests/gui/test_dem_page.py`.

- `DemPage` muestra **Min / Max / Mean / NoData** de la banda seleccionada (campos read-only).
- `dataProvider().bandStatistics(band, QgsRasterBandStats.All, QgsRectangle(), 250_000)` con
  `sampleSize` acotado y `try/except` → rásteres remotos/raros muestran "—" sin bloquear.
- `sourceNoDataValue(band)` (None/NaN → "—").
- Refresco en `raster_combo.layerChanged` y `band_combo.bandChanged` (desconexión simétrica);
  `reset()` limpia.
- Sin caché persistente; no se modifica la capa origen.

**Criterios**: valores correctos vs mock; sin capa o fallo → guiones; unidades coherentes con
`Resolution`; suite verde. (Pendiente: smoke manual QGIS 4.)

## Fase 2 — Modo de color del perfil (solo Present, sin core)

**Status**: ✅ IMPLEMENTADO 2026-09-23 (rama `feature/dem-section-v3.9.0`; radios Gradient/
Simple + `QgsColorRampButton`/`QgsColorButton`; `color_mode/ramp_name/single_color_hex` en
`PreviewParams` + hasher; `TopoRenderer` single/gradient con fallback; 10 tests nuevos;
suite 691 OK).

**Archivos**: `section_page.py`, `gui/main_dialog_config.py` (`DialogDefaults`),
`preview_layer_factory.py` (`create_topo_layer(..., style_kwargs)`),
`gui/renderers/topo_renderer.py`, `tests/gui/renderers/test_renderers.py`,
`tests/gui/test_section_page.py`.

- Controles: radio Gradiente/Simple + `QComboBox` con `QgsStyle.defaultStyle().colorRampNames()`
  + `QgsColorButton` (matriz de compatibilidad: mínimo declarado 3.28 + LTR 3.44.14
  'Solothurn' + **test manual en QGIS 4**; el Docker CI usa `qgis/qgis:latest`).
- Claves nuevas `get_data/dump/load/reset`: `color_mode` (`gradient|single`), `ramp_name`,
  `single_color_hex` (+ defaults). Plomería: page → `input_manager` → params de preview →
  `create_topo_layer` → `apply_style(layer, **kwargs)`.
- `TopoRenderer`: `ramp_name` con fallback al Spectral→RdYlGn actual si falta; modo simple →
  `QgsSingleSymbolRenderer`. Se mantienen las 8 clases fijas en modo gradiente.
- Nunca se modifica la capa origen; el estilo vive solo en memory layers de preview.

**Criterios**: rampa elegida visible en preview; color único aplicado; rampa inexistente →
fallback sin crash; round-trip dump/load; suite verde.

## Fase 3 — Stats perfil-vs-DEM (solo lectura)

**Status**: ✅ IMPLEMENTADO 2026-09-23 (rama `feature/dem-section-v3.9.0`;
`profile_raster_statistics` con dedupe por celda + `ProfileRasterStats`; grupo "DEM Profile"
en `SectionPage` alimentado por `set_dem_provider` y refrescado en señales de línea/ráster/
banda; 5 tests nuevos; suite 696 OK).

**Archivos**: `section_page.py` (+ acceso al ráster vía `dialog`/`input_manager`, **sin**
import page→page), `tests/gui/test_section_page.py` (ráster mockeado).

- Reutilizar `sample_elevation_along_line` con la banda de `page_dem`; display Min/Max/Media
  + **`n muestras @ resolución`** (imprescindible con DEM 30 m: ~10 muestras en 300 m).
- **Dedupe**: colapsar muestras consecutivas del mismo píxel antes de agregar (el `ceil()`
  sesgaría min/max/media hacia valores repetidos). No se toca el densificado.
- Sin ráster o línea inválida: guiones, sin bloquear. Recalcular en `layerChanged` de
  línea/raster/banda con señales simétricas.

**Criterios**: stats correctas vs fixture mockeado; duplicados no sesgan; `n @ res` visible;
guiones sin ráster; suite verde.

---

## Decisiones (resueltas 2026-09-23, ver `1consideraciones*.md`)

| # | Decisión | Resolución |
|---|---|---|
| 1 | ¿Botón OK en S1 o S2? | ✅ **S1** — exigir preview para aceptar añade fricción en cambios menores (color, VE); Export/Measure sí requieren S2 (operan sobre el resultado) |
| 2 | Azimut: ¿inicio-fin o util core? | ✅ **`calculate_line_azimuth`** (`core/utils/spatial.py`, SSoT; exacto con 2 puntos) |
| 3 | CRS geográfico: ¿error o warning? | ✅ **Error** — buffers/azimuts/muestreo en grados carecen de sentido; bloquear en validación previene bugs en render/core |
| 4 | Nº clases del gradiente configurable | ✅ **Diferido** (hacia Goal 1.1); 8 clases + fallback bastan |

## Recomendaciones técnicas vinculantes (de `1consideraciones*.md`)

- **Hash ligero (Fase 0)**: `is_preview_current()` corre en cada `update_all`; el hash debe
  basarse estrictamente en `layer.id()` + primitivos de widgets, **nunca** en leer
  geometrías (`PreviewParamHasher` ya usa `layer.id()` — verificar que
  `_get_and_validate_inputs()` no extraiga data espacial).
- **Dedupe por celda, no por Z (Fase 3)**: en terrenos planos (salares) el mismo Z en
  píxeles distintos es natural; deduplicar por distancia 2D vs `rasterUnitsPerPixelX()`
  o por coordenadas de celda origen.
- **`bandStatistics` en remoto (Fase 1 DEM)**: pasar `extent` o limitar sampleo; capturar
  excepción/timeout (~1-2 s) para no colgar QGIS con WCS/VRT gigantes.
- **Mensaje 2-pt explícito**: `"La línea de sección debe tener exactamente 2 vértices
  (inicio y fin)"`.

## Transversales (las fases)

- **i18n**: todo string visible con `self.tr()` (páginas) / `QCoreApplication.translate` (mixins).
- **Señales**: toda conexión nueva con su `disconnect_signals` simétrico (`contextlib.suppress`).
- **Tests Mock-first**: `tests/base_test.py`; ráster/capas mockeadas, sin QGIS real en unit.
- **Docs**: actualizar notas v2 afectadas (`dem_page`, `section_page`, `topo_renderer`,
  `preview_layer_factory`, `project_validator`) o el gate `--strict` las marcará obsoletas
  solo si cambian líneas (no es gate de contenido; opcional pero recomendado).
- **Riesgos**: `QgsColorRampComboBox` no existe como tal → combo manual + verificación en
  3.28 y LTR 3.44.14 (las APIs propuestas — `bandStatistics`, `sourceNoDataValue`,
  `colorRampNames`, `QgsColorButton` — existen en todo el rango 3.28–3.44, pero el
  Docker CI corre `latest`, así que la LTR se verifica manual);
  `bandStatistics` bloqueante en rásteres remotos → solo banda actual, sin caché persistente;
  `colorRampNames()` vacío en estilos mínimos → fallback actual;
  `is_preview_current()` reconstruye params en cada `update_all` → vigilar costo si hay
  spam de señales (el hash es barato; la validación ya corre en ese flujo);
  renombrar `lbl_*`/items del sidebar rompe `ui_status_manager` (nombres hardcodeados,
  documentado en bóveda) → usar refs guardadas, no índices.

## Fuera de alcance (registrado)

- Selector de feature multi-línea → ver **Deuda técnica** abajo.
- Remuestreo bilineal. **Perfil suavizado ya implementado** (extra v3.9.0); la
  **geología sobre el perfil suavizado** se planifica en
  [`implementation_plan_smoothed_geology_v3.9.1.md`](implementation_plan_smoothed_geology_v3.9.1.md).
- Nº de clases del gradiente configurable; editor de estilos por unidad (hacia Goal 1.1).

## Deuda técnica registrada — Selector de feature multi-línea

> **Actualización 2026-09-23**: la parte **estructural** (puntos 1 y 2: resolutor central +
> plomería de `section_feature_id`) pasa a la **Fase 1.5**. La deuda que permanece aquí es la
> **cara al usuario**: selector UI, identidad estable entre sesiones, orientación/invertir,
> elegibilidad y sub-keys de caché.

**Qué**: permitir que la capa de sección tenga varias líneas y que el usuario elija cuál
usar (hoy se toma siempre la primera feature). Dificultad **media-alta, ancha más que
profunda**: el core casi no cambia; el 80% es GUI + consistencia.

**Por qué es costoso**:

1. ~~**No hay resolutor central**~~ → **resuelto en Fase 1.5** (`resolve_section_feature` en
   `geometry.py`), que además evita el drift entre los sitios (p. ej. `buffer(..., 25)` vs
   `DEFAULT_BUFFER_SEGMENTS = 8`).
2. ~~**Plomería del dato**~~ → **resuelto en Fase 1.5 (Bloque B)**: `section_feature_id` ya
   recorre `PreviewParams`/hasher/validación/`InputManager`; el selector solo añade el widget.
3. **Identidad estable (mayor riesgo)** — `QgsFeature.id()` no es estable entre
   ediciones/exportaciones. Fid solo para la sesión (fácil) o campo identificador estable +
   fallback (requiere elegir un "campo etiqueta" → otro parámetro).
4. **Orientación del perfil (inicio/fin)** — la distancia 0 se ancla al primer vértice
   (`geometry.py:209`); con selección hay que fijar el orden y probablemente ofrecer invertir.
   El invariante 2-pt de Fase 1 debe validar el feature **elegido**, no el primero.
5. **Geometría/elegibilidad** — MultiLineString o features de N vértices; decidir si el
   selector filtra candidatos a 2 puntos para no romper el invariante.
6. **Caché** — invalidar `DataCache` por buckets y `LayerResolver` al cambiar la selección;
   confirmar que los sub-keys de caché del controller incluyan la selección (si no,
   reutilizaría topo/geol de otra línea).
7. **UI/UX** — `QgsFeaturePickerWidget`/combo fid+campo etiqueta (selección desde capa),
   pick en canvas (reusar `measure_tool`/`snapper`) o **dibujar la línea** (esta última evita
   identidad de feature: elimina los puntos 3 y 5).

**Enfoque recomendado**: Fase 1.5 aporta el resolutor + la plomería; después un selector por
fid en sesión (sin persistencia entre sesiones) + filtrar candidatos a 2 puntos, y mapear a un
campo estable en una fase posterior. Estimación restante: ~4-5 archivos GUI (widget + persistencia) +
tests; 1 sesión.

---

## Plan complementario — Geología sobre el perfil suavizado (v3.9.1)

Tras implementar el **perfil suavizado** (extra v3.9.0), se acordó hacer que la **geología**
siga la línea suavizada (**Opción A**: suavizar el perfil maestro de geología al extraer;
estructuras y collares se mantienen crudos por ser datos de interpretación). `Smooth` pasa a
ser un **dato del perfil** (entra en `PreviewParams`/hash ⇒ invalida S2 y se aplica al pulsar
Preview; el export de geología también sale suavizado).

Detalle completo (archivos, tests, riesgos y alcance) en
[`implementation_plan_smoothed_geology_v3.9.1.md`](implementation_plan_smoothed_geology_v3.9.1.md).
Estado: ✅ IMPLEMENTADO 2026-09-23.

---

## Plan complementario — Preview Side Panel: leyenda + interpretaciones + interacción (v3.10.0)

La leyenda (overlay que tapaba el perfil) se mueve a un **panel lateral colapsable** con
**lista de interpretaciones** y, además, **ocultar/editar color por unidad geológica**
(núcleo de Goal 1.1). La leyenda del export no cambia. Detalle en
[`implementation_plan_preview_side_panel_legend_v3.10.0.md`](implementation_plan_preview_side_panel_legend_v3.10.0.md).
Estado: ✅ IMPLEMENTADO 2026-09-23 (L-A + L-B).

---

## Plan relacionado — Goal 1.1: Live Symbology & Legend Styling Preview (v3.11.0)

Editor de simbología con vista previa en vivo bajo Settings (estilos por capa + editor por
unidad completo: color/ocultar/renombrar/reordenar + opciones de leyenda). El núcleo por
unidad ya se entregó en v3.10.0. Detalle, fases y decisiones abiertas en
[`implementation_plan_symbology_preview_v3.11.0.md`](implementation_plan_symbology_preview_v3.11.0.md).
Estado: 📝 PLAN propuesto (alcance pendiente de confirmar).
