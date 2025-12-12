# Informe Técnico: Refactorización de Lógica de Negocio y Arquitectura

**Fecha:** 11 de Diciembre, 2025
**Proyecto:** SecInterp QGIS Plugin
**Autor:** Antigravity (Assistant) & Juan M Bernales
**Versión:** 1.0

## 1. Resumen Ejecutivo

Este informe detalla la refactorización profunda realizada en el plugin `SecInterp`. El objetivo principal fue desacoplar la lógica de negocio de la interfaz de usuario (GUI) y de los exportadores, centralizándola en servicios dedicados (`Services`). Se introdujeron "Objetos Ricos" (`Rich Data Objects`) para el intercambio de datos, eliminando la duplicación de cálculos y mejorando la mantenibilidad y testabilidad del código.

## 2. Evolución de la Arquitectura

### 2.1. Estado Anterior (Legacy)

Anteriormente, la lógica de cálculo (proyección de estructuras, intersección geológica) estaba dispersa y duplicada.
*   `algorithms.py`: Orquestaba pero con lógica mezclada.
*   `profile_exporters.py`: Recalculaba proyecciones e intersecciones internamente para escribir Shapefiles, duplicando el trabajo de la vista previa.
*   `preview_renderer.py`: Recibía tuplas simples `(dist, elev)` y carecía de contexto geológico completo.

### 2.2. Nueva Arquitectura (Servicios y Tipos Ricos)

La nueva arquitectura sigue un patrón de **Inyección de Dependencias** y **Separación de Responsabilidades**.

```mermaid
graph TD
    UI[GUI / Main Dialog] -->|Inputs| Alg[Orchestrator (algorithms.py)]
    Alg -->|Calls| QS[QgsRaster/Vector Layers]
    
    subgraph "Core Services"
        Alg --> StructServ[StructureService]
        Alg --> GeolServ[GeologyService]
        Alg --> ProfServ[ProfileService]
    end
    
    subgraph "Domain Objects (core/types.py)"
        StructServ -->|Returns| SM[List[StructureMeasurement]]
        GeolServ -->|Returns| GS[List[GeologySegment]]
    end
    
    subgraph "Consumers"
        SM & GS --> Prev[PreviewRenderer]
        SM & GS --> Exp[Exporters (CSV, SHP, DXF)]
    end
```

## 3. Cambios Clave

### 3.1. Tipos de Datos (Core Types)
Se crearon `dataclasses` en `core/types.py` para estandarizar la transferencia de datos.
*   **`StructureMeasurement`**: Encapsula distancia, elevación, buzamiento aparente, y *todos* los atributos originales del rasgo estructural.
*   **`GeologySegment`**: Encapsula la geometría exacta de intersección y los atributos de la unidad litológica.

### 3.2. Servicios (Services)
*   **`StructureService`**: Ahora maneja integralmente la proyección. Realiza el muestreo de elevación internamente y retorna objetos `StructureMeasurement` completos.
*   **`GeologyService`**: Retorna `GeologySegment`, preservando la geometría real en lugar de solo puntos de muestreo dispersos.

### 3.3. Exportadores (Exporters)
Los exportadores (`StructureShpExporter`, `GeologyShpExporter`) fueron "aligerados". Ya no realizan cálculos geométricos pesados. Su única responsabilidad es:
1.  Recibir la lista de objetos ricos.
2.  Mapear atributos a campos de Shapefile.
3.  Escribir el archivo.
Esto garantiza que lo que se ve en el Preview es **matemáticamente idéntico** a lo que se exporta.

### 3.4. Interfaz de Usuario (GUI)
`main_dialog_preview.py` y `preview_renderer.py` fueron actualizados para consumir estos nuevos objetos.
*   **Logs Claros**: Se diferenció la terminología en los logs: "segmentos" para geología y "mediciones" para estructura, facilitando la depuración.

## 4. Verificación y Calidad

### 4.1. Pruebas Automatizadas (Mocking)
Ante la falta de un entorno QGIS completo para CI/CD, se desarrolló un script de verificación (`scripts/verify_refactor_mock.py`) que usa `unittest.mock` para simular clases de QGIS (`QgsFeature`, `QgsGeometry`, etc.).
*   **Resultado**: Validación exitosa de lógica de proyección y encapsulamiento de atributos.

### 4.2. Verificación Manual
*   **Preview**: Verificado gráficamente en QGIS.
*   **Exportación**: Confirmado que los Shapefiles de salida contienen los atributos correctos (`dip`, `strike`, `unit_name`).
*   **Consistencia**: Se resolvió un problema donde logs antiguos causaban confusión; el despliegue final confirmó la consistencia total.

## 5. Beneficios Obtenidos

1.  **Eliminación de Duplicidad**: Un solo "Source of Truth" para cálculos geométricos.
2.  **Extensibilidad**: Agregar nuevos formatos de exportación es trivial; solo necesitan iterar sobre la lista de objetos pre-calculados.
3.  **Observabilidad**: Los logs ahora son semánticamente precisos.
4.  **Testabilidad**: Los servicios aislados son testeables sin requerir la GUI.

## 6. Recomendaciones Futuras

Basado en la investigación realizada durante este sprint:

1.  **Muestreo Adaptativo**: Implementar algoritmos como Ramer-Douglas-Peucker (RDP) en `ProfileService` para optimizar la cantidad de puntos en perfiles topográficos largos sin perder detalle visual.
2.  **Procesamiento Asíncrono (QgsTask)**: Para perfiles muy largos o DEMs de alta resolución, mover la ejecución de los servicios a un `QgsTask` en segundo plano para no congelar la GUI.
3.  **Refactorización de `measure_tool.py`**: Integrar la lógica de medición directamente con los nuevos tipos de datos para ofrecer "snapping" a estructuras geológicas.

---
**Fin del Informe**
