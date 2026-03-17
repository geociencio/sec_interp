import json
import subprocess
import time


def call_mcp_tool(method, params):
    proc = subprocess.Popen(
        ["python3", "scripts/mcp_server.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    request = {"jsonrpc": "2.0", "id": 1, "method": method, "params": params}
    stdout, stderr = proc.communicate(input=json.dumps(request) + "\n", timeout=5)
    return json.loads(stdout)


def test_list_tools():
    response = call_mcp_tool("listTools", {})
    tools = [t["name"] for t in response["result"]["tools"]]
    print(f"Tools: {tools}")
    assert "generate_unit_test_template" in tools
    assert "audit_core_decoupling" in tools
    assert "get_latest_lessons" in tools


def test_generate_template():
    params = {
        "name": "generate_unit_test_template",
        "arguments": {
            "class_name": "ExportService",
            "module_path": "sec_interp.core.services.export_service",
        },
    }
    response = call_mcp_tool("callTool", params)
    content = response["result"]["content"][0]["text"]
    print(f"Template:\n{content}")
    assert "class TestExportService(BaseTestCase):" in content


def test_audit_decoupling():
    # Audit a known core file (or a temporary one)
    params = {
        "name": "audit_core_decoupling",
        "arguments": {"file_path": "core/services/drillhole_service.py"},
    }
    response = call_mcp_tool("callTool", params)
    content = response["result"]["content"][0]["text"]
    print(f"Audit result: {content}")
    assert "Audit" in content


if __name__ == "__main__":
    test_list_tools()
    test_generate_template()
    test_audit_decoupling()
    print("All MCP tests passed!")
