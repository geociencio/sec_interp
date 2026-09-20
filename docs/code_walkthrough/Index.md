---
tags:
  - secinterp
  - code-walkthrough
  - moc
aliases:
  - SecInterp Code Walkthrough
  - Guía de Código SecInterp
cssclass: secinterp-moc
---

# 🗺️ SecInterp — Code Walkthrough (MOC)

> [!abstract] Propósito
> Esta bóveda documenta **archivo por archivo** la implementación de SecInterp.
> Cada nota explica el rol, los patrones y las relaciones de un módulo del código.
> Se irá ampliando progresivamente.

> [!info] Contexto del proyecto
> - **Plugin**: SecInterp (Section Interpreter) — QGIS ≥ 3.28, QGIS 4.x ready
> - **Arquitectura**: Clean Architecture (Core/GUI separation)
> - **Versión documentada**: 3.8.0
> - Ver también: [[ARCHITECTURE_EN]] · [[ARCHITECTURE_MONOLITHIC_VS_CLEAN_EN]] · [[PLUGIN_REPORT_AND_COMPARISON_EN]]

---

## 📚 Índice de notas

### Nivel raíz (entry point)
| Archivo | Estado | Descripción breve |
|---|:------:|------------------|
| [[sec_interp_plugin]] | ✅ | Clase raíz `SecInterp`: ciclo de vida del plugin, toolbar, DI |
| [[__init__]] | ✅ | Factory `classFactory` que QGIS invoca |
| [[logger_config]] | ✅ | Logging centralizado + handler QGIS |

### Capa Core (`core/`)
| Archivo | Estado | Descripción breve |
|---|:------:|------------------|
| [[controller]] | ✅ | `ProfileController` — orquestador de servicios |
| [[domain]] | ✅ | DTOs: `PreviewParams`, `ProfileData`, `GeologySegment`… |
| [[exceptions]] | ✅ | Jerarquía `SecInterpError` |
| [[profile_service]] | ✅ | Extracción de topografía |
| [[geology_service]] | ✅ | Intersecciones geológicas |
| [[drillhole_service]] | ✅ | Proyección de sondajes |
| [[validation]] | ✅ | Pipeline de validación |
| [[safe_loader]] | ✅ | Carga lazy y tolerante a fallos |
| [[i18n]] | ✅ | `TranslatableMixin` |
| [[structure_service]] | ✅ | Proyección estructural |
| [[config]] | ✅ | Servicio de configuración (QgsSettings) |
| [[data_cache]] | ✅ | Caché por buckets (SHA256 + TTL) |
| [[performance_metrics]] | ✅ | Timings, conteos y memoria |
| [[export_service]] | ✅ | Orquestación de exportación |
| [[preview_service]] | ✅ | Generación de preview |
| [[access_control_service]] | ✅ | Control de acceso |
| [[trajectory_engine]] | ✅ | Trayectoria de sondajes |
| [[collar_processor]] | ✅ | Procesador de collares |
| [[survey_processor]] | ✅ | Procesador de surveys |
| [[interval_processor]] | ✅ | Procesador de intervalos |
| [[projection_engine]] | ✅ | Proyección 3D→2D |

