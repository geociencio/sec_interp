# Guía de Implementación Antigravity

Sigue estos pasos para activar la inteligencia agentica en cualquier repositorio nuevo.

## 1. Fase de Despegue (Scaffolding)

Ejecuta los siguientes comandos en la raíz de tu proyecto:

```bash
mkdir -p .agent/{skills,workflows,memory,resources}
```

## 2. Configuración de Roles

Crea `.agent/AGENTS.md`. Este archivo es el "cerebro" que decide qué skill activar ante cada tarea.

> [!TIP]
> Usa el [Template de AGENTS.md](file:///home/jmbernales/qgispluginsdev/sec_interp/docs/research/sistema_agent_ai/scaffold/AGENTS.md) disponible en este kit.

## 3. Instalación de Habilidades Base (Modularidad)

Copia los archivos del directorio `scaffold/skills/` a tu carpeta `.agent/skills/`. Según tu proyecto, elige el set adecuado:

### 📦 Set Universal (Cualquier proyecto Python)
- `coding-standards.md`: Forzar tipado, docstrings y buenas prácticas.
- `commit-standards.md`: Implementar Conventional Commits.
- `project-context.md`: El mapa de navegación para la IA.

### 🌍 Set QGIS/Spatial (Plugins)
- `qgis-core.md`: Conocimiento de la API de QGIS y asincronía.
- `ui-framework.md`: Estándares de creación de widgets programáticos.

## 4. Activación de Workflows (Rieles de Calidad)

Los flujos en `.agent/workflows/` guían al agente. Los tres pilares son:

| Workflow | Propósito | Cuándo usar |
| :--- | :--- | :--- |
| `inicia-sesion` | Carga el contexto y valida el entorno | Al empezar a trabajar |
| `cierra-sesion` | Documenta logros y limpia el repo | Antes de desconectarse |
| `run-tests` | Verificación técnica de estabilidad | Antes de cada commit |

## 5. Adaptación por Tipo de Proyecto

### 🐍 Python Genérico (Django/FastAPI)
- **Agentes**: Backend Dev, API Designer.
- **Skills**: `django-orm`, `rest-api-standards`.
- **Workflows**: `create-migration`, `deploy-cloud`.

### 📊 Data Science
- **Agentes**: Data Scientist, ML Engineer.
- **Skills**: `pandas-opt`, `model-versioning`.
- **Workflows**: `clean-dataset`, `generate-report`.

### 🌍 QGIS Plugin
- **Agentes**: GIS Architect, Plugin Specialist.
- **Skills**: `qgis-core`, `geo-algorithms`.
- **Workflows**: `release-plugin`, `mocking-reference`.

## 6. Checklist de Replicación Estratégica

- [ ] Crear estructura base `.agent/`.
- [ ] Definir skill `project-context` (Es el alma del proyecto).
- [ ] Implementar `/inicia-sesion` (Garantiza que la IA sepa dónde está).
- [ ] Inicializar `memory/AGENT_LESSONS.md` (Para que la IA aprenda de ti).

---
*¡Felicidades! Has activado la conciencia operativa de tu proyecto.*
