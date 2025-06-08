"""Master script to run the entire data pipeline sequentially.

This script loads the configured assets, fetches historical data from CoinGecko,
computes indicators and updates the knowledge base. Any exception during a step
is logged and the script continues with the next asset.
"""

from __future__ import annotations

import json
import logging
from typing import Dict

from decision_maker import generate_decisions
from telegram_utils import send_message
import cli

from config import CG_LOG_PATH, CRYPTOS_PATH


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler(CG_LOG_PATH)],
)
logger = logging.getLogger(__name__)


def load_assets() -> Dict[str, Dict]:
    """Load asset configuration from ``cryptos.json``."""
    try:
        with open(CRYPTOS_PATH, "r", encoding="utf-8") as fp:
            return json.load(fp)
    except FileNotFoundError as exc:
        logger.error("Asset configuration not found: %s", exc)
    except json.JSONDecodeError as exc:
        logger.error("Invalid JSON in %s: %s", CRYPTOS_PATH, exc)
    except OSError as exc:
        logger.error("Failed reading %s – %s", CRYPTOS_PATH, exc)
    return {}


def run_pipeline() -> int:
    """Run the concurrent pipeline from ``cli.py`` then generate decisions."""

    # Use the faster threaded implementation from ``cli.py``
    cli_result = cli.main()
    if cli_result != 0:
        logger.error("cli.py failed with exit code %d", cli_result)
        return cli_result

    logger.info("cli.py pipeline complete")

    # After pipeline, generate trading decisions from the knowledge base
    try:
        decisions = generate_decisions()
        for asset, decision in decisions.items():
            logger.info("Decision for %s: %s", asset, decision)
    except (OSError, ValueError) as exc:
        logger.error("Failed generating decisions – %s", exc)
    else:
        summary = ", ".join(f"{a}:{d}" for a, d in decisions.items())
        sent = send_message(f"Decisions: {summary}")
        if sent:
            logger.info("Telegram notification sent")
        else:
            logger.info("Telegram notification failed or disabled")

    return 0


if __name__ == "__main__":
    raise SystemExit(run_pipeline())
