# Release 2.8.0 - {title} - 2026-01-25

Short Summary
-------------
A brief description (1-2 lines) of what is included in this release.

Highlights
----------
- Highlight 1 (new feature / improvement).
- Highlight 2 (important fix or security patch).

Notable Changes (Detailed)
----------------------------
- [PR #NNN](link) — feat: brief description of the improvement.
- [PR #MMM](link) — fix: brief description of the fixed bug.
- [PR #PPP](link) — docs: changes in documentation.

Security Fixes
-------------------------
- CVE / CVE-like notes (if applicable) and mitigation measures.
- Recommendation for affected users (update immediately, steps, etc.).

Breaking Changes
----------------------------------------------------
If applicable, detail:
- What changed.
- Why it was necessary.
- How to migrate (clear steps and commands).

Installation / Update Instructions
--------------------------------------------
- Installation from QGIS Repository:
  1. Search for `SecInterp` in Plugins Manager.
  2. Click Install.
- Installation from ZIP:
  1. Download `sec_interp.2.8.0.zip` from GitHub.
  2. In QGIS: Plugins > Manage and Install Plugins > Install from ZIP.

Published Artifacts
---------------------
- Plugin ZIP: `sec_interp.2.8.0.zip` (attached).
- Checksum: `sec_interp.2.8.0.zip.sha256` (attached).

Verifications Performed (CI)
------------------------------
- [ ] Tests and Linter passed.
- [ ] Manual verification in QGIS.

Suggested Commands
------------------
```bash
# Build artifacts (SecInterp ZIP)
make package VERSION=main

# Create release using GitHub CLI
gh release create v2.8.0 --title "v2.8.0" --notes-file /tmp/release_notes.md dist/*.zip dist/*.sha256 --draft
```

Example (execute upon publishing)
------------------------------
Title: Release v1.1.0 - The Security & Licensing Release

Summary:
- Added GPLv3 license.
- SSRF/XXE/Path Traversal fixes.
- Documentation and badges updates.

(Add links to PRs and workflows supporting the release)
