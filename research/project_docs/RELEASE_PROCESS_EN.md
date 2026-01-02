# Release Process

This document describes the detailed steps to prepare and release a new version of the **Sec Interp** plugin, optimized for generating clean and professional packages.

> [!WARNING]
> **Manual Trigger Required**: This process (especially documentation updates and tagging) **must only be executed when explicitly triggered by the user**. Do not perform automatic or preemptive releases.

## 1. Environment Preparation and Metrics

1.  **Synchronize Context**:
    *   Run `uv run qgis-analyzer analyze .` to get updated metrics.
    *   This command generates `PROJECT_SUMMARY.md` and records history in `.ai-context/metrics_history.json`.
    *   Update `.ai-context/project_brain.md` with new results if necessary.

2.  **Update Version and Changelog (Crucial)**:
    *   **metadata.txt**: Increment `version=X.Y.Z` and update the `changelog=` section.
        *   > [!IMPORTANT]
        *   > The QGIS repository uses `configparser`. You must **escape all percentage signs (`%`) as `%%`** in the `changelog` and `about` sections to avoid interpretation errors.
    *   **docs/docsec/CHANGELOG.md**: Add the new version at the top following the [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) standard.

3.  **Technical Documentation Update**:
    The version must be synchronized in the following files:
    *   **README.md**: Update version badges and "What's New" section.
    *   **README_DEV.md**: Update version and development standards if changed.
    *   **docs/docsec/PROJECT_STRUCTURE.md**: Update version and file map if there were structural changes.
    *   **docs/docsec/ARCHITECTURE_EN.md**: Update version and architecture diagrams/descriptions.
    *   **ARCHITECTURE.md**: Synchronize with the current system state (ES).
    *   **DEVELOPMENT_GUIDE.md**: Review if quality standards have evolved.

4.  **License and Help**:
    *   Ensure `LICENSE` is present.
    *   (Optional) Regenerate help documentation: `make doc`.

## 2. Clean Packaging

To prevent development files like `.git`, `tests/`, or tool configurations (`.pylintrc`, etc.) from ending up in the official ZIP, we use **`qgis-manage package`**. This tool automatically filters development and system files by integrating predefined blocklists (it does not use `git archive` but achieves the same cleanliness goal).

1.  **Generate the Package**:
    *   Ensure all preceding documentation changes have been committed.
    *   Run the package command (defined in the `Makefile`):
        ```bash
        make package VERSION=main
        ```
    *   Rename the file to be descriptive (optional, the script generates a versioned name but `make` might output generic):
        ```bash
        mv sec_interp.zip sec_interp_vX.Y.Z.zip
        ```

2.  **Content Verification**:
    *   List content to confirm no garbage files are present:
        ```bash
        unzip -l sec_interp_vX.Y.Z.zip | head -n 20
        ```

## 3. Versioning and Git

1.  **Tagging**:
    *   Create the official tag once the ZIP has been verified:
        ```bash
        git tag vX.Y.Z -m "Release version X.Y.Z: Summary of changes"
        ```

2.  **Push**:
    *   Push the main branch and the tag:
        ```bash
        git push origin main
        git push origin vX.Y.Z
        ```

## 4. Final Publishing

1.  **GitHub Release**:
    *   Create a "Release" on GitHub using the newly uploaded tag.
    *   Attach the `sec_interp_vX.Y.Z.zip` file as a binary.
    *   Paste the Changelog content in the description.

2.  **QGIS Plugin Repository**:
    *   Upload the same ZIP file to [plugins.qgis.org](https://plugins.qgis.org/).
    *   Remember that the ZIP **must** contain files inside a folder named `sec_interp/` (this is automatically handled by the `make package` command).
