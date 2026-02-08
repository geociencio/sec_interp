import pathlib
import ast
from ai_context_core.analyzer.fs_utils import scan_project, load_exclusion_patterns
from ai_context_core.analyzer.ast_qgis import QGISComplianceVisitor


def find_strings_source():
    root = pathlib.Path.cwd()
    exclusions = load_exclusion_patterns(root, None)
    scan_res = scan_project(root, exclusions)

    file_stats = []

    for py_file in scan_res.python_files:
        try:
            content = py_file.read_text(encoding="utf-8")
            tree = ast.parse(content)
            visitor = QGISComplianceVisitor()
            visitor.visit(tree)

            i18n = visitor.results.get("i18n_usage", {})
            total = i18n.get("total_strings", 0)
            tr = i18n.get("tr", 0) + i18n.get("translate", 0)

            if total > 0:
                file_stats.append(
                    {
                        "path": py_file.relative_to(root),
                        "total": total,
                        "translated": tr,
                        "untranslated": total - tr,
                    }
                )
        except Exception:
            continue

    # Sort by untranslated count descending
    file_stats.sort(key=lambda x: x["untranslated"], reverse=True)

    print(f"{'Path':<60} {'Total':<10} {'Tr':<5} {'Untr':<5}")
    print("-" * 85)
    for stat in file_stats[:20]:
        print(
            f"{str(stat['path']):<60} {stat['total']:<10} {stat['translated']:<5} {stat['untranslated']:<5}"
        )


if __name__ == "__main__":
    find_strings_source()
