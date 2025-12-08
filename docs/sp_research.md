# Investigación: Integración de SP (Potencial Espontáneo) en Perfiles

Este documento detalla los requisitos, cálculos y pasos necesarios para integrar la visualización de datos de Potencial Espontáneo (SP - Spontaneous Potential) en los perfiles transversales del plugin.

## 1. Datos Necesarios

El Potencial Espontáneo (SP) es una medición geofísica que registra diferencias de potencial eléctrico natural en el subsuelo, típicamente medido a lo largo de perfiles o en sondajes. Para integrarlo en un perfil 2D, se requieren los siguientes datos:

### A. Perfiles de SP en Superficie
Mediciones realizadas a lo largo de una línea en la superficie.

*   **Profile_ID**: Identificador único del perfil (String).
*   **Station**: Número de estación o distancia a lo largo del perfil (Float, en metros).
*   **X**: Coordenada Este de la estación (Float).
*   **Y**: Coordenada Norte de la estación (Float).
*   **Z**: Elevación de la estación (Float).
*   **SP_Value**: Valor de potencial espontáneo medido (mV - milivoltios).
*   *(Opcional)* **Date**: Fecha de medición.

### B. Registros de SP en Sondajes (Well Logs)
Mediciones de SP a lo largo de un pozo vertical.

*   **Well_ID**: Identificador único del pozo (String).
*   **X**: Coordenada Este del collar del pozo (Float).
*   **Y**: Coordenada Norte del collar del pozo (Float).
*   **Z**: Elevación del collar del pozo (Float).
*   **Depth**: Profundidad de la medición (Float, en metros).
*   **SP_Value**: Valor de potencial espontáneo (mV).

## 2. Cálculos y Fórmulas

### A. Proyección de Perfiles de Superficie al Plano de Sección

**Definición de la Sección:**
*   Punto Inicio: $(X_a, Y_a)$
*   Punto Fin: $(X_b, Y_b)$
*   Vector de Sección: $\vec{S} = (X_b - X_a, Y_b - Y_a)$
*   Longitud de Sección: $|\vec{S}|$

**Fórmulas de Proyección:**
Para una estación de SP en $P(X_p, Y_p, Z_p)$:

1.  **Vector desde inicio de sección a punto P**: $\vec{V} = (X_p - X_a, Y_p - Y_a)$
2.  **Distancia a lo largo de la sección (Coordenada X del perfil)**:
    $$Dist_{sec} = \frac{\vec{V} \cdot \vec{S}}{|\vec{S}|}$$
3.  **Distancia Perpendicular (Offset)**:
    $$Offset = \frac{(X_p - X_a)(Y_b - Y_a) - (Y_p - Y_a)(X_b - X_a)}{|\vec{S}|}$$
4.  **Filtrado por Buffer**: Incluir solo estaciones donde $|Offset| \le Buffer$.

### B. Conversión de Profundidad a Elevación (Para Well Logs)
Para pozos verticales:

$$Elevation = Z_{collar} - Depth$$

Donde:
- $Z_{collar}$ es la elevación del collar del pozo.
- $Depth$ es la profundidad de la medición.

### C. Normalización de Valores SP
Los valores de SP pueden variar significativamente. Para visualización, puede ser útil normalizar:

**Normalización Min-Max:**
$$SP_{norm} = \frac{SP - SP_{min}}{SP_{max} - SP_{min}}$$

**Normalización Z-Score:**
$$SP_{z} = \frac{SP - \mu}{\sigma}$$

Donde $\mu$ es la media y $\sigma$ es la desviación estándar.

## 3. Pasos para la Implementación

### Paso 1: Interfaz de Usuario (GUI)

#### Para Perfiles de Superficie:
*   Agregar selector de capa para **Perfiles SP** (capa de puntos o líneas).
*   Agregar selectores de campos para:
    *   **Station/Distance**: Distancia a lo largo del perfil.
    *   **SP_Value**: Valor de potencial espontáneo.
    *   **X, Y, Z**: Coordenadas (o usar geometría directamente).
*   Agregar campo para definir el **Ancho de Buffer**.

#### Para Well Logs:
*   Agregar selector de capa para **Pozos con SP** (capa de puntos para collares).
*   Agregar selector de tabla para **Datos de SP por profundidad**.
*   Agregar selectores de campos para:
    *   **Well_ID**: Identificador del pozo.
    *   **Depth**: Profundidad de medición.
    *   **SP_Value**: Valor de SP.

### Paso 2: Procesamiento de Datos (Core Logic)

#### Para Perfiles de Superficie:
1.  **Lectura**: Leer la capa de perfiles SP.
2.  **Filtrado por Buffer**:
    *   Calcular el *Offset* de cada estación respecto a la línea de sección.
    *   Incluir solo estaciones donde $|Offset| \le Buffer$.
