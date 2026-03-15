#!/bin/bash
# Auto-deploy script for Ganchos Taalim
# Commits and pushes any changes to GitHub Pages

cd "$(dirname "$0")"

# Check for changes
if [ -z "$(git status --porcelain)" ]; then
  echo "No changes to deploy."
  exit 0
fi

# Stage, commit, and push
git add -A
git commit -m "Update site — $(date '+%Y-%m-%d %H:%M')"
git push origin main

echo "Deployed! Changes will be live in ~30 seconds at:"
echo "https://beni-yorohan.github.io/ganchos-taalim/"
