"""HTTP layer for CoinGecko queries with retry & rate–limit guards."""
from __future__ import annotations

import time
import logging
from typing import Any, Dict, Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from config import RATE_LIMIT_INTERVAL

# Session with retry policy ---------------------------------------------------

_session: Optional[requests.Session] = None


def _get_session() -> requests.Session:
    global _session
    if _session is None:
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST"],
        )
        _session = requests.Session()
        adapter = HTTPAdapter(max_retries=retry_strategy)
        _session.mount("http://", adapter)
        _session.mount("https://", adapter)
    return _session

# ---------------------------------------------------------------------------


def get_market_chart(
    coingecko_url: str,
    vs_currency: str,
    days: str,
    interval: str,
) -> Dict[str, Any]:
    """Return JSON dict or empty dict on error."""
    sess = _get_session()

    # Build URL by adding query params even if they already exist
    from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

    parsed = urlparse(coingecko_url)
    q = parse_qs(parsed.query)
    q.update({"vs_currency": vs_currency, "days": days, "interval": interval})

    final_url = urlunparse(parsed._replace(query=urlencode(q, doseq=True)))

    _respect_rate_limit()

    try:
        r = sess.get(final_url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
        r.raise_for_status()
        data = r.json()
        if not isinstance(data, dict) or "prices" not in data:
            logging.error("Unexpected CoinGecko format for %s", final_url)
            return {}
        return data
    except requests.exceptions.RequestException as exc:
        logging.error("Error fetching %s – %s", final_url, exc)
        return {}


def get_ohlc(
    coingecko_url: str,
    vs_currency: str,
    days: str,
) -> list:
    """Return OHLC list or empty list on error."""
    sess = _get_session()

    from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

    ohlc_url = coingecko_url.replace("market_chart", "ohlc")
    parsed = urlparse(ohlc_url)
    q = parse_qs(parsed.query)
    q.update({"vs_currency": vs_currency, "days": days})

    final_url = urlunparse(parsed._replace(query=urlencode(q, doseq=True)))

    _respect_rate_limit()

    try:
        r = sess.get(final_url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
        r.raise_for_status()
        data = r.json()
        if not isinstance(data, list):
            logging.error("Unexpected CoinGecko OHLC format for %s", final_url)
            return []
        return data
    except requests.exceptions.RequestException as exc:
        logging.error("Error fetching %s – %s", final_url, exc)
        return []


# ---------------------------------------------------------------------------


def _respect_rate_limit():
    now = time.time()
    last = getattr(_respect_rate_limit, "_last", 0.0)
    if now - last < RATE_LIMIT_INTERVAL:
        time.sleep(RATE_LIMIT_INTERVAL - (now - last))
    _respect_rate_limit._last = time.time()  # type: ignore[attr-defined]


__all__ = ["get_market_chart", "get_ohlc"]
