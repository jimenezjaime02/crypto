"""Minimal Telegram messaging helper."""
from __future__ import annotations

import logging
from typing import Any

import requests

from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID


def send_photo(path: str, caption: str | None = None) -> bool:
    """Send a photo from *path* with optional *caption*."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        logging.info("Telegram credentials not configured")
        return False

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
    with open(path, "rb") as fp:
        files = {"photo": fp}
        data = {"chat_id": TELEGRAM_CHAT_ID}
        if caption:
            data["caption"] = caption
        try:
            response = requests.post(url, data=data, files=files, timeout=10)
            response.raise_for_status()
            logging.info("Telegram photo sent")
            return True
        except requests.exceptions.RequestException as exc:
            logging.error("Failed sending Telegram photo: %s", exc)
            return False


def send_message(text: str) -> bool:
    """Send *text* to configured Telegram chat if credentials available."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        logging.info("Telegram credentials not configured")
        return False

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": text}
    try:
        response = requests.post(url, data=payload, timeout=10)
        response.raise_for_status()
        logging.info("Telegram message sent")
        return True
    except requests.exceptions.RequestException as exc:
        logging.error("Failed sending Telegram message: %s", exc)
        return False


__all__ = ["send_message", "send_photo"]
