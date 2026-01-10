#!/bin/bash
# Helper script to regenerate static search pages without tracking changes in git

# Generate the static search page
echo "Generating static search page..."
python3 scripts/generate_static_search.py kpro.html

# Ensure git ignores changes to the generated file
echo "Configuring git to ignore local changes to kpro.html..."
git update-index --skip-worktree static_search/kpro.html 2>/dev/null || true

echo "✓ Done! File updated locally but git will ignore changes."
echo "To track changes again, run: git update-index --no-skip-worktree static_search/kpro.html"
