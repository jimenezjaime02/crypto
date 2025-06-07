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

from config import CG_LOG_PATH, CRYPTOS_PATH
from fetcher import get_market_chart, get_ohlc
from io_utils import write_asset_csv, init_kb, append_kb_row
from processing import transform_json, enrich_indicators


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
    except Exception as exc:  # pylint: disable=broad-except
        logger.error("Failed loading %s – %s", CRYPTOS_PATH, exc)
        return {}


def run_pipeline() -> int:
    """Run the entire pipeline sequentially for all configured assets."""
    vs_currency = "usd"
    days = "365"
    interval = "daily"
    rsi_windows = [7, 14, 21]

    assets = load_assets()
    if not assets:
        logger.error("No assets to process – check %s", CRYPTOS_PATH)
        return 1

    init_kb(rsi_windows)

    for symbol, info in assets.items():
        try:
            url = info.get("coingecko_id")
            if not url:
                logger.warning("Skipping %s – no CoinGecko URL", symbol)
                continue

            raw = get_market_chart(url, vs_currency, days, interval)
            ohlc = get_ohlc(url, vs_currency, days)
            if not raw:
                raise RuntimeError("empty data returned")

            recs = transform_json(raw, symbol, ohlc)
            recs = enrich_indicators(recs, rsi_windows)

            write_asset_csv(symbol, recs, rsi_windows, days)
            append_kb_row(symbol, recs[-1], rsi_windows)
            logger.info("%s processed (%d records)", symbol, len(recs))
        except Exception as exc:  # pylint: disable=broad-except
            logger.error("Failed processing %s – %s", symbol, exc)

    logger.info("Pipeline complete")

    # After pipeline, generate trading decisions from the knowledge base
    try:
        decisions = generate_decisions()
        for asset, decision in decisions.items():
            logger.info("Decision for %s: %s", asset, decision)
    except Exception as exc:  # pylint: disable=broad-except
        logger.error("Failed generating decisions – %s", exc)

    return 0


if __name__ == "__main__":
    raise SystemExit(run_pipeline())
