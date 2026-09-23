# Consideraciones — Implementation Plan DEM/Section v3.9.0

Revisión del plan `implementation_plan_dem_section_v3.9.0.md`: resuelve las decisiones
abiertas y aporta recomendaciones técnicas vinculantes (ya integradas en el plan).

1. Sobre las Decisiones Abiertas (Open Decisions)
Decisión #1 (Botón OK en S1 vs S2): Recomiendo S1.
Por qué: Obligar al usuario a generar un Preview (S2) cada vez que hace un cambio menor (como cambiar el color o un multiplicador de exageración) añade fricción innecesaria. Si los inputs son válidos (S1), el usuario debe poder aceptar y cerrar el diálogo. Export / Measure sí deben requerir S2 porque operan sobre el resultado generado.
Decisión #3 (CRS Geográfico como Error o Warning): Recomiendo Error.
Por qué: SecInterp depende de distancias métricas para calcular buffers, azimuts, y espaciamientos de muestreo. Si se usa un CRS en grados (ej. EPSG:4326), calcular un buffer de "50" o un muestreo de "10" generará resultados sin sentido. Bloquearlo desde la página de validación (Fase 1) prevendrá bugs extraños en el motor de renderizado o en el core matemático.
Decisión #2 (Azimut): De acuerdo con calculate_line_azimuth.
Por qué: Reutilizar la función centralizada de core/utils/spatial.py mantiene la consistencia (Single Source of Truth) y al forzar a que la línea tenga 2 puntos (Fase 1), el cálculo será exacto.
Decisión #4 (Clases de gradiente): De acuerdo con Diferir.
Por qué: Mantener el alcance acotado (Goal 1.1 lo podrá abordar después). Empezar con el fallback default y 8 clases es suficiente para esta fase.
2. Recomendaciones Técnicas para la Implementación
Fase 0 (Rendimiento del Hashing S0/S1/S2):
El plan menciona que is_preview_current() se llamará ante cualquier cambio para actualizar los botones (update_all). Debemos asegurarnos de que _get_and_validate_inputs() sea extremadamente ligero. Si extrae todas las geometrías de las capas cada vez que se mueve un slider, trabará la UI. El hash debe basarse estrictamente en layer.id() y en los valores primitivos de los widgets (números, strings, booleanos), no en leer la data espacial.
Fase 3 (Deduplicación de Muestras del DEM):
El plan advierte sobre sesgos por duplicación debido a resoluciones menores al intervalo de muestreo. Para el dedupe, no confíes solo en valores Z consecutivos idénticos. En terrenos planos como salares o llanuras, es natural tener el mismo valor Z en diferentes píxeles. La deduplicación debe basarse en la distancia bidimensional respecto al tamaño del píxel (raster.rasterUnitsPerPixelX()) o en las coordenadas de la celda de la que provienen.
Fase 3 (Riesgo de bandStatistics en remoto):
Pedir bandStatistics() a una capa WCS o un VRT gigantesco puede colgar QGIS si las estadísticas no están cacheadas. Recomiendo pasar el argumento de extensión (extent) o al menos un sampleo limitado, o simplemente capturar la excepción / timeout si QGIS demora más de 1-2 segundos.
Fase 1 (Invariante de 2 Puntos):
Asegúrate de que la validación en SectionPage avise explícitamente al usuario por qué falla ("La línea de sección debe tener exactamente 2 vértices (inicio y fin)"). Esto evita frustración si el usuario intenta dibujar una polilínea compleja.
