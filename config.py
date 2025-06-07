"""Configuration module for cryptocurrency data processing.

This module centralizes all configurable constants and environment-dependent
settings so that other modules can import them without duplicating logic.
"""

from __future__ import annotations

import os
from pathlib import Path

# ---------------------------------------------------------------------------
# Core paths
# ---------------------------------------------------------------------------

# Base directory is the repository root (directory that contains this file)
BASE_DIR: Path = Path(__file__).resolve().parent

# Directory where per-asset historical CSVs will be written
CRYPTO_DATA_DIR: Path = BASE_DIR / "data"

# Knowledge-base CSV (aggregated latest snapshot for every asset)
KB_PATH: Path = BASE_DIR / "knowledgebase.csv"

# Log file for CoinGecko fetcher
CG_LOG_PATH: Path = BASE_DIR / "coingecko.log"

# JSON file that lists the assets we want to track
CRYPTOS_PATH: Path = BASE_DIR / "cryptos.json"

# ---------------------------------------------------------------------------
# Technical-indicator parameters
# ---------------------------------------------------------------------------

BB_WINDOW: int = 20
BB_STD_DEV: float = 2.0

MACD_SHORT_WINDOW: int = 12
MACD_LONG_WINDOW: int = 26
MACD_SIGNAL_WINDOW: int = 9

MOMENTUM_WINDOWS: list[int] = [7, 14, 30]
LOG_RETURN_WINDOWS: list[int] = [7, 14, 30]

# Rate-limit guard – seconds between consecutive CoinGecko calls
RATE_LIMIT_INTERVAL: float = 1.2

# ---------------------------------------------------------------------------
# Optional Telegram integration (currently unused in code base)
# ---------------------------------------------------------------------------

try:
    from telegram_config import (
        TELEGRAM_BOT_TOKEN as CFG_BOT_TOKEN,
        TELEGRAM_CHAT_ID as CFG_CHAT_ID,
        BOT_NAME as CFG_BOT_NAME,
    )
except Exception:  # pragma: no cover - optional file
    CFG_BOT_TOKEN = ""
    CFG_CHAT_ID = ""
    CFG_BOT_NAME = "Price_change_24hr_bot"

TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", CFG_BOT_TOKEN)
TELEGRAM_CHAT_ID: str = os.getenv("TELEGRAM_CHAT_ID", CFG_CHAT_ID)
BOT_NAME: str = os.getenv("BOT_NAME", CFG_BOT_NAME)

__all__ = [
    "CRYPTO_DATA_DIR",
    "KB_PATH",
    "CG_LOG_PATH",
    "CRYPTOS_PATH",
    "BB_WINDOW",
    "BB_STD_DEV",
    "MACD_SHORT_WINDOW",
    "MACD_LONG_WINDOW",
    "MACD_SIGNAL_WINDOW",
    "MOMENTUM_WINDOWS",
    "LOG_RETURN_WINDOWS",
    "RATE_LIMIT_INTERVAL",
    "TELEGRAM_BOT_TOKEN",
    "TELEGRAM_CHAT_ID",
    "BOT_NAME",
]
