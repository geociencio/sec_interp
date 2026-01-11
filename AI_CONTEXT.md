# CONTEXTO PARA IA - sec_interp
Generado automáticamente por ProjectAnalyzer v2.0 (Optimizado)

## 📁 ESTRUCTURA DEL PROYECTO

./
    .analyzer_state.json
    .analyzerignore
    .coverage
    .dockerignore
    .flake8
    .gitattributes
    .gitignore
    ... (+33 más)
    i18n/
        SecInterp_de.qm
        SecInterp_de.ts
        SecInterp_es.qm
        SecInterp_es.ts
        SecInterp_fr.qm
        SecInterp_fr.ts
        SecInterp_pt_BR.qm
        ... (+6 más)
    help/
        html/
            .nojekyll
            ARCHITECTURE.html
            DEVELOPMENT_GUIDE.html
            MAINTENANCE_LOG.html
            TECHNICAL_COMPENDIUM.html
            USER_GUIDE.html
            genindex.html
            ... (+101 más)
    scripts/
        clean_imports.py
        fix-ui-syntax.sh
        inspect_qgs_api.py
        package-for-qgis.sh
        run_benchmarks.py
        run_tests_in_qgis.py
        setup_venv.sh
        ... (+1 más)
    docs/
        CHANGELOG.md
        DEVELOPMENT_LOG.md
        PLUGIN_ANALYSIS.md
        release_process_ai.md
        images/
            ui_main_dialog.png
            workflow_01_select_dem.png
            workflow_02_select_dem.png
            workflow_03_select_section_line.png
            workflow_04_preview_generated.png
            workflow_04_preview_panels_co


## 🎯 PUNTOS DE ENTRADA
- `.ai-context/ai_workflow.py`
- `.ai-context/analyze_project_optfixed.py`
- `.ai-context/context_manager.py`
- `.venv/lib/python3.13/site-packages/analyzer/cli.py`
- `.venv/lib/python3.13/site-packages/black/__main__.py`
- `.venv/lib/python3.13/site-packages/blackd/__main__.py`
- `.venv/lib/python3.13/site-packages/certifi/__main__.py`
- `.venv/lib/python3.13/site-packages/charset_normalizer/__main__.py`
- `.venv/lib/python3.13/site-packages/charset_normalizer/cli/__main__.py`
- `.venv/lib/python3.13/site-packages/dill/__diff.py`

... y 78 más

## 🏗️ PATRONES DETECTADOS
- **MVC**: Detectado (confianza: 100%)
## 📈 COMPLEJIDAD Y MÉTRICAS
- **Módulos totales**: 100
- **Líneas de código**: 15,324
- **Funciones**: 539
- **Clases**: 95
- **Complejidad promedio**: 14.5
- **Módulos más complejos**: core/services/drillhole_service.py, gui/main_dialog_settings.py, gui/preview_layer_factory.py

## 🔗 DEPENDENCIAS PRINCIPALES

### Third Party (más frecuentes):
- `qgis` (117 imports)
- `sec_interp` (61 imports)
- `pages` (8 imports)
- `geometry_utils` (7 imports)
- `layer_validator` (7 imports)
- `field_validator` (5 imports)
- `geometry` (5 imports)
- `profile_exporters` (4 imports)
- `spatial` (4 imports)
- `drillhole` (3 imports)
- `parsing` (3 imports)
- `project_validator` (3 imports)
- `rendering` (3 imports)
- `sampling` (3 imports)
- `abc` (2 imports)

## 💡 RECOMENDACIONES DE OPTIMIZACIÓN

### core/services/profile_service.py (Prioridad: MEDIA)
- **funciones_demasiado_largas**: Funciones muy largas (promedio 87.0 líneas/función)

### core/utils/drillhole.py (Prioridad: MEDIA)
- **funciones_demasiado_largas**: Funciones muy largas (promedio 75.0 líneas/función)

### core/validation/layer_validator.py (Prioridad: ALTA)
- **refactorizacion_complejidad**: Alta complejidad (36) con 6 funciones

### core/utils/io.py (Prioridad: MEDIA)
- **funciones_demasiado_largas**: Funciones muy largas (promedio 58.0 líneas/función)

### core/types.py (Prioridad: ALTA)
- **refactorizacion_complejidad**: Alta complejidad (44) con 9 funciones
- **modulo_demasiado_grande**: Módulo muy grande (374 líneas)

## 🕸️  ESTRUCTURA DE DEPENDENCIAS
- **Nodos**: 100
- **Aristas**: 120
- **Densidad**: 0.012
- **Grafo acíclico**: Sí
- **Componentes conectados**: 34

## 🕸️ DIAGRAMA DE DEPENDENCIAS (Conceptuall)
```mermaid
graph TD
```

## 🔑 PALABRAS CLAVE DEL PROYECTO
- **Tecnologías**: .py, .dat, .pyc, .pyi, .sip, .qml, .so, .mo
- **Patrones**: mvc
