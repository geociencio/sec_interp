# Maintenance Session: 2026-10-11 - QGIS MCP Integration (Vendored Fork + `qgis_driver`)

## Technical Summary

SecInterp can now be **smoke-tested against a live QGIS session through the Model
Context Protocol**. The session closes the exploration opened in
`docs/plans/exploration_qgis4_qa_mcp.md` (which proposed building a bespoke QGIS QA
MCP — "Option B"): the deep web research showed that design already exists, is
published on `plugins.qgis.org` and supports `opencode` natively. Instead of
building it, we **adopted + forked + extended** it.

Decisions taken with the user:

1. **Adopt + extend** `nkarasiak/qgis-mcp` (published as "QGIS MCP").
2. **Fork** it into the repo (`tools/qgis_mcp/`) so SecInterp-specific tools can be added.
3. Register the MCP **only for a new subagent** (`qgis_driver`), not globally.
4. Fork instance runs on port **9877** (upstream default is 9876).

## Research (why adopt, not build)

| Project | Tools | QGIS | Notes |
| :--- | :--- | :--- | :--- |
| **nkarasiak/qgis-mcp** (chosen) | 125 | 3.28–4.x | On `plugins.qgis.org`; length-prefixed framing; token auth; multi-instance; compound mode; **opencode support**; `compat.py` (3.x/4.x enums) |
| jjsantos01/qgis_mcp | 15 | 3.x | Original; `execute_code` without auth |
| Sir-Adrien-Claudington/QGIS-MCP | ~15 | 3.38 | Hardened fork (token + loopback) |
| BLD933/qgis_mcp_server | 23 | 3.x/4 | Headless + SSE; `opencode` config example |

The upstream's `compat.py` (runtime, newest-first enum resolution) is also a
directly reusable pattern for SecInterp's QGIS 4 migration.

## Changes Made

### Fork (`tools/qgis_mcp/`) — vendored
- Fork of `nkarasiak/qgis-mcp` **v0.15.1** (`55519eb`, 2026-10-07). Plugin
  `GPLv2+`, server `MIT` — both compatible with SecInterp's `GPL-2.0-or-later`.
- Default port **9876 → 9877** (`qgis_mcp_plugin/constants.py`,
  `src/qgis_mcp/protocol.py`).
- Added `PROVENANCE.md` (upstream commit, changes, install, sync, packaging note)
  and a fork banner in `README.md`.

### SecInterp extension (no `execute_code`)
- Plugin side: `qgis_mcp_plugin/handlers/secinterp.py` (`SecInterpHandlers`
  mixin), registered in `handlers/__init__.py` and `server.py`.
- Server side: six `secinterp_*` tools in `src/qgis_mcp/server.py` plus a
  compound `secinterp` group in `src/qgis_mcp/compound_tools.py`.
- Commands/tools: `secinterp_status`, `secinterp_open`, `secinterp_run_preview`,
  `secinterp_assert_preview_ready`, `secinterp_read_results`,
  `secinterp_export_preview`.
  - `secinterp_open` mirrors `PluginLifecycleMixin.run` **minus `exec()`**: a
    nested Qt loop would hold the socket server's re-entrancy guard and freeze
    every later command.
  - `secinterp_export_preview` calls `ExportManager._execute_preview_export`
    directly (the public `export_preview()` opens a modal file dialog).
- Read-only commands added to `UNRECORDED_COMMANDS`; the fork's structural tests
  (`test_plugin_structure.py`) pin handler↔tool parity and the journal set in both
  directions, and they pass.

### opencode wiring (`opencode.json`)
- `mcp.secinterp_qgis` (local, `cwd: tools/qgis_mcp`, `QGIS_MCP_TOOL_MODE=compound`,
  `QGIS_MCP_PORT=9877`, 20 s tool-fetch timeout).
- `tools: { "secinterp_qgis*": false }` — disabled globally.
- New subagent **`qgis_driver`** (`permission: edit deny`) that enables the MCP.

### Scope / packaging
- `tools/` is a `DEV_DIRECTORY` for `qgis-manage` → the fork is **never packaged**
  (verified with `IgnoreMatcher`).
- `.analyzerignore` += `tools/`; `[tool.ruff] exclude` += `tools` (the fork has
  its own `pyproject.toml`/ruff config).
- Docs: `.agent-state/workflows/smoke-qgis4.md` (+ row in `AGENTS.md`);
  `validate_agent_system.py` → 14 skills / 14 workflows PASS.

## Verification Results

- **Fork suite**: `429 passed, 2 skipped` (live/stress/TDD excluded).
- **Lint**: `ruff check` clean in the fork; `ruff check .` clean at root.
- **stdio handshake**: `initialize` + `tools/list` → **131** tools (granular) /
  **28** compound (incl. `secinterp`).
- **Packaging ignore**: `tools/qgis_mcp/**` excluded, `core/`, `gui/` included.
- **Agent-system validator**: PASS (14/14).
- **Live smoke on QGIS 4.2.1** (plugin installed via symlink into the QGIS4
  profile, server on 9877):

  | Step | Result |
  | :--- | :--- |
  | `ping` (socket 9877) | `{"pong": true}` |
  | `get_qgis_info` | QGIS 4.2.1, profile QGIS4/default |
  | `secinterp_status` | loaded, dialog ready |
  | `secinterp_open` | `{opened: true, visible: true}` |
  | `secinterp_run_preview` | `{success: true}` |
  | `secinterp_assert_preview_ready` | `{ready: true}` |
  | `secinterp_read_results` | 430 topo pts · 9 geo segments · 9 structures · 10 drillholes |
  | `secinterp_export_preview` | PNG written (valid, 2286×900, 179 KB) |

## Impact

- The mock↔real-QGIS gap (lesson: `setDisabled`) now has a **programmatic smoke
  path**: the `/smoke-qgis4` workflow (`@qgis_driver`) drives the real Qt6/QGIS 4
  dialog (open → preview → assert → results → export) instead of a manual click-through.
- Mock-first unit tests remain the base layer; this is additive integration tooling.

## Follow-up

- Keep the fork and the forked plugin **in sync** with upstream (`PROVENANCE.md`
  documents the merge procedure); run `diagnose` after any update.
- Optional: contribute the `secinterp` tool group upstream, or trim the fork to
  the subset actually used to cut maintenance.
- The fork's default port (9877) means the published "QGIS MCP" plugin can be
  installed side-by-side without a clash.
