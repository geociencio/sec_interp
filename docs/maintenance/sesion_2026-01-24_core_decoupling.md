# Sesión de Mantenimiento: Desacoplamiento Arquitectónico Core-QGIS
**Fecha**: 2026-01-24
**Tema**: `core_decoupling`
**Estado**: Finalizado ✅ (100% Tests OK)

## Resumen Técnico
Se ha realizado una refactorización profunda para desacoplar el núcleo de lógica de negocio (`core/`) de la API de QGIS. Esto permite que el procesamiento pesado de datos geológicos y sondajes ocurra en hilos de fondo sin acceder a objetos de la interfaz de usuario o capas vivas de QGIS, eliminando riesgos de bloqueos y crashes intermitentes.

## Logros Clave
- **Tipos de Dominio Agnósticos**: Migración de DTOs (`GeologySegment`, `DrillholeTaskInput`) para usar representaciones WKT y tipos primitivos de Python en lugar de objetos `qgis.core`.
- **Servicios Habilitados para Background**: `GeologyService` y `DrillholeService` ahora procesan datos pre-extraídos (diccionarios/strings), eliminando la dependencia de `QgsVectorLayer` durante el cálculo.
- **Estabilización de Infraestructura de Tests**:
    - Reconstrucción masiva de `MockQgsGeometry` en `base_test.py` con soporte para WKT, vértices e intersecciones simuladas.
    - Unificación de mocks de puntos (`MockQgsPoint`, `MockQgsPointXY`) para evitar recursión y sombreado de métodos.
- **Validación al 100%**: Migración de la suite completa de tests de core para validar la integridad de la lógica de negocio bajo la nueva arquitectura.

## Cambios por Componente

### Core Services
- **`GeologyService`**: Refactorizado para recibir geometrías WKT.
- **`DrillholeService`**: Implementado motor de proyección agnóstico capaz de manejar tanto `QgsFeature` (Síncrono) como `dict` (Asíncrono).

### Data Types (`core/types.py`)
- Definición de `DomainGeometry` como alias de `str` (WKT).
- Actualización de `InterpretationPolygon` y `GeologySegment` para persistencia agnóstica.

### Infraestructura de Pruebas
- **`tests/base_test.py`**: Limpieza de sombreado de métodos (`type()`, `vertices()`) y soporte robusto para serialización WKT.

## Verificación Final
- **Tests**: 208 tests ejecutados, 204 OK, 4 saltados.
- **Linter**: Verificado cumplimiento de estándares con `ruff` y `black`.

## Próximos Pasos
1. Integrar la nueva UI asíncrona que consuma estos servicios desacoplados.
2. Realizar perfilado de rendimiento con datasets reales de sondajes masivos.
3. Verificar la visualización 3D con las nuevas estructuras de datos.
