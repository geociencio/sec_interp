---
description: Perform a full or partial plugin audit using qgis-plugin-analyzer v1.9.0+.
agent: Agent Auditor
skills: [project-context, coding-standards, i18n-standards]
---

# Workflow: Plugin Audit

This workflow executes a series of specialized static checks to ensure the quality, security, and performance of the plugin.

### Steps

1. **Security Analysis (Bandit & Secret Scan)**
   Scans the code for known vulnerabilities and hardcoded secrets.
   ```bash
   uv run qgis-analyzer analyze security .
   ```

2. **Internationalization Audit (i18n)**
   Detects user text strings that are not wrapped in `self.tr()` or `QCoreApplication.translate()`.
   ```bash
   uv run qgis-analyzer analyze i18n .
   ```

3. **Performance Analysis**
   Identifies potential UI blocks, expensive loops, and signal leaks.
   ```bash
   uv run qgis-analyzer analyze performance .
   ```

4. **Architecture Verification (Optional)**
   Analyzes dependencies between modules and QGIS API usage.
   ```bash
   uv run qgis-analyzer analyze architecture .
   ```

5. **Report Generation (Optional)**
   Generates a consolidated HTML report if deep details are required.
   ```bash
   uv run qgis-analyzer analyze . --report
   ```

## Expected Result
- Clear identification of security risks or performance bottlenecks.
- Verification of 100% translatable string coverage.
- Detailed report for technical debt prioritization.
