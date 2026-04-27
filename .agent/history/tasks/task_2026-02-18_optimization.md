# Tareas Activas - SecInterp

## [x] Sesión Actual: Corrección de Regresiones y Estabilización
- [x] **Corrección de Mocks (Qt/QGIS)**
    - [x] Añadir `setPixmap` y `pixmap` a `MockQWidget`
    - [x] Implementar `MockQIcon.pixmap`
    - [x] Implementar parsing de WKT en `MockQgsGeometry`
    - [x] Corregir pérdida de atributos en `MockQgsFeature.setFields`
- [x] **Corrección de Exportadores 3D**
    - [x] Usar `QgsLineString` y `QgsPoint` en `DrillholeTrace3DExporter`
    - [x] Usar `QgsPolygon` y `QgsLineString` en `Interpretation3DExporter`
    - [x] Corregir URI de capa de memoria y generación de QML
- [x] **Verificación de Estabilidad**
    - [x] Ejecutar suite completa de tests y asegurar 100% OK (378 tests)

## 🔜 Siguientes Pasos: Fase 6 (QGIS 4.0 Prep)
- [ ] **Migración PyQt (Hacia QGIS 4.0)**
    - [ ] Identificar todos los `from PyQt5...` restantes
- [ ] **Limpieza de i18n y Señales**
    - [ ] Resolver 22 señales remanentes según `qgis-analyzer`
    - [ ] Abordar cadenas MISSING_I18N en `controller.py` y `config.py`
