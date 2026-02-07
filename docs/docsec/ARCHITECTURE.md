# Arquitectura de SecInterp

Este documento describe la arquitectura técnica del plugin SecInterp para QGIS, enfocándose en su diseño desacoplado, orientado a servicios y asíncrono.

## 🏗️ Visión General
SecInterp sigue un patrón de diseño que separa estrictamente la lógica de negocio (Core) de la interfaz de usuario (GUI), y utiliza patrones de concurrencia seguros para QGIS.

```mermaid
graph TD
    UI[GUI Layer: Main Dialog] --> PM[PreviewManager]
    PM --> TS[Task System (QgsTask)]
    TS --> DTO[DTOs: Task Inputs]
    DTO --> GS[GeologyService (Stateless)]
    PM --> PS[PreviewService]
    PS --> DS[DrillholeService]
    PS --> SS[StructureService]
```

## 📂 Estructura de Capas

### 🎨 Capa de UI (gui/)
Responsable de la interacción con el usuario y la orquestación.
- **`main_dialog.py`**: Controlador principal de la ventana.
- **`main_dialog_preview.py` (PreviewManager)**: Gestiona el estado de la previsualización, caché por hash y lanzamiento de tareas.
- **`tasks/`**: Contiene implementaciones de `QgsTask` (e.g., `GeologyGenerationTask`) para procesamiento en segundo plano.

### ⚙️ Capa de Negocio (core/)
Lógica pura, desacoplada de la GUI y thread-safe.

#### Servicios (`core/services/`)
- **`geology_service.py`**: Implementa lógica pura de intersección geométrica. Diseñado para ser invocado tanto sincrónicamente como desde hilos secundarios.
- **`drillhole_service.py`**: Procesamiento de sondajes y desurvey 3D.
- **`structure_service.py`**: Proyección de medidas estructurales.

#### Tipos y DTOs (`core/types.py`)
El intercambio de datos entre la UI y los hilos de fondo se realiza exclusivamente mediante **Data Transfer Objects (DTOs)**.
- **`GeologyTaskInput`**: Encapsula geometrías copiadas y parámetros simples. Evita pasar objetos `QgsVectorLayer` vivos a hilos secundarios, previniendo crashes de la API C++.
- **`PreviewParams`**: Objeto validado que contiene toda la configuración necesaria para generar una sección.

### 🛠️ Interfaces y Desacople
- **`core/interfaces/`**: Define contratos abstractos (`IGeologyService`, `IPreviewService`) que permiten Inyección de Dependencias y facilitan el Mocking en tests.

## 🚀 Patrones de Concurrencia
Para garantizar que la interfaz de QGIS no se congele durante cálculos complejos, SecInterp utiliza el patrón **QgsTask + DTO**:

1.  **Prepare (Main Thread)**: La UI recopila datos y crea un DTO (ej. `GeologyTaskInput`) copiando las geometrías necesarias.
2.  **Process (Background Thread)**: Se lanza un `QgsTask` que invoca un servicio puro usando *solo* el DTO. No hay acceso a `QgsProject` ni capas.
3.  **Finish (Main Thread)**: El resultado (otro DTO o lista de primitivas) se devuelve al hilo principal para actualizar la UI.

## 🛡️ Estándares y Calidad
- **Type Safety**: Uso extensivo de Type Hints y validación con `mypy`.
- **Linting**: Reglas estrictas de Ruff (incluyendo complejidad ciclomática).
- **ADR**: Las decisiones arquitectónicas importantes se registran en `docs/adr/`.

---
**Version**: 2.9.1 | **Updated**: 2026-02-07
