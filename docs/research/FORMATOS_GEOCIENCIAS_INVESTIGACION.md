# Investigación de Formatos de Almacenamiento para Datos de Geociencias y `sec_interp`

Este documento consolida la investigación en profundidad sobre los diversos formatos de datos geoespaciales y bases de datos más adecuados para el almacenamiento y la visualización de modelos geológicos 3D, sondajes (drillholes) y perfiles transversales dentro del ecosistema de **QGIS**, con el fin de guiar las futuras decisiones de arquitectura del plugin **sec_interp**.

---

## 1. GeoPackage (.gpkg) vs Shapefile (.shp) para Geología 3D

Para el almacenamiento de datos vectoriales procesados (como perfiles poligonales, trazas de pozos 3D y estructuras), existe un consenso claro: **GeoPackage es el formato superior y recomendado**, mientras que el histórico Shapefile presenta limitaciones críticas.

### Ventajas Críticas de GeoPackage:
* **Soporte Nativo 3D (Valores Z/M)**: GeoPackage es capaz de almacenar geometrías complejas con valores Z (elevación) y M (medida), fundamentales para modelos del subsuelo.
* **Múltiples Capas (Multi-layer)**: Un solo archivo `.gpkg` puede contener múltiples capas vectoriales (p. ej., collares, trazas, polígonos de litología) y raster de manera simultánea, actuando como un contenedor de proyecto completo.
* **Atributos Avanzados**: Supera el límite de 10 caracteres para nombres de columnas impuesto por los DBF del Shapefile, permitiendo nombres descriptivos completos (ej. `alteration_intensity` en lugar de `alter_int`).
* **Límites de Tamaño Relajados**: No cuenta con el límite estricto de 2GB que tienen los archivos de los Shapefiles.
* **Índices Espaciales**: Al basarse en SQLite, maneja índices espaciales robustos (R-Tree), acelerando enormemente el renderizado y las consultas para grandes sets de datos de sondajes.

### ¿Por qué evitar Shapefile para 3D?
* Fundamentalmente diseñado para 2D; su soporte 3D es básico y puede perder información topológica.
* Un archivo por cada tipo de geometría. Representar todos los resultados de un perfil requeriría docenas de archivos `.shp`, `.shx`, `.dbf`, `.prj` sueltos en el disco.

---

## 2. Formatos Ideales para Sondajes (Drillholes)

Para datos de pozos, el flujo de trabajo moderno en QGIS distingue entre los **datos crudos (input)** y la **geometría 3D renderizada (output)**.

### A. Para Ingreso de Datos (Input Crudo): CSV
Sorprendentemente, para el flujo de captura inicial, los **Archivos de Valores Separados por Comas (CSV)** siguen siendo el estándar de facto. La arquitectura ideal para ingestar pozos requiere separar en tablas relacionales:
1.  **Collar**: `Hole_ID`, `X`, `Y`, `Z`, `Max_Depth`.
2.  **Survey**: `Hole_ID`, `Depth`, `Azimuth`, `Dip/Inclination`. (Requerido para el proceso de *desurveying* o cálculo de la traza curva en 3D).
3.  **Intervalos (Litología/Ensayo)**: `Hole_ID`, `From`, `To`, `Attribute_Value`.

**Enfoque para sec_interp**: Mantener la ingesta inicial desde capas tabulares/CSV, y el plugin se encargará de generar la "geometría al vuelo" usando el procedimiento Extract-then-Compute.

### B. Para Resultados (Output 3D): GeoPackage
Una vez procesado el pozo en QGIS (mediante desurveying), el formato destino perfecto es GeoPackage, guardando las geometrías de las "trazas" como `LineStringZ` o `PolygonZ` para representar tuberías de litologías.

---

## 3. OMF (Open Mining Format)

El **Open Mining Format (OMF)** fue concebido por el Global Mining Guidelines Group (GMG) para permitir una transferencia fluida de mallas 3D, modelos de bloques, geo-superficies y pozos entre diferentes software propietarios de minería (como Leapfrog, Datamine o Micromine).

* **Desafío Técnico con QGIS**: Actualmente, la investigación revela que **no existe una integración nativa o directa completa** de OMF en QGIS (GDAL no lo soporta de fábrica como lo hace con GeoJSON o GPKG).
* **Posibilidad Futura**: OMF cuenta con una API en Python. Sería posible construir una herramienta dentro de `sec_interp` que utilice la librería `omf` de Python para importar/exportar a OMF interactuando directamente con las capas QGIS. Sin embargo, no será un formato "plug and play".

---

## 4. Otros Estándares Industriales

* **LAS / DLIS**: Son el estándar inamovible para datos continuos de registros de pozo (wireline logs). Integrar soporte para `.las` abriría las puertas a interpretaciones de geofísica de pozos en `sec_interp`.
* **PostgreSQL + PostGIS**: Si se requiere un entorno Enterprise donde múltiples geocientistas interactúen en tiempo real con la misma base de datos estructural y litológica. Funciona de manera transparente con las capas de QGIS, pero requiere una configuración de servidor compleja por parte del usuario, lo que choca con la portabilidad actual del plugin.

## 5. GeoSciML y Estándares OGC para Geociencias

**GeoSciML** (Geoscience Markup Language) es el estándar internacional (basado en GML/XML y respaldado por OGC e IUGS) para el intercambio de datos geológicos digitales, incluyendo mapas geológicos, estructuras y datos de pozos (boreholes).

* **Naturaleza del Formato**: GeoSciML **no es una base de datos relacional** optimizada para lectura/escritura rápida en herramientas de escritorio, sino un esquema de aplicación (Application Schema) rico y complejo diseñado para la **interoperabilidad y transferencia** de datos (típicamente a través de servicios web WFS).
* **Representación de Pozos (Boreholes)**: Posee un módulo específico (`GeoSciML/Borehole`) que modela topología de pozos de manera muy avanzada (collares como puntos espaciales, y el pozo definido como un sistema de referencia lineal con intervalos relativos).
* **Integración con QGIS**: QGIS puede consumir GeoSciML a través del plugin **GML Application Schema Toolbox**, que parsea estos complejos XMLs. Sin embargo, para trabajar de manera nativa y performante, QGIS y otros plugins (como el "Geoscience plugin") requieren que estos datos se "aplanen" (flattening) hacia tablas y vectores estándar almacenados en formatos como... **GeoPackage**.

---

## 🚀 Conclusión Estratégica para sec_interp

1.  **Continuar con GeoPackage como Eje Central**: Para la "Unificación de Exportación" de la versión v3.4.0, la decisión de utilizar `.gpkg` está totalmente alineada con las mejores prácticas de la industria geoespacial moderna. Es capaz de agrupar topografía, pozos e interpretaciones en un solo contenedor SQLite. Además, es el formato de almacenamiento destino preferido cuando se consume información compleja desde estándares como **GeoSciML**.
2.  **Mantener CSV para Ingesta**: No es necesario forzar al usuario a transformar sus mediciones originales a formatos espaciales complicados antes de cargarlos. CSV sigue siendo extremadamente válido.
3.  **Diferir OMF y GeoSciML Nativos**: Por ahora, dejar OMF fuera del roadmap a corto plazo dado que GDAL/QGIS no lo soportan de forma nativa. Del mismo modo, aunque **GeoSciML** es el estándar de modelado ideal, requeriría transformar la estructura interna del plugin a complejos esquemas XML, lo cual está fuera del alcance de la herramienta orientada a la edición rápida. Podría considerarse en el futuro únicamente como un módulo de exportación "Hacia GeoSciML", pero el almacenamiento local debe seguir siendo GeoPackage.
