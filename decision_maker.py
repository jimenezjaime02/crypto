"""Simple trading decision logic based on the knowledge-base."""
from __future__ import annotations

import csv
from typing import Dict, List

from config import KB_PATH


# ---------------------------------------------------------------------------

def load_knowledge_base(path: str | None = None) -> List[Dict[str, str]]:
    """Load the knowledge-base CSV and return rows as dictionaries."""
    path = path or str(KB_PATH)
    rows: List[Dict[str, str]] = []
    try:
        with open(path, newline="", encoding="utf-8") as fp:
            reader = csv.DictReader(fp)
            for row in reader:
                rows.append(row)
    except FileNotFoundError as exc:
        print(f"Knowledge base not found: {exc}")
    except csv.Error as exc:
        print(f"Malformed CSV in {path}: {exc}")
    except OSError as exc:
        print(f"Error reading {path}: {exc}")
    return rows


# ---------------------------------------------------------------------------

def decide(row: Dict[str, str]) -> str:
    """Return BUY/SELL/HOLD decision based on RSI and MACD."""
    try:
        rsi = float(row.get("RSI_14", "nan"))
        macd_hist = float(row.get("MACD_hist", "nan"))
    except ValueError:
        return "UNKNOWN"

    if rsi < 30 and macd_hist > 0:
        return "BUY"
    if rsi > 70 and macd_hist < 0:
        return "SELL"
    return "HOLD"


# ---------------------------------------------------------------------------

def generate_decisions(path: str | None = None) -> Dict[str, str]:
    """Generate a decision per asset from the knowledge base."""
    rows = load_knowledge_base(path)
    decisions: Dict[str, str] = {}
    for row in rows:
        asset = row.get("Crypto", "?")
        decisions[asset] = decide(row)
    return decisions


if __name__ == "__main__":
    for asset, decision in generate_decisions().items():
        print(f"{asset}: {decision}")
