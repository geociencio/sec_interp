# Investigación: Integración de Drilllogs (Sondajes) en Perfiles

Este documento detalla los requisitos, cálculos y pasos necesarios para integrar la visualización de trazas de sondajes (drillholes) y sus intervalos (litología, leyes) en los perfiles transversales del plugin.

## 1. Datos Necesarios

Para reconstruir y visualizar sondajes en 3D y proyectarlos en una sección 2D, se requieren tres tablas de datos fundamentales relacionadas por un identificador único (`HoleID`).

### A. Collar (Cabezales)
Define la ubicación inicial del sondaje en la superficie.
*   **HoleID**: Identificador único del sondaje (String/Integer).
*   **X**: Coordenada Este del collar (Float).
*   **Y**: Coordenada Norte del collar (Float).
*   **Z**: Elevación del collar (Float).
*   *(Opcional)* **Total Depth**: Profundidad total del pozo.

### B. Survey (Desviación)
Define la geometría del sondaje a lo largo de su profundidad.
*   **HoleID**: Identificador del sondaje.
*   **Depth (At)**: Profundidad a la que se toma la medición (Float).
*   **Azimuth**: Dirección del sondaje en grados (0-360).
*   **Dip**: Inclinación del sondaje en grados (habitualmente -90 a 90, donde negativo suele ser hacia abajo).

### C. Intervalos (Assay/Lithology)
Contiene la información geológica o geoquímica a lo largo del sondaje.
*   **HoleID**: Identificador del sondaje.
*   **From**: Profundidad inicial del intervalo (Float).
*   **To**: Profundidad final del intervalo (Float).
*   **Value**: Valor a visualizar (Código litológico, valor de ley, etc.).

## 2. Cálculos y Fórmulas

### A. Desurveying (Compositación de Coordenadas 3D)
El proceso de "Desurvey" convierte los datos de *Profundidad, Azimut y Manteo* en coordenadas absolutas (X, Y, Z) para cada punto a lo largo del pozo.

El método más simple es el **Tangencial** (asumiendo línea recta entre mediciones), aunque el **Minimum Curvature** es más preciso. Para visualización en perfiles a escala regional, el método tangencial o de promedio de ángulos suele ser suficiente.

**Fórmulas Básicas (Método de Ángulo Promedio):**
Para un segmento entre profundidad $d_1$ y $d_2$:
1.  Longitud del segmento: $L = d_2 - d_1$
2.  Azimut promedio: $Az_{avg} = (Az_1 + Az_2) / 2$
3.  Manteo promedio: $Dip_{avg} = (Dip_1 + Dip_2) / 2$
4.  Desplazamientos:
    *   $\Delta Z = L \times \sin(Dip_{avg})$
    *   $H_{proj} = L \times \cos(Dip_{avg})$ (Proyección horizontal)
    *   $\Delta X = H_{proj} \times \sin(Az_{avg})$
    *   $\Delta Y = H_{proj} \times \cos(Az_{avg})$

### B. Proyección al Plano de Sección
Una vez que tenemos las coordenadas (X, Y, Z) de cada punto del sondaje, debemos proyectarlas al plano 2D de la sección transversal.

**Definición de la Sección:**
*   Punto Inicio: $(X_a, Y_a)$
*   Punto Fin: $(X_b, Y_b)$
*   Vector de Sección: $\vec{S} = (X_b - X_a, Y_b - Y_a)$
*   Longitud de Sección: $|\vec{S}|$

**Fórmulas de Proyección:**
Para un punto $P(X_p, Y_p, Z_p)$ del sondaje:

1.  **Vector desde inicio de sección a punto P**: $\vec{V} = (X_p - X_a, Y_p - Y_a)$
2.  **Distancia a lo largo de la sección (Coordenada X del perfil)**:
    Es el producto punto normalizado.
    $$Dist_{sec} = \frac{\vec{V} \cdot \vec{S}}{|\vec{S}|}$$
    $$Dist_{sec} = \frac{(X_p - X_a)(X_b - X_a) + (Y_p - Y_a)(Y_b - Y_a)}{\sqrt{(X_b - X_a)^2 + (Y_b - Y_a)^2}}$$
3.  **Distancia Perpendicular (Offset)**:
    Distancia del punto a la línea de sección (usada para filtrar por "buffer").
    $$Offset = \frac{(X_p - X_a)(Y_b - Y_a) - (Y_p - Y_a)(X_b - X_a)}{|\vec{S}|}$$
4.  **Coordenada Y del perfil**:
    Simplemente la elevación $Z_p$.

## 3. Pasos para la Implementación

### Paso 1: Interfaz de Usuario (GUI)
*   Agregar selectores de capa para **Collar**, **Survey** e **Intervalos**.
*   Agregar selectores de campos para las columnas requeridas (HoleID, X, Y, Z, Azimuth, Dip, From, To, Value).
*   Agregar campo para definir el **Ancho de Buffer** (distancia máxima de proyección).

### Paso 2: Procesamiento de Datos (Core Logic)
1.  **Lectura**: Leer las capas vectoriales o tablas CSV seleccionadas.
2.  **Validación**: Asegurar que los HoleIDs coincidan entre tablas.
3.  **Desurvey**: Generar una estructura de datos (lista de objetos o DataFrames) que contenga la geometría 3D completa de cada sondaje.
    *   Calcular coordenadas (X, Y, Z) para cada punto de inicio y fin de intervalo.
4.  **Filtrado y Proyección**:
    *   Iterar sobre cada sondaje.
    *   Calcular el *Offset* promedio del collar o de los puntos medios.
    *   Si $|Offset| \le Buffer$, incluir el sondaje.
    *   Calcular `Dist_sec` para cada punto.

### Paso 3: Renderizado (PreviewRenderer)
1.  **Trazas (Traces)**: Dibujar líneas que conecten los puntos proyectados $(Dist_{sec}, Z)$.
2.  **Intervalos**: Dibujar líneas más gruesas o rectángulos coloreados sobre la traza según el valor del intervalo (Litología/Ley).
    *   Requerirá un mapeo de colores (categórico para litología, gradiente para leyes).
3.  **Etiquetas**: Dibujar el nombre del sondaje (HoleID) cerca del collar (parte superior de la traza).

### Paso 4: Exportación
*   Asegurar que las geometrías generadas se puedan exportar a Shapefile/DXF junto con el perfil topográfico.
