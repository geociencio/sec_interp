# Procedimiento de Bootstrap Antigravity

Sigue estos pasos para convertir un repositorio "mudo" en un proyecto "Agent-Native" en menos de 5 minutos.

## Paso 1: Clonar el Corazon
Copia la carpeta `.agent/` base o créala:
```bash
mkdir -p .agent/{skills,workflows,memory,resources}
```

## Paso 2: Inyectar Muebles (Templates)
Copia los archivos del kit de investigación (`docs/research/sistema_agent_ai/scaffold/`) a tu nueva carpeta `.agent/`:
```bash
cp scaffold/AGENTS.md .agent/
cp scaffold/skills/*.md .agent/skills/
cp scaffold/workflows/*.md .agent/workflows/
```

## Paso 3: Definir el Contexto (Vital)
Crea `.agent/skills/project-context.md` y describe el propósito de TU proyecto. Sin esto, el asistente será genérico.

## Paso 4: Inicializar Memoria
Crea un archivo vacío o con una estructura básica en `.agent/memory/AGENT_LESSONS.md`. Explícale a la IA en tu primer mensaje:
> "He implementado el Framework Antigravity. A partir de ahora, cualquier preferencia o solución compleja que discutamos debe guardarse en nuestra memoria de lecciones."

## Paso 5: Primera Sincronización
Pide al asistente que analice el nuevo entorno:
> "He implementado el Framework Antigravity. Lee .agent/AGENTS.md y mis nuevos skills. Confirma que entiendes tu rol y que el proyecto está Agentic-Ready."

---
*¡Felicidades! Has activado la conciencia de equipo en tu repositorio.*
