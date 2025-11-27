#!/usr/bin/env bash

# Safer deploy script for SecInterp plugin
# - fails on errors
# - accepts overrides via env vars
# - creates a timestamped backup if destination already exists

set -euo pipefail

# --- Configuration ---
# Source directory (where this script is located)
SOURCE_DIR=$(dirname "$(readlink -f "$0")")

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
            "$SOURCE_DIR/sec_interp.py" \
            "$SOURCE_DIR/sec_interp_dialog.py" \
            "$SOURCE_DIR/sec_interp_dialog_base.ui" \
            "$SOURCE_DIR/ui_sec_interp_dialog_base.py" \
            "$SOURCE_DIR/resources.py" \
            "$SOURCE_DIR/preview_renderer.py" \
            "$SOURCE_DIR/si_core_utils.py" \
            "$SOURCE_DIR/validation_utils.py" \
            "$SOURCE_DIR/logger_config.py" \
            "$DEST_DIR/"

echo "Copying metadata and icon..."
cp -v "$SOURCE_DIR/metadata.txt" \
            "$SOURCE_DIR/icon.png" \
            "$DEST_DIR/"

if [ -d "$SOURCE_DIR/i18n" ]; then
        echo "Copying translations..."
        cp -a "$SOURCE_DIR/i18n" "$DEST_DIR/"
else
        echo "No 'i18n' directory found, skipping."
fi

# Copy pre-built help (if present)
if [ -d "$SOURCE_DIR/help/build/html" ]; then
        echo "Copying help files..."
        cp -a "$SOURCE_DIR/help/build/html" "$DEST_DIR/help"
else
        echo "No 'help/build/html' directory found. Run 'make doc' first or ignore if not needed."
fi

echo "Deployment complete."
