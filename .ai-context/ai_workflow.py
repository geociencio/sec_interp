#!/usr/bin/env python3
"""ai_workflow.py - Workflow optimizado para desarrollo con IA."""

import json
import os
import time
import unicodedata
from datetime import datetime
from pathlib import Path

import yaml


class AIWorkflowManager:
    """Gestiona workflow completo con IA."""

    def __init__(self, project_root: str):
        self.root = Path(project_root)
        self.context_dir = self.root / ".ai-context"
        self._ensure_structure()

        # Estado actual
        self.session_id = f"session_{int(time.time())}"
        self.current_task = None
        self.token_usage = 0

    def _ensure_structure(self):
        """Crea estructura de directorios necesaria."""
        dirs = [
            self.context_dir,
            self.context_dir / "sessions",
            self.context_dir / "workflows",
            self.context_dir / "templates",
            self.context_dir / "cache",
        ]

        for dir_path in dirs:
            dir_path.mkdir(exist_ok=True)

        # Archivos esenciales
        essential_files = {
            "project_brain.md": self._default_brain_template(),
            "tech_stack.yaml": self._default_tech_stack(),
            "decisions_log.md": "# Registro de Decisiones\n\n",
            "context_cheatsheet.md": self._cheatsheet_template(),
        }

        for filename, content in essential_files.items():
            filepath = self.context_dir / filename
            if not filepath.exists():
                filepath.write_text(content, encoding="utf-8")

    def start_session(self, task_type: str, description: str) -> str:
        """Inicia una nueva sesión de trabajo con IA."""
        session_dir = self.context_dir / "sessions" / f"{self.session_id}_{task_type}"
        session_dir.mkdir(exist_ok=True)

        # Configurar sesión
        session_info = {
            "id": self.session_id,
            "type": task_type,
            "description": description,
            "start_time": datetime.now().isoformat(),
            "status": "active",
            "files_involved": [],
            "prompts_sent": 0,
            "responses_received": 0,
        }

        # Guardar info
        with open(session_dir / "session_info.yaml", "w") as f:
            yaml.dump(session_info, f)

        # Inicializar log
        with open(session_dir / "work_log.md", "w") as f:
            f.write(f"# Sesión: {task_type}\n")
            f.write(f"**Descripción**: {description}\n")
            f.write(f"**Inicio**: {datetime.now()}\n\n")
            f.write("## Progreso\n\n")

        self.current_task = task_type
        print(f"🚀 Sesión iniciada: {self.session_id}")
        print(f"📝 Tarea: {description}")
        print(f"📁 Directorio: {session_dir}")

        return self.session_id

    def generate_optimized_prompt(
        self,
        task_description: str,
        ai_model: str = "deepseek-coder",
        context_level: str = "normal",
    ) -> dict:
        """Genera prompt optimizado basado en contexto."""
        # Cargar contexto relevante
        context = self._load_relevant_context(task_description, context_level)

        # Seleccionar template según modelo
        template = self._select_template(ai_model, self.current_task)

        # Construir prompt
        prompt_data = {
            "system": template["system"].format(
                project_name=self.root.name, **context.get("project_info", {})
            ),
            "user": template["user"].format(
                task=task_description,
                context=self._truncate_to_tokens(context["relevant_context"], 2000),
                constraints=context["constraints"],
                project_name=self.root.name,
            ),
            "meta": {
                "model": ai_model,
                "session_id": self.session_id,
                "task_type": self.current_task,
                "estimated_tokens": self._estimate_tokens(task_description + str(context)),
                "timestamp": datetime.now().isoformat(),
            },
        }

        # Guardar prompt
        prompt_file = (
            self.context_dir
            / "sessions"
            / f"{self.session_id}_{self.current_task}"
            / f"prompt_{int(time.time())}.json"
        )

        # Asegurar que el directorio existe
        prompt_file.parent.mkdir(parents=True, exist_ok=True)

        with open(prompt_file, "w") as f:
            json.dump(prompt_data, f, indent=2, ensure_ascii=False)

        # Actualizar log
        self._log_action(
            "prompt_generated",
            {
                "file": str(prompt_file),
                "model": ai_model,
                "task": (
                    task_description[:100] + "..."
                    if len(task_description) > 100
                    else task_description
                ),
            },
        )

        return prompt_data

    def _load_relevant_context(self, task: str, level: str = "normal") -> dict:
        """Carga contexto relevante para la tarea."""
        # Extraer keywords
        keywords = self._extract_keywords(task)

        # Niveles de contexto
        if level == "minimal":
            return self._load_minimal_context(keywords)
        elif level == "deep":
            return self._load_deep_context(keywords)
        else:  # normal
            return self._load_normal_context(keywords)

    def _load_normal_context(self, keywords: list[str]) -> dict:
        """Carga contexto normal."""
        context = {
            "project_info": {},
            "relevant_context": "",
            "constraints": "",
            "examples": [],
        }

        # Leer archivos de contexto
        context_files = {
            "project_brain.md": "general",
            "tech_stack.yaml": "technical",
            "decisions_log.md": "decisions",
            "context_cheatsheet.md": "cheatsheet",
        }

        # Archivos generados por ProjectAnalyzer (en la raíz)
        analyzer_files = {"AI_CONTEXT.md": "analyzer_findings"}

        relevant_parts = []

        # 1. Archivos en .ai-context
        for file, category in context_files.items():
            filepath = self.context_dir / file
            if filepath.exists():
                content = filepath.read_text(encoding="utf-8")
                # Forzar inclusión parcial de cerebro y stack técnico
                force_include = category in ["general", "technical"]
                self._add_if_relevant(
                    content, category, keywords, relevant_parts, force=force_include
                )

                if category == "technical":
                    context["project_info"] = yaml.safe_load(content) or {}

        # 2. Archivos en el root (ProjectAnalyzer)
        for file, category in analyzer_files.items():
            filepath = self.root / file
            if filepath.exists():
                content = filepath.read_text(encoding="utf-8")
                self._add_if_relevant(content, category, keywords, relevant_parts)

        context["relevant_context"] = "\n\n".join(relevant_parts) or "Sin contexto específico"

        # Añadir restricciones comunes
        context["constraints"] = self._get_constraints()

        return context

    def _normalize(self, text: str) -> str:
        """Normaliza texto eliminando acentos y convirtiendo a minúsculas."""
        if not text:
            return ""
        text = text.lower()
        # Eliminar acentos
        text = "".join(
            c for c in unicodedata.normalize("NFD", text) if unicodedata.category(c) != "Mn"
        )
        return text

    def _add_if_relevant(
        self,
        content: str,
        category: str,
        keywords: list[str],
        parts: list[str],
        force: bool = False,
    ):
        """Añade contenido a las partes relevantes si coincide con keywords."""
        norm_content = self._normalize(content)

        is_relevant = force
        if not is_relevant and keywords:
            for kw in keywords:
                if self._normalize(kw) in norm_content:
                    is_relevant = True
                    break

        if is_relevant or not keywords:
            parts.append(
                f"## {category.upper()}\n{content[:2000]}"
            )  # Aumentado a 2000 para capturar más contexto

    def _get_constraints(self) -> str:
        """Obtiene restricciones del proyecto."""
        constraints = [
            "Python 3.8+ compatible",
            "Mantener retrocompatibilidad donde sea posible",
            "Seguir PEP 8",
            "Añadir type hints",
            "Incluir docstrings",
            "Manejar errores apropiadamente",
        ]

        # Añadir restricciones específicas del proyecto
        constraints_file = self.context_dir / "constraints.yaml"
        if constraints_file.exists():
            with open(constraints_file) as f:
                custom = yaml.safe_load(f) or []
                constraints.extend(custom.get("constraints", []))

        return "\n".join(f"- {c}" for c in constraints)

    def _select_template(self, model: str, task_type: str) -> dict:
        """Selecciona template según modelo y tipo de tarea."""
        # 1. Intentar cargar template personalizado desde archivo
        templates_dir = self.context_dir / "templates"
        model_clean = model.lower().replace("/", "_").replace("-", "_")
        task_clean = task_type.lower().replace(" ", "_")
        specific_template = templates_dir / f"{model_clean}_{task_clean}.yaml"
        if specific_template.exists():
            with open(specific_template) as f:
                return yaml.safe_load(f)
        if "gemini-3-pro" in model_lower or "gemini 3 pro" in model_lower:
            return self._gemini_3_pro_template()
        elif "claude-sonnet-4.5" in model_lower or "sonnet 4.5" in model_lower:
            return self._claude_sonnet_45_template()
        elif (
            "gpt-oss-120b" in model_lower
            or "oss-120b" in model_lower
            or "llama-3-120b" in model_lower
        ):
            return self._gpt_oss_120b_template()

        # 2. Si no hay archivo, usar templates integrados
        elif "deepseek" in model.lower():
            return self._deepseek_template()
        elif "gpt" in model.lower() or "openai" in model.lower():
            return self._chatgpt_template()
        elif "claude" in model.lower() or "anthropic" in model.lower():
            return self._claude_template()
        elif "gemini" in model.lower() or "google" in model.lower():
            return self._gemini_template()

        # 3. Fallback genérico
        return self._default_template(model)

    def _qwen_cli_template(self) -> dict:
        """Prompt template ajustado al estilo de Qwen (usado con qwen-cli)."""
        return {
            "system": (
                "You are Qwen, an expert Python developer. "
                "Respond with working code, type hints, and minimal explanation. "
                "Assume the user will copy your output directly into their project."
            ),
            "user": (
                "[Project: {project_name}]\n"
                "[Task: {task}]\n\n"
                "[Relevant Context]\n{context}\n\n"
                "[Constraints]\n{constraints}\n\n"
                "Instructions:\n"
                "- Provide only the solution: code or concise steps.\n"
                "- Use modern Python (3.10+), TypedDict, pathlib, etc.\n"
                "- Include Google-style docstrings if writing functions.\n"
                "- Never wrap code in ```markdown fences.\n"
                "- Do not add introductions like 'Sure!' or 'Here is...'\n"
                "- If uncertain, make one clear assumption and state it in a comment."
            ),
        }

    def _deepseek_template(self) -> dict:
        """Template optimizado para DeepSeek."""
        return {
            "system": """Eres un experto en Python analizando el proyecto: {project_name}.
            Objetivos:
            1. Código práctico y eficiente
            2. Optimizaciones de performance
            3. Compatibilidad con Python 3.8+
            4. Ejemplos específicos""",
            "user": """## TAREA
            {task}

            ## CONTEXTO
            {context}

            ## RESTRICCIONES
            {constraints}

            ## INSTRUCCIONES DEEPSEEK:
            Por favor responde con este formato JSON/Markdown:
            ```analysis
            [Análisis breve]
            suggestions
            [Lista de sugerencias]
            code_examples
            [Código si aplica]
            next_steps
            [Pasos a seguir]
            ```""",
        }

    def _chatgpt_template(self) -> dict:
        """Template optimizado para ChatGPT."""
        return {
            "system": "Actúa como un Ingeniero de Software Senior especializado en Python y arquitecturas escalables.",
            "user": """Estás trabajando en el proyecto '{project_name}'.
            Tarea: {task}

            Contexto relevante:
            {context}

            Restricciones:
            {constraints}

            Por favor, provee una solución detallada, explicando el 'por qué' de tus decisiones. Si sugieres código, asegúrate de que sea robusto y maneje excepciones.""",
        }

    def _claude_template(self) -> dict:
        """Template optimizado para Claude."""
        return {
            "system": "Eres Claude, un asistente de IA experto en desarrollo de software, análisis de código y redacción técnica.",
            "user": """Por favor ayuda con la siguiente tarea en el proyecto '{project_name}'.
            Tarea: {task}

            Aquí está el contexto del proyecto:
            {context}

            Y las restricciones técnicas:
            {constraints}

            Analiza la situación paso a paso. Si encuentras ambigüedades, haz preguntas aclaratorias antes de sugerir código.""",
        }

    def _gemini_3_pro_template(self) -> dict:
        """Template optimizado para Google Gemini 3 Pro."""
        return {
            "system": (
                "Eres un ingeniero senior de Google con 10+ años en Python, arquitectura de software y sistemas geoespaciales (QGIS). "
                "Tu rol es asistir a desarrolladores con soluciones técnicamente sólidas, seguras y mantenibles. "
                "Prioriza claridad, eficiencia y principios SOLID. No asumas; razona explícitamente."
            ),
            "user": (
                "## 🧠 Tarea para '{project_name}'\n{task}\n\n"
                "## 📚 Contexto técnico relevante (extraído de análisis estático y cerebro del proyecto)\n"
                "{context}\n\n"
                "## ⚠️ Restricciones del proyecto\n{constraints}\n\n"
                "## 📌 Instrucciones específicas para GEMINI 3 Pro:\n"
                "- Utiliza tu ventana de contexto extendida (1M+ tokens) para integrar todo el contexto disponible.\n"
                "- Proporciona una explicación técnica breve **antes** de cualquier bloque de código.\n"
                "- El código debe incluir: type hints, docstrings (Google style), y manejo de errores.\n"
                "- Si identificas riesgo de seguridad o de rendimiento, menciónalo explícitamente.\n"
                "- Si la tarea involucra refactorización, muestra **código antes / después** y explica el 'por qué'.\n"
                "- Sé conciso, pero no omitas justificaciones técnicas importantes."
            ),
        }

    def _claude_sonnet_45_template(self) -> dict:
        """Template optimizado para Claude Sonnet 4.5."""
        return {
            "system": (
                "Eres Claude Sonnet 4.5, un asistente de desarrollo altamente confiable, especializado en Python, patrones de diseño y código legado. "
                "Tu prioridad es ayudar a los desarrolladores a tomar decisiones sostenibles, seguras y bien fundamentadas. "
                "Razona paso a paso. Si algo no está claro, pide clarificación antes de proponer soluciones."
            ),
            "user": (
                "<project>{project_name}</project>\n"
                "<task>{task}</task>\n"
                "<context>\n{context}\n</context>\n"
                "<constraints>\n{constraints}\n</constraints>\n\n"
                "Responde **estrictamente** en el siguiente formato XML-like:\n"
                "<analysis>\n[Análisis técnico breve, incluyendo suposiciones si las hay]\n</analysis>\n"
                "<recommendations>\n- ...\n</recommendations>\n"
                "<code_examples>\n<![CDATA[\n# Código listo para usar\n]]>\n</code_examples>\n"
                "<risks>\n- ...\n</risks>\n"
                "<clarification_questions>\n- ¿...?</clarification_questions>"
            ),
        }

    def _gpt_oss_120b_template(self) -> dict:
        """Template optimizado para GPT OSS 120B (Llama-3-120B, CodeLlama-120B, etc.)."""
        return {
            "system": (
                "You are a pragmatic Python expert. Respond with minimal explanation and maximum utility. "
                "Assume the user will copy your code directly. Avoid markdown unless necessary. "
                "Be concise, precise, and focused on working solutions."
            ),
            "user": (
                "Project: {project_name}\n"
                "Task: {task}\n"
                "Relevant context (keep short):\n{context}\n"
                "Constraints:\n{constraints}\n\n"
                "Instructions for GPT OSS 120B:\n"
                "- Return only code if the task is implementation.\n"
                "- If explanation is needed, keep it under 3 sentences.\n"
                "- Never ask questions—make best-effort assumptions.\n"
                "- Use modern Python (3.8+), type hints, and error handling.\n"
                "- Do not use XML, JSON, or extra formatting unless explicitly requested."
            ),
        }

    def _gemini_template(self) -> dict:
        """Template optimizado para Google Gemini."""
        return {
            "system": "Eres un experto ingeniero de software de Google, especializado en Python y QGIS.",
            "user": """Analiza la siguiente tarea para el proyecto '{project_name}'.

            Tarea: {task}

            Contexto Técnico:
            {context}

            Restricciones:
            {constraints}

            Instrucciones para Gemini:
            1. Utiliza tu capacidad de razonamiento multimodal y lógico para ofrecer la mejor solución.
            2. Si se requiere código, que sea limpio, moderno y bien documentado.
            3. Explica tus decisiones de diseño.
            4. Identifica posibles problemas de seguridad o rendimiento.""",
        }

    def _default_template(self, model: str) -> dict:
        """Template genérico para otras IAs."""
        return {
            "system": "Eres un asistente experto en desarrollo Python.",
            "user": "Tarea: {task}\n\nContexto: {context}\n\nRestricciones: {constraints}",
        }

    def _truncate_to_tokens(self, text: str, max_tokens: int = 4000) -> str:
        """Trunca texto aproximando tokens de forma inteligente."""
        # Estimación: 1 token ≈ 4 caracteres
        max_chars = max_tokens * 4
        if len(text) <= max_chars:
            return text

        # Truncar intentando no cortar frases
        truncated = text[:max_chars]
        last_period = truncated.rfind(".")
        last_newline = truncated.rfind("\n")

        cutoff = max(last_period, last_newline)
        if cutoff > max_chars * 0.8:
            return truncated[: cutoff + 1] + "\n\n[...Contexto truncado...]"

        return truncated + "\n\n[...Contexto truncado...]"

    def process_ai_response(self, response: str, prompt_meta: dict) -> dict:
        """Procesa y guarda respuesta de IA."""
        session_dir = self.context_dir / "sessions" / f"{self.session_id}_{self.current_task}"

        # Extraer secciones estructuradas
        parsed_response = self._parse_structured_response(response)

        # Guardar respuesta completa
        response_file = session_dir / f"response_{int(time.time())}.md"
        response_file.write_text(response, encoding="utf-8")

        # Guardar versión estructurada
        structured_file = session_dir / "response_structured.json"
        with open(structured_file, "w") as f:
            json.dump(parsed_response, f, indent=2, ensure_ascii=False)

        # Extraer acciones concretas
        actions = self._extract_actions(parsed_response)

        # Actualizar contexto del proyecto si es necesario
        if actions.get("context_updates"):
            self._update_project_brain(actions["context_updates"])

        # Actualizar log
        self._log_action(
            "response_received",
            {
                "file": str(response_file),
                "has_code": len(actions.get("code_suggestions", [])) > 0,
                "actions_identified": len(actions.get("actions", [])),
            },
        )

        return {
            "parsed": parsed_response,
            "actions": actions,
            "files": {"full": str(response_file), "structured": str(structured_file)},
        }

    def _parse_structured_response(self, response: str) -> dict:
        """Parsea respuesta estructurada de IA."""
        sections = {
            "analysis": "",
            "suggestions": [],
            "code_examples": [],
            "next_steps": [],
            "warnings": [],
            "questions": [],
        }

        # Patrones comunes
        import re

        # Buscar secciones con backticks
        pattern = r"```(\w+)\n(.*?)```"
        matches = re.findall(pattern, response, re.DOTALL)

        for section, content in matches:
            section = section.lower()
            if section in sections:
                if isinstance(sections[section], list):
                    # Dividir en items si es lista
                    items = [item.strip() for item in content.split("\n") if item.strip()]
                    sections[section] = items
                else:
                    sections[section] = content.strip()

        # Si no encuentra secciones estructuradas, analizar texto libre
        if not any(sections.values()):
            sections["analysis"] = response[:1500]

            # Intentar extraer sugerencias automáticamente
            suggestions = []
            lines = response.split("\n")
            for line in lines:
                if line.strip().startswith(("-", "*", "•", "1.", "2.", "3.")):
                    suggestions.append(line.strip())

            if suggestions:
                sections["suggestions"] = suggestions[:10]

        return sections

    def _extract_actions(self, parsed_response: dict) -> dict:
        """Extrae acciones concretas de la respuesta."""
        actions = {
            "code_changes": [],
            "refactors": [],
            "tests_needed": [],
            "context_updates": {},
            "questions_to_ask": [],
        }

        # Analizar sugerencias
        for suggestion in parsed_response.get("suggestions", []):
            suggestion_lower = suggestion.lower()

            # Clasificar sugerencias
            if any(word in suggestion_lower for word in ["refactor", "rewrite", "reorganize"]):
                actions["refactors"].append(suggestion)
            elif any(
                word in suggestion_lower for word in ["add test", "write test", "test coverage"]
            ):
                actions["tests_needed"].append(suggestion)
            elif any(
                word in suggestion_lower for word in ["change", "modify", "update", "implement"]
            ):
                actions["code_changes"].append(suggestion)

        # Extraer preguntas para clarificar
        if "questions" in parsed_response:
            actions["questions_to_ask"] = parsed_response["questions"]

        # Identificar actualizaciones de contexto
        if "architecture" in parsed_response.get("analysis", "").lower():
            actions["context_updates"]["architecture_notes"] = parsed_response["analysis"][:500]

        return actions

    def _update_project_brain(self, updates: dict):
        """Actualiza el 'cerebro' del proyecto."""
        brain_file = self.context_dir / "project_brain.md"

        if brain_file.exists():
            content = brain_file.read_text(encoding="utf-8")

            # Añadir sección de actualizaciones
            update_section = f"\n\n## Actualización {datetime.now().date()}\n"
            for key, value in updates.items():
                update_section += f"\n### {key}\n{value}\n"

            # Mantener tamaño razonable (últimas 20 actualizaciones)
            sections = content.split("## Actualización")
            if len(sections) > 20:
                content = "## Actualización".join(sections[:1] + sections[-19:])

            brain_file.write_text(content + update_section, encoding="utf-8")

    def _log_action(self, action_type: str, data: dict):
        """Registra acción en el log."""
        log_file = (
            self.context_dir / "sessions" / f"{self.session_id}_{self.current_task}" / "work_log.md"
        )

        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"\n### {datetime.now().strftime('%H:%M:%S')} - {action_type}\n")
            for key, value in data.items():
                f.write(f"- **{key}**: {value}\n")

    def end_session(self, success: bool = True, summary: str = ""):
        """Finaliza la sesión actual."""
        session_dir = self.context_dir / "sessions" / f"{self.session_id}_{self.current_task}"

        # Actualizar info de sesión
        info_file = session_dir / "session_info.yaml"
        if info_file.exists():
            with open(info_file) as f:
                info = yaml.safe_load(f)

            info["end_time"] = datetime.now().isoformat()
            info["status"] = "completed" if success else "failed"
            info["summary"] = summary

            with open(info_file, "w") as f:
                yaml.dump(info, f)

        # Generar resumen ejecutivo
        self._generate_session_summary(session_dir, success, summary)

        print(f"\n✅ Sesión finalizada: {self.session_id}")
        print(f"📊 Resumen: {summary[:100]}...")
        print(f"📁 Detalles en: {session_dir}")

        self.current_task = None

    def _generate_session_summary(self, session_dir: Path, success: bool, summary: str):
        """Genera resumen de la sesión."""
        summary_file = session_dir / "session_summary.md"

        # Contar archivos generados
        prompt_files = list(session_dir.glob("prompt_*.json"))
        response_files = list(session_dir.glob("response_*.md"))

        with open(summary_file, "w", encoding="utf-8") as f:
            f.write("# Resumen de Sesión\n\n")
            f.write(f"**ID**: {self.session_id}\n")
            f.write(f"**Tipo**: {self.current_task}\n")
            f.write(f"**Estado**: {'✅ Completado' if success else '❌ Fallido'}\n")
            f.write(f"**Duración**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            f.write(f"## Resumen Ejecutivo\n\n{summary}\n\n")

            f.write("## Métricas\n\n")
            f.write(f"- Prompts generados: {len(prompt_files)}\n")
            f.write(f"- Respuestas recibidas: {len(response_files)}\n")

            # Listar archivos
            f.write("\n## Archivos Generados\n\n")
            for file in prompt_files + response_files:
                f.write(f"- {file.name}\n")

            f.write("\n## Próximos Pasos\n\n")
            f.write("1. Revisar código sugerido\n")
            f.write("2. Aplicar cambios seleccionados\n")
            f.write("3. Actualizar documentación\n")
            f.write("4. Ejecutar tests\n")

    def _default_brain_template(self) -> str:
        """Template para el cerebro del proyecto."""
        return f"""# Cerebro del Proyecto: {self.root.name}

## Visión General
[Descripción breve del propósito del proyecto]

## Arquitectura Principal
[Patrones, componentes principales, flujo de datos]

## Decisiones Clave
1. [Decisión importante 1]
2. [Decisión importante 2]

## Supuestos
- [Supuesto 1]
- [Supuesto 2]

## Dependencias Críticas
- Internas: [ ]
- Externas: [ ]

## Restricciones Conocidas
1. [Restricción 1]
2. [Restricción 2]

## Patrones de Código Comunes
[Ejemplos de patrones repetidos]

## Lecciones Aprendidas
[Errores comunes, soluciones efectivas]

## Estado Actual
[Qué funciona, qué necesita atención]
"""

    def _default_tech_stack(self) -> str:
        """Template para tech stack."""
        return """# Stack Tecnológico

## Python
version: "3.8+"
type_checking: true
async_support: false

## Principales Dependencias
- framework: null
- database: null
- testing: pytest
- docs: null

## Herramientas de Desarrollo
- formatter: black
- linter: ruff
- package_manager: pip

## Convenciones
code_style: "pep8"
docstring_format: "google"
import_order: "standard"
"""

    def _cheatsheet_template(self) -> str:
        """Template para cheatsheet."""
        return """# Cheatsheet de Contexto

## Comandos Comunes
[Comandos específicos del proyecto]

## Estructuras de Datos Clave
[Estructuras importantes y su propósito]

## Funciones Útiles
[Funciones helper frecuentemente usadas]

## Configuraciones Importantes
[Configs que afectan comportamiento]

## Atajos Mentales
[Reglas heurísticas para el proyecto]
"""

    def _extract_keywords(self, text: str) -> list[str]:
        """Extrae palabras clave."""
        # Limpiar puntuación básica
        for char in ".,;:()[]{}?!\"'":
            text = text.replace(char, " ")

        words = text.lower().split()
        stopwords = {
            "el",
            "la",
            "los",
            "las",
            "de",
            "en",
            "y",
            "o",
            "a",
            "para",
            "con",
            "que",
            "es",
            "un",
            "una",
            "del",
            "al",
        }
        return [w for w in words if w not in stopwords and len(w) > 3]

    def _estimate_tokens(self, text: str) -> int:
        """Estima tokens en texto."""
        # Aproximación simple: 1 token ≈ 4 caracteres para inglés
        return len(text) // 4


# ============================================================================
# WORKFLOW COMPLETO DE EJEMPLO
# ============================================================================


def example_workflow():
    """Ejemplo completo de workflow."""
    print("=" * 60)
    print("WORKFLOW OPTIMIZADO PARA IA - DEMOSTRACIÓN")
    print("=" * 60)

    # 1. Inicializar manager
    manager = AIWorkflowManager(".")

    # 2. Iniciar sesión para refactorización
    manager.start_session(
        task_type="refactor",
        description="Refactorizar módulo de procesamiento de datos para mejorar performance",
    )

    # 3. Generar prompt optimizado
    prompt_data = manager.generate_optimized_prompt(
        task_description="""
Necesito optimizar la función `process_large_dataset` en `data_processor.py`.
Actualmente tarda 30 segundos en procesar 100MB de datos.
Restricciones:
- No puedo cambiar la interfaz pública
- Debo mantener compatibilidad con formatos existentes
- El dataset puede crecer hasta 1GB
        """,
        ai_model="deepseek-coder",
        context_level="normal",
    )

    print("\n📤 PROMPT GENERADO:")
    print("-" * 40)
    print(f"System: {prompt_data['system'][:200]}...")
    print(f"User: {prompt_data['user'][:300]}...")

    # 4. [SIMULACIÓN] Procesar respuesta de IA
    print("\n⏳ Simulando respuesta de IA...")
    time.sleep(1)

    simulated_response = """
```analysis
La función actual usa procesamiento en memoria completa. Para datasets grandes (>100MB), esto causa problemas de memoria y performance.
suggestions
1. Implementar procesamiento por chunks usando pandas.read_csv con chunksize
2. Usar dtypes específicos para reducir uso de memoria
3. Aplicar vectorización en lugar de loops Python
4. Considerar usar modin.pandas para paralelización
code_examples
# Versión optimizada
def process_large_dataset_optimized(filepath, chunk_size=10000):
    import pandas as pd

    results = []
    for chunk in pd.read_csv(filepath, chunksize=chunk_size,
                             dtype={'col1': 'int32', 'col2': 'float32'}):
        # Procesamiento vectorizado
        chunk['processed'] = chunk['col1'] * chunk['col2']
        results.append(chunk)

    return pd.concat(results, ignore_index=True)
next_steps
1. Alta prioridad: Implementar procesamiento por chunks
2. Media prioridad: Optimizar dtypes
3. Baja prioridad: Evaluar modin.pandas
"""
    # 5. Procesar respuesta
    result = manager.process_ai_response(simulated_response, prompt_data["meta"])

    print("\n✅ RESPUESTA PROCESADA:")
    print("-" * 40)
    print(f"Acciones identificadas: {len(result['actions']['code_changes'])}")
    print(f"Archivos guardados: {result['files']['full']}")

    # 6. Finalizar sesión
    manager.end_session(
        success=True,
        summary="Recibidas sugerencias para optimizar procesamiento de datos grandes. Listo para implementar.",
    )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="AI Workflow Manager CLI")
    subparsers = parser.add_subparsers(dest="command", help="Comandos disponibles")

    # Comando: init
    init_parser = subparsers.add_parser("init", help="Inicializar estructura del proyecto")
    init_parser.add_argument("--root", default=".", help="Raíz del proyecto")

    # Comando: start
    start_parser = subparsers.add_parser("start", help="Iniciar nueva sesión")
    start_parser.add_argument("type", help="Tipo de tarea (refactor, feature, bugfix, etc)")
    start_parser.add_argument("description", help="Descripción breve de la tarea")

    # Comando: prompt
    prompt_parser = subparsers.add_parser("prompt", help="Generar prompt para la sesión actual")
    prompt_parser.add_argument("description", help="Descripción detallada de la tarea")
    prompt_parser.add_argument("--model", default="deepseek-coder", help="Modelo de IA a usar")

    # Comando: example
    example_parser = subparsers.add_parser("example", help="Ejecutar workflow de ejemplo")

    args = parser.parse_args()

    current_dir = os.getcwd()
    manager = AIWorkflowManager(current_dir)

    if args.command == "init":
        manager._ensure_structure()
        print(f"✅ Estructura .ai-context inicializada en {manager.context_dir}")

    elif args.command == "start":
        session_id = manager.start_session(args.type, args.description)
        # Guardar ID de sesión actual para uso futuro (simple implementacion en archivo)
        (manager.context_dir / "current_session.txt").write_text(session_id)
        print(f"✅ Sesión iniciada: {session_id}")

    elif args.command == "prompt":
        # Intentar recuperar sesión actual
        session_file = manager.context_dir / "current_session.txt"
        if session_file.exists():
            manager.session_id = session_file.read_text().strip()
            # Asumir tipo de tarea basado en el nombre de la sesión o default
            # Para simplificar, usamos el que está en el nombre del directorio de sesión si es posible
            # o simplemente leemos el session_info.yaml
            # Implementación rápida:
            sessions_dir = manager.context_dir / "sessions"
            for p in sessions_dir.glob(f"{manager.session_id}_*"):
                if p.is_dir():
                    manager.current_task = p.name.split("_", 2)[2]  # session_timestamp_tasktype
                    break

        if not manager.current_task:
            manager.current_task = "general"

        prompt = manager.generate_optimized_prompt(args.description, ai_model=args.model)
        print(f"✅ Prompt generado en: sessions/{manager.session_id}_{manager.current_task}/")
        print("📋 Copia el contenido del archivo JSON generado para tu IA.")

    elif args.command == "example":
        example_workflow()

    else:
        parser.print_help()
