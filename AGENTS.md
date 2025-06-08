# Agent Context for push_repo.sh

This document provides full context for the `push_repo.sh` script so that AI agents and collaborators understand its purpose, workflow, and usage.

## Overview
`push_repo.sh` is a one-shot Bash script that:

1. Initializes a Git repository (if not already initialized).
2. Sets up the `origin` remote to your GitHub URL.
3. Ensures the branch is named `main`.
4. Bootstraps a sensible Python `.gitignore` (if missing).
5. Stages and commits any uncommitted changes.
6. Pushes the `main` branch to GitHub (`origin`).

## Prerequisites

- Bash shell environment (e.g., Git Bash, WSL).
- Git installed and on your PATH.
- Network access to GitHub.

## Detailed Steps

1. **Strict mode**:
   ```bash
   set -euo pipefail
   ```
   - Exits on any error or unset variable.

2. **Define remote URL**:
   ```bash
   REMOTE_URL="https://github.com/jimenezjaime02/crypto.git"
   ```

3. **Change to script directory**:
   ```bash
   cd "$(dirname "$0")"
   ```
   - Ensures operations run from the repo root.

4. **Initialize repo**:
   ```bash
   [ ! -d .git ] && git init -q
   ```

5. **Add `origin` remote**:
   ```bash
   git remote add origin "$REMOTE_URL"
   ```
   - Only if `origin` does not exist.

6. **Ensure on `main` branch**:
   ```bash
   CURRENT=$(git symbolic-ref --short HEAD 2>/dev/null || echo "")
   [ "$CURRENT" != "main" ] && git branch -M main
   ```

7. **Bootstrap `.gitignore`**:
   - Creates a Python-focused ignore list if none exists.

8. **Stage & commit**:
   ```bash
   git add -A
   git commit -m "Automated commit" || true
   ```
   - Commits any changes, but does not fail if there’s nothing to commit.

9. **Push**:
   ```bash
   git push -u origin main
   ```
   - Sets upstream on first push; exits with success or failure message.

## Usage

```bash
./push_repo.sh
```

## Notes & Customization

- By default, only the `main` branch is pushed.
- To push all branches, replace the push command with:
  ```bash
  git push --all
  ```
- You can integrate this script into CI/CD or cron jobs for automated deployments.

## Autonomous AI Agent Vision

The long-term goal of this project is to build an AI-driven agent that can autonomously analyze market data and execute cryptocurrency trades. At this stage we are concentrating on producing reliable trading signals. Automated trade execution will come later once the signal quality is proven.

