import ast
import os
import sys


def check_file(filepath):
    with open(filepath, "r") as f:
        try:
            tree = ast.parse(f.read())
        except Exception:
            return

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.returns is None:
                # Check if it's __init__ (usually returns None but sometimes omitted)
                if node.name == "__init__":
                    print(f"{filepath}:{node.lineno}: {node.name} (Missing -> None)")
                else:
                    print(f"{filepath}:{node.lineno}: {node.name}")


if __name__ == "__main__":
    directory = sys.argv[1] if len(sys.argv) > 1 else "core"
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                check_file(os.path.join(root, file))
