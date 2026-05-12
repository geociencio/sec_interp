#!/bin/bash
# Apply all translations from master data to .ts files
# Usage: ./scripts/apply-all-i18n.sh

set -e

LOCALES="de es fi fr hi id it ja nl pl pt_BR ru zh_CN"

for LOCALE in $LOCALES; do
    JSON_FILE="scripts/i18n/master_data/${LOCALE}.json"
    echo "Applying translations for ${LOCALE}..."
    if [ -f "$JSON_FILE" ]; then
        python3 scripts/i18n/apply_full.py "${LOCALE}" "${JSON_FILE}"
    else
        echo "Warning: Master data not found for ${LOCALE} (${JSON_FILE})"
    fi
done

echo "All translations applied."
