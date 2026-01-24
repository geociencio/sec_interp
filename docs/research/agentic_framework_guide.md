# The Agentic Workflow Framework: Guía de Implementación y Replicación

**Fecha**: 2026-01-22
**Contexto**: Extraído del éxito en la implementación en `SecInterp` (QGIS Plugin).

---

## 1. Introducción: ¿Qué es el Agentic Workflow Framework?

Es una metodología de desarrollo asistida por IA que estructura el conocimiento del proyecto y los procesos operativos en tres componentes interconectados: **Agentes**, **Skills** y **Workflows**.

**Objetivo**: Transformar el prompt engineering ad-hoc en un sistema de ingeniería de contexto estructurado, permitiendo que cualquier LLM (Gemini, Claude, GPT) actúe como un especialista experto en el dominio específico del proyecto.

### ¿Por qué funciona?
1.  **Reducción de Alucinaciones**: La IA no adivina procesos; sigue workflows estrictos.
2.  **Contexto Especializado**: En lugar de cargar todo el contexto, se cargan "Skills" específicas bajo demanda.
3.  **Estandarización**: Todos los desarrolladores (y la IA) siguen los mismos pasos para commits, releases, y testing.

---

## 2. Arquitectura del Sistema

Para replicar este sistema en cualquier proyecto (Python, JS, Rust, etc.), necesitas crear esta estructura de directorios en la raíz de tu repositorio:

```bash
.agent/
├── AGENTS.md                    # El cerebro: Define roles y capacidades
├── skills/                      # El conocimiento: Módulos de "saber cómo"
│   ├── [skill-name]/
│   │   └── SKILL.md
│   └── ...
├── workflows/                   # El proceso: Guías paso a paso ejecutables
│   ├── [workflow-name].md
│   └── ...
└── scripts/                     # La automatización (Ops)
    └── skill_sync.py            # Validador y sincronizador
```

---

## 3. Guía de Implementación Paso a Paso

### Paso 1: Definir los Agentes (`AGENTS.md`)
Crea un archivo maestro que defina **QUIÉN** hace el trabajo.

**Ejemplo Genérico**:
```markdown
# Definición de Agentes

## Roles
- **Senior Architect**: Responsable de diseño, refactorización y decisiones estructurales.
- **QA Engineer**: Responsable de tests, pipelines y releases.
- **Frontend Specialist**: Responsable de UI/UX y tecnologías web.

## Matriz de Skills
| Skill | Trigger | Agente Principal |
|-------|---------|------------------|
| git-flow | commits, PRs | QA Engineer |
| backend-core | lógica de negocio | Senior Architect |
```

### Paso 2: Crear Skills Modulares (`skills/`)
Empaqueta el conocimiento técnico en unidades discretas. Cada skill debe tener un `SKILL.md` con frontmatter YAML.

**Estructura de `SKILL.md`**:
```yaml
---
name: [nombre-skill]
description: [breve descripción]
trigger: [palabras clave que activan esta skill]
---

# Título de la Skill

## Conocimiento Clave
...

## Checklists de Validación
...

## Comandos Frecuentes
...
```

**Skills Recomendadas para Empezar**:
1.  `commit-standards`: Convenciones de commmit (Conventional Commits).
2.  `tech-stack`: Reglas específicas del lenguaje/framework (ej: PEP8, React Hooks).
3.  `testing-standards`: Cómo correr y escribir tests en este proyecto.

### Paso 3: Diseñar Workflows Inteligentes (`workflows/`)
Documenta tus procesos repetitivos. La clave es añadir **Metadata** y **Agent Actions**.

**Formato de Workflow**:
```markdown
---
description: Cómo desplegar a producción
agent: DevOps Engineer
skills: [ci-cd, docker-expert]
validation:
  - Tests deben pasar en verde
  - Versión en package.json actualizada
---

# Proceso de Despliegue

1. Preparar el entorno
   🤖 **Agent Action**: Usar skill `ci-cd` para validar credenciales.

2. Ejecutar Tests
   ...
```

