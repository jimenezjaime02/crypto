#!/usr/bin/env bash
# Setup Git identity, credential helper, and remote.
# NOTE: Storing a personal-access token (PAT) in plain-text is insecure. Use
#       Git credential managers or environment variables in production.

# ---------------------------------------------------------------------------
# User identity
# ---------------------------------------------------------------------------

git config --global user.name "jimenezjaime02"
git config --global user.email "jimenezjaime02@gmail.com"

# ---------------------------------------------------------------------------
# Credential storage (insecure convenience)
# ---------------------------------------------------------------------------

git config --global credential.helper store

# Personal access token – replace with a safer mechanism if possible
PAT=""

echo "https://jimenezjaime02:${PAT}@github.com" > "$HOME/.git-credentials"
chmod 600 "$HOME/.git-credentials"

# ---------------------------------------------------------------------------
# Remote setup
# ---------------------------------------------------------------------------

REMOTE_URL="https://github.com/jimenezjaime02/crypto.git"
if git remote | grep -q '^origin$'; then
  git remote set-url origin "$REMOTE_URL"
else
  git remote add origin "$REMOTE_URL"
fi

echo "Git configuration complete. Remote 'origin' set to $REMOTE_URL"
