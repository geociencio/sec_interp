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

# 3. Run sphinx-build to generate HTML for each language
# Supported locales (Web and Plugin)
LOCALES="en es fr pt_BR de ru zh_CN id it pl nl fi hi ja"
PLUGIN_LOCALES="$LOCALES"

echo "🛠️  Building HTML documentation for multiple languages..."
for lang in $LOCALES; do
    echo "  - Language: $lang"
    if [ "$lang" == "en" ]; then
        # Default language (English)
        uv run sphinx-build -M html "$SOURCE_DIR" "$BUILD_DIR/en" -D language=en
    else
        # Translated languages
        uv run sphinx-build -M html "$SOURCE_DIR" "$BUILD_DIR/$lang" -D language="$lang"
    fi
done

# 4. Move/Copy output to external directory (Full Web Version)
echo "📤 Exporting documentation to $OUTPUT_DIR..."
for lang in $LOCALES; do
    mkdir -p "$OUTPUT_DIR/$lang"
    cp -r "$BUILD_DIR/$lang/html/"* "$OUTPUT_DIR/$lang/"
done

# 5. [OPTIONAL] Sync with internal help directory (for plugin usage - OPTIMIZED)
INTERNAL_HELP_DIR="help/html"
if [ -d "help" ]; then
    echo "🔄 Syncing with internal help directory (OPTIMIZED OFFLINE MANUAL)..."
    rm -rf "$INTERNAL_HELP_DIR"
    mkdir -p "$INTERNAL_HELP_DIR"

    # A. Sync all languages
    for lang in $PLUGIN_LOCALES; do
        if [ -d "$BUILD_DIR/$lang/html" ]; then
            echo "    - Syncing $lang..."
            mkdir -p "$INTERNAL_HELP_DIR/$lang"
            cp -r "$BUILD_DIR/$lang/html/"* "$INTERNAL_HELP_DIR/$lang/"
        fi
    done

    # B. Deduplicate Images: Mover _images al nivel superior compartido
    echo "🖼️  Deduplicating images (shared assets)..."
    if [ -d "$INTERNAL_HELP_DIR/en/_images" ]; then
        mv "$INTERNAL_HELP_DIR/en/_images" "$INTERNAL_HELP_DIR/"
        # Eliminar _images de los demás idiomas
        rm -rf "$INTERNAL_HELP_DIR"/*/_images
        # Actualizar rutas en los HTML (cambiar _images/ por ../_images/)
        echo "🔗 Patching HTML image paths..."
        find "$INTERNAL_HELP_DIR" -name "*.html" -exec sed -i 's/src="_images\//src="..\/_images\//g' {} +
        find "$INTERNAL_HELP_DIR" -name "*.html" -exec sed -i 's/href="_images\//href="..\/_images\//g' {} +
    fi

    # C. Remove Search and bulky navigation artifacts from Offline Help
    echo "🧹 Removing search indexes and developer docs from offline help..."
    find "$INTERNAL_HELP_DIR" -name "searchindex.js" -delete
    find "$INTERNAL_HELP_DIR" -name "search.html" -delete
    find "$INTERNAL_HELP_DIR" -name "genindex.html" -delete
    find "$INTERNAL_HELP_DIR" -name "py-modindex.html" -delete
    find "$INTERNAL_HELP_DIR" -name "objects.inv" -delete

    # Remove Developer API docs
    echo "🧪 Removing API docs and source code..."
    find "$INTERNAL_HELP_DIR" -type d -name "_modules" -exec rm -rf {} +
    find "$INTERNAL_HELP_DIR" -type d -name "_sources" -exec rm -rf {} +
    find "$INTERNAL_HELP_DIR" -name "sec_interp*.html" -delete
    find "$INTERNAL_HELP_DIR" -name "modules.html" -delete
    find "$INTERNAL_HELP_DIR" -name "ARCHITECTURE.html" -delete
    find "$INTERNAL_HELP_DIR" -name "DEVELOPMENT_GUIDE.html" -delete
    find "$INTERNAL_HELP_DIR" -name "MAINTENANCE_LOG.html" -delete
    find "$INTERNAL_HELP_DIR" -name "CORE_DISTINCTION_GUIDE*.html" -delete
    find "$INTERNAL_HELP_DIR" -name "phase_closure_*.html" -delete
    find "$INTERNAL_HELP_DIR" -name "v2.9.0_technical_analysis.html" -delete

    # Remove large font sets
    echo "📦 Pruning large fonts..."
    find "$INTERNAL_HELP_DIR" -type d -path "*/_static/fonts/Lato" -exec rm -rf {} +
    find "$INTERNAL_HELP_DIR" -type d -path "*/_static/fonts/RobotoSlab" -exec rm -rf {} +
    find "$INTERNAL_HELP_DIR" -type d -path "*/_static/css/fonts" -exec rm -rf {} +

    # Micro-optimizations
    find "$INTERNAL_HELP_DIR" -name "badge_only.js" -delete
    find "$INTERNAL_HELP_DIR" -name "versions.js" -delete
    find "$INTERNAL_HELP_DIR" -name "badge_only.css" -delete
    find "$INTERNAL_HELP_DIR" -type d -empty -delete

    echo "✅ Optimization complete."
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
