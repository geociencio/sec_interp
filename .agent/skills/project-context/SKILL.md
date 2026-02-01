---
name: project-context
description: Resumen del propósito, arquitectura y estructura del proyecto SecInterp.
trigger: al iniciar nuevas tareas, solicitar resúmenes o explicar la arquitectura del plugin.
---

# Contexto del Proyecto SecInterp

Proporciona una visión integral del plugin de QGIS para interpretación de secciones geológicas, facilitando la toma de decisiones arquitectónicas coherentes.

## Cuándo usar este skill
- Al inicio de una sesión para refrescar la arquitectura.
- Al proponer cambios estructurales o nuevas integraciones.
- Cuando el usuario solicita un estado actual del proyecto.

## Grado de Libertad
- **Guiado**: Utilizar esta información como marco de referencia para proponer soluciones alineadas con la visión del proyecto.

## Workflow
1. **Lectura**: Consultar `AI_CONTEXT.md` y `PROJECT_SUMMARY.md`.
2. **Análisis**: Identificar los límites entre `core`, `gui` y `exporters`.
3. **Validación**: Asegurar que las nuevas propuestas no violen el desacoplamiento definido.

## Instrucciones y Reglas

### Propósito
SecInterp es una herramienta avanzada para geólogos que permite interpolar datos de sondajes en secciones 2D/3D dentro de QGIS, optimizando el flujo de trabajo de modelamiento.

### Arquitectura Core
- **Local First**: Prioriza el rendimiento local y el manejo eficiente de memoria.
- **Agnóstico a la UI**: El núcleo del procesamiento debe funcionar sin depender de elementos gráficos de Qt.
- **Validación de 3 Niveles**: (Tipo, Esquema, Negocio) en todos los servicios de dominio.

### Estructura de Carpetas
- `core/`: Cerebro del plugin (servidores, lógica de sondajes).
- `gui/`: Interfaz de usuario dinámica y responsiva.
- `exporters/`: Lógica de exportación multi-formato.

## Checklist de Calidad
- [ ] ¿La propuesta respeta la separación Core/GUI?
- [ ] ¿Se alinea con la visión "Local First"?
- [ ] ¿Se mantiene la integridad de la validación de 3 niveles?
