# QGIS Plugin Analyzer 🛡️

![License: GPL v2](https://img.shields.io/badge/License-GPL%20v2-blue.svg)
![Python: 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)
![QGIS: 3.0+](https://img.shields.io/badge/QGIS-3.0+-green.svg)
![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)

## 🎯 Mission
**Empowering the PyQGIS community by providing professional-grade static analysis, ensuring every plugin follows official standards, maintains architectural integrity, and is optimized for the future of AI-assisted development.**

---

**QGIS Plugin Analyzer** is a high-performance static analysis tool specifically designed for QGIS plugin developers. It is installed as the package `qgis-plugin-analyzer` and provides the command-line interface `qgis-analyzer`. It serves as a guardian for your code, ensuring compliance with community best practices while preparing your project for seamless collaboration with Modern LLMs.

## ✨ Key Features

- **QGIS Standards Audit**: Detects missing internationalization (i18n), obsolete API calls, and unsafe threading risks. See [Rules Catalog](RULES.md).
- **Architecture Enforcement**: Identifies violations in the separation of concerns (Core vs. GUI).
- **Quality Metrics**: Calculates cyclomatic complexity and documentation coverage.
- **AI-Native Preparation**: Generates structured summaries and optimized contexts for LLMs.
- **High Performance**: Leverages multiprocessing to analyze large projects in seconds.

## ⚖️ Why use this Analyzer? (Comparison)

| Feature | QGIS Plugin Analyzer | flake8-qgis | qgis-plugin-dev-tools | Official Repo Bot |
| :--- | :---: | :---: | :---: | :---: |
| **Static Linting** | ✅ (Custom Rules) | ✅ (Strict) | ❌ | ✅ (Limited) |
| **Complexity (AST)** | ✅ | ❌ | ❌ | ❌ |
| **QGIS i18n Audit** | ✅ | ❌ | ❌ | ✅ |
| **Architecture Audit** | ✅ (UI/Core) | ❌ | ❌ | ❌ |
| **Performance Rules** | ✅ (Spatial Index) | ✅ | ❌ | ❌ |
| **Security Scanning** | ✅ | ❌ | ❌ | ✅ (Malware only) |
| **AI Context Generation**| ✅ | ❌ | ❌ | ❌ |
| **Multiprocessing Support**| ✅ | ❌ | ❌ | ❌ |
| **External Reporting** | ✅ (MD, JSON) | ❌ | ✅ (Packaging) | ❌ |

### Key Differentiators

1.  **Holistic Quality Score**: Unlike linters that only report errors, the Analyzer provides a weighted **Quality Score (0-100)**.
2.  **AI-Native Infrastructure**: Generates a structured "Project Brain" that enables AI assistants to provide much more accurate refactoring suggestions.
3.  **Architecture Enforcement**: Detects pattern violations (e.g., heavy logic inside UI files), the #1 cause of technical debt.
4.  **Zero-Friction Independence**: Runs on any project without being part of it, keeping your plugin repository production-ready.

## 🚀 Installation and Usage

### Local installation (development):
```bash
git clone https://github.com/geociencio/qgis-plugin-analyzer
cd qgis-plugin-analyzer
pip install -e .
```

### Run analysis:
```bash
qgis-analyzer /path/to/your/plugin -o ./quality_report
```

## 📊 Generated Reports

- `PROJECT_SUMMARY.md`: Executive summary with quality scoring and critical findings.
- `project_context.json`: Full structured data for external integrations.

## 📚 References and Standards

- **[PyQGIS Developer Cookbook](https://docs.qgis.org/latest/en/docs/pyqgis_developer_cookbook/)**: The bible for PyQGIS development.
- **[QGIS Plugin Repository Requirements](https://plugins.qgis.org/publish/)**: Official approval criteria.
- **[QGIS Coding Standards](https://docs.qgis.org/latest/en/docs/developer_guide/codingstandards.html)**: Style and organization guidelines.
- **[Conventional Commits](https://www.conventionalcommits.org/)**: Standard for clear commit messages.

## 🛠️ Contributing
Audit rules are defined in `src/analyzer/scanner.py`. Feel free to add new rules following the existing patterns!

---
*Developed for the SecInterp team and the global QGIS community.*
