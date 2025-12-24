# Investigación: Integración de VES/SEV (Sondeos Eléctricos Verticales) en Perfiles

Este documento detalla los requisitos, cálculos y pasos necesarios para integrar la visualización de datos de Sondeos Eléctricos Verticales (VES - Vertical Electrical Sounding / SEV - Sondeo Eléctrico Vertical) en los perfiles transversales del plugin.

## 1. Datos Necesarios

Los sondeos eléctricos verticales (VES/SEV) son mediciones geofísicas que determinan la resistividad eléctrica del subsuelo a diferentes profundidades. Para integrarlos en un perfil 2D, se requieren los siguientes datos:

### A. Ubicación de Estaciones VES
Define la posición geográfica donde se realizó el sondeo.
*   **Station_ID**: Identificador único de la estación VES (String).
*   **X**: Coordenada Este de la estación (Float).
*   **Y**: Coordenada Norte de la estación (Float).
*   **Z**: Elevación de la estación (Float).
*   *(Opcional)* **Date**: Fecha de medición.
*   *(Opcional)* **Operator**: Operador que realizó la medición.

### B. Curva de Resistividad Aparente
Datos de campo obtenidos durante la medición.
*   **Station_ID**: Identificador de la estación.
*   **AB/2**: Semidistancia del arreglo de corriente (metros).
*   **MN/2**: Semidistancia del arreglo de potencial (metros).
*   **Rho_a**: Resistividad aparente medida (Ohm·m).

### C. Modelo de Capas Invertido
Resultado de la inversión geofísica que interpreta las capas del subsuelo.
*   **Station_ID**: Identificador de la estación.
*   **Layer**: Número de capa (Integer, 1 = superficie).
*   **Thickness**: Espesor de la capa en metros (Float). La última capa suele tener espesor infinito.
*   **Resistivity**: Resistividad verdadera de la capa (Ohm·m).
*   **Depth_Top**: Profundidad al tope de la capa (Float, calculada acumulando espesores).
*   **Depth_Bottom**: Profundidad a la base de la capa (Float).

## 2. Cálculos y Fórmulas

### A. Conversión de Profundidad a Elevación
Para visualizar en un perfil topográfico, las profundidades deben convertirse a elevaciones absolutas.

**Fórmula:**
$$Elevation = Z_{station} - Depth$$

Donde:
- $Z_{station}$ es la elevación de la estación VES.
- $Depth$ es la profundidad bajo la superficie.

### B. Proyección al Plano de Sección
Similar a la proyección de sondajes mecánicos, se debe proyectar la ubicación de cada estación VES al plano 2D de la sección.

**Definición de la Sección:**
*   Punto Inicio: $(X_a, Y_a)$
*   Punto Fin: $(X_b, Y_b)$
*   Vector de Sección: $\vec{S} = (X_b - X_a, Y_b - Y_a)$
*   Longitud de Sección: $|\vec{S}|$

**Fórmulas de Proyección:**
Para una estación VES en $P(X_p, Y_p, Z_p)$:

1.  **Vector desde inicio de sección a punto P**: $\vec{V} = (X_p - X_a, Y_p - Y_a)$
2.  **Distancia a lo largo de la sección (Coordenada X del perfil)**:
    $$Dist_{sec} = \frac{\vec{V} \cdot \vec{S}}{|\vec{S}|}$$
    $$Dist_{sec} = \frac{(X_p - X_a)(X_b - X_a) + (Y_p - Y_a)(Y_b - Y_a)}{\sqrt{(X_b - X_a)^2 + (Y_b - Y_a)^2}}$$
3.  **Distancia Perpendicular (Offset)**:
    $$Offset = \frac{(X_p - X_a)(Y_b - Y_a) - (Y_p - Y_a)(X_b - X_a)}{|\vec{S}|}$$
4.  **Filtrado por Buffer**: Incluir solo estaciones donde $|Offset| \le Buffer$.

### C. Escala de Color para Resistividad
La resistividad varía en varios órdenes de magnitud (de 1 a 10,000+ Ohm·m), por lo que se recomienda usar una escala logarítmica.

**Escala Logarítmica:**
$$Log_{Rho} = \log_{10}(Resistivity)$$

**Mapeo de Colores:**
Se puede usar una paleta de colores (e.g., viridis, jet) donde:
- Resistividades bajas (arcillas, agua salada): Azul/Verde
- Resistividades medias (arenas, gravas): Amarillo/Naranja
- Resistividades altas (rocas, basamento): Rojo/Magenta

## 3. Pasos para la Implementación

### Paso 1: Interfaz de Usuario (GUI)
*   Agregar selector de capa para **Estaciones VES** (capa de puntos).
*   Agregar selectores de campos para:
    *   **Station_ID**: Campo identificador.
    *   **X, Y, Z**: Coordenadas (o usar geometría del punto directamente).
