import pathlib
import json
from ai_context_core.analyzer.engine import ProjectAnalyzer
from ai_context_core.config.loader import ConfigLoader
from ai_context_core.analyzer.builders import aggregator

# Monkeypatch the bug in ai-context-core v3.2.0
original_run_qgis = aggregator.ResultsAggregator._run_qgis_aggregation


def patched_run_qgis(self, m_data, metadata):
    qgis_enabled = (
        self.config.get("patterns", {}).get("qgis_compliance", {}).get("enabled", False)
    )
    if not qgis_enabled:
        return {}

    from ai_context_core.analyzer.builders.aggregator_qgis import (
        aggregate_qgis_compliance,
    )
    import fnmatch
    from pathlib import Path

    def _match_path(path_str: str, pattern: str) -> bool:
        try:
            # Use pathlib for more robust matching if available,
            # or a better fnmatch combo
            from pathlib import Path

            p = Path(path_str)
            # Match the pattern against the relative path
            # glob/match patterns in pathlib handle ** in newer versions
            if p.match(pattern) or p.match("**/" + pattern):
                return True

            # Manual check for gui/ etc.
            if pattern.startswith("gui/") and path_str.startswith("gui/"):
                return True
        except Exception:
            pass
        return False

    # FIX: Pass the i18n config!
    i18n_config = self.config.get("patterns", {}).get("i18n", {})

    # Debug: Check some matches
    scope = i18n_config.get("scope")
    patterns = i18n_config.get("gui_patterns", [])
    print(f"DEBUG: Scope={scope}, Patterns={patterns}")

    included_count = 0
    for m in m_data:
        m_path = m.get("file", "")
        # Convert absolute to relative if needed for matching
        try:
            rel_m_path = str(Path(m_path).relative_to(Path.cwd()))
        except ValueError:
            rel_m_path = m_path

        matches = any(_match_path(rel_m_path, p) for p in patterns)
        if matches:
            included_count += 1

        if "gui" in rel_m_path and "main_dialog.py" in rel_m_path:
            print(f"SAMPLE MATCH (rel): {rel_m_path} -> {matches}")
        elif "core/services" in rel_m_path and matches:
            print(f"ERROR: {rel_m_path} included in gui_only!")

    print(f"DEBUG: Total modules: {len(m_data)}, Included for i18n: {included_count}")
    return aggregate_qgis_compliance(m_data, metadata, i18n_config)


aggregator.ResultsAggregator._run_qgis_aggregation = patched_run_qgis


def verify_gui_only():
    proj = pathlib.Path.cwd()
    loader = ConfigLoader()
    cfg = loader.load_config(profile_name="qgis")

    # Force gui_only scope
    if "patterns" not in cfg:
        cfg["patterns"] = {}
    if "i18n" not in cfg["patterns"]:
        cfg["patterns"]["i18n"] = {}
    cfg["patterns"]["i18n"]["scope"] = "gui_only"

    analyzer = ProjectAnalyzer(project_path=str(proj), config=cfg)
    res = analyzer.analyze()

    qgis = res.get("qgis_compliance", {})
    i18n = qgis.get("i18n_stats", {})

    print("\n--- RESULTS WITH gui_only SCOPE ---")
    print(f"Total Strings: {i18n.get('total_strings')}")
    print(f"Translated: {i18n.get('total_tr')}")
    print(f"Compliance Score: {qgis.get('compliance_score')}")


if __name__ == "__main__":
    verify_gui_only()
