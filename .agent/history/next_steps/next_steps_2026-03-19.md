# Próximos Pasos (Handover)

**Contexto:** Se ha finalizado la integración de formatos DXF y GeoPackage para la exportación de datos, con especial atención a los sondeos 3D. Se corrigieron desajustes de firmas en `ExportService` y se verificó la integridad de los archivos generados mediante pruebas en el entorno Docker de QGIS.

**Logros de esta sesión:**
- [x] Corrección de `ExportService._export_drillholes_3d` para evitar fallos con DXF.
- [x] Eliminación de lógica redundante de `DXFExporter` genérico en el servicio de exportación.
- [x] Verificación exitosa de exportaciones SHP, GPKG y DXF 3D en contenedor QGIS.
- [x] Confirmación de estabilidad con los 604 tests del proyecto (100% OK).

**Pendiente para la próxima sesión:**
1. **Reducción de Deuda Técnica (I18N)**: Abordar las >1000 advertencias de `MISSING_I18N` reportadas por `qgis-manage analyze`.
2. **Refactorización de Exportadores Genéricos**: Evaluar la eliminación definitiva de `DXFExporter` y `ShapefileExporter` genéricos si los especializados cubren todos los casos de uso.
3. **Mejora de Cobertura de Type Hints**: Incrementar la cobertura de retornos (actualmente en 44.7% según el analizador).

**Comando de Reinicio Sugerido:**
Usa `/start-session` para retomar el trabajo. Se recomienda comenzar con una pasada de internacionalización en los módulos del core.
