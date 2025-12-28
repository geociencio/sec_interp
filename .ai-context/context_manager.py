#!/usr/bin/env python3
"""context_manager.py - Gestiona contexto para múltiples IAs."""

import json
from pathlib import Path
from typing import Dict, List, Optional

import yaml


class AIContextManager:
    """Gestiona contexto optimizado para diferentes IAs."""

    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.contexts = self._load_contexts()

    def _load_contexts(self) -> dict:
        """Carga contextos existentes."""
        contexts = {}
        context_files = ["project_context.json", "AI_CONTEXT.md", ".ai-context.yaml"]

        for file in context_files:
            path = self.project_path / file
            if path.exists():
                contexts[file] = self._load_file(path)

        return contexts

    def create_optimized_prompt(
        self, task: str, ai_model: str = "deepseek-coder", max_tokens: int = 4000
    ) -> str:
        """Crea prompt optimizado para la tarea específica."""
        # Contexto base del proyecto
        base_context = self._extract_relevant_context(task)

        # Optimizar según modelo de IA
        if "deepseek" in ai_model.lower():
            prompt_template = self._deepseek_template()
        elif "gpt" in ai_model.lower():
            prompt_template = self._chatgpt_template()
        elif "claude" in ai_model.lower():
            prompt_template = self._claude_template()
        else:
            prompt_template = self._generic_template()

        # Ensamblar prompt final
        full_prompt = prompt_template.format(
            task=task,
            context=base_context[: max_tokens // 2],
            project_name=self.project_path.name,
        )

        return self._truncate_to_tokens(full_prompt, max_tokens)

    def _deepseek_template(self) -> str:
        """Template optimizado para DeepSeek."""
        return """Eres un experto en Python analizando el proyecto: {project_name}

## CONTEXTO DEL PROYECTO:
{context}

## TAREA ASIGNADA:
{task}

## INSTRUCCIONES ESPECÍFICAS PARA DEEPSEEK:
1. Enfócate en código práctico y eficiente
2. Sugiere optimizaciones de performance
3. Mantén compatibilidad con Python 3.8+
4. Incluye ejemplos de código específicos
5. Prioriza soluciones con bibliotecas estándar

## FORMATO DE RESPUESTA:
```analysis
[Análisis breve del problema]
suggestions
[Lista numerada de sugerencias]
code_examples
[Código de ejemplo si aplica]
next_steps
[Próximos pasos recomendados]
```"""

    def _extract_relevant_context(self, task: str) -> str:
        """Extrae contexto relevante para la tarea específica."""
        keywords = self._extract_keywords(task)
        relevant_parts = []

        # Buscar en contextos existentes
        for context_name, context_content in self.contexts.items():
            if isinstance(context_content, dict):
                content_str = json.dumps(context_content)
            else:
                content_str = str(context_content)

            # Verificar relevancia
            if any(keyword.lower() in content_str.lower() for keyword in keywords):
                relevant_parts.append(f"=== {context_name} ===\n{content_str[:1000]}")

        return (
            "\n\n".join(relevant_parts)
            if relevant_parts
            else "No hay contexto específico"
        )

    def _extract_keywords(self, text: str) -> list[str]:
        """Extrae palabras clave del texto."""
        # Palabras comunes a ignorar
        stop_words = {"el", "la", "los", "las", "de", "en", "y", "o", "a", "para"}
        words = text.lower().split()
        return [w for w in words if w not in stop_words and len(w) > 3]

    def _truncate_to_tokens(self, text: str, max_tokens: int) -> str:
        """Trunca texto aproximando tokens."""
        # Estimación simple: 1 token ≈ 4 caracteres en inglés, 2 en español
        max_chars = max_tokens * 3  # Conservador para español/código
        if len(text) <= max_chars:
            return text

        # Truncar en punto lógico
        truncated = text[:max_chars]
        last_period = truncated.rfind(".")
        last_newline = truncated.rfind("\n")

        cutoff = max(last_period, last_newline)
        if cutoff > max_chars * 0.8:  # Si encontramos punto cercano
            return truncated[: cutoff + 1] + "\n\n[Contexto truncado por límites...]"

        return truncated + "\n\n[Contexto truncado por límites...]"

    def update_context(self, new_info: dict) -> None:
        """Actualiza contexto con nueva información."""
        update_file = self.project_path / ".ai-context-updates.yaml"

        current = (
            yaml.safe_load(update_file.read_text()) or {}
            if update_file.exists()
            else {}
        )

        # Mergear nueva información
        for key, value in new_info.items():
            if key in current:
                if isinstance(current[key], list) and isinstance(value, list):
                    current[key].extend(value)
                elif isinstance(current[key], dict) and isinstance(value, dict):
                    current[key].update(value)
                else:
                    current[key] = value
            else:
                current[key] = value

        # Guardar
        with open(update_file, "w", encoding="utf-8") as f:
            yaml.dump(current, f, allow_unicode=True)

        print(f"✅ Contexto actualizado en {update_file}")


# Uso del gestor de contexto
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print("Uso: python context_manager.py <proyecto> <tarea> [modelo]")
        print(
            "Ejemplo: python context_manager.py mi_proyecto 'optimizar función X' deepseek-coder"
        )
        sys.exit(1)

    manager = AIContextManager(sys.argv[1])
    task = sys.argv[2]
    model = sys.argv[3] if len(sys.argv) > 3 else "deepseek-coder"

    prompt = manager.create_optimized_prompt(task, model)

    print("=" * 80)
    print("PROMPT OPTIMIZADO GENERADO:")
    print("=" * 80)
    print(prompt)
    print("=" * 80)

    # Guardar prompt para uso
    output_file = Path(sys.argv[1]) / f"prompt_{model}_{int(time.time())}.txt"
    output_file.write_text(prompt, encoding="utf-8")
    print(f"📝 Prompt guardado en: {output_file}")
