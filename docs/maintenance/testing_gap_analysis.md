# Reporte de Brechas de Testing (Marzo 2026)

Tras un análisis comparativo entre los 122+ módulos de producción y la suite de 368 tests distribuidos en 54 archivos de prueba, se han identificado las siguientes lagunas críticas de cobertura:

## 1. Core Services (Lógica de Dominio)
Módulos críticos que carecen de tests unitarios especializados:
- **`core/services/access_control_service.py`**: Sin pruebas de permisos y control de funcionalidades.
- **`core/services/drillhole/`**: Falta cobertura granular para los procesadores de `Collar`, `Survey` e `Interval` de forma aislada (están cubiertos principalmente por tests de integración gruesos).
- **`core/services/geology/`**: Los procesadores de afloramientos y muestreo carecen de tests de estrés con grandes volúmenes de datos.

## 2. Core Utils (Infraestructura)
- **`core/utils/safe_loader.py`**: Solo tiene tests de inyección de dependencias básicos. Falta probar escenarios de fallo de red o corrupción de módulos.
- **`core/utils/resource_manager.py`**: Sin pruebas de ciclo de vida de recursos de sistema.
- **`core/performance_metrics.py`**: No hay tests que validen la precisión de las métricas reportadas.

## 3. GUI Tasks (Asincronía - Área Ciega Crítica)
No existe el directorio `tests/gui/tasks/`. La lógica asíncrona de:
- **`gui/tasks/drillhole_task.py`**
- **`gui/tasks/geology_task.py`**
Solo se prueba mediante tests de integración de "caja negra". Falta validación de cancelación de tareas y manejo de estados intermedios.

## 4. Renderizadores Especializados
No existe cobertura para los componentes de dibujo específicos:
- **`gui/renderers/topo_renderer.py`**
- **`gui/renderers/drillhole_renderer.py`**
- **`gui/preview_legend_renderer.py`**

## 5. Utilidades de UI
- **`gui/lod_calculator.py`**: Crucial para el rendimiento, pero no tiene validación de umbrales de detalle.
- **`gui/preview_reporter.py`**: Encargado del feedback al usuario, sin pruebas de renderizado de reportes.

---
### Recomendación Prioritaria:
Implementar tests unitarios para **`gui/tasks/`** y **`core/services/access_control_service.py`**, ya que son componentes fundamentales para la estabilidad y seguridad (Phase 4).
