# Sesión Técnica: Intento de Implementación de SEV e Infraestructura Geofísica

**Fecha**: 2026-02-18
**Tema**: Intento de implementación de Sondeos Eléctricos Verticales (SEV) y posterior regresión por inestabilidad.

## Resumen Técnico
Se intentó implementar la infraestructura completa para el manejo de SEV (Sondeos Eléctricos Verticales), incluyendo:
- Nueva página en la GUI (`GeophysicsPage`).
- Servicio de procesamiento (`SevService`) con cálculo de factores geométricos K.
- Renderizado de puntos de sondeo proyectados (`SevRenderer`).
- Plan de inversión 1D usando `scipy`.

Sin embargo, tras la integración con el sistema de pre visualización y la refactorización de la configuración del proyecto, se detectaron errores críticos de carga (`classFactory` error, `TypeError` en widgets y `NameError` por desacoplamiento incompleto). Debido a la complejidad de las interdependencias y para asegurar la estabilidad del plugin en producción, se decidió realizar una **regresión total**.

## Cambios Revertidos
- **GUI**: Pestaña de "Geosep" (Geophysics) eliminada de `SecInterpMainWindow`.
- **Core**: Eliminados servicios `SevService`, interfaces y modelos de dominio asociados.
- **Utils**: Eliminados módulos de geofísica e inversión.
- **Docs**: Revertida la generación de documentación API que incluía los nuevos módulos.

## Estado Final
- **Versión**: 4.0.4 (Estable).
- **Git**: HEAD en `d5b5837`.
- **Acción**: El proyecto se encuentra limpio y funcional, sin rastros de la implementación de geofísica.

## Próximos Pasos (Re-intentar SEV)
1. **Rediseño**: Evaluar un desacoplamiento más agresivo de la lógica de negocio antes de volver a tocar la GUI.
2. **Infraestructura**: Asegurar que las dependencias (`numpy`, `scipy`) estén integradas en los entornos de usuario final antes de desplegar código que las use.
3. **Validación**: Implementar tests unitarios para los servicios **antes** de conectarlos a la GUI de QGIS.
