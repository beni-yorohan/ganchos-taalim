#!/bin/bash
# Auto-deploy watcher for Ganchos Taalim
# Watches for file changes and automatically pushes to GitHub Pages
# Usage: cd ~/Desktop/ganchos-taalim-site && ./auto-deploy.sh

cd "$(dirname "$0")"

echo "👀 Watching ganchos-taalim-site for changes..."
echo "   Site: https://beni-yorohan.github.io/ganchos-taalim/"
echo "   Press Ctrl+C to stop."
echo ""

LAST_HASH=""

while true; do
  # Get a hash of all tracked + untracked file contents (excluding .git and this script)
  CURRENT_HASH=$(find . -not -path './.git/*' -not -name 'auto-deploy.sh' -type f -exec md5 -q {} \; 2>/dev/null | sort | md5 -q 2>/dev/null || \
                 find . -not -path './.git/*' -not -name 'auto-deploy.sh' -type f -exec md5sum {} \; 2>/dev/null | sort | md5sum 2>/dev/null)

  if [ -n "$LAST_HASH" ] && [ "$CURRENT_HASH" != "$LAST_HASH" ]; then
    echo "$(date '+%H:%M:%S') — Changes detected, deploying..."
    git add -A
    git commit -m "Auto-deploy — $(date '+%Y-%m-%d %H:%M')"
    git push origin main
    echo "$(date '+%H:%M:%S') — Deployed! Live in ~30 seconds."
    echo ""
  fi

  LAST_HASH="$CURRENT_HASH"
  sleep 3
done
