# Mon Petit Aquarium — Developer recipes

# Default recipe: list available commands
default:
    @just --list

# Convert images from dessins/ to web-ready png/webp in site/images/
convert:
    python3 scripts/convert-fish.py

# Generate multi-device favicons from site/favicon.svg
favicon:
    #!/usr/bin/env bash
    set -euo pipefail
    src="site/favicon.svg"
    if [ ! -f "$src" ]; then
        echo "ERROR: $src not found"
        exit 1
    fi
    cmd="magick"
    if ! command -v magick &> /dev/null; then
        cmd="convert"
        if ! command -v convert &> /dev/null; then
            echo "ERROR: ImageMagick is required."
            exit 1
        fi
    fi
    echo "Generating favicons from $src ..."
    $cmd "$src" -resize 16x16   site/favicon-16.png
    $cmd "$src" -resize 32x32   site/favicon-32.png
    $cmd "$src" -resize 48x48   site/favicon-48.png
    $cmd "$src" -resize 180x180 site/apple-touch-icon.png
    $cmd "$src" -resize 192x192 site/icon-192.png
    $cmd "$src" -resize 512x512 site/icon-512.png
    $cmd site/favicon-16.png site/favicon-32.png site/favicon-48.png site/favicon.ico
    echo "Done — favicons generated."

# Sync site/images/ directory with site/index.html
sync: convert favicon
    python3 scripts/sync-fish.py

# Serve the site locally (python http server)
serve port="8000":
    @echo "Aquarium running at http://localhost:{{port}}"
    python3 -m http.server {{port}} -d site

# Sync then serve with auto-reload on file changes
dev port="8000": sync
    npx --yes concurrently --names "sync,serve" --prefix-colors "yellow,cyan" \
        "npx chokidar-cli 'scripts/**' 'dessins/**' 'site/favicon.svg' -c 'just sync'" \
        "npx browser-sync start --server site --port {{port}} --files 'site/**/*' --no-open --no-notify"

# Serve the production build (dist/)
serve-prod port="8000": build
    @echo "Production build running at http://localhost:{{port}}"
    python3 -m http.server {{port}} -d dist

# Check that site/images/ and site/index.html are in sync (useful in CI)
check:
    #!/usr/bin/env bash
    set -euo pipefail
    cp site/index.html site/index.html.bak
    python3 scripts/sync-fish.py
    if ! diff -q site/index.html site/index.html.bak > /dev/null 2>&1; then
        echo "ERROR: site/index.html is out of sync with site/images/ directory."
        echo "Run 'just sync' to fix it."
        mv site/index.html.bak site/index.html
        exit 1
    fi
    rm site/index.html.bak
    echo "OK: site/index.html is in sync."

# Build for production: copy site/ to dist/, then minify JS/CSS in dist/
build: sync
    #!/usr/bin/env bash
    set -euo pipefail
    rm -rf dist
    cp -r site dist
    echo "Minifying JS and CSS ..."
    npx --yes esbuild dist/aquarium.js --minify --outfile=dist/aquarium.js --allow-overwrite
    npx --yes esbuild dist/style.css --minify --outfile=dist/style.css --allow-overwrite
    echo "Done — production build ready in dist/"

# List all fish in the aquarium
list:
    @echo "Fish in the aquarium:"
    @ls -1 site/images/ 2>/dev/null | grep -E '\.(svg|png|jpe?g|webp)$' || echo "  (none)"
