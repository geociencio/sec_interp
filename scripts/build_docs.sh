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

# 2.4 Sync version/date headers from metadata.txt
echo "🔢 Syncing documentation version headers..."
uv run python scripts/sync_docs_version.py || true

# 2.5 Compile translation catalogs (.po -> .mo)
echo "🌐 Compiling translation catalogs..."
python3 scripts/i18n/translate_docs.py compile

# 3. Run sphinx-build to generate HTML for each language.
#
# Two independent sets:
#   * WEB_LOCALES  -> published website (index.rst, full docs, only languages
#                     with meaningful coverage).
#   * HELP_LOCALES -> in-plugin offline manual (help_index.rst, USER_GUIDE only,
#                     all UI-supported languages).
#
# Policy: a language joins WEB_LOCALES only when its USER_GUIDE.po reaches >= 80%
# (see docs/DOCS_STYLE_GUIDE.md). Full UI-supported set:
#   en es fr pt_BR de ru zh_CN id it pl nl fi hi ja
WEB_LOCALES="${DOCS_LOCALES:-en es}"
HELP_LOCALES="${DOCS_HELP_LOCALES:-en es fr pt_BR de ru zh_CN id it pl nl fi hi ja}"

echo "🛠️  Building HTML documentation..."
echo "    Web (published): $WEB_LOCALES"
echo "    Offline help:    $HELP_LOCALES (USER_GUIDE only)"

# A. Website: full documentation set (root_doc = index).
for lang in $WEB_LOCALES; do
    echo "  - [web] Language: $lang"
    uv run sphinx-build -M html "$SOURCE_DIR" "$BUILD_DIR/$lang" -D language="$lang" -j auto
done

# B. Offline help: only the User Guide (root_doc = help_index, other docs excluded).
for lang in $HELP_LOCALES; do
    echo "  - [help] Language: $lang"
    SECINTERP_DOCS_HELP=1 uv run sphinx-build -M html "$SOURCE_DIR" "$BUILD_DIR/help/$lang" \
        -D language="$lang" -D root_doc=help_index -j auto
done

# 4. Move/Copy output to external directory (published website).
# Only WEB_LOCALES are published; other languages are built for the offline help only.
echo "📤 Exporting documentation to $OUTPUT_DIR (web locales: $WEB_LOCALES)..."
for lang in $WEB_LOCALES; do
    rm -rf "$OUTPUT_DIR/$lang"
    mkdir -p "$OUTPUT_DIR/$lang"
    cp -r "$BUILD_DIR/$lang/html/"* "$OUTPUT_DIR/$lang/"
done

# 5. [OPTIONAL] Sync with internal help directory (for plugin usage - OPTIMIZED)
INTERNAL_HELP_DIR="help/html"
mkdir -p help
if [ -d "help" ]; then
    echo "🔄 Syncing with internal help directory (OPTIMIZED OFFLINE MANUAL)..."
    rm -rf "$INTERNAL_HELP_DIR"
    mkdir -p "$INTERNAL_HELP_DIR"

    # A. Sync all languages (from the USER_GUIDE-only help build)
    for lang in $HELP_LOCALES; do
        if [ -d "$BUILD_DIR/help/$lang/html" ]; then
            echo "    - Syncing $lang..."
            mkdir -p "$INTERNAL_HELP_DIR/$lang"
            cp -r "$BUILD_DIR/help/$lang/html/"* "$INTERNAL_HELP_DIR/$lang/"
            # Rename the help master doc to index.html so the plugin Help button
            # keeps opening index.html while only the User Guide is shown.
            if [ -f "$INTERNAL_HELP_DIR/$lang/help_index.html" ]; then
                mv "$INTERNAL_HELP_DIR/$lang/help_index.html" "$INTERNAL_HELP_DIR/$lang/index.html"
                find "$INTERNAL_HELP_DIR/$lang" -name "*.html" -exec \
                    sed -i 's/help_index\.html/index.html/g' {} +
            fi
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

    # Remove bulky raw sources (the offline manual only ships rendered HTML).
    echo "🧪 Removing raw sources..."
    find "$INTERNAL_HELP_DIR" -type d -name "_modules" -exec rm -rf {} +
    find "$INTERNAL_HELP_DIR" -type d -name "_sources" -exec rm -rf {} +

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

    # D. Deduplicate shared _static assets across languages (one shared copy).
    # Sphinx emits an identical theme.css/jquery.js/... per language; only a few
    # files (documentation_options.js, language_data.js, translations.js) differ.
    echo "🧩 Deduplicating shared _static assets across languages..."
    uv run python - <<'PY'
from collections import defaultdict
from pathlib import Path
import hashlib
import shutil

root = Path("help/html")
langs = [
    d for d in sorted(root.iterdir())
    if d.is_dir() and d.name not in ("_static", "_images")
]
shared_root = root / "_static"

digests = defaultdict(dict)
for lang in langs:
    static_dir = lang / "_static"
    if not static_dir.is_dir():
        continue
    for f in static_dir.rglob("*"):
        if f.is_file():
            rel = f.relative_to(static_dir).as_posix()
            digests[rel][lang.name] = hashlib.sha256(f.read_bytes()).hexdigest()

# A file is shareable when every language that ships it has identical content.
shared_rels = [
    rel
    for rel, per_lang in digests.items()
    if len(set(per_lang.values())) == 1
]

for rel in shared_rels:
    dst = shared_root / rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    first = True
    for lang in langs:
        src = lang / "_static" / rel
        if not src.exists():
            continue
        if first:
            shutil.move(str(src), str(dst))
            first = False
        else:
            src.unlink()

# Point the per-language HTML at the shared assets (keep language-specific ones).
for lang in langs:
    for html in lang.glob("*.html"):
        text = html.read_text(encoding="utf-8")
        updated = text
        for rel in shared_rels:
            updated = updated.replace(f"_static/{rel}", f"../_static/{rel}")
        if updated != text:
            html.write_text(updated, encoding="utf-8")

for lang in langs:
    static_dir = lang / "_static"
    if static_dir.is_dir() and not any(static_dir.rglob("*")):
        static_dir.rmdir()

total = sum(f.stat().st_size for f in (root / "_static").rglob("*") if f.is_file())
print(f"    - shared assets: {len(shared_rels)} files ({total / 1048576:.2f} MiB)")
PY

    # E. Lossless PNG optimization of the shared images.
    echo "🖼️  Optimizing PNG images (lossless)..."
    uv run --with pyoxipng python - <<'PY' || echo "    ⚠️ PNG optimization skipped"
from pathlib import Path
import oxipng

count = 0
for png in sorted(Path("help/html/_images").rglob("*.png")):
    oxipng.optimize(str(png), level=6)
    count += 1
    print(f"    - optimized {count} PNG files")
PY

    # Remove directories left empty after deduplication.
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
