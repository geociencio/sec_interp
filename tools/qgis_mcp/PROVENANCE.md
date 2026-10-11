# Vendored fork: `tools/qgis_mcp/`

This directory is a **fork** of [`nkarasiak/qgis-mcp`](https://github.com/nkarasiak/qgis-mcp)
(the plugin published on `plugins.qgis.org` as **"QGIS MCP"**, author `lennepkade`).
It is the runtime half of SecInterp's QGIS-via-MCP integration: an agent drives a
live QGIS session through it, and the SecInterp extension lets it smoke-test this
plugin's dialog (open → preview → assert → results → export).

## Provenance

| | |
|---|---|
| Upstream | `https://github.com/nkarasiak/qgis-mcp` |
| Forked commit | `55519ebe009e7c7e06603d802f0ce931d6c9b20f` (`v0.15.1`, 2026-10-07) |
| Plugin license (`qgis_mcp_plugin/`) | GNU GPL v2 or later |
| Server license (`src/qgis_mcp/`) | MIT |
| SecInterp license | GPL-2.0-or-later (compatible) |

## Changes made by this fork

1. **Default port `9877`** (upstream: `9876`) so it can run next to an official
   "QGIS MCP" install without a clash — in `qgis_mcp_plugin/constants.py` and
   `src/qgis_mcp/protocol.py`.
2. **SecInterp extension** — six commands/tools that drive the SecInterp dialog:
   - Plugin side: `qgis_mcp_plugin/handlers/secinterp.py` (`SecInterpHandlers`
     mixin, registered in `handlers/__init__.py` and `server.py`).
   - Server side: the six `secinterp_*` tools in `src/qgis_mcp/server.py`, plus a
     compound `secinterp` group in `src/qgis_mcp/compound_tools.py`.
   - Commands: `secinterp_status`, `secinterp_open`, `secinterp_run_preview`,
     `secinterp_assert_preview_ready`, `secinterp_read_results`,
     `secinterp_export_preview`. No `execute_code` is involved.
3. **Test count constants** updated for the new tools (`tests/conftest.py`:
   `TOOL_COUNT 131`, `COMPOUND_TOOL_COUNT 28`) and the port in the live-test
   skips.

Everything else is upstream, unmodified.

## Install

The MCP server runs from this checkout (see `opencode.json` →
`mcp.secinterp_qgis`). The **plugin** must run inside QGIS:

```bash
# Enable the plugin in QGIS (symlink into the active profile):
ln -s "$(pwd)/tools/qgis_mcp/qgis_mcp_plugin" \
  ~/.local/share/QGIS/QGIS4/profiles/default/python/plugins/qgis_mcp_plugin
# Restart QGIS, then: Plugins > QGIS MCP > Start Server (port 9877)
```

## Validate

```bash
cd tools/qgis_mcp
uv sync
uv run --no-sync pytest tests/ \
  --ignore=tests/test_qgis_live.py --ignore=tests/test_stress.py --ignore=tests/test_tdd.py -q
# Live smoke (needs QGIS + plugin running on 9877):
uv run --no-sync pytest tests/test_qgis_live.py -q
```

## Keeping in sync with upstream

```bash
git remote add qgis-mcp https://github.com/nkarasiak/qgis-mcp
git fetch qgis-mcp
# Merge, re-resolve the port + test-count conflicts, re-run the suite.
```

The plugin and the server **must match versions**; run the `diagnose` tool after
updating either half.

## Notes

- This directory is dev-only for `qgis-manage` (`tools/` is in its
  `DEV_DIRECTORIES`), so it is **never** packaged into the SecInterp ZIP.
- It is excluded from `qgis-plugin-analyzer` (`.analyzerignore`) and from root
  `ruff` (`[tool.ruff].exclude`). It has its own `pyproject.toml`/`ruff` config.
