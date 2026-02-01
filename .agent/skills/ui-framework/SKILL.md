---
name: ui-framework
description: Estándares para la interfaz personalizada de SecInterp, enfocados en creación programática y estética premium.
trigger: al modificar o crear widgets de GUI, layouts o estilos CSS.
---

# Framework de UI y UX

Define las reglas para crear interfaces de usuario elegantes, responsivas y eficientes dentro de QGIS, priorizando el control total mediante código.

## Cuándo usar este skill
- Al diseñar nuevos diálogos o paneles de herramientas.
- Al aplicar estilos visuales o animaciones sutiles.
- Al mejorar la usabilidad de widgets existentes.

## Grado de Libertad
- **Guiado**: Se fomenta la creatividad en el diseño visual siempre que se respete la creación programática y la responsividad.

## Workflow
1. **Diseño**: Bocetar la estructura de layouts (HBox, VBox, Grid).
2. **Implementación**: Crear widgets programáticamente (evitar archivos `.ui`).
3. **Estilo**: Aplicar CSS personalizado para una apariencia "premium".
4. **Validación**: Asegurar hilos seguros y feedback visual al usuario.

## Instrucciones y Reglas

### Principios de Diseño
- **Programático**: No usar Qt Designer. Todo el diseño vive en el código Python.
- **Responsividad**: El diálogo debe adaptarse a diferentes tamaños de ventana.
- **Feedback**: Indicadores visuales claros para estados de validación o carga.

### Estándares de Componentes
- **Tooltips**: Obligatorios en cada elemento interactivo.
- **Iconografía**: Usar recursos estandarizados del proyecto.
- **Asincronía**: Actualizaciones de UI mediante señales/slots desde hilos secundarios.

## Checklist de Calidad
- [ ] ¿Se ha evitado el uso de archivos `.ui`?
- [ ] ¿La interfaz es responsiva ante cambios de tamaño?
- [ ] ¿Existen tooltips para todos los elementos de interacción?
- [ ] ¿Las actualizaciones son seguras en términos de hilos (thread-safe)?
