"""CSV reading/writing helpers and knowledge-base updates."""
from __future__ import annotations

import csv
import logging
from pathlib import Path
from typing import Any, Dict, List

from config import CRYPTO_DATA_DIR, KB_PATH, MOMENTUM_WINDOWS, LOG_RETURN_WINDOWS

# ---------------------------------------------------------------------------


def ensure_dirs():
    CRYPTO_DATA_DIR.mkdir(exist_ok=True, parents=True)
    KB_PATH.parent.mkdir(exist_ok=True, parents=True)

# ---------------------------------------------------------------------------


def write_asset_csv(
    asset: str,
    records: List[Dict[str, Any]],
    rsi_windows: List[int],
    days: str,
) -> Path:
    """Write per-asset historical CSV and return its path."""
    ensure_dirs()
    path = CRYPTO_DATA_DIR / f"{asset.lower()}_{days}d.csv"
    header: list[str] = [
        "Date",
        "Open",
        "High",
        "Low",
        "Price",
        "Volume",
        "obv",
        "24h_Change",
        "1d_Return",
        "7d_Return",
    ]
    for w in rsi_windows:
        header += [f"rsi_{w}", f"rsi_{w}_status"]
    header += [
        "sma_20",
        "ema_20",
        "bb_mid",
        "bb_upper",
        "bb_lower",
        "macd",
        "macd_signal",
        "macd_hist",
    ]
    for w in MOMENTUM_WINDOWS:
        header.append(f"momentum_{w}")
    for w in LOG_RETURN_WINDOWS:
        header.append(f"log_return_{w}")

    try:
        with path.open("w", newline="", encoding="utf-8") as fp:
            writer = csv.DictWriter(fp, fieldnames=header, extrasaction="ignore")
            writer.writeheader()
            for rec in records:
                writer.writerow(rec)
        logging.info("Wrote %s", path)
    except Exception as exc:  # pylint: disable=broad-except
        logging.exception("Failed writing %s – %s", path, exc)
    return path

# ---------------------------------------------------------------------------


def init_kb(rsi_windows: List[int]):
    ensure_dirs()
    header = [
        "Crypto",
        "Date",
        "Price",
        "Volume",
        "1d Return",
        "7d Return",
    ]
    for w in rsi_windows:
        header += [f"RSI_{w}", f"Status_{w}"]
    header += [
        "EMA_20",
        "BB_mid",
        "BB_upper",
        "BB_lower",
        "MACD",
        "MACD_signal",
        "MACD_hist",
    ]
    for w in MOMENTUM_WINDOWS:
        header.append(f"Momentum_{w}")
    for w in LOG_RETURN_WINDOWS:
        header.append(f"LogReturn_{w}")
    header.append("OBV")

    with KB_PATH.open("w", newline="", encoding="utf-8") as fp:
        csv.writer(fp).writerow(header)
    logging.info("Initialized knowledge-base %s", KB_PATH)


def append_kb_row(asset: str, latest: Dict[str, Any], rsi_windows: List[int]):
    row = [
        asset,
        latest["Date"],
        latest["Price"],
        latest["Volume"],
        latest.get("1d_Return"),
        latest.get("7d_Return"),
    ]
    for w in rsi_windows:
        row.append(latest.get(f"rsi_{w}"))
        row.append(latest.get(f"rsi_{w}_status"))
    row += [
        latest.get("ema_20"),
        latest.get("bb_mid"),
        latest.get("bb_upper"),
        latest.get("bb_lower"),
        latest.get("macd"),
        latest.get("macd_signal"),
        latest.get("macd_hist"),
    ]
    for w in MOMENTUM_WINDOWS:
        row.append(latest.get(f"momentum_{w}"))
    for w in LOG_RETURN_WINDOWS:
        row.append(latest.get(f"log_return_{w}"))
    row.append(latest.get("obv"))

    with KB_PATH.open("a", newline="", encoding="utf-8") as fp:
        csv.writer(fp).writerow(row)

__all__ = [
    "write_asset_csv",
    "init_kb",
    "append_kb_row",
]
