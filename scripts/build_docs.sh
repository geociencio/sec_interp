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

    # Remove Developer API docs from User Help (User Preference)
    echo "🧹 Removing API docs and source code from plugin help..."
    rm -rf "$INTERNAL_HELP_DIR/_modules"
    rm -rf "$INTERNAL_HELP_DIR/_sources"
    # shellcheck disable=SC2086
    rm -f $INTERNAL_HELP_DIR/sec_interp*.html
    # shellcheck disable=SC2086
    rm -f $INTERNAL_HELP_DIR/modules.html

    # Remove large font sets to save space (~9MB reduction)
    echo "📦 Pruning large fonts from help (optimizing for ZIP size)..."
    rm -rf "$INTERNAL_HELP_DIR/_static/fonts/Lato"
    rm -rf "$INTERNAL_HELP_DIR/_static/fonts/RobotoSlab"
    rm -rf "$INTERNAL_HELP_DIR/_static/css/fonts" # FontAwesome

    # Further micro-optimizations (removing unused RTD extras)
    rm -f "$INTERNAL_HELP_DIR/_static/js/badge_only.js"
    rm -f "$INTERNAL_HELP_DIR/_static/js/versions.js"
    rm -f "$INTERNAL_HELP_DIR/_static/css/badge_only.css"
    find "$INTERNAL_HELP_DIR" -type d -empty -delete

    echo "🔍 Verifying cleanup..."
    ls -d "$INTERNAL_HELP_DIR"/sec_interp*.html 2>/dev/null || echo "✅ API docs gone"
    ls -d "$INTERNAL_HELP_DIR/_static/fonts/Lato" 2>/dev/null || echo "✅ Lato gone"
fi

# 6. [AUTO] Deploy to GitHub Pages (if output is a git repo)
if [ -d "$OUTPUT_DIR/.git" ]; then
    echo "☁️  Detected Git repository in output. Checking for changes..."

    # Check if there are changes
    if [ -n "$(git -C "$OUTPUT_DIR" status --porcelain)" ]; then
        echo "📝 Changes detected. Committing and pushing..."

        # Get current commit hash for reference
        CURRENT_COMMIT=$(git rev-parse --short HEAD)

        git -C "$OUTPUT_DIR" add .
        git -C "$OUTPUT_DIR" commit -m "docs: auto-build from sec_interp@$CURRENT_COMMIT"

        # Pull first to avoid conflicts (though we are the only writer usually)
        # git -C "$OUTPUT_DIR" pull --rebase origin main

        echo "🚀 Pushing to remote..."
        git -C "$OUTPUT_DIR" push origin main

        echo "✅ Deployed to GitHub Pages."
    else
        echo "✨ No changes to deploy."
    fi
else
    echo "⚠️  Output directory is not a git repository. Skipping deployment."
fi

echo "============================================================"
echo "✅ SUCCESS: Documentation built and exported."
echo "🔗 Open $OUTPUT_DIR/index.html to view."
echo "============================================================"
