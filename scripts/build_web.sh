#!/bin/bash
# Build Bob the Pirate for web deployment using pygbag

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

echo "🏴‍☠️ Building Bob the Pirate for web..."

# Clean previous build
rm -rf build/web build/web-cache build/web.zip build/version.txt

# Run pygbag build
# --build: Build only, don't serve
# --archive: Create a zip archive for deployment
# --ume_block 0: Don't block on user media (autoplay)
# --can_close 1: Allow closing the game
# --title: Set the page title
# Note: pygbag.ini configures which directories/files to ignore
uv run pygbag --build --archive \
    --ume_block 0 \
    --can_close 1 \
    --title "Bob the Pirate" \
    .

echo ""
echo "✅ Build complete!"
echo "📁 Output: build/web/"
echo "📦 Archive: build/web.zip (for itch.io upload)"
echo ""
echo "To test locally:"
echo "  uv run pygbag ."
echo "  # Then open http://localhost:8000 in your browser"
echo ""
echo "To deploy:"
echo "  - GitHub Pages: Push to main branch (auto-deploys via GitHub Actions)"
echo "  - itch.io: Upload build/web.zip as HTML game"
echo "  - Other hosts: Upload contents of build/web/ to static hosting"
