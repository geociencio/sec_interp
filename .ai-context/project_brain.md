# Cerebro del Proyecto: sec_interp

## 🚨 Reglas Críticas (Globales)
- **ESCAPADO DE METADATOS**: Escapar % como %% en metadata.txt.

## Visión General
Plugin de QGIS para interpretación de secciones geológicas, manejo de sondajes (drillholes) y perfiles estructurales.

<!-- METRICS_START -->
## 📊 Métricas de Salud (Actualizado: 2026-01-17)
- **Score de Calidad**: 83.5/100
- **Líneas de Código**: 16,960
- **Complejidad Promedio**: Reducida tras refactorización de `gui/main_dialog.py`.
<!-- METRICS_END -->
## 🏗️ Arquitectura Principal (Patrones Detectados)
- **MVC (Model-View-Controller)**: Separación clara entre la lógica de QGIS (Model), los diálogos de PyQt (View) y el coordinador (`core/controller.py`).
- **Gestores (Managers)**: Uso intensivo de gestores especializados para desacoplar la lógica de UI (`InterpretationManager`, `SettingsManager`, `ToolManager`, etc.).

## 🔗 Componentes Críticos
1. **Controller (`core/controller.py`)**: Cerebro de la aplicación.
2. **Measure Tool (`gui/tools/measure_tool.py`)**: Herramienta de medición con snapping avanzado.
3. **Preview Renderer (`gui/preview_renderer.py`)**: Motor de renderizado nativo QGIS (Complejidad 21.8).
4. **Drillhole Service (`core/services/drillhole_service.py`)**.

## 🚨 Deuda Técnica y Prioridades
- **Violaciones de Arquitectura**: 10 casos detectados (mezcla UI en Core).
- **Alta Complejidad**: `core/validation.py` requiere fragmentación. `gui/main_dialog.py` ahora tiene complejidad 13 (reducida desde 95).
- **Refactorización de Workflow**: `ai_workflow.py` ha sido mejorado con normalización, pero necesita mayor modularidad.
- **Snapping**: Expandir `QgsPointLocator` a otros tipos de entidades si es necesario.
