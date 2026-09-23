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

**Diferido explícito** (futuro): selector de feature si la capa trae varias líneas;
remuestreo bilineal (hoy `sample()` es vecino más cercano → perfil escalonado aceptado).

**Gating UI incluido**: etiquetas Mandatory en DEM/Section; páginas Geology/Structural/
Drillholes deshabilitadas hasta DEM+Section; botones en 3 estados (S0 todo bloqueado,
S1 solo Preview+OK, S2 resto tras preview vigente verificado por hash). Detalle en Fase 0.

**Objetivo cuantitativo**: 6 call sites `next(getFeatures())` intactos (sin selector no hay
plomería); 0 imports `qgis` nuevos en `core/`; `check_notes` y suite verdes.

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

**Archivos**: `gui/ui/pages/section_page.py`, `core/validation/project_validator.py`
(+ `ValidationParams`/metadata que porte nº de vértices), `tests/gui/test_section_page.py` (nuevo),
tests de `project_validator` en `tests/core/`.

- `SectionPage.validate()`: exige `LineString` de exactamente 2 vértices (más capa presente).
- Regla core con primitivos (nº vértices, sin QGIS): el semáforo `lbl_section_status`,
  `can_preview()` y `validate_inputs()` la heredan sin tocar managers.
- Longitud > 0 y CRS no geográfico como errores en la misma regla (el buffer en m y la
  escala solo tienen sentido proyectados).
- Con 2 puntos, `calculate_line_azimuth` == azimut de toda la línea: definición única.

**Criterios**: línea 2-pt OK; 3-pt/multi/vacía rechazadas en page y core; punto rojo + preview
bloqueado; suite verde.

## Fase 2 — Modo de color del perfil (solo Present, sin core)

**Archivos**: `section_page.py`, `gui/main_dialog_config.py` (`DialogDefaults`),
`preview_layer_factory.py` (`create_topo_layer(..., style_kwargs)`),
`gui/renderers/topo_renderer.py`, `tests/gui/renderers/test_renderers.py`,
`tests/gui/test_section_page.py`.

- Controles: radio Gradiente/Simple + `QComboBox` con `QgsStyle.defaultStyle().colorRampNames()`
  + `QgsColorButton` (matriz de compatibilidad: mínimo declarado 3.28 + LTR 3.44.14
  'Solothurn'; verificar ambos en build — el Docker CI usa `qgis/qgis:latest`).
- Claves nuevas `get_data/dump/load/reset`: `color_mode` (`gradient|single`), `ramp_name`,
  `single_color_hex` (+ defaults). Plomería: page → `input_manager` → params de preview →
  `create_topo_layer` → `apply_style(layer, **kwargs)`.
- `TopoRenderer`: `ramp_name` con fallback al Spectral→RdYlGn actual si falta; modo simple →
  `QgsSingleSymbolRenderer`. Se mantienen las 8 clases fijas en modo gradiente.
- Nunca se modifica la capa origen; el estilo vive solo en memory layers de preview.

**Criterios**: rampa elegida visible en preview; color único aplicado; rampa inexistente →
fallback sin crash; round-trip dump/load; suite verde.

## Fase 3 — Stats perfil-vs-DEM (solo lectura)

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

## Decisiones abiertas (resolver antes o durante build)

| # | Decisión | Propuesta | Estado |
|---|---|---|---|
| 1 | ¿Botón OK en S1 o S2? | S1 (OK genera/acepta; no requiere preview previo) | ⏳ pendiente usuario |
| 2 | Azimut: ¿inicio-fin o util core (2 primeros puntos)? | Util `calculate_line_azimuth` (con líneas 2-pt son idénticos) | ✅ implícito |
| 3 | CRS geográfico: ¿error o warning? | Error (buffer en m y escala exigen proyectado) | ⏳ confirmar en build |
| 4 | Nº clases del gradiente configurable (hoy 8 fijas) | No en este alcance (hacia Goal 1.1) | ✅ diferido |

## Transversales (las 4 fases)

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
  `bandStatistics` bloqueante en rásteres remotos → solo banda actual, sin caché persistente;
  `bandStatistics` bloqueante en rásteres remotos → solo banda actual, sin caché persistente;
  `colorRampNames()` vacío en estilos mínimos → fallback actual.

## Fuera de alcance (registrado)

- Selector de feature multi-línea (requiere migrar 6 `next(getFeatures())` a helper central).
- Remuestreo bilineal / perfil suavizado.
- Nº de clases del gradiente configurable; editor de estilos por unidad (hacia Goal 1.1).
