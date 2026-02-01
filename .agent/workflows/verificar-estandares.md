---
description: Audita la consistencia del sistema agentico (Skills y Workflows) contra el estándar maestro.
agent: Senior Architect
skills: [qgis-core, commit-standards]
validation:
  - ¿Todos los Skills tienen Checklist de Calidad?
  - ¿La documentación de los Skills está en español?
  - ¿Los Workflows tienen secciones de Resultado Esperado?
---

# Workflow: Verificar Estándares Agenticos

Este flujo garantiza que el "cerebro" de la IA se mantenga ordenado, legible y bajo los estándares de calidad definidos en la investigación técnica.

## 1. Auditoría de Habilidades (Skills)

Revisar cada archivo en `.agent/skills/` buscando:
1.  **YAML**: Presencia de `name` y `description`.
2.  **Idioma**: Descripción y contenido principal en español.
3.  **Estructura**: Secciones de Cuándo usar, Grado de Libertad, Workflow e Instrucciones.

## 2. Auditoría de Flujos (Workflows)

Revisar cada archivo en `.agent/workflows/` buscando:
1.  **YAML**: Descripción clara del objetivo.
2.  **Estructura**: Pasos numerados y uso de `// turbo` donde aplique.
3.  **Resultado Esperado**: Presencia de métricas de éxito al final del documento.

## 3. Sincronización Automática

Ejecutar la sincronización para asegurar que `AGENTS.md` está al día.
// turbo
```bash
python3 scripts/skill_sync.py
```

## Resultado Esperado
- Informe detallado de desviaciones de estándar.
- Propuesta de corrección inmediata para componentes obsoletos.
- Sincronización garantizada de la matriz de habilidades.
