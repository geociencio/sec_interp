# Reporte de Análisis Técnico y Recomendaciones Arquitectónicas
**Proyecto:** SecInterp (QGIS Plugin)
**Versión Analizada:** 3.1.0
**Fecha:** 25 de febrero de 2026

## 1. Resumen Ejecutivo
El proyecto `sec_interp` presenta una arquitectura robusta basada en servicios y una clara separación de responsabilidades (Domain, Logic, UI). Sin embargo, el crecimiento del plugin ha generado una "dispersión de utilidades", donde funciones críticas de la API de QGIS y lógica transversal se han duplicado en múltiples capas, aumentando la deuda técnica y el riesgo de inconsistencias.

---

## 2. Hallazgos: Errores y Deficiencias Técnicas

### 2.1. Fallo en la Cadena de Inyección de Dependencias (SafeLoader)
*   **Componente:** `core/utils/safe_loader.py` -> `lazy_load`
*   **Descripción:** El método asume constructores vacíos (`klass()`).
*   **Impacto:** Los servicios que requieren dependencias (como `DrillholeService` o `GeologyService`) fallan silenciosamente o registran excepciones al ser cargados perezosamente, rompiendo la arquitectura de DI definida en el `ProfileController`.

### 2.2. Invalidez de Caché por Sobre-Alcance
*   **Componente:** `core/controller.py` -> `connect_layer_notifications`
*   **Descripción:** Cualquier cambio en una capa (ej. mover un punto estructural) dispara `data_cache.clear()`.
*   **Impacto:** Pérdida total de datos procesados. El usuario experimenta latencia innecesaria al tener que recalcular topografía y sondeos cuando solo cambió un dato menor de otra categoría.

### 2.3. Código "Boilerplate" en el Punto de Entrada
*   **Componente:** `sec_interp_plugin.py` -> `run()`
*   **Descripción:** Presencia de comentarios de plantilla y bloques `if result: pass`.
*   **Impacto:** Reduce la legibilidad y calidad percibida del código fuente principal.

---

## 3. Redundancias y Code Smells (Deuda Técnica)

### 3.1. Duplicidad Masiva: Resolución de Capas
*   **Hallazgo:** **41 implementaciones** de `_resolve_layer` o lógica equivalente.
*   **Ubicación:** `sec_interp_plugin.py`, `ProfileController`, `DrillholeOrchestrator`, y múltiples Managers de GUI.
*   **Riesgo:** Inconsistencia en el manejo de errores si una capa es inválida o ha sido eliminada del proyecto.

### 3.2. Fragmentación de Traducciones (`tr`)
*   **Hallazgo:** **8 métodos `tr()`** implementados manualmente invocando `QCoreApplication.translate`.
*   **Riesgo:** Errores en el contexto de traducción de Qt (context name), dificultando la internacionalización precisa.

### 3.3. Tipado Débil en Capa de Servicios
*   **Hallazgo:** Uso extensivo de `list[tuple]` en retornos de servicios críticos (ej. `project_collars`).
*   **Impacto:** Código frágil que depende de índices numéricos (`res[0]`) en lugar de nombres semánticos, dificultando la refactorización de los modelos de datos.

---

## 4. Plan de Acción y Recomendaciones

### Fase 1: Consolidación de Utilidades (Corto Plazo)
1.  **Crear `core/utils/qgis.py`:** Centralizar la resolución de capas en una única función robusta que valide `isValid()` y maneje IDs/nombres uniformemente.
2.  **Implementar `TranslatableMixin`:** Crear un Mixin en `core/utils/` para estandarizar la lógica de `tr()` en clases que no heredan de `QObject`.

### Fase 2: Refactorización de Servicios (Medio Plazo)
1.  **Migración a Dataclasses:** Reemplazar todos los retornos basados en tuplas por las entidades ya definidas en `core/domain/entities.py`.
2.  **Caché Granular:** Modificar `DataCache` para permitir la limpieza por "buckets" o etiquetas. Así, un cambio en la capa de sondeos solo invalidaría el bucket `"drill"`, preservando el resto de los datos procesados.
3.  **Mejora de SafeLoader:** Extender `lazy_load` para soportar argumentos de construcción (`*args`, `**kwargs`).

### Fase 3: Limpieza y Estándares (Mantenimiento)
1.  **Centralizar Validaciones:** Mover toda la lógica de validación de los servicios hacia el `ValidationPipeline`.
2.  **Eliminación de Código Muerto:** Limpiar `sec_interp_plugin.py` de residuos de la plantilla original.
