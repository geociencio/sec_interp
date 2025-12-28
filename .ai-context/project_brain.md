# Cerebro del Proyecto: sec_interp

## Visión General
Plugin de QGIS para interpretación de secciones geológicas, manejo de sondajes (drillholes) y perfiles estructurales.

## 📊 Métricas de Salud (Actualizado: 2025-12-27)
- **Score de Calidad**: 89.7/100
- **Score Cumplimiento QGIS**: 100.0/100
- **Líneas de Código**: 12,334 en 90 módulos.
- **Complejidad Promedio**: 12.5. (Módulos más complejos: `gui/main_dialog_preview.py`, `core/services/drillhole_service.py`, `gui/preview_layer_factory.py`).
## 🏗️ Arquitectura Principal (Patrones Detectados)
- **MVC (Model-View-Controller)**: Separación clara entre la lógica de QGIS (Model), los diálogos de PyQt (View) y el coordinador (`core/controller.py`).
- **Repository**: Manejo de persistencia y acceso a datos a través de servicios.
- **Snapping Manual**: Uso de `QgsPointLocator` para snapping en capas de memoria sin polucionar el proyecto.

## 🔗 Componentes Críticos
1. **Controller (`core/controller.py`)**: Cerebro de la aplicación.
2. **Measure Tool (`gui/tools/measure_tool.py`)**: Herramienta de medición con snapping avanzado.
3. **Preview Renderer (`gui/preview_renderer.py`)**: Motor de renderizado nativo QGIS (Complejidad 21.8).
4. **Drillhole Service (`core/services/drillhole_service.py`)**.

## 🚨 Deuda Técnica y Prioridades
- **Violaciones de Arquitectura**: 10 casos detectados (mezcla UI en Core).
- **Alta Complejidad**: `gui/main_dialog.py` (Complexity 95) y `core/validation.py` requieren fragmentación.
- **Refactorización de Workflow**: `ai_workflow.py` ha sido mejorado con normalización, pero necesita mayor modularidad.
- **Snapping**: Expandir `QgsPointLocator` a otros tipos de entidades si es necesario.