### Capa GUI (`gui/`)
| Archivo | Estado | Descripción breve |
|---|:------:|------------------|
| [[main_dialog]] | ✅ | `SecInterpDialog` — orquestador de managers |
| [[dialog_preview_manager]] | ✅ | Ciclo de preview y canvas |
| [[dialog_export_manager]] | ✅ | UI de exportación |
| [[renderers]] | ✅ | Renderers especializados |
| [[tasks]] | ✅ | `QgsTask` en background |
| [[adapters]] | ✅ | Fase "Extract" (QGIS → DTOs) |
| [[ui_pages]] | ✅ | Ventana + páginas (Sidebar/Stack) |
| [[state_manager]] | ✅ | Delegación estado visual + persistencia |
| [[input_manager]] | ✅ | Agregación de entradas + validación |
| [[signal_manager]] | ✅ | Centralización idempotente de signals |
| [[interpretation_manager]] | ✅ | Polígonos + herencia + persistencia dual |
| [[tool_manager]] | ✅ | Pan + Measure + Interpretation tools |
| [[layer_notification_manager]] | ✅ | dataChanged → invalidate(bucket) |
| [[ui_status_manager]] | ✅ | Indicadores + enable/disable |
| [[preview_state]] | ✅ | PreviewCache + RenderState |
| [[preview_layer_factory]] | ✅ | Factory de capas de memoria |
| [[preview_renderer]] | ✅ | Orquestador de render |
| [[preview_axes_manager]] | ✅ | Rejilla + ejes (nice 1-2-5) |
| [[drillhole_extractor]] | ✅ | Extract de sondajes |
| [[structure_extractor]] | ✅ | Extract de estructuras |
| [[geology_extractor]] | ✅ | Extract de geología |
| [[validation_extractor]] | ✅ | Extract de validación |
| [[measure_tool]] | ✅ | Herramienta de medición |
| [[interpretation_tool]] | ✅ | Herramienta de interpretación |
| [[drillhole_page]] | ✅ | Página de sondajes |
| [[settings_page]] | ✅ | Página de configuración |

### Capa Exporters (`exporters/`)
| Archivo | Estado | Descripción breve |
|---|:------:|------------------|
| [[base_exporter]] | ✅ | Contrato `BaseExporter` |
| [[vector_exporter]] | ✅ | GPKG/SHP/DXF |
| [[csv_exporter]] | ✅ | CSV tabular |
| [[interpretation_3d_exporter]] | ✅ | Export 3D interpretaciones |
| [[drillhole_3d_exporter]] | ✅ | Export 3D sondajes |
| [[pdf_exporter]] | ✅ | PDF |
| [[svg_exporter]] | ✅ | SVG |
| [[image_exporter]] | ✅ | Imagen raster |
| [[profile_exporters]] | ✅ | Export de perfil |
| [[dxf_exporter]] | ✅ | DXF |
| [[interpretation_exporters]] | ✅ | Export 2D interpretaciones |
| [[drillhole_exporters]] | ✅ | Export vectorial sondajes |

> [!tip] Leyenda
> ✅ documentado · ⏳ pendiente · 🔄 en revisión

> [!note] Documentos espejo
> Los archivos `ARCHITECTURE_EN.md`, `ARCHITECTURE_MONOLITHIC_VS_CLEAN_EN.md` y `PLUGIN_REPORT_AND_COMPARISON_EN.md` dentro de esta bóveda son **copias espejo** de `docs/` (fuente de verdad). Se mantienen aquí para que los wikilinks resuelvan en Obsidian. Si actualizas el original en `docs/`, re-sincroniza estas copias.

> [!info] Convención de nombres
> **Actualizado 2026-09-20**: se eliminaron los prefijos `NN -` de todas las notas. Los nombres son ahora el slug del archivo (p. ej. `preview_renderer.md`). La navegación es por secciones/tags, no por número.

---

## 🧭 Cómo leer estas notas

Cada nota sigue la misma plantilla:

1. **Frontmatter** — tags y aliases para búsqueda.
2. **Resumen** — qué hace y por qué existe.
3. **Diagrama** — Mermaid de relaciones.
4. **Recorrido del código** — método por método.
5. **Patrones** — qué patrones de diseño aplica.
6. **Relaciones** — wikilinks a módulos relacionados.
7. **Observaciones** — notas, riesgos y mejoras.

> [!warning] Convención de enlaces
> Los enlaces `[[...]]` pueden aparecer **sin resolver** hasta que se cree la nota.
> Eso es intencional: marcan el trabajo futuro.

---

## 🔖 Tags usados

`#secinterp` · `#code-walkthrough` · `#moc` · `#core` · `#gui` · `#exporters` · `#entry-point` · `#di` · `#i18n` · `#qgstask`

---

*Nota raíz de la bóveda — actualizar al añadir cada nueva nota.*
