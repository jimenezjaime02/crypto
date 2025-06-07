#!/usr/bin/env bash
# One-shot script: initialise (if needed), set remote, add sensible ignores,
# commit (if nothing to commit it’s fine) and push main branch.
# Exits with 0 on success, non-zero otherwise.
set -euo pipefail

REMOTE_URL="https://github.com/jimenezjaime02/crypto.git"

# Ensure we’re in repo root (script’s directory)
cd "$(dirname "$0")"

if [ ! -d .git ]; then
  echo "Initialising git repo…"
  git init -q
fi

# Add remote if missing
if ! git remote | grep -q '^origin$'; then
  git remote add origin "$REMOTE_URL"
fi

# Ensure branch is main
CURRENT=$(git symbolic-ref --short HEAD 2>/dev/null || echo "")
if [ "$CURRENT" != "main" ]; then
  git branch -M main
fi

# .gitignore bootstrap
if [ ! -f .gitignore ]; then
  cat > .gitignore <<'EOF'
__pycache__/
*.py[cod]
.venv/
data/
knowledgebase.csv
coingecko.log
EOF
fi

# Stage & commit
if ! git diff --quiet --cached || ! git diff --quiet; then
  git add -A
  git commit -m "Automated commit" || true
fi

# Push
if git push -u origin main; then
  echo "Push succeeded."
  exit 0
else
  echo "Push failed." >&2
  exit 1
fi
