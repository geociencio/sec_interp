# Próximos Pasos - SecInterp

## Resumen de la Situación
La implementación de Sondeos Eléctricos Verticales (SEV) fue **revertida** debido a inestabilidades detectadas en el entorno de QGIS tras la integración de la nueva GUI y dependencias externas (`numpy`, `scipy`). El proyecto ha vuelto al estado estable v4.0.4.

## Tareas Pendientes
1.  **Auditoría de Estabilidad**: Verificar que la versión actual (v4.0.4) carga perfectamente en entornos con y sin las nuevas dependencias instaladas.
2.  **Preparación para SEV (Futuro)**:
    - Diseñar una arquitectura de "Plugins internos" o "Módulos opcionales" para que fallos en la carga de una nueva funcionalidad no rompan el funcionamiento core de SecInterp.
    - Considerar el uso de `importlib` para cargas perezosas (lazy imports) de dependencias pesadas como `numpy`.
    - Separar completamente la lógica de `SevService` de la GUI para permitir tests unitarios exhaustivos fuera de QGIS.
3.  **Modernización de qgis-manager**: Continuar con la hoja de ruta de la herramienta de despliegue para mejorar el ciclo de feedback durante errores de carga.

## Comando para retomar
Para iniciar una nueva sesión de estabilización:
```bash
/inicia-sesion
```
