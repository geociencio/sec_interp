# Skill: Agentic Memory (Cerebro)

Esta habilidad permite al agente gestionar su propia memoria semántica, extrayendo lecciones, patrones y preferencias del usuario para mejorar la efectividad a largo plazo.

## Directrices de Extracción

El agente debe buscar activamente los siguientes elementos durante la interacción:

1.  **Patrones de Error**: Soluciones a bugs que tomaron más de 3 intentos o requirieron investigación profunda.
2.  **Preferencias Implícitas**: Decisiones de estilo o arquitectura que el usuario aprueba repetidamente.
3.  **Hotspots Técnicos**: Zonas del código que son difíciles de testear o refactorizar.
4.  **Decisiones de Diseño**: Justificaciones de por qué se eligió una implementación sobre otra.

## Protocolo de Actualización (`AGENT_LESSONS.md`)

Al final de cada sesión significativa, el agente debe:

1.  **Sintetizar**: Resumir los hallazgos en entradas de máximo 3 líneas.
2.  **Categorizar**: Usar tags como `[TECHNICAL]`, `[USER_PREFERENCE]`, `[ARCHITECTURE]`.
3.  **Estructurar**: Mantener el formato YAML-friendly para futuras integraciones RAG.

## Ejemplo de Entrada Estructurada

```yaml
- date: 2026-02-05
  category: TECHNICAL
  topic: QgsGeometry Mocking
  lesson: "El método 'is3D' falla en mocks simples; requiere inyección de contexto QGIS."
  action: "Usar QgsGeometry.fromWkt() siempre que sea posible para evitar mocks manuales."
```

---
*Skill generada para la evolución de la Arquitectura de Agentes de SecInterp.*
