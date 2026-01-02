# Registro de Cambios

Todos los cambios notables en este proyecto serán documentados en este archivo.

El formato se basa en [Keep a Changelog](https://keepachangelog.com/es/1.0.0/),
y este proyecto se adhiere a [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.5.0] - 2026-01-01
### 🚀 Características Principales
- **Exportación de Interpretación 3D**:
  - Exportar interpretaciones geológicas como Shapefiles 3D reales (PolygonZ).
  - Transformación afín vértice a vértice asegurando la integridad geométrica de estructuras complejas del subsuelo (ej. pliegues volcados).
  - Implementación nativa con API de QGIS usando `QgsPolygon` y `QgsLineString`.
- **Control Avanzado e UI**:
  - **Página de Configuración**: Navegación lateral dedicada para configuración avanzada del plugin.
  - **Servicio de Control de Acceso**: Infraestructura lista para usar para gestionar características restringidas y niveles de usuario.
  - **Configuración persistente** vía `QgsSettings`.

## [2.4.0] - 2025-12-31
### Añadido
- **Soporte de Internacionalización (I18n)**:
  - Soporte multi-idioma para 5 lenguas: Español (ES), Francés (FR), Alemán (DE), Ruso (RU), Portugués Brasil (PT_BR).
  - Traducción completa de cadenas de UI usando el sistema de traducción de Qt.
  - Detección automática de idioma basada en la configuración regional de QGIS.
  - Archivos de traducción (`.ts`) y binarios compilados (`.qm`) para todos los idiomas soportados.
  - Scripts para gestión de traducciones (`update-strings.sh`, `compile-strings.sh`).
- **Infraestructura de Calidad de Código**:
  - Hooks de pre-commit configurados con ruff, trailing-whitespace, end-of-file-fixer y validadores YAML/TOML.
  - Comprobaciones automáticas de calidad de código en cada commit.
  - Analizador de proyecto con seguimiento de historial de métricas (`.ai-context/metrics_history.json`).
- **Herramientas de Desarrollo**:
  - Registro de historial de métricas para rastrear la evolución de la calidad del código a lo largo del tiempo.
  - Script de análisis de proyecto mejorado con optimizaciones de rendimiento.

### Cambiado
- **Refactorización Arquitectónica Mayor (Fases 1-6)**:
  - **Fase 1 - Arquitectura y Desacoplamiento**: Definición de interfaces de servicio usando `abc.ABC` y `typing.Protocol`, implementación de inyección de dependencias en clases Manager.
  - **Fase 2 - Manejo de Errores y Logging**: Creación de jerarquía de excepciones específica del dominio, implementación de manejo de errores centralizado, migración a logging estructurado.
  - **Fase 3 - Rendimiento y Optimización**: CacheManager avanzado con conciencia de TTL y LOD, operaciones espaciales optimizadas, cálculos geométricos vectorizados.
  - **Fase 4 - Async y Gestión de Recursos**: Refinamiento de `AsyncGeologyProcessor` con tokens de cancelación, implementación de limpieza robusta de recursos con Context Managers.
  - **Fase 5 - Validación y Modernización**: Uso de `dataclasses` para manejo de parámetros, refinamiento de type hinting con Protocols, modernización a características de Python 3.10+.
  - **Fase 6 - Documentación y ExpDev**: Estandarización de docstrings al formato Google en todos los módulos `core/`, implementación integral de I18n.
- **Mejoras de Calidad de Código**:
  - Reemplazo de `typing.Dict/List/Tuple` obsoletos con sintaxis moderna `dict/list/tuple`.
  - Reducción de errores de linting Ruff de 287 a 261 (mejora del 9%).
  - Corrección de errores de sintaxis de refactorización automatizada.
  - Normalización de espacios en blanco en 158 archivos.
  - Puntuación de calidad: 69.1/100, Cumplimiento QGIS: 100.0/100.

### Corregido
- **Correcciones de Bugs Críticos**:
  - Solucionada la falta de importación de `QgsProject` en `preview_axes_manager.py` que causaba cierres al renderizar la vista previa.
  - Corregida la renderización de vista previa asignando explícitamente el CRS del proyecto a las capas en memoria.
  - Corregido `RuntimeError` en clases Page llamando a `super().__init__()` antes de `self.tr()`.
  - Corregidas traducciones vacías eliminando atributos `type="unfinished"` de archivos `.ts`.
  - Corregida corrupción XML en archivo de traducción ruso.
  - Corregido falso positivo `ValidationError` para capas de sondeos.
- **Correcciones del Sistema de Traducción**:
  - Corregida compilación `lrelease` manejando adecuadamente múltiples locales en Makefile.
  - Creados scripts de inyección de traducciones para población eficiente de archivos `.ts`.
  - Verificada la carga de traducciones con pruebas unitarias.

### Documentación
- Actualizados todos los módulos `core/` con docstrings estilo Google.
- Creado recorrido completo documentando todas las mejoras arquitectónicas.
- Añadidos artefactos de sesión rastreando el progreso del desarrollo.

## [2.3.0] - 2025-12-25
### Añadido
- **Herramienta de Medición Multi-Punto Mejorada**:
  - Soporte para trazado de polilíneas con puntos de medición ilimitados.
  - Botón "**Finalizar**" dedicado para completar explícitamente la medición.
  - Métricas completas: Distancia 3D total, distancia horizontal, cambio de elevación y pendiente promedio.
  - Retroalimentación visual persistente con marcadores de vértices verdes y líneas de medición después de finalizar.
  - Auto-reinicio en nueva medición para flujo de trabajo mejorado.
- **Plan de Mejora Estructural - Fase 1 (Desacoplamiento Arquitectónico)**:
  - Extraído `DialogToolManager` para encapsular manejo de herramientas de mapa y eventos de rueda del ratón.
  - Centralizada lógica de generación de vista previa en `PreviewManager`.
  - Eliminadas dependencias PyQt de `core/validation` usando `FieldType` basado en enum.
- **Plan de Mejora Estructural - Fase 2 (Reducción de Complejidad)**:
  - Modularizado `core/utils/geometry.py` en subpaquetes `extraction`, `processing`, y `filtering`.
  - Refactorizado `DrillholeService.process_intervals` con métodos privados extraídos.
  - Implementado Nivel de Detalle (LOD) adaptativo para perfiles topográficos.
- **Plan de Mejora Estructural - Fase 3 (Optimización de Rendimiento)**:
  - Sistema de caché robusto con invalidación basada en hash en `PreviewManager`.
  - Indexación espacial (`QgsSpatialIndex`) para filtrado eficiente de sondeos.
  - Logrado tiempo de renderizado de 84ms para secciones transversales de 6km.
- **Plan de Mejora Estructural - Fase 4 (Documentación)**:
  - Creado `ARCHITECTURE.md` con documentación técnica unificada.
  - Creado `DEVELOPMENT_GUIDE.md` para incorporación de desarrolladores.
  - Mejorada cobertura de docstrings al 75.9%.

### Cambiado
- **Mejoras de Calidad de Código**:
  - Puntuación de calidad aumentada de 71.1 a 74.4 (+4.6%).
  - Eliminados imports de typing obsoletos (`Dict`/`List` → `dict`/`list`).
  - Corregido orden y organización de imports en todos los módulos.
  - Mejorado manejo de errores con `logger.exception` en lugar de `logger.error`.

### Corregido
- **Correcciones de Bugs Críticos**:
  - Corregido `ModuleNotFoundError` para subpaquete `geometry_utils` en despliegue.
  - Resuelto `NameError` para `Optional` en `profile_service.py`.
  - Corregido `AttributeError` en herramienta de medición (acceso vía `DialogToolManager`).
  - Corregido `TypeError` en firma de `create_buffer_geometry` (añadidos parámetros `crs` y `segments`).
  - Corregido `UnboundLocalError` en manejo de caché de `PreviewManager`.
  - Añadido soporte de transformación CRS en utilidad `filter_features_by_buffer`.
  - Implementada validación de campos para procesamiento de sondeos para prevenir `KeyError`.
  - Corregida falta de definición de `logger` en `preview_service.py`.
- **Correcciones de Renderización de Vista Previa**:
  - Corregida geología que desaparecía en clics subsiguientes de vista previa con parámetros sin cambios.
  - Corregido sondeos no renderizados a pesar de ser detectados (faltaba return en `_generate_drillholes()`).
  - Añadido logging diagnóstico completo para generación de trazas de sondeos.
  - Mejorada persistencia de caché para datos geológicos asíncronos.

## [2.2.0] - 2025-12-21
### Añadido
- **Evolución Arquitectónica: Core Modular y Punto de Entrada Limpio**:
  - Mover clase principal `SecInterp` a raíz del plugin (`sec_interp_plugin.py`) para separar estrictamente integración QGIS de lógica de negocio.
  - Modularizado `validation.py` en paquete especializado `core/validation/` (validadores de Campo, Capa, Ruta y Proyecto).
  - Fragmentado `SecInterpDialog` en managers especializados (`DialogSignalManager`, `DialogDataAggregator`) reduciendo complejidad y tamaño de archivo.
  - Refactorizado Sistema de Ayuda a "Híbrido Nativo" (HTML/CSS en un solo archivo) para mejor rendimiento y UX.
- **Mejoras de Vista Previa e UI**:
  - Corregidas etiquetas de eje Y y alineación de rejilla para elevaciones negativas.
  - Mejorado espaciado de etiquetas de eje y manejo de CUADRANTES de etiquetas.
  - Corregida ruta de carga de icono de barra de herramientas tras movimiento arquitectónico.
- **Documentación**:
  - Actualizada documentación de "Outputs" con detalles de traza/intervalos de sondeos.
  - Creada documentación técnica de arquitectura completa.

### Corregido
- Resueltas violaciones arquitectónicas `UI_IMPORT_IN_CORE` moviendo componentes dependientes de UI fuera de la capa core.
- Corregido `TypeError` en `PreviewParams` y `AttributeError` al inicio reordenando inicialización de servicios.
- Corregido bug de recolección de campos en `PreviewManager` usando `currentField()`.
- Mejorada estabilidad de Exportación de Vista Previa con mejor manejo de tamaño.

## [2.1.0] - 2025-12-17
### Añadido
- **Característica Mayor: Herramienta de Medición con Snap**:
  - Implementación de lógica de snap iterativo a vértices usando `QgsPointLocator`.
  - Enfoque de snap manual que evita contaminación del proyecto (no añade capas temporales a `QgsProject`).
  - Optimización de rendimiento con caché de localizador.
- **Mejoras de Flujo de Trabajo AI**:
  - Mejorado `ai_workflow.py` con normalización Unicode (NFD) para extracción robusta de palabras clave (soporta acentos/caracteres especiales).
  - Carga de contexto robusta con archivos obligatorios a nivel de proyecto (`AI_CONTEXT.md`, `project_brain.md`).

### Corregido
- Corregido `AttributeError` crítico en `QgsSnappingConfig` usando correctamente `QgsTolerance.Pixels`.
- Eliminada advertencia de "capas temporales" usando lógica de snap manual.

## [2.0.0] - 2025-12-14
### Añadido
- **Característica Mayor: Manejo de Datos de Sondeos**:
  - Proyección 3D de trazas de sondeos en secciones de perfil 2D.
  - Auto-cálculo de profundidades totales y manejo de agujeros verticales sin survey.
  - Visualización de intervalos geológicos a lo largo de trazas de sondeos.
- **Exportación de Datos de Sondeos**:
  - Exportar trazas de sondeos a Shapefile (`drillhole_traces.shp`).
  - Exportar datos de intervalos con atributos a Shapefile (`drillhole_intervals.shp`).

### Cambiado
- **Refactorización Mayor de UI y Mejoras**:
  - Nueva Página de Entrada de Sondeos especializada.
  - Sistema de Vista Previa mejorado con renderizado persistente dedicado para todos los tipos de datos.
  - Corregidos bugs críticos de renderizado (persistencia de zoom, actualizaciones asíncronas).
- **Arquitectura**:
  - Implementado `DrillholeService` para lógica encapsulada.
  - Refactorizado `ProfileController` para orquestar múltiples servicios de datos.
  - Unificada lógica de exportación con patrón Exporter extensible.

## [1.1.0] - 2025-12-12
### Añadido
- **Rendimiento y Optimización**:
  - Implementado procesamiento paralelo asíncrono para generación geológica.
  - Integrado Monitor de Rendimiento (seguimiento de RAM y Tiempo de Ejecución).
  - Añadida UI no bloqueante durante cálculos pesados.
- **Mejoras del Sistema de Vista Previa**:
  - Implementado Nivel de Detalle (LOD) adaptativo para renderizado de alto rendimiento.
  - Añadido LOD Dinámico basado en Zoom (detalles aumentan al hacer zoom).
  - Añadida Herramienta de Medición (Distancia y Pendiente/Gradiente).

### Cambiado
- **Arquitectura y Correcciones**:
  - Refactorizados servicios para usar Patrón Comando para ejecución paralela.
  - Mejorado manejo de CRS.

### Corregido
- Corregida consistencia de proyección de estructuras.
- Resueltas advertencias "No valid layers to render".
- Corregida aplicación de Factor de Escala de Buzamiento.
- Corregidos problemas de renderizado en blanco.

## [1.0.0] - 2025-12-08
### Añadido
- **Refactorización y Arquitectura**:
  - Divididos módulos monolíticos (algorithms.py, main_dialog.py) en componentes enfocados.
  - Modularizado ecosistema de exportadores.
  - Implementada indexación espacial y algoritmos nativos de QGIS para rendimiento.
- **Aseguramiento de Calidad**:
  - Añadido type hinting completo en todos los módulos.
  - Mejorada infraestructura de pruebas con pytest y soporte QGIS.
  - Implementadas correcciones de seguridad (protección path traversal).
- **Documentación**:
  - Añadido COMMIT_GUIDELINES.md para mensajes de commit estandarizados.
  - Añadido RELEASE_PROCESS.md con flujo de trabajo de liberación de versiones.
  - Añadido drilllogs_research.md con requerimientos de integración futura.

### Cambiado
- **Refactorización Mayor de UI - Estilo Plugin Manager**:
  - Rediseñado diálogo principal con navegación lateral (QListWidget + QStackedWidget).
  - Reemplazado posicionamiento absoluto con layouts responsivos (QVBoxLayout, QHBoxLayout, QSplitter).
  - Integrados iconos de tema nativo QGIS para ítems de barra lateral.
  - Mejoradas proporciones de área de vista previa/resultados con mejor gestión de espacio vertical.
- **Mejoras de Calidad de Código**:
  - Extraído LegendWidget a módulo separado (gui/legend_widget.py).
  - Refactorizado preview_profile_handler con métodos auxiliares y retornos tempranos.
  - Refactorizado export_preview con métodos dedicados por formato (PNG, JPG, SVG, PDF).
  - Aplicados principios SOLID en toda la clase del diálogo principal.

### Corregido
- Corregidos problemas de renderizado y redimensionamiento de leyenda.

## [0.3.0] - 2025-12-03
### Cambiado
- **Refactorización Mayor - Estructura de Proyecto Modular**:
  - Reorganizada base de código en paquetes core/, gui/, resources/.
  - Mejorada mantenibilidad y escalabilidad del código.
  - Mejor separación de preocupaciones (lógica de negocio, UI, recursos).
- **Sistema de Construcción**:
  - Actualizado Makefile para nueva estructura.
  - Refactorizado deploy.sh para despliegue modular.
  - Organizados scripts de construcción en directorio scripts/.

### Añadido
- **Mejoras de Calidad**:
  - Lograda puntuación Pylint 10/10.
  - Manejo específico de excepciones en toda la base de código.
  - Documentación de código completa.
  - Configurado .pylintrc para calidad de código consistente.
- **Pruebas y CI/CD**:
  - Añadida infraestructura pytest con soporte QGIS.
  - Creadas pruebas unitarias iniciales.
  - Configurado GitHub Actions para pruebas automatizadas.
  - Configuración de pruebas en tests/conftest.py.
- **Documentación**:
  - Añadido REFACTORING_PR.md con cambios detallados.
  - Mejorada estructura de documentación del proyecto.
  - Añadidos planes de implementación para características futuras.

## [0.2.0] - 2025-11-30
### Cambiado
- **Revisión Mayor de UI - Integración de Widgets Nativos QGIS**:
  - Reemplazados ComboBoxes Qt estándar con QgsMapLayerComboBox para población automática de capas.
  - Integrado QgsRasterBandComboBox para selección inteligente de bandas ráster.
  - Añadido QgsFileWidget para navegación nativa de archivos/directorios con integración QGIS.
  - Eliminado código manual de población de capas - widgets auto-sincronizan con proyecto QGIS.
  - Mejorada experiencia de usuario con apariencia nativa QGIS.
  - Corregida sintaxis de enum Qt para mejor compatibilidad entre versiones.
- **Calidad de Código**:
  - Eliminadas 200+ líneas de código manual de población de widgets.
  - Arquitectura más limpia aprovechando capacidades nativas QGIS.

### Añadido
- **Mejoras de UI**:
  - Panel de resultados colapsable (QgsCollapsibleGroupBox) para mejor gestión de espacio.
  - Campo de resultados de solo lectura para prevenir ediciones accidentales.
- **Nuevas Características**:
  - Parsers flexibles para mediciones estructurales geológicas (formatos dip/strike).
  - Sistema de logging completo integrado con Panel de Mensajes QGIS.
  - Lógica de validación mejorada para objetos QgsMapLayer.

## [0.1.0] - Lanzamiento Inicial
### Añadido
- Extracción de perfil topográfico DEM.
- Extracción de datos de afloramientos geológicos.
- Extracción de datos de puntos estructurales.
- Visualización interactiva de vista previa.
