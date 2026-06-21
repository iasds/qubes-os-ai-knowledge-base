#!/bin/bash
# Bundle kb/ into single markdown file + tar.gz for release.
# Usage: ./bundle.sh [YYYY-MM-DD]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_DIR="$(dirname "$SCRIPT_DIR")"
KB_DIR="$REPO_DIR/kb"
RELEASE_DIR="$REPO_DIR/release"

DATE="${1:-$(date +%Y-%m-%d)}"

mkdir -p "$RELEASE_DIR"
echo "=== Bundle for release $DATE ==="

# ── Single markdown file ──
MD_OUT="$RELEASE_DIR/qubes-archive-${DATE}.md"
> "$MD_OUT"

echo "# Qubes OS Knowledge Base — $DATE" >> "$MD_OUT"
echo "" >> "$MD_OUT"

if [ -f "$KB_DIR/index.md" ]; then
    cat "$KB_DIR/index.md" >> "$MD_OUT"
    echo "" >> "$MD_OUT"
    echo "---" >> "$MD_OUT"
    echo "" >> "$MD_OUT"
fi

for section in official forum mailing-lists; do
    if [ -d "$KB_DIR/$section" ]; then
        echo "" >> "$MD_OUT"
        find "$KB_DIR/$section" -name "*.md" -type f | sort | while read f; do
            rel="${f#$KB_DIR/}"
            echo "<!-- $rel -->" >> "$MD_OUT"
            cat "$f" >> "$MD_OUT"
            echo "" >> "$MD_OUT"
        done
    fi
done

MD_SIZE=$(wc -c < "$MD_OUT" | tr -d ' ')
echo "  $MD_OUT ($MD_SIZE bytes)"

# ── Tar.gz ──
TGZ_OUT="$RELEASE_DIR/qubes-kb-${DATE}.tar.gz"
tar -czf "$TGZ_OUT" -C "$REPO_DIR" kb/ 2>/dev/null
TGZ_SIZE=$(wc -c < "$TGZ_OUT" | tr -d ' ')
echo "  $TGZ_OUT ($TGZ_SIZE bytes)"

echo "=== Done ==="