### Paso 4: Automatización (`skill_sync.py`)
Implementa un script simple que:
1.  Escanee la carpeta `workflows/`.
2.  Lea el frontmatter YAML.
3.  Valide que las `skills` referenciadas existan en `skills/`.
4.  Genere/Actualice `AGENTS.md` dinámicamente con una lista de capacidades disponibles.

---

## 4. Adaptación por Tipo de Proyecto

### 🌍 Proyecto QGIS Plugin (Caso Actual)
*   **Agentes**: GIS Specialist, Qt Developer.
*   **Skills**: `qgis-core` (PyQGIS API), `geo-algorithms`, `qt-ui`.
*   **Workflows**: `release-plugin` (subida a repositorio oficial), `run-tests-in-qgis` (testing visual).

### 🐍 Proyecto Python Genérico (Django/FastAPI)
*   **Agentes**: Backend Dev, API Designer.
*   **Skills**: `django-orm`, `rest-api-standards`, `celery-tasks`.
*   **Workflows**: `create-migration`, `deploy-heroku`, `api-docs-update`.

### 📊 Proyecto Data Science
*   **Agentes**: Data Scientist, ML Engineer.
*   **Skills**: `pandas-optimization`, `visualization-rules`, `model-versioning`.
*   **Workflows**: `train-model`, `clean-dataset`, `generate-report`.

---

## 5. Beneficios Tangibles

| Beneficio | Descripción |
|-----------|-------------|
| **Onboarding Instantáneo** | Un nuevo desarrollador (o IA) solo necesita leer `AGENTS.md` para entender qué puede hacer. |
| **Calidad Consistente** | Los checklists de validación en skills aseguran que "Done" signifique lo mismo siempre. |
| **Reducción de Errores** | Los workflows actúan como *checklists de vuelo* para procesos críticos. |
| **Contexto Eficiente** | No necesitas cargar 100 archivos en la ventana de contexto; el workflow te dice exactamente qué 3 archivos (skills) necesitas leer. |

---

## 6. Checklist de Replicación

Para llevar esto a tu próximo proyecto:

- [ ] Copiar directorio `.agent` base.
- [ ] Limpiar skills específicas del proyecto anterior.
- [ ] Crear skill `project-context` con reglas específicas del nuevo repo.
- [ ] Definir el workflow `/inicia-sesion` (es el más importante para empezar).
- [ ] Configurar el script de sincronización en el `pre-commit` o hook de inicio.

---

## 7. Uso Rápido con el Pack de Inicio

Para acelerar la adopción, hemos preparado un **Pack de Inicio ("Skeleton")** listo para usar.

### Contenido del Pack (`agentic_framework_skeleton.zip`)
- Estructura de directorios estándar (`.agent/`, `skills/`, `workflows/`, `scripts/`).
- Templates base para `AGENTS.md`, `SKILL.md` y `example-workflow.md`.
- Script de automatización `skill_sync.py` pre-configurado.

### Instrucciones de Instalación

1.  **Descargar**: Obtén el archivo `agentic_framework_skeleton.zip` (disponible en este repositorio).
2.  **Descomprimir**: Extrae el contenido en la raíz de tu nuevo proyecto.
    ```bash
    unzip agentic_framework_skeleton.zip
    mv agentic_framework_skeleton/* .
    mv agentic_framework_skeleton/.agent .
    rm -r agentic_framework_skeleton
    ```
3.  **Instalar Dependencias**: El script de sincronización requiere `PyYAML`.
    ```bash
    pip install pyyaml
    # O si usas uv:
    uv pip install pyyaml
    ```
4.  **Validar Instalación**: Ejecuta el script de sincronización para verificar que todo esté en su lugar.
    ```bash
    python3 .agent/scripts/skill_sync.py
    ```
    *Deberías ver un mensaje de éxito indicando que se han sincronizado 1 skill y 1 workflow.*

5.  **Personalizar**:
    - Edita `.agent/AGENTS.md` para tus roles.
    - Renombra la carpeta `.agent/skills/example-skill` a tu primera skill real (ej: `project-context`).
    - Crea tu primer workflow real en `.agent/workflows/`.

¡Listo! Tu proyecto ahora es "Agentic-Ready".
