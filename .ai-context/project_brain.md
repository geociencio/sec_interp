# Cerebro del Proyecto: sec_interp

## 🚨 Reglas Críticas (Globales)
- **ESCAPADO DE METADATOS**: Escapar % como %% en metadata.txt.

## Visión General
Plugin de QGIS para interpretación de secciones geológicas, manejo de sondajes (drillholes) y perfiles estructurales.

<!-- METRICS_START -->
## 📊 Métricas de Salud (Actualizado: 2026-01-22)
- **Score de Calidad (ai-ctx)**: 54.6/100
- **Module Stability Score**: 55.3/100
- **Code Maintainability Score**: 100.0/100
- **Overall Plugin Score**: 27.6/100
- **QGIS Compliance**: 0/100
- **Líneas de Código**: 17,246
- **Total Files**: 171
- **Type Hint Coverage (Params)**: 75.5%
- **Type Hint Coverage (Returns)**: 36.9%
- **Docstring Coverage**: 66.3%
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

### Desviaciones Técnicas Detectadas: 692
- **Falta de Docstrings**: 171 módulos sin docstring de módulo (PEP 257)
- **Alta Complejidad Ciclomática** (2 casos):
  - `core/services/drillhole_service.py:132` - `prepare_task_input()` (CC=16, límite: 15)
  - `gui/main_dialog_interpretation.py:156` - `apply_attribute_inheritance()` (CC=21, límite: 15)
- **Imports Legacy**: Uso de `from PyQt5 import ...` en tests (debería usar `qgis.PyQt`)
- **Constantes Obsoletas**: Uso de `QVariant` en tests (debería usar `QMetaType` o tipos nativos)

### Prioridades de Mejora
1. **Documentación**: Añadir docstrings a módulos y funciones públicas
2. **Refactorización**: Reducir complejidad en los 2 métodos identificados
3. **Modernización**: Actualizar imports legacy en tests
4. **Type Hints**: Mejorar cobertura de returns (36.9% → 60%+)