3.  **Proyección**:
    *   Calcular `Dist_sec` para cada estación incluida.
4.  **Estructura de Datos**:
    *   Lista de tuplas: `(Dist_sec, Elevation, SP_Value)`.

#### Para Well Logs:
1.  **Lectura**: Leer capa de pozos y tabla de datos SP.
2.  **Validación**: Asegurar que los Well_IDs coincidan.
3.  **Filtrado por Buffer**: Similar a perfiles de superficie.
4.  **Conversión de Profundidad**:
    *   Para cada medición: `Elevation = Z_collar - Depth`.
5.  **Proyección**:
    *   Calcular `Dist_sec` para cada pozo.
6.  **Estructura de Datos**:
    *   Lista de listas: Para cada pozo, lista de `(Dist_sec, Elevation, SP_Value)`.

### Paso 3: Renderizado (PreviewRenderer)

#### Opción 1: Curva de SP (Para Perfiles de Superficie)
1.  **Gráfico Superpuesto**: Dibujar una curva de SP sobre el perfil topográfico.
2.  **Eje Secundario**: Usar un eje Y secundario para valores de SP (mV).
3.  **Línea de SP**: Conectar los puntos `(Dist_sec, SP_Value)` con una línea.
4.  **Relleno**: Opcionalmente, rellenar el área bajo la curva con color según el signo (positivo/negativo).

#### Opción 2: Mapa de Calor (Para Well Logs)
1.  **Columnas Verticales**: Para cada pozo, dibujar una columna vertical en `Dist_sec`.
2.  **Gradiente de Color**: Colorear cada segmento de la columna según el valor de SP.
    *   Valores negativos: Azul (típicamente arcillas).
    *   Valores positivos: Rojo/Naranja (típicamente arenas).
3.  **Ancho de Columna**: Fijo o configurable.

#### Opción 3: Símbolos (Para Puntos Discretos)
1.  **Marcadores**: Dibujar símbolos (círculos, cuadrados) en cada punto `(Dist_sec, Elevation)`.
2.  **Tamaño/Color**: Variar tamaño o color según el valor de SP.

### Paso 4: Leyenda
*   Agregar una leyenda que muestre:
    *   Escala de colores para valores de SP.
    *   Rango de valores (mínimo, máximo).
    *   Unidades (mV).

### Paso 5: Exportación
*   Exportar datos SP a CSV con columnas:
    *   `Dist_sec`, `Elevation`, `SP_Value`, `Well_ID` (si aplica).
*   Exportar geometrías a Shapefile:
    *   Puntos con atributos de SP.
    *   Líneas de curva SP.

## 4. Consideraciones Adicionales

### A. Interpretación Geológica
Los valores de SP pueden indicar:
*   **SP Negativo**: Presencia de arcillas, lutitas.
*   **SP Positivo**: Presencia de arenas, areniscas permeables.
*   **Línea Base (0 mV)**: Referencia, típicamente en lutitas.

### B. Correcciones
Los datos de SP pueden requerir correcciones por:
*   **Deriva instrumental**: Corrección de línea base.
*   **Efectos topográficos**: En perfiles de superficie.
*   **Temperatura**: En pozos profundos.

### C. Integración con Otros Datos
Los datos de SP pueden visualizarse junto con:
*   Perfil topográfico.
*   Unidades geológicas.
*   Datos de resistividad (VES/SEV).
*   Registros de pozos (litología, gamma ray).

### D. Formatos de Datos de Entrada
*   **Shapefile/GeoPackage**: Capa de puntos o líneas.
*   **CSV**: Tablas con coordenadas y valores.
*   **Formatos LAS/LIS**: Para well logs (requeriría parser específico).

## 5. Ejemplo de Visualización

### Perfil de Superficie:
```
Elevación (m)
    |
    |     Perfil Topográfico
    |    /\  /\    /\
    |   /  \/  \  /  \
    |  /        \/    \
    +-------------------> Distancia (m)
    |
    |  Curva SP (mV)
    |     /\    /\
    |    /  \  /  \
    |___/____\/____|____
    |        \/
```

### Well Log:
```
Elevación (m)
    |
    |     Pozo-1    Pozo-2
    |       |         |
    |    [  SP  ]  [  SP  ]  <- Columna coloreada
    |    [  SP  ]  [  SP  ]     según valor
    |    [  SP  ]  [  SP  ]
    |       |         |
    +-------+---------+-----> Distancia (m)
```

Cada segmento de la columna tiene un color según el valor de SP (azul para negativo, rojo para positivo).
