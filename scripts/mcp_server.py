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
        self.tools: Dict[str, Any] = {
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
            "generate_unit_test_template": {
                "description": "Generate a unittest boilerplate following project standards.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "class_name": {"type": "string"},
                        "module_path": {"type": "string"},
                    },
                    "required": ["class_name", "module_path"],
                },
            },
            "audit_core_decoupling": {
                "description": "Scan module for architectural violations (GUI in Core).",
                "parameters": {
                    "type": "object",
                    "properties": {"file_path": {"type": "string"}},
                    "required": ["file_path"],
                },
            },
            "get_latest_lessons": {
                "description": "Retrieve recent technical lessons from AGENT_LESSONS.md.",
                "parameters": {
                    "type": "object",
                    "properties": {"limit": {"type": "integer", "default": 5}},
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
                    "serverInfo": {"name": "sec-interp-mcp", "version": "1.1.0"},
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

        result = ""
        try:
            if name == "get_architectural_pattern":
                result = "SecInterp follows the 'Extract-then-Compute' pattern to isolate QGIS GUI from core logic."
            elif name == "check_geological_logic":
                result = "Geological logic requires strict interval endpoint interpolation in trajectories."
            elif name == "validate_i18n":
                result = "I18n audit: All user-facing strings must use self.tr() or QCoreApplication.translate()."
            elif name == "generate_unit_test_template":
                class_name = str(args.get("class_name", ""))
                module_path = str(args.get("module_path", ""))
                result = self._generate_test_template(class_name, module_path)
            elif name == "audit_core_decoupling":
                file_path = str(args.get("file_path", ""))
                result = self._audit_decoupling(file_path)
            elif name == "get_latest_lessons":
                limit = int(args.get("limit", 5))
                result = self._get_lessons(limit)
            else:
                return {
                    "id": request_id,
                    "error": {"code": -32602, "message": f"Tool not found: {name}"},
                }
        except Exception as e:
            logger.exception(f"Tool execution failed: {e}")
            return {
                "id": request_id,
                "error": {"code": -32603, "message": f"Internal error: {str(e)}"},
            }

        return {
            "id": request_id,
            "result": {"content": [{"type": "text", "text": result}]},
        }

    def _generate_test_template(self, class_name: str, module_path: str) -> str:
        return f"""from __future__ import annotations
from tests.base_test import BaseTestCase
from {module_path} import {class_name}

class Test{class_name}(BaseTestCase):
    def setUp(self):
        super().setUp()
        # Mock-First: Initialize dependencies here

    def test_initialization(self):
        # TODO: Implement test case
        self.assertTrue(True)
"""

    def _audit_decoupling(self, file_path: str) -> str:
        if "core/" not in file_path:
            return f"Audit skipped: {file_path} is not in the core directory."

        violations = []
        try:
            with open(file_path, "r") as f:
                for i, line in enumerate(f, 1):
                    if "qgis.gui" in line or "PyQt" in line and "qgis.PyQt" not in line:
                        violations.append(f"Line {i}: {line.strip()}")
        except Exception as e:
            return f"Error reading file: {e}"

        if not violations:
            return f"Audit passed: No decoupling violations found in {file_path}."
        return f"Violations found in {file_path}:\n" + "\n".join(violations)

    def _get_lessons(self, limit: int) -> str:
        import os

        lessons_path = ".agent/memory/AGENT_LESSONS.md"
        if not os.path.exists(lessons_path):
            return "AGENT_LESSONS.md not found."

        try:
            with open(lessons_path, "r") as f:
                content = f.read()
                # Very simple parser for proof of concept
                lessons: List[str] = content.split("  - date:")[1:]
                latest_list = lessons[:limit]
                return "Latest Lessons:\n" + "\n".join(
                    [" - date:" + l.strip() for l in latest_list]
                )
        except Exception as e:
            return f"Error reading lessons: {e}"


if __name__ == "__main__":
    server = SecInterpMCPServer()
    server.run()
