# SecInterp: Framework Implementation & Sync Guide

> [!NOTE]
> **Summary (ES)**: Guía operativa para sincronizar el framework agéntico **Agentic Forge**
> (`agentic-forge`) que SecInterp consume como submódulo en `.agent/`, y para especializar el
> sistema con skills propias del proyecto (overlay en `.agent-state/`).

## 🧩 Modelo

- **Framework** — [`agentic-forge`](https://codeberg.org/geociencio/agentic-forge) (MIT),
  montado en **`.agent/`** como submódulo git. Contiene `skills/`, `workflows/`, `resources/`,
  `architecture/` y los docs del framework.
- **Estado del proyecto** — **`.agent-state/`** (memoria, tablero de tareas, `next_steps.md`,
  métricas) y el **overlay de skills** de proyecto en `.agent-state/skills/`. Nunca se versiona
  dentro del framework.
- **Contrato de rutas** — `forge.toml` (raíz) declara `[forge].framework` y `[forge].state`;
  `scripts/forge_paths.py` las resuelve.

## 🚀 Clonar / actualizar el submódulo

```bash
# Clonar el proyecto con el framework incluido
git clone --recurse-submodules git@github.com:geociencio/sec_interp.git

# Si ya clonaste sin submódulos
git submodule update --init --recursive

# Traer la última versión del framework
git submodule update --remote .agent
git add .agent && git commit -m "chore(agent): bump agentic-forge submodule"
```

> `git submodule update --remote .agent` fija el nuevo commit del framework en el `gitlink`.
> Siempre valida con `uv run python scripts/validate_agent_system.py` tras el bump.

## 🛠️ Especialización (skills del proyecto)

1. Añade la skill en **`.agent-state/skills/<nombre>/SKILL.md`** (overlay), no en `.agent/`.
2. Documenta sus triggers en el `SKILL.md`.
3. Valida: `uv run python scripts/validate_agent_system.py`.

El validador escanea **framework + overlay** (`skill_dirs()`), así que las skills de proyecto
participan en el grafo de workflows y en la detección de conflictos.

## 🧪 Comprobaciones habituales

```bash
uv run python scripts/validate_agent_system.py          # estructura + overlay
uv run python scripts/validate_agent_system.py --graph  # referencias
uv run python scripts/sync_metrics.py --validate        # coherencia de métricas
uv run python scripts/check_docs.py                     # consistencia de docs
```

---
*Agentic Forge framework — Gen 8. Updated 2026-10-04 (submodule model).*
