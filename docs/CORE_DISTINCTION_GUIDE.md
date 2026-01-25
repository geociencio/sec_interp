# Guía de Distinción de Componentes "Core"

Este documento tiene como objetivo aclarar la distinción entre los diferentes componentes denominados "Core" dentro del proyecto **SecInterp**, para evitar confusiones tanto por parte de desarrolladores humanos como de agentes de IA.

## ⚠️ La Distinción Fundamental

Existen dos entidades "Core" que coexisten en este entorno de desarrollo:

1.  **SecInterp Core** (El Núcleo del Proyecto):
    *   **Ubicación**: Directorio `/core` dentro de la raíz del proyecto.
    *   **Propósito**: Contiene la lógica de negocio pura, algoritmos geológicos, servicios de procesamiento y modelos de datos (DTOs) específicos de SecInterp.
    *   **Estado Actual**: **Desacoplado**. A partir de la versión 2.8.0, este módulo ha sido saneado para no tener dependencias directas de las clases vivas de QGIS durante el procesamiento pesado (Thread-Safe).

2.  **QGIS Core** (La API de QGIS):
    *   **Referencia**: Paquete de Python `qgis.core`.
    *   **Propósito**: Proporciona la infraestructura geoespacial subyacente (geometrías, capas, proyectos, CRS).
    *   **Interacción**: SecInterp utiliza `qgis.core` para extraer datos en el hilo principal, pero el **SecInterp Core** procesa estos datos usando tipos agnósticos (WKT, diccionarios, primitivos).

---

## 🧭 Reglas para Desarrolladores e IA

Para mantener la integridad arquitectónica, siga estas directrices:

### 1. No asuma que "Core" siempre es QGIS
Si se le pide "revisar el core", se refiere casi exclusivamente al directorio `/core` de este plugin. No intente buscar o modificar archivos internos del motor de QGIS.

### 2. Límites de Datos (Decoupling)
*   **En `/core`**: Se deben usar tipos de dominio agnósticos. Evite instanciar `QgsVectorLayer` o acceder a `QgsProject.instance()` dentro de los servicios del núcleo. Use `DomainGeometry` (WKT) y diccionarios de atributos.
*   **En `/gui`**: Es el lugar donde se realiza la traducción entre la API real de QGIS (`qgis.core`) y el **SecInterp Core**. Aquí es donde se extraen las geometrías y se preparan los DTOs.

### 3. Nomenclatura de Archivos e Importaciones
*   **Archivos Locales**: Los archivos en `core/` (ej. `core/services/geology_service.py`) son el **Cerebro de SecInterp**.
*   **API Externa**: Las importaciones que empiezan con `qgis.core`, `qgis.gui` o `qgis.utils` son **Dependencias Externas**.
*   **Regla de Nomenclatura**: En discusiones o comentarios de código, use "Internal Core" para referirse a `/core` y "PyQGIS API" para la del software.

### 4. El Patrón "Extract-then-Compute" (Extraer y Calcular)
Para evitar complicaciones futuras, el flujo de datos **DEBE** seguir este patrón:
1.  **Capa GUI/Task Interface**: Recibe objetos de QGIS (`QgsVectorLayer`, `QgsFeature`). Extrae lo necesario (geometría en WKT, diccionarios de atributos).
2.  **Capa Core**: Recibe únicamente los datos extraídos (strings, dicts, floats). Realiza los cálculos geométricos pesados.
3.  **Resultado**: El Core devuelve DTOs (Data Transfer Objects) definidos en `core/types.py`. La capa GUI se encarga de convertir esto de nuevo a capas de QGIS si es necesario.

### 5. Reglas de Oro de Hilo-Seguridad (Thread-Safety)
*   **Prohibido**: Importar `qgis.gui` dentro de `core/`. Los hilos de fondo morirán si intentan tocar cualquier widget o ventana.
*   **Restricción**: Minimizar el uso de `qgis.core` dentro de `core/`. Aunque algunas clases como `QgsGeometry` son seguras, es preferible operar sobre WKT para garantizar total independencia.
*   **Contexto de Aplicación**: Nunca use `iface` o `QgsProject.instance()` dentro de `core/`. Si necesita datos del proyecto, páselos como argumentos pre-extraídos.

---

## 🧪 Estrategia de Testing Diferenciada

*   **Tests del Core (`tests/core/`)**: Deben poder ejecutarse sin instalar QGIS completo. Usan mocks ligeros. Son el termómetro de la lógica geológica.
*   **Tests de Integración (`tests/integration/`)**: Requieren QGIS real. Prueban que nuestro "Core" se entiende correctamente con la "API de QGIS".

---

## 🛠️ Resumen de Desacoplamiento (Enero 2026)

Se ha completado un esfuerzo mayor para asegurar que:
*   `GeologyService` no use capas vivas de QGIS en su método de procesamiento.
*   `DrillholeService` use diccionarios en lugar de objetos `QgsFeature` durante el cálculo de trazas.
*   La lógica de proyección 3D acepta tuplas y tipos primitivos.

**En resumen: Mantenga nuestro Core "puro". Trate a QGIS como un proveedor de servicios externo. No permita que las raíces de uno entren en la lógica del otro.**
