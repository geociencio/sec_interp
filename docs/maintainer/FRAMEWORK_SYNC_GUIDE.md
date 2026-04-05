# SecInterp: Framework Implementation & Sync Guide (Gen 5)

> [!NOTE]
> **Summary (ES)**: Guía operativa para desarrolladores del proyecto SecInterp sobre cómo sincronizar mejoras del framework maestro y aplicar planos especializados (*blueprints*).

## 🚀 Mastering Synchronization
This project depends on the **Antigravity Gen 5 Framework**. Follow these steps to stay updated:

### 1. Pull Latest Framework Foundations
Sync foundational skills and scripts from `/home/jmbernales/qgispluginsdev/antigravity-framerepo/`.
```bash
rsync -av --exclude='.git' /path/to/framerepo/.agent/ .agent/
```

### 2. Apply Blueprints (`scaffold/`)
To extend the project with specialized capabilities (e.g., QGIS features):
```bash
cp -r antigravity-framerepo/scaffold/qgis/skills/* .agent/skills/
cp -r antigravity-framerepo/scaffold/qgis/workflows/* .agent/workflows/
```

## 🛠️ Specialization Workflow
When customizing a generic skill (e.g., `domain-logic`):
1. **Inherit**: Maintain the generic 3-level validation structure.
2. **Document**: Clearly mark project-specific triggers in `SKILL.md`.
3. **Validate**: Always run `python3 scripts/skill_sync.py` to ensure the agentic system is intact.

## 🧪 Daily Health Checks
- **Automated Sync**: Before starting any feature, verify standards:
  ```bash
  python3 scripts/skill_sync.py
  ```
- **MCP Server**: Ensure `scripts/mcp_server.py` is running for optimal AI tool orchestration.

---
*Antigravity Framework Project Implementation Standard - Gen 5*
