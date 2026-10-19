---
description: Drive a live QGIS session via the forked QGIS-MCP server to smoke-test SecInterp
agent: qgis_driver
skills: [qgis-core, testing-standards]
validation: |
  - SecInterp plugin is enabled and the MCP server (fork) is running on 127.0.0.1:9877
  - The compound `secinterp` tool answers `status`
  - A preview is generated and asserted ready, and the results text is non-empty
  - An export file is written to disk
---

# Workflow: Smoke test SecInterp in QGIS 4 via MCP

Runs the manual "deploy + open dialog + preview + export" smoke test
programmatically, through the vendored QGIS-MCP fork (`tools/qgis_mcp/`, port
`9877`). This complements the Mock-first unit suite: it exercises the **real**
QGIS 4 API surface (Qt6 enums, live `iface`, dock widget).

## Prerequisites

1. SecInterp is deployed to the target QGIS profile (`make deploy QGIS_VERSION=4`).
2. The forked plugin is enabled and its server is **started** in QGIS:
   `Plugins > QGIS MCP > Start Server` (dock shows *Server running*, port `9877`).
   - Install: symlink `tools/qgis_mcp/qgis_mcp_plugin` into the profile's
     `python/plugins/` (see `tools/qgis_mcp/PROVENANCE.md`).
3. A project with the section inputs loaded (use `examples/sample_data`).
4. The `secinterp_qgis` MCP server is registered (it is, in `opencode.json`) and
   enabled for the `qgis_driver` agent.

## Steps

Run these with the `secinterp_qgis` compound tool. Report each raw result as
evidence.

1. **Connect** — `secinterp` / `{"action": "status"}`.
   Expect `{"loaded": true, "dialog_ready": true, ...}`. Also call `system`
   `ping`/`diagnose` once to confirm the socket and version match.
2. **Open the dialog** — `secinterp` / `{"action": "open"}`.
   Expect `{"opened": true, "visible": true}` (opens with `show()`, not
   `exec()`, so the server stays responsive).
3. **Load sample data (optional)** — `project load` + `layer add_vector` to map
   the DEM/section/geology/structure layers SecInterp expects.
4. **Run the preview** — `secinterp` / `{"action": "preview"}`.
   Expect `{"success": true, "message": ...}`.
5. **Assert readiness** — `secinterp` / `{"action": "ready"}`.
   Expect `{"ready": true, ...}`. This is the S2 gate (dependent buttons armed).
6. **Read results** — `secinterp` / `{"action": "results"}`.
   Expect a non-empty `text` (the metrics summary).
7. **Export** — `secinterp` / `{"action": "export", "params": {"path": "/tmp/secinterp_preview.png"}}`.
   Expect `{"success": true}` and the file to exist on disk.

## Failure triage

- `status.loaded == false` → the SecInterp plugin is not enabled in this profile.
- Connection refused → the fork plugin's server is not started, or the port is
  not `9877` (check the dock widget).
- `preview` fails → surface the `message`; the validation dialog usually names
  the missing/invalid layer mapping.

## Out of scope

`execute_code` is **never** used here; every action is an explicit `secinterp`
tool. The Mock-first suite (`make docker-test`) remains the base layer.
