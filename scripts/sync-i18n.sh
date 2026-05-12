#!/bin/bash
# Update all SecInterp translation files
# Usage: ./scripts/sync-i18n.sh

set -e

LOCALES="de es fi fr hi id it ja nl pl pt_BR ru zh_CN"
PYLUPDATE=pylupdate5

mkdir -p i18n

for LOCALE in $LOCALES; do
    TS_FILE="i18n/SecInterp_${LOCALE}.ts"
    echo "Updating ${TS_FILE}..."
    # Scan project files and update .ts
    $PYLUPDATE -noobsolete sec_interp_plugin.py core/*.py core/*/*.py core/*/*/*.py gui/*.py gui/*/*.py gui/*/*/*.py exporters/*.py -ts "${TS_FILE}"
done

echo "All translation files synchronized with source code."
