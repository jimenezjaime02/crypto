"""Utility helpers shared across modules."""
from __future__ import annotations

import json
import logging
from typing import Dict

from config import CRYPTOS_PATH

logger = logging.getLogger(__name__)


def load_assets(path: str | None = None) -> Dict[str, Dict]:
    """Load asset configuration from ``cryptos.json`` and return a dict."""
    path = path or str(CRYPTOS_PATH)
    try:
        with open(path, "r", encoding="utf-8") as fp:
            return json.load(fp)
    except FileNotFoundError as exc:
        logger.error("Asset configuration not found: %s", exc)
    except json.JSONDecodeError as exc:
        logger.error("Invalid JSON in %s: %s", path, exc)
    except OSError as exc:
        logger.error("Failed reading %s – %s", path, exc)
    return {}

__all__ = ["load_assets"]
