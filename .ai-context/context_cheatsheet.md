# Cheatsheet de Contexto e Integración

## 🔄 Ciclo de Sincronización
Para mantener a la IA "inteligente" sobre tu proyecto, sigue este ciclo:

1. **Analizar**: Corre el script cuando añadas archivos o cambies la lógica principal.
   ```bash
   python3 analyze_project_optfixed.py
   ```
2. **Consultar**: Revisa los problemas críticos en `PROJECT_SUMMARY.md`.
3. **Prompt**: Usa el workflow para generar tareas basadas en esos problemas.
   ```bash
   python3 .ai-context/ai_workflow.py start refactor "Reducir complejidad"
   python3 .ai-context/ai_workflow.py prompt "Refactorizar profile_exporters.py" --model gemini
   ```

## 📂 Archivos Clave
| Archivo | Propósito | Fuente |
| :--- | :--- | :--- |
| `AI_CONTEXT.md` | Mapa de archivos y dependencias para la IA | `analyze_project_optfixed.py` |
| `PROJECT_SUMMARY.md` | Reporte de salud y complejidad para el humano | `analyze_project_optfixed.py` |
| `.ai-context/project_brain.md` | Memoria a largo plazo de arquitectura y metas | Manual + Sincronización |
| `.ai-context/tech_stack.yaml` | Definición de tecnologías y convenciones | Manual + Sincronización |

## 💡 Tips de Uso
- **Instrucciones específicas**: Si quieres que la IA se enfoque sólo en un módulo, menciónalo en la tarea: *"Analiza lo que dice AI_CONTEXT.md sobre gui/main_dialog.py"*.
- **Métricas**: Menciona el **Score de Calidad** (ej. 82.3) para que la IA sepa qué tan estricta debe ser con la limpieza del código.