*   Agregar selector de tabla o capa para **Modelo de Capas Invertido**.
*   Agregar selectores de campos para:
    *   **Station_ID**: Para vincular con estaciones.
    *   **Layer, Thickness, Resistivity** (o **Depth_Top, Depth_Bottom, Resistivity**).
*   Agregar campo para definir el **Ancho de Buffer** (distancia máxima de proyección).
*   *(Opcional)* Agregar selector de paleta de colores para resistividad.

### Paso 2: Procesamiento de Datos (Core Logic)
1.  **Lectura**: Leer la capa de estaciones VES y la tabla de modelo de capas.
2.  **Validación**: Asegurar que los Station_IDs coincidan entre ambas fuentes.
3.  **Filtrado por Buffer**:
    *   Iterar sobre cada estación VES.
    *   Calcular el *Offset* de la estación respecto a la línea de sección.
    *   Si $|Offset| \le Buffer$, incluir la estación.
4.  **Cálculo de Coordenadas del Perfil**:
    *   Calcular `Dist_sec` para cada estación incluida.
    *   Para cada capa del modelo:
        *   Calcular `Elevation_Top = Z_station - Depth_Top`.
        *   Calcular `Elevation_Bottom = Z_station - Depth_Bottom`.
5.  **Estructura de Datos**:
    *   Crear una lista de objetos o diccionarios que contengan:
        *   `Dist_sec`: Distancia a lo largo de la sección.
        *   `Elevation_Top`, `Elevation_Bottom`: Elevaciones de tope y base de capa.
        *   `Resistivity`: Valor de resistividad.
        *   `Station_ID`: Identificador de la estación.

### Paso 3: Renderizado (PreviewRenderer)
1.  **Columnas Verticales**: Para cada estación VES proyectada, dibujar una columna vertical en la posición `Dist_sec`.
2.  **Rectángulos Coloreados**: Dentro de cada columna, dibujar rectángulos para cada capa:
    *   **Posición X**: `Dist_sec` (puede tener un ancho fijo, e.g., 50m).
    *   **Posición Y**: Entre `Elevation_Top` y `Elevation_Bottom`.
    *   **Color**: Asignado según el valor de `Resistivity` usando la escala logarítmica y la paleta de colores.
3.  **Leyenda**: Agregar una barra de escala de colores que muestre la relación entre color y resistividad (en escala logarítmica).
4.  **Etiquetas**: Opcionalmente, etiquetar cada estación con su `Station_ID` en la parte superior de la columna.

### Paso 4: Exportación
*   Asegurar que las columnas VES se puedan exportar a Shapefile/DXF junto con el perfil topográfico.
*   Cada rectángulo de capa puede ser un polígono con atributos:
    *   `Station_ID`
    *   `Layer`
    *   `Resistivity`
    *   `Elevation_Top`
    *   `Elevation_Bottom`

## 4. Consideraciones Adicionales

### A. Ancho de Columna
El ancho de las columnas VES en el perfil puede ser:
*   **Fijo**: Un valor constante (e.g., 50m o 100m).
*   **Proporcional al espaciado**: Basado en la distancia entre estaciones adyacentes.
*   **Configurable**: Permitir al usuario definir el ancho.

### B. Superposición de Datos
Si hay múltiples estaciones VES muy cercanas en el perfil, pueden superponerse. Opciones:
*   Dibujar con transparencia (alpha).
*   Desplazar ligeramente las columnas.
*   Mostrar solo la estación más cercana a la línea de sección.

### C. Integración con Otros Datos
Las columnas VES pueden visualizarse junto con:
*   Perfil topográfico (línea de superficie).
*   Unidades geológicas (polígonos).
*   Datos estructurales (símbolos de manteo).
*   Trazas de sondajes mecánicos (líneas).

### D. Formatos de Datos de Entrada
Los datos VES pueden venir en diversos formatos:
*   **Shapefile/GeoPackage**: Capa de puntos para estaciones, tabla para modelo de capas.
*   **CSV**: Tablas separadas para estaciones y capas.
*   **Formatos específicos de software geofísico**: IPI2Win, RES2DINV, etc. (requeriría parsers específicos).

## 5. Ejemplo de Visualización

```
Perfil Topográfico
    |
    |     VES-1      VES-2      VES-3
    |      |          |          |
    |   [Capa 1]  [Capa 1]  [Capa 1]  <- Resistividad alta (rojo)
    |   [Capa 2]  [Capa 2]  [Capa 2]  <- Resistividad media (amarillo)
    |   [Capa 3]  [Capa 3]  [Capa 3]  <- Resistividad baja (azul)
    |      |          |          |
    +------+----------+----------+-----> Distancia a lo largo de la sección
```

Cada rectángulo coloreado representa una capa del modelo VES, con color según su resistividad.
