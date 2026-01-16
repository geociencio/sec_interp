#!/bin/bash

# /***************************************************************************
#  SecInterp - Documentation Build Script
#  Automates Sphinx documentation generation with external output.
#  ***************************************************************************/

# Exit on error
set -e

# Configuration
PROJECT_NAME="sec_interp"
SOURCE_DIR="docs/source"
BUILD_DIR="docs/build"
DEFAULT_OUTPUT_DIR="../sec_interp_docs"

# Determine output directory
OUTPUT_DIR="${1:-$DEFAULT_OUTPUT_DIR}"

echo "============================================================"
echo "🚀 Starting Sphinx Documentation Build"
echo "📂 Project: $PROJECT_NAME"
echo "📂 Output Directory: $OUTPUT_DIR"
echo "============================================================"

# Ensure output directory exists
mkdir -p "$OUTPUT_DIR"

# 1. Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR"

# 2. Run sphinx-apidoc to generate module sources
echo "📦 Generating API documentation sources..."
# --force: Overwrite existing files
# --separate: Put each module on its own page
# --module-first: Put module documentation before submodule documentation
uv run sphinx-apidoc -o "$SOURCE_DIR" . \
    docs/ \
    tests/ \
    scripts/ \
    help/ \
    build/ \
    --force --separate --module-first

# 3. Run sphinx-build to generate HTML
echo "🛠️  Building HTML documentation..."
uv run sphinx-build -M html "$SOURCE_DIR" "$BUILD_DIR"

# 4. Move/Copy output to external directory
echo "📤 Exporting documentation to $OUTPUT_DIR..."
# We use copy followed by clean to ensure external directory is fresh
# but we might want to keep history if it's a git repo.
# For now, we sync the content of docs/build/html to the output dir.
cp -r "$BUILD_DIR/html/"* "$OUTPUT_DIR/"

# 5. [OPTIONAL] Sync with internal help directory (for plugin usage)
INTERNAL_HELP_DIR="help/html"
if [ -d "help" ]; then
    echo "🔄 Syncing with internal help directory ($INTERNAL_HELP_DIR)..."
    rm -rf "$INTERNAL_HELP_DIR"
    mkdir -p "$INTERNAL_HELP_DIR"
    cp -r "$BUILD_DIR/html/"* "$INTERNAL_HELP_DIR/"
fi

echo "============================================================"
echo "✅ SUCCESS: Documentation built and exported."
echo "🔗 Open $OUTPUT_DIR/index.html to view."
echo "============================================================"
