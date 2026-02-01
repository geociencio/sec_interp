---
name: qa-docker
description: Estándares para pruebas en entorno Dockerizado y uso de Mocks para QGIS.
trigger: al escribir o ejecutar tests, usar mocks o manejar infraestructura Docker.
---

# QA y Automatización Docker

Garantiza la estabilidad del código mediante un entorno de ejecución controlado (Docker) y estrategias de simulación (Mocks) para PyQGIS.

## Cuándo usar este skill
- Al crear nuevos casos de prueba unitarios o de integración.
- Al depurar fallos en el pipeline de CI/CD.
- Al configurar o modificar el entorno de desarrollo Docker.

## Grado de Libertad
- **Guiado**: Se deben seguir las estrategias de mocking definidas, pero existe libertad en el diseño de los casos de prueba.

## Workflow
1. **Diseño**: Aplicar estrategia "Mock-First" para lógica independiente de la UI.
2. **Implementación**: Crear tests usando `unittest` o `pytest`.
3. **Ejecución**: Validar localmente y luego en Docker (`make docker-test`).
4. **Cobertura**: Verificar que se alcanza el mínimo del 80% en nuevos servicios.

## Instrucciones y Reglas

### Estrategia de Mocking
- **Mock-First**: Seguir el [ADR-0004](file:///home/jmbernales/qgispluginsdev/sec_interp/docs/adr/ADR-0004-Mock-First-Testing-Strategy.md).
- **Aislamiento**: Ejecutar tests en procesos separados para evitar contaminación de Mocks.
- **FORCE_MOCKS**: Usar `FORCE_MOCKS=0` solo para tests de integración reales.

### Entorno Docker
- **Imagen**: Usar `qgis/qgis:latest` como base.
- **Comando Maestro**: `make docker-test` es el control de salud definitivo.

## Checklist de Calidad
- [ ] ¿La cobertura de nuevos servicios es > 80%?
- [ ] ¿Se limpian los patches de Mocks después de cada test?
- [ ] ¿El test de integración se ejecuta en un proceso aislado?
- [ ] ¿El reporte de Docker muestra 0 fallos?
