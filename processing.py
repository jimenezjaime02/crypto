"""Data processing: transform raw CoinGecko JSON -> indicator-enriched records."""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Dict, List, Tuple

from indicators import (
    compute_bollinger_bands,
    compute_ema,
    compute_macd,
    compute_momentum,
    compute_multiple_rsi,
    compute_obv,
    compute_sma,
    compute_log_return,
)
from config import (
    MOMENTUM_WINDOWS,
    LOG_RETURN_WINDOWS,
)

# ---------------------------------------------------------------------------


def transform_json(
    data: Dict[str, Any],
    asset: str,
    ohlc: List[List[float]] | None = None,
) -> List[Dict[str, Any]]:
    """Convert CoinGecko *market_chart* response to list of dicts."""
    prices = data.get("prices", [])
    total_volumes = data.get("total_volumes", [])
    market_caps = data.get("market_caps", [])

    records: list[dict[str, Any]] = []
    prev_price: float | None = None

    for idx, price_pair in enumerate(prices):
        ts, price = price_pair
        price = float(price)
        volume = (
            float(total_volumes[idx][1]) if idx < len(total_volumes) and len(total_volumes[idx]) > 1 else 0.0
        )
        ts_str = datetime.utcfromtimestamp(ts / 1000).strftime("%Y-%m-%d %H:%M:%S")
        pct_24h = None
        if prev_price and prev_price > 0:
            pct_24h = (price - prev_price) / prev_price * 100.0
        rec = {
            "Date": ts_str,
            "Price": price,
            "Volume": volume,
            "24h_Change": pct_24h,
            "crypto": asset,
        }
        if ohlc and idx < len(ohlc):
            _, o_open, o_high, o_low, _ = ohlc[idx]
            rec["Open"] = float(o_open)
            rec["High"] = float(o_high)
            rec["Low"] = float(o_low)
        if idx < len(market_caps) and len(market_caps[idx]) > 1:
            rec["Market_Cap"] = float(market_caps[idx][1])
        records.append(rec)
        prev_price = price
    return records

# ---------------------------------------------------------------------------


def enrich_indicators(
    records: List[Dict[str, Any]],
    rsi_windows: List[int],
) -> List[Dict[str, Any]]:
    if not records:
        return records

    prices = [rec["Price"] for rec in records]
    volumes = [rec["Volume"] for rec in records]

    # Returns
    for idx in range(1, len(records)):
        prev = records[idx - 1]["Price"]
        cur = records[idx]["Price"]
        records[idx]["1d_Return"] = (cur - prev) / prev * 100.0 if prev else None
        if idx >= 7:
            week_prev = records[idx - 7]["Price"]
            records[idx]["7d_Return"] = (cur - week_prev) / week_prev * 100.0 if week_prev else None

    # RSI family
    rsi_dict = compute_multiple_rsi(prices, rsi_windows)
    for w in rsi_windows:
        arr = rsi_dict[w]
        for idx, val in enumerate(arr):
            records[idx][f"rsi_{w}"] = val
            if val is not None:
                status = "OVERBOUGHT" if val > 70 else "OVERSOLD" if val < 30 else "NEUTRAL"
                records[idx][f"rsi_{w}_status"] = status

    # SMA / EMA 20
    sma20 = compute_sma(prices, 20)
    ema20 = compute_ema(prices, 20)
    bb_mid, bb_up, bb_low = compute_bollinger_bands(prices, 20)
    macd, macd_sig, macd_hist = compute_macd(prices)

    for idx in range(len(records)):
        records[idx].update(
            {
                "sma_20": sma20[idx],
                "ema_20": ema20[idx],
                "bb_mid": bb_mid[idx],
                "bb_upper": bb_up[idx],
                "bb_lower": bb_low[idx],
                "macd": macd[idx],
                "macd_signal": macd_sig[idx],
                "macd_hist": macd_hist[idx],
            }
        )

    # Momentum & log returns
    for window in MOMENTUM_WINDOWS:
        vals = compute_momentum(prices, window)
        for idx, v in enumerate(vals):
            records[idx][f"momentum_{window}"] = v

    for window in LOG_RETURN_WINDOWS:
        vals = compute_log_return(prices, window)
        for idx, v in enumerate(vals):
            records[idx][f"log_return_{window}"] = v

    # OBV
    obv = compute_obv(prices, volumes)
    for idx, v in enumerate(obv):
        records[idx]["obv"] = v

    logging.debug("Enriched %d records with indicators", len(records))
    return records


def validate_records(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Return only records that contain numeric price and volume."""
    clean: list[Dict[str, Any]] = []
    for rec in records:
        try:
            float(rec["Price"])
            float(rec["Volume"])
        except (KeyError, TypeError, ValueError):
            logging.warning("Invalid record skipped: %s", rec)
            continue
        clean.append(rec)
    return clean

__all__ = ["transform_json", "enrich_indicators", "validate_records"]
