# Bug Report: `qgis-plugin-analyzer` Type Hint Coverage Fails on Multi-Line Signatures

## 🐛 Description
The `qgis-plugin-analyzer` CLI tool incorrectly reports an artificially low **Type Hint Coverage (Returns)** metric for Python projects that use code formatters like `black` or strictly wrap long lines.

For instance, in the `sec_interp` project, the analyzer reports **44.7%** return type hint coverage, while an Abstract Syntax Tree (AST) scan of the exact same codebase proves the actual coverage is **89.0%** (821 out of 922 functions properly annotated).

## 🔍 Root Cause Analysis
The tool appears to rely on a naive regular expression (RegEx) or line-by-line string matching to detect the presence of `->` in function definitions.

When a code formatter like `black` encounters a function with multiple parameters or long type hints, it breaks the `def` statement across multiple lines. For example:

```python
# The analyzer ONLY sees this line and assumes no return type hint exists:
def _process_survey_segment(
    depth: float,
    azimuth: float,
    inclination: float,
    x: float,
    y: float,
    z: float,
    prev_depth: float,
    densify_step: float,
    trajectory: list,
# The analyzer misses this line entirely:
) -> tuple[float, float, float, float]:
    pass
```

Instead of reading the entire logical statement up to the colon (`:`), the underlying parsing logic evaluates line-by-line. If the line starting with `def` does not contain `->`, the function is incorrectly flagged with the `MISSING_TYPE_HINTS` rule.

## 🛠️ Reproduction Steps
1. Create a Python file (`test.py`) with a single-line function:
   ```python
   def simple(a: int) -> int:
       return a
   ```
2. Create a second function in the same file formatted over multiple lines:
   ```python
   def complex(
       a: int,
       b: int
   ) -> int:
       return a + b
   ```
3. Run `qgis-analyzer analyze .`
4. Observe that `complex()` is flagged for `MISSING_TYPE_HINTS` while `simple()` passes, resulting in a 50% reported coverage despite 100% actual coverage.

## 💡 Proposed Resolution (For AI/Tool Developers)

### Migration to AST-Based Parsing
Relying on string manipulation/RegEx for static analysis of Python source code is inherently flawed due to formatting flexibility. The module should be refactored to use the native Python `ast` module.

**Example Fix (AST Implementation):**
```python
import ast

def get_return_hint_coverage(file_path: str) -> dict:
    with open(file_path, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read())

    total_funcs = 0
    missing_hints = []

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            # Exclude magic methods like __init__ which implicitly return None
            if node.name == "__init__":
                continue

            total_funcs += 1
            if node.returns is None:
                missing_hints.append(f"{node.name} at line {node.lineno}")

    return {
        "total": total_funcs,
        "missing": len(missing_hints),
        "details": missing_hints
    }
```

### Benefits of the Fix
1. **Formatting Agnostic:** `ast.parse` inherently understands multi-line statements.
2. **Comment/String Safe:** RegEx can easily be confused by `->` appearing inside a multi-line docstring or string literal; AST completely eliminates this edge case.
3. **Speed:** AST parsing for structural analysis in modern Python is highly optimized.
