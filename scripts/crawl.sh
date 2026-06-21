#!/bin/bash
# Qubes KB Crawler — main orchestrator.
# Crawls forum (all 34 categories, ~18.5k topics), qubes-doc, mailing lists.
# Generates index, bundles release, commits and pushes to GitHub.
#
# Run from repo root. Cron: 0 0 * * 0  cd /opt/qubes-kb && ./scripts/crawl.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_DIR="$(dirname "$SCRIPT_DIR")"
cd "$REPO_DIR"

DRY_RUN=false
[ "${1:-}" = "--dry-run" ] && DRY_RUN=true && echo "=== DRY RUN MODE ==="

# Ensure UTF-8 locale for Python unicode output
export LANG=C.UTF-8
export PYTHONIOENCODING=utf-8
export PYTHONUNBUFFERED=1

DATE_TAG=$(date +%Y-%m-%d)
LOG="/tmp/qubes-crawl-${DATE_TAG}.log"
exec > >(tee "$LOG") 2>&1

echo "=== Qubes KB Crawler — $DATE_TAG ==="
echo "Started: $(date)"
echo ""

# Run all phases from scripts/ so modules resolve
cd "$SCRIPT_DIR"

DRY_FLAG=""
$DRY_RUN && DRY_FLAG="--dry-run"

echo "╔══════════════════════════════════════════╗"
echo "║  Phase 1: Forum (all 34 categories)     ║"
echo "╚══════════════════════════════════════════╝"
python3 -m crawler.forum $DRY_FLAG || echo "[WARN] Forum crawl had errors"

echo ""
echo "╔══════════════════════════════════════════╗"
echo "║  Phase 2: Qubes Official Docs           ║"
echo "╚══════════════════════════════════════════╝"
python3 -m crawler.qubesdoc $DRY_FLAG || echo "[WARN] Docs crawl had errors"

echo ""
echo "╔══════════════════════════════════════════╗"
echo "║  Phase 3: Mailing Lists                 ║"
echo "╚══════════════════════════════════════════╝"
python3 -m crawler.mailinglist $DRY_FLAG || echo "[WARN] Mailing list crawl had errors"

cd "$REPO_DIR"

echo ""
echo "╔══════════════════════════════════════════╗"
echo "║  Phase 4: Generate index.md             ║"
echo "╚══════════════════════════════════════════╝"
python3 scripts/index_gen.py

echo ""
echo "╔══════════════════════════════════════════╗"
echo "║  Phase 5: Bundle release artifacts      ║"
echo "╚══════════════════════════════════════════╝"
$DRY_RUN || bash scripts/bundle.sh "$DATE_TAG"

echo ""
echo "╔══════════════════════════════════════════╗"
echo "║  Phase 6: Git commit & push             ║"
echo "╚══════════════════════════════════════════╝"
if $DRY_RUN; then
    echo "[DRY RUN] Would commit and push"
else
    if git diff --quiet && git diff --cached --quiet; then
        echo "No changes to commit."
    else
        git add kb/ release/
        F_COUNT=$(find kb/forum -name "*.md" 2>/dev/null | wc -l)
        O_COUNT=$(find kb/official -name "*.md" 2>/dev/null | wc -l)
        M_COUNT=$(find kb/mailing-lists -name "*.md" 2>/dev/null | wc -l)
        git commit -m "crawl: update $DATE_TAG — F:$F_COUNT O:$O_COUNT M:$M_COUNT"
        git push origin main

        if command -v gh &>/dev/null; then
            gh release create "v$DATE_TAG" \
                release/qubes-archive-${DATE_TAG}.md \
                release/qubes-kb-${DATE_TAG}.tar.gz \
                --title "Qubes Knowledge Base — $DATE_TAG" \
                --notes "Weekly crawl. See [kb/index.md](kb/index.md)." \
                || echo "[WARN] gh release create failed"
        else
            echo "[WARN] gh CLI not found. Artifacts in: release/"
        fi
    fi
fi

echo ""
echo "╔══════════════════════════════════════════╗"
echo "║  Phase 7: Cleanup temp                  ║"
echo "╚══════════════════════════════════════════╝"
rm -rf /tmp/qubes-doc-*
echo "Log: $LOG"

echo ""
echo "=== Done: $(date) ==="
