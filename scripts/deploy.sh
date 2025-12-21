#!/usr/bin/env bash

# Safer deploy script for SecInterp plugin
# - fails on errors
# - accepts overrides via env vars
# - creates a timestamped backup if destination already exists

set -euo pipefail

# --- Configuration ---
# Source directory (where this script is located)
# Source directory (parent of this script)
SOURCE_DIR=$(dirname "$(dirname "$(readlink -f "$0")")")

# Destination directory for QGIS plugins
# Default can be overridden with the environment variable QGIS_PLUGINS_DIR
QGIS_PLUGINS_DIR="${QGIS_PLUGINS_DIR:-$HOME/.local/share/QGIS/QGIS3/profiles/default/python/plugins}"

# Name of the plugin (override if needed)
PLUGIN_NAME="${PLUGIN_NAME:-sec_interp}"

# --- Deployment ---

# Full path to the deployed plugin directory
DEST_DIR="$QGIS_PLUGINS_DIR/$PLUGIN_NAME"

echo "Deploying plugin to: $DEST_DIR"

# Basic checks for required commands
for cmd in mkdir cp readlink; do
    if ! command -v "$cmd" >/dev/null 2>&1; then
        echo "Required command '$cmd' not found in PATH. Aborting." >&2
        exit 2
    fi
done

# Ensure source dir exists
if [ ! -d "$SOURCE_DIR" ]; then
    echo "Source directory not found: $SOURCE_DIR" >&2
    exit 3
fi

# Create DEST_DIR parent if missing
mkdir -p "$DEST_DIR"

# If destination already has content, back it up first (timestamped)
if [ -d "$DEST_DIR" ] && [ "$(ls -A "$DEST_DIR")" ]; then
    BACKUP_DIR="${DEST_DIR}.bak.$(date +%Y%m%d%H%M%S)"
    echo "Found existing installation at $DEST_DIR — creating backup at: $BACKUP_DIR"
    cp -a "$DEST_DIR" "$BACKUP_DIR"
fi

echo "Copying core files..."
cp -v "$SOURCE_DIR/__init__.py" \
      "$SOURCE_DIR/logger_config.py" \
      "$SOURCE_DIR/metadata.txt" \
      "$SOURCE_DIR/icon.png" \
      "$SOURCE_DIR/LICENSE" \
      "$SOURCE_DIR/LICENSE-GPL-2.0.txt" \
      "$SOURCE_DIR/LICENSE-GPL-3.0.txt" \
      "$DEST_DIR/"

echo "Copying modules..."
# Create subdirectories
mkdir -p "$DEST_DIR/core"
mkdir -p "$DEST_DIR/core/services"
mkdir -p "$DEST_DIR/core/utils"
mkdir -p "$DEST_DIR/exporters"
mkdir -p "$DEST_DIR/gui/ui"
mkdir -p "$DEST_DIR/resources"

# Copy core module
cp -v "$SOURCE_DIR/core/"*.py "$DEST_DIR/core/"

# Copy core/services module
cp -v "$SOURCE_DIR/core/services/"*.py "$DEST_DIR/core/services/"

# Copy core/utils module
cp -v "$SOURCE_DIR/core/utils/"*.py "$DEST_DIR/core/utils/"

# Copy exporters module
cp -v "$SOURCE_DIR/exporters/"*.py "$DEST_DIR/exporters/"

# Copy gui module
cp -v "$SOURCE_DIR/gui/"*.py "$DEST_DIR/gui/"
cp -v "$SOURCE_DIR/gui/ui/"*.py "$DEST_DIR/gui/ui/"
mkdir -p "$DEST_DIR/gui/ui/pages"
cp -v "$SOURCE_DIR/gui/ui/pages/"*.py "$DEST_DIR/gui/ui/pages/"

mkdir -p "$DEST_DIR/gui/tools"
cp -v "$SOURCE_DIR/gui/tools/"*.py "$DEST_DIR/gui/tools/"


# Copy resources module
cp -v "$SOURCE_DIR/resources/"*.py "$DEST_DIR/resources/"
cp -v "$SOURCE_DIR/resources/"*.qrc "$DEST_DIR/resources/"

# Copy documentation images (required for help files)
if [ -d "$SOURCE_DIR/docs/images" ]; then
    echo "Copying documentation images..."
    mkdir -p "$DEST_DIR/docs/images"
    cp -v "$SOURCE_DIR/docs/images/"* "$DEST_DIR/docs/images/"
fi

if [ -d "$SOURCE_DIR/i18n" ]; then
        echo "Copying translations..."
        cp -a "$SOURCE_DIR/i18n" "$DEST_DIR/"
else
        echo "No 'i18n' directory found, skipping."
fi

# Copy Native Hybrid help
if [ -d "$SOURCE_DIR/help/html" ]; then
        echo "Copying help files from help/html..."
        rm -rf "$DEST_DIR/help"  # Clean old help files (Sphinx artifacts, etc.)
        mkdir -p "$DEST_DIR/help"
        cp -a "$SOURCE_DIR/help/html" "$DEST_DIR/help/"
else
        echo "Warning: No 'help/html' directory found. Help button in plugin may not work."
fi

echo "Deployment complete."
