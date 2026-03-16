from __future__ import annotations

import json
import sys
import logging
from typing import Any, Dict, List, Optional

# Configure logging to stderr to keep stdout clean for JSON-RPC
logging.basicConfig(level=logging.INFO, stream=sys.stderr)
logger = logging.getLogger("sec-interp-mcp")


class SecInterpMCPServer:
    """Lightweight MCP server for SecInterp skills orchestration."""

    def __init__(self):
        self.tools = {
            "get_architectural_pattern": {
                "description": "Retrieve SecInterp architectural patterns (Extract-then-Compute).",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "scope": {
                            "type": "string",
                            "enum": ["core", "gui", "exporters"],
                        }
                    },
                    "required": ["scope"],
                },
            },
            "check_geological_logic": {
                "description": "Validate geological data consistency and interpolation rules.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "enum": ["validate_traj", "check_intervals"],
                        }
                    },
                },
            },
            "validate_i18n": {
                "description": "Audit internationalization coverage and scope.",
                "parameters": {
                    "type": "object",
                    "properties": {"file_path": {"type": "string"}},
                },
            },
        }

    def run(self):
        """Main JSON-RPC loop over stdin/stdout."""
        logger.info("SecInterp MCP Server started (Stdio transport)")
        for line in sys.stdin:
            try:
                request = json.loads(line)
                response = self.handle_request(request)
                sys.stdout.write(json.dumps(response) + "\n")
                sys.stdout.flush()
            except json.JSONDecodeError:
                logger.error("Failed to parse JSON request")
            except Exception as e:
                logger.exception(f"Unexpected error: {e}")

    def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming JSON-RPC requests."""
        request_id = request.get("id")
        method = request.get("method")
        params = request.get("params", {})

        if method == "initialize":
            return {
                "id": request_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "serverInfo": {"name": "sec-interp-mcp", "version": "1.0.0"},
                },
            }

        if method == "listTools":
            return {
                "id": request_id,
                "result": {
                    "tools": [
                        {"name": name, **info} for name, info in self.tools.items()
                    ]
                },
            }

        if method == "callTool":
            name = params.get("name")
            args = params.get("arguments", {})
            return self.call_tool(request_id, name, args)

        return {
            "id": request_id,
            "error": {"code": -32601, "message": f"Method not found: {method}"},
        }

    def call_tool(
        self, request_id: Any, name: str, args: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a specific tool logic."""
        logger.info(f"Calling tool: {name} with args: {args}")

        # In a real implementation, this would look up data in .agent/skills/
        if name == "get_architectural_pattern":
            result = "SecInterp follows the 'Extract-then-Compute' pattern to isolate QGIS GUI from core logic."
        elif name == "check_geological_logic":
            result = "Geological logic requires strict interval endpoint interpolation in trajectories."
        elif name == "validate_i18n":
            result = "I18n audit: All user-facing strings must use self.tr() or QCoreApplication.translate()."
        else:
            return {
                "id": request_id,
                "error": {"code": -32602, "message": f"Tool not found: {name}"},
            }

        return {
            "id": request_id,
            "result": {"content": [{"type": "text", "text": result}]},
        }


if __name__ == "__main__":
    server = SecInterpMCPServer()
    server.run()
