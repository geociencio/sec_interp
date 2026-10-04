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
  `.agent/tools/forge_paths.py` las resuelve.

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
> Siempre valida con `uv run python .agent/tools/forge.py validate` tras el bump.

## 🛠️ Especialización (skills del proyecto)

1. Añade la skill en **`.agent-state/skills/<nombre>/SKILL.md`** (overlay), no en `.agent/`.
2. Documenta sus triggers en el `SKILL.md`.
3. Valida: `uv run python .agent/tools/forge.py validate`.

El validador escanea **framework + overlay** (`skill_dirs()`), así que las skills de proyecto
participan en el grafo de workflows y en la detección de conflictos.

## 🧪 Comprobaciones habituales

```bash
uv run python .agent/tools/forge.py validate          # estructura + overlay
uv run python .agent/tools/forge.py validate --graph  # referencias
uv run python scripts/sync_metrics.py --validate        # coherencia de métricas
uv run python scripts/check_docs.py                     # consistencia de docs
```

## 🏛️ Gobernanza del framework

- **Fuente de verdad**: el repo [`agentic-forge`](https://codeberg.org/geociencio/agentic-forge)
  (público, MIT). SecInterp solo consume y fija una revisión.
- **Cambios genéricos** (skills/workflows/tooling del framework): se hacen **en el repo del
  framework** (o en `.agent/` y se empuja), con su commit/tag, y después se sube el `gitlink`
  en SecInterp.
- **Cambios del proyecto** (estado, skills de dominio): viven en `.agent-state/`, no se empujan
  al framework.
- **Bump seguro** del submódulo:
  ```bash
  scripts/update_agentic_forge.sh            # actualiza + valida
  scripts/update_agentic_forge.sh --commit   # además commitea el bump del gitlink
  ```
- **Versionado**: el framework usa tags (`v1.0.0`, …). Para fijar una versión concreta en
  SecInterp, haz checkout del tag dentro de `.agent/` y sube el `gitlink`.
- **Issues / PRs / ideas**: se reportan en el repo del framework en **Codeberg** (seguimiento
  separado del plugin).

---
*Agentic Forge framework — Gen 8. Updated 2026-10-04 (submodule model + governance).*
