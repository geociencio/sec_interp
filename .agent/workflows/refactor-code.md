---
description: Workflow guiado para refactorización de código con validación de complejidad
agent: Senior Architect
skills: [qgis-core, geological-logic]
validation: |
  - Verificar que complejidad ciclomática se redujo (CC < 15)
  - Confirmar que tests siguen pasando después de refactorización
  - Validar que no se introdujeron violaciones de arquitectura
---

Este workflow guía la refactorización de código siguiendo los estándares del proyecto y usando conocimiento especializado de skills.

## Cuándo Usar Este Workflow

- Cuando `qgis-analyzer` detecta métodos con CC > 15
- Cuando `AI_CONTEXT.md` identifica deuda técnica crítica
- Antes de añadir nuevas funcionalidades a módulos complejos


## Pasos de Refactorización

1. **Identificar Objetivo de Refactorización**:
   // turbo
   ```bash
   uv run ai-ctx analyze .
   ```

   🤖 **Agent Action**: Analizar `analysis_results/PROJECT_SUMMARY.md` para identificar hotspots (CC > 15) y deuda técnica.

2. **Cargar Contexto Especializado**:

   🤖 **Agent Action**: Según el módulo, cargar skill apropiado (geological-logic, qgis-core, o ui-framework).

3. **Aplicar Refactorización**:

   🤖 **Agent Action**: Aplicar principios SOLID y reducir complejidad ciclomática.

4. **Validar con Tests**:
   // turbo
   ```bash
   make docker-test
   ```

   🤖 **Agent Action**: Usar skill **qa-docker** para asegurar que no hay regresiones.

5. **Verificar Métricas de Calidad**:
   // turbo
   ```bash
   uv run ai-ctx analyze .
   ```

   🤖 **Agent Action**: Confirmar mejora en el Quality Score y reducción de la Complejidad Ciclomática (CC).

6. **Commit de Refactorización**:
   Usar workflow `/crea-commit` con mensaje técnico estructurado.

## Resultado Esperado
- Código más mantenible, testeable y con menor complejidad ciclomática.
- Cero regresiones funcionales confirmadas por tests.
- Documentación técnica (docstrings) actualizada.
