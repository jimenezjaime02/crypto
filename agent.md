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

## Trading Automation Logic

This repository includes Python utilities for fetching cryptocurrency prices,
computing indicators, and producing trading signals. Key modules are:

- `fetcher.py` – downloads OHLC data from CoinGecko.
- `processing.py` – calculates SMA, EMA, RSI, MACD and more.
- `decision_maker.py` – loads the latest snapshot from `knowledgebase.csv` and
  labels each asset as `BUY`, `SELL`, or `HOLD`.

The current decision rule is straightforward:

```python
def decide(row: Dict[str, str]) -> str:
    if rsi < 30 and macd_hist > 0:
        return "BUY"
    if rsi > 70 and macd_hist < 0:
        return "SELL"
    return "HOLD"
```

`master.py` orchestrates the pipeline, updating data and optionally sending a
Telegram summary.

## Using the Agent for Base Network Trading

To automate trading on the Base network, extend the agent as follows:

1. Run `cli.py` regularly to refresh market data and compute indicators.
2. Call `generate_decisions()` to produce signals for each tracked asset.
3. Translate the signals into swaps or trades on a Base-compatible exchange or
   smart contract.
4. Log executed orders and apply risk-management rules (stop-loss, position
   sizing, etc.).

Currently the code stops after generating signals, but integrating a Base
network trading layer will enable full automation.
