"""Master script to run the entire data pipeline sequentially.

This script loads the configured assets, fetches historical data from CoinGecko,
computes indicators and updates the knowledge base. Any exception during a step
is logged and the script continues with the next asset.
"""

from __future__ import annotations

import logging
import argparse
from typing import Dict, List

from decision_maker import generate_decisions
from telegram_utils import send_message, send_photo
from visualization import plot_all
import cli

from config import CG_LOG_PATH


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler(CG_LOG_PATH)],
)
logger = logging.getLogger(__name__)



def run_pipeline(send_plots: bool = False) -> int:
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
        if send_plots:
            for path in plot_all():
                send_photo(str(path), caption=path.stem)

    return 0


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run full pipeline")
    parser.add_argument(
        "--plot",
        action="store_true",
        help="Generate price/RSI plots and send via Telegram",
    )
    args = parser.parse_args(argv)
    return run_pipeline(send_plots=args.plot)


if __name__ == "__main__":
    raise SystemExit(main())
