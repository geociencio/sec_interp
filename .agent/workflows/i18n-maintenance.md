---
description: Procedure for i18n maintenance and expansion (Translations)
agent: QA Engineer
skills: [i18n-standards, project-context]
---

# Workflow: i18n Maintenance

This workflow ensures that translations are synchronized with the code and expanded following the "Master Data" standard.

## Steps

1. **Synchronize Strings**:
   // turbo
   Run `./scripts/update-strings.sh "<locales>"` to extract the latest strings from the source code.

2. **Validate Untranslated Strings**:
   Run `python3 scripts/i18n_diagnostic.py` to see which files have the most pending strings.

3. **Update Master Data (JSON)**:
   - If it's a new language: Create `scripts/i18n/master_data/<lang>.json`.
   - If it's an existing language: Update the corresponding JSON with newly detected keys.

4. **Apply Translations**:
   // turbo
   Run `python3 scripts/i18n/apply_full.py <lang> scripts/i18n/master_data/<lang>.json` to inject changes into the `.ts` file.

5. **Compile and Publish**:
   // turbo
   Run `lrelease i18n/SecInterp_<lang>.ts` to generate the `.qm` binary.

6. **Update Metadata**:
   Ensure `metadata.txt` reflects changes in the `changelog` section and language count.
