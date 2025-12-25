#!/bin/bash
# Script to update translation files
# Usage: ./update-strings.sh [locales] [pylupdate5]

LOCALES=$1
PYLUPDATE=$2

if [ -z "$LOCALES" ]; then
    echo "No locales specified"
    exit 1
fi

if [ -z "$PYLUPDATE" ]; then
    PYLUPDATE=pylupdate5
fi

# Create i18n directory if it doesn't exist
mkdir -p i18n

# Generate .ts files for each locale
for LOCALE in $LOCALES; do
    echo "Updating $LOCALE.ts..."
    $PYLUPDATE -noobsolete sec_interp_plugin.py gui/*.py gui/ui/pages/*.py -ts i18n/$LOCALE.ts
done
