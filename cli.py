"""CLI entry-point replacing the monolithic `coingecko_fetcher.py`."""
from __future__ import annotations

import json
import logging
import sys
import time
from pathlib import Path
from typing import List, Dict

from config import (
    CG_LOG_PATH,
    CRYPTOS_PATH,
    MOMENTUM_WINDOWS,
    LOG_RETURN_WINDOWS,
)
from fetcher import get_market_chart, get_ohlc
from io_utils import write_asset_csv, init_kb, append_kb_row
from processing import transform_json, enrich_indicators, validate_records

# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler(CG_LOG_PATH)],
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------

def load_assets() -> dict[str, dict]:
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

# ---------------------------------------------------------------------------

def process_asset(
    symbol: str,
    info: dict,
    vs_currency: str,
    days: str,
    interval: str,
    rsi_windows: List[int],
) -> bool:
    url = info.get("coingecko_id")
    if not url:
        logger.warning("Skipping %s – no CoinGecko URL", symbol)
        return False

    raw = get_market_chart(url, vs_currency, days, interval)
    ohlc = get_ohlc(url, vs_currency, days)
    if not raw:
        return False

    recs = transform_json(raw, symbol, ohlc)
    recs = validate_records(recs)
    recs = enrich_indicators(recs, rsi_windows)

    write_asset_csv(symbol, recs, rsi_windows, days)
    append_kb_row(symbol, recs[-1], rsi_windows)
    logger.info("%s processed (%d records)", symbol, len(recs))
    return True

# ---------------------------------------------------------------------------

def main() -> int:
    vs_currency = "usd"
    days = "365"
    interval = "daily"
    rsi_windows = [7, 14, 21]

    assets = load_assets()
    if not assets:
        logger.error("No assets to process – check %s", CRYPTOS_PATH)
        return 1

    init_kb(rsi_windows)

    total = len(assets)
    success = 0
    start_t = time.perf_counter()

    from concurrent.futures import ThreadPoolExecutor, as_completed
    max_workers = min(8, total)

    def _task(item: tuple[str, Dict]):
        sym, info = item
        ok = process_asset(sym, info, vs_currency, days, interval, rsi_windows)
        return ok

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(_task, itm): itm[0] for itm in assets.items()}
        for fut in as_completed(futures):
            sym = futures[fut]
            try:
                if fut.result():
                    success += 1
            except (RuntimeError, ValueError, OSError) as exc:
                logger.error("%s failed: %s", sym, exc)

    elapsed = time.perf_counter() - start_t
    logger.info("Done – %d/%d succeeded in %.1fs (using %d workers)", success, total, elapsed, max_workers)
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
