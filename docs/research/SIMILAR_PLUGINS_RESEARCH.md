# Investigación de Plugins Similares a SecInterp

Este documento presenta una investigación detallada de los plugins de QGIS que comparten características con **SecInterp** (Geological Interpretation for QGIS), con el fin de identificar el panorama competitivo y las capacidades únicas de cada herramienta.

---

## 1. Resumen de Capacidades de SecInterp
Para realizar una comparación justa, recordamos los pilares de `sec_interp`:
- **Previsualización Interactiva**: Sistema en tiempo real con LOD (Level of Detail) y procesamiento asíncrono.
- **Proyección de Sondajes (Drillholes)**: Manejo de collares, surveys e intervalos lithológicos en 2D.
- **Datos Estructurales**: Cálculo automático de buzamientos aparentes.
- **Extracción de Topografía**: Uso de DEMs para generar perfiles precisos.
- **Herramientas de Medición**: Medición de distancias y pendientes con snapping.

---

## 2. Competidores Principales

### 🔴 [Geoscience Plugin](https://github.com/geosience/geoscience)
Es probablemente el competidor más robusto en el ámbito de la exploración minera.
- **Fortalezas**:
    - **Gestión de Sondajes**: Excelente desurveying y visualización de leyes (assays) y litología.
    - **Section Manager**: Permite gestionar múltiples secciones y regenerarlas fácilmente.
    - **Integración con QGIS**: Las secciones se crean como capas nativas de QGIS, permitiendo usar su simbología estándar.
- **Comparación con SecInterp**: Geoscience está más enfocado en la gestión masiva de datos de exploración, mientras que SecInterp destaca por su **interfaz moderna de previsualización** y agilidad en la interpretación directa.

### 🔵 [OpenLog](https://plugins.qgis.org/plugins/openlog/)
Un módulo de alto rendimiento actualizado recientemente (diciembre 2025).
- **Fortalezas**:
    - **Visualización 3D**: Capacidad nativa para ver logs de sondajes en 3D.
    - **Vistas de Sección y Log**: Enfoque profesional en la creación de "logs" de perforación.
- **Comparación con SecInterp**: OpenLog es ideal para quienes necesitan documentación técnica de pozos individuales, mientras que SecInterp es más potente para la **correlación y construcción de perfiles transversales** interactivos.

### 🟢 [GIS4GEOLOGY](https://github.com/gis4geology/gis4geology)
Enfocado en el modelado geológico 2D y 3D.
- **Fortalezas**:
    - **Geometrías Complejas**: Permite digitalizar interpretaciones complejas sobre el perfil.
    - **Salida a 3D**: Sus secciones sirven de base para generar modelos de volumen geoscientíficos.
- **Comparación con SecInterp**: GIS4GEOLOGY es una herramienta de construcción de modelos, mientras que SecInterp es una herramienta de **extracción y visualización rápida** de datos de campo para toma de decisiones rápida.

---

## 3. Matriz Comparativa de Características

| Característica | SecInterp | Geoscience | OpenLog | GIS4GEOLOGY | Profile Tool |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Previsualización en tiempo real** | ⭐⭐⭐ | ⭐ | ⭐⭐ | ⭐ | ⭐⭐⭐ |
| **Procesamiento Asíncrono** | ✅ | ❌ | ✅ | ❌ | ✅ |
| **Sondajes (Drillholes)** | ✅ | ✅ | ⭐⭐⭐ | ✅ | ❌ |
| **Buzamientos Aparentes** | ✅ | ✅ | ❌ | ✅ | ❌ |
| **Exportación CAD (DXF)** | ✅ | ⚠️ | ❌ | ✅ | ❌ |
| **Medición con Snapping** | ✅ | ❌ | ❌ | ✅ | ❌ |
| **Facilidad de Uso (UI)** | ⭐⭐⭐ | ⭐⭐ | ⭐⭐ | ⭐ | ⭐⭐⭐ |

---

## 4. Plugins Especializados (Nicho)

- **[Profile Tool](https://plugins.qgis.org/plugins/profiletool/) / qProf**: Excelentes y muy populares para extraer perfiles topográficos puros de DEMs, pero carecen de la dimensión geológica (sondajes/estructuras).
- **Dip-Strike Tools / ThreePointMethod**: Enfocados puramente en la trigonometría geológica (cálculos de rumbo y buzamiento) a partir de puntos o DEMs.
- **[QGeoloGIS](https://oslandia.com/en/blog/qgeologis-the-borehole-log-viewer-for-qgis/)**: Un visor de logs de perforación muy potente, pero menos orientado a la creación de secciones transversales transversales.

---

## 5. El Valor Diferencial de SecInterp

Lo que hace que **SecInterp** destaque frente a las opciones existentes es:

1.  **Velocidad de Iteración**: La capacidad de mover la línea de sección en el mapa y ver el perfil actualizarse instantáneamente (gracias al procesamiento en paralelo y LOD) no es común en plugins más antiguos como Geoscience.
2.  **UI/UX Moderna**: El uso de un panel lateral (sidebar) y widgets nativos de QGIS hace que el flujo de trabajo sea mucho más fluido que las interfaces cargadas de menús de sus competidores.
3.  **Herramientas de Medición Integradas**: La posibilidad de medir pendientes y distancias directamente sobre el perfil interpretado, con soporte para "snapping", lo convierte en una herramienta "todo en uno" para interpretación de gabinete rápida.

> [!TIP]
> Si el objetivo es el **modelado 3D profesional**, GIS4GEOLOGY es el compañero ideal. Pero para **interpretación rápida, control de datos y generación de perfiles técnicos operativos**, SecInterp ofrece la mejor experiencia de usuario en QGIS actualmente.
