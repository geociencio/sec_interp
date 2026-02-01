---
name: geological-logic
description: Estándares para el manejo de datos de sondajes, interpolación de secciones y validación de 3 niveles.
trigger: al implementar algoritmos geológicos, validación de datos o lógica de procesamiento de sondajes.
---

# Lógica Geológica y de Dominio

Define las reglas de negocio para el procesamiento de datos mineros/geológicos, asegurando la consistencia geométrica y la integridad de los datos de sondajes.

## Cuándo usar este skill
- Al modificar servicios de procesamiento de sondajes (`DrillholeService`).
- Al diseñar algoritmos de interpolación o intersección de secciones.
- Al implementar nuevas reglas de validación de datos geológicos.

## Grado de Libertad
- **Estricto**: Las reglas de validación de 3 niveles y el desacoplamiento de PyQGIS son obligatorios.

## Workflow
1. **Modelado**: Definir las entidades usando Dataclasses y tipos estrictos.
2. **Validación**: Implementar los 3 niveles (Tipo, Esquema, Negocio).
3. **Abstracción**: Asegurar que la lógica core use WKT o DTOs, no `QgsGeometry`.
4. **Pruebas**: Crear tests unitarios con contextos de CRS variados.

## Instrucciones y Reglas

### Validación de 3 Niveles
1. **Nivel 1 (Tipo)**: Tipos de datos básicos y rangos permitidos.
2. **Nivel 2 (Esquema)**: Consistencia entre campos (ej. `StartDepth < EndDepth`).
3. **Nivel 3 (Negocio)**: Consistencia externa (ej. "Capa existe", "Sin solapes en geología").

### Reglas de Geometría
- **Desacoplamiento**: Los servicios core NUNCA deben depender de `QgsGeometry`.
- **Estándar WKT**: Operar con strings WKT; convertir a PyQGIS solo en la frontera de UI.
- **Mocks**: Usar `MockQgsGeometry` para tests unitarios locales.

## Checklist de Calidad
- [ ] ¿La lógica core es independiente de PyQGIS?
- [ ] ¿Se implementan los 3 niveles de validación?
- [ ] ¿Existen tests para casos de borde (sondajes verticales, paralelos)?
- [ ] ¿Se manejan correctamente las unidades y CRS?
