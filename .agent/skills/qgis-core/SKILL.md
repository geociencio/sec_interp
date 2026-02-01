---
name: qgis-core
description: Conocimiento sobre la API de QGIS, estructura de plugins y procesamiento asíncrono con QgsTask.
trigger: al trabajar con PyQGIS, capas, CRS o QgsTask.
---

# Desarrollo Core QGIS

Estandariza la interacción con la API de QGIS, asegurando un plugin responsivo y bien estructurado.

## Cuándo usar este skill
- Al implementar nuevas herramientas que interactúen con el lienzo del mapa.
- Al manejar capas vectoriales o ráster.
- Al realizar operaciones pesadas que requieran hilos secundarios.

## Grado de Libertad
- **Estricto**: El uso de `QgsTask` para procesos largos y el desacoplamiento Core/GUI son obligatorios.

## Workflow
1. **Arquitectura**: Separar la lógica en `core/` (procesamiento) y `gui/` (visualización).
2. **Validación**: Siempre verificar `isValid()` en las capas antes de operar.
3. **Asincronía**: Envolver procesos de >0.5s en una `QgsTask`.
4. **Gestión de CRS**: Manejar explícitamente las transformaciones de coordenadas.

## Instrucciones y Reglas

### Reglas de Oro
- **QgsTask**: No bloquear la UI. Usar señales y slots para comunicación.
- **Fronteras**: Usar WKT para comunicar la lógica core con la interfaz gráfica.
- **Inyección**: Evitar el uso global de `iface`; preferir pasar objetos en constructores.

### Estructura del Plugin
- `core/`: Lógica de negocio agnóstica a la UI.
- `gui/`: Widgets y diálogos dependientes de PyQGIS.
- `exporters/`: Módulos de salida de datos.

## Checklist de Calidad
- [ ] ¿Se evitan bloqueos en la interfaz mediante `QgsTask`?
- [ ] ¿Se valida la integridad de las capas en cada operación?
- [ ] ¿Las transformaciones de CRS están explícitamente definidas?
- [ ] ¿Se sigue la separación de responsabilidades Core/GUI?
