# CONTEXTO PARA IA - sec_interp

> [!CAUTION]
> **REGLA CRÍTICA DE METADATOS**: El repositorio de QGIS usa `configparser`. Debes **escapar todos los signos de porcentaje (%%) como %%%%** en las secciones `changelog` y `about` de `metadata.txt` para evitar errores de interpretación.

Generado automáticamente por ProjectAnalyzer v2.0 (Optimizado)

## 📁 ESTRUCTURA DEL PROYECTO

./
    .analyzer_state.json
    .analyzerignore
    .flake8
    .gitattributes
    .gitignore
    .pre-commit-config.yaml
    .pylintrc
    ... (+29 más)
    i18n/
        SecInterp_de.qm
        SecInterp_de.ts
        SecInterp_es.qm
        SecInterp_es.ts
        SecInterp_fr.qm
        SecInterp_fr.ts
        SecInterp_pt_BR.qm
        ... (+4 más)
    help/
        html/
            ARCHITECTURE.html
            DEVELOPMENT_GUIDE.html
            MAINTENANCE_LOG.html
            TECHNICAL_COMPENDIUM.html
            USER_GUIDE.html
            genindex.html
            index.html
            ... (+103 más)
    scripts/
        clean_imports.py
        compile-strings.sh
        deploy.sh
        fix-ui-syntax.sh
        inspect_qgs_api.py
        package-for-qgis.sh
        setup_venv.sh
        ... (+1 más)
    docs/
        CHANGELOG.md
        images/
            ui_main_dialog.png
            workflow_01_select_dem.png
            workflow_02_select_dem.png
            workflow_03_select_section_line.png
            workflow_04_preview_generated.png
            workflow_04_preview_panels_colapsed.png
            workflow_05_geology_setup.png
            ... (+3 más)



## 🎯 PUNTOS DE ENTRADA
- `.ai-context/ai_workflow.py`
- `.ai-context/context_manager.py`
- `.venv/lib/python3.13/site-packages/black/__main__.py`
- `.venv/lib/python3.13/site-packages/blackd/__main__.py`
- `.venv/lib/python3.13/site-packages/certifi/__main__.py`
- `.venv/lib/python3.13/site-packages/charset_normalizer/__main__.py`
- `.venv/lib/python3.13/site-packages/charset_normalizer/cli/__main__.py`
- `.venv/lib/python3.13/site-packages/distlib/index.py`
- `.venv/lib/python3.13/site-packages/docutils/__main__.py`
- `.venv/lib/python3.13/site-packages/docutils/parsers/commonmark_wrapper.py`

... y 54 más

## 🏗️ PATRONES DETECTADOS
- **MVC**: Detectado (confianza: 100%)
- **REPOSITORY**: Detectado (confianza: 100%)
- **FACTORY**: Detectado (confianza: 80%)
## 📈 COMPLEJIDAD Y MÉTRICAS
- **Módulos totales**: 95
- **Líneas de código**: 13,706
- **Funciones**: 433
- **Clases**: 90
- **Complejidad promedio**: 12.7
- **Módulos más complejos**: core/services/drillhole_service.py, core/validation/project_validator.py, gui/preview_layer_factory.py

## 🔗 DEPENDENCIAS PRINCIPALES

### Third Party (más frecuentes):
- `qgis` (107 imports)
- `sec_interp` (60 imports)
- `geometry_utils` (8 imports)
- `layer_validator` (7 imports)
- `geometry` (6 imports)
- `pages` (6 imports)
- `field_validator` (5 imports)
- `profile_exporters` (4 imports)
- `spatial` (4 imports)
- `drillhole` (3 imports)
- `main_dialog_config` (3 imports)
- `parsing` (3 imports)
- `project_validator` (3 imports)
- `rendering` (3 imports)
- `sampling` (3 imports)

## 💡 RECOMENDACIONES DE OPTIMIZACIÓN

### core/services/geology_service.py (Prioridad: ALTA)
- **refactorizacion_complejidad**: Alta complejidad (32) con 7 funciones
- **modulo_demasiado_grande**: Módulo muy grande (404 líneas)

### core/services/structure_service.py (Prioridad: ALTA)
- **refactorizacion_complejidad**: Alta complejidad (24) con 7 funciones
- **modulo_demasiado_grande**: Módulo muy grande (345 líneas)

### core/utils/sampling.py (Prioridad: MEDIA)
- **funciones_demasiado_largas**: Funciones muy largas (promedio 51.7 líneas/función)

### core/utils/drillhole.py (Prioridad: MEDIA)
- **funciones_demasiado_largas**: Funciones muy largas (promedio 74.0 líneas/función)

### core/services/export_service.py (Prioridad: ALTA)
- **refactorizacion_complejidad**: Alta complejidad (29) con 9 funciones

## 🕸️  ESTRUCTURA DE DEPENDENCIAS
- **Nodos**: 95
- **Aristas**: 109
- **Densidad**: 0.012
- **Grafo acíclico**: Sí
- **Componentes conectados**: 35
