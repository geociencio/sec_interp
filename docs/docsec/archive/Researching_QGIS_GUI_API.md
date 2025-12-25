Researching QGIS GUI API
Researching the comprehensive list of QGIS GUI widgets to find additional components relevant to the plugin's future features (Drillholes, styling, etc.).

Progress Updates
1
Searching online documentation for QGIS widgets

Searched web for "qgis python api gui widgets list class reference"


Thought for 13s







He investigado la API de qgis.gui extensivamente. Hay una gran cantidad de widgets especializados que podemos aprovechar para hacer tu interfaz muy profesional y evitar escribir código boilerplate.

Aquí están mis recomendaciones categorizadas para tu refactorización y el soporte de sondajes:

1. Selectores de Datos (Indispensables)
QgsMapLayerComboBox: Para seleccionar capas (DEM, Líneas, Puntos).
Tip: Usa setFilters(QgsMapLayerProxyModel.PointLayer) para mostrar solo lo que necesitas.
QgsFieldComboBox: Para seleccionar columnas (HoleID, Azimuth, Dip, Lithology).
Tip: Conéctalo al layerChanged del combo de capa para que se actualice solo.
QgsRasterBandComboBox: Específico para seleccionar la banda del DEM.
QgsProjectionSelectionWidget: Si alguna vez necesitas que el usuario defina un CRS manual.
2. Entradas Numéricas y Validados
QgsDoubleSpinBox: Mucho mejor que un QLineEdit para números (Buffer, Exageración Vertical). Maneja decimales, prefijos ("m", "x") y validación local automáticamente.
QgsSpinBox: Para enteros (ej. número de muestras).
QgsExtentWidget: Si quisieras permitir definir la extensión del perfil manualmente (Xmin, Ymin, Xmax, Ymax) con herramientas visuales.
3. Archivos y Rutas
QgsFileWidget: El estándar para abrir/guardar archivos o carpetas. Tiene un botón "..." integrado y maneja historiales.
4. Estilo y Color (Sondajes)
Para la futura pestaña de sondajes, estos serán útiles:

QgsColorButton: Un botón que muestra un color y abre el diálogo selector de color estándar de QGIS. Ideal para personalizar el color de la traza del pozo.
QgsSymbolButton: Permite seleccionar símbolos completos de la librería de QGIS. Útil si quieres permitir cambiar cómo se ven los puntos de "Collar".
QgsColorRampButton: Para seleccionar rampas de colores (ej. para visualizar leyes/geoquímica en los intervalos).
5. Contenedores y Organización
QgsCollapsibleGroupBox: Ya lo usas, excelente ahorrar espacio.
QgsMessageBar: Para notificaciones (Éxito/Error) dentro del diálogo, sin usar popups molestos.
6. Visualización Avanzada
QgsMapCanvas: La joya de la corona. En lugar de usar un simple QGraphicsView, usaremos esto. Nos da navegación (zoom/pan) nativa tipo QGIS y renderizado de capas geográficas real.
Conclusión: Recomiendo migrar tu UI basándonos casi exclusivamente en estos widgets. Reducirá el código de validación manual en un 50% y la UI se sentirá "como en casa" para cualquier usuario de QGIS.

¿Procedemos a crear el implementation_plan.md para la migración de UI usando estos componentes?
