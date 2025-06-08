"""Minimal Telegram messaging helper."""
from __future__ import annotations

import logging
from typing import Any
from pathlib import Path

import requests

from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID


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


def send_image(image_path: str | Path, caption: str = "") -> bool:
    """Send an image file to the configured Telegram chat."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        logging.info("Telegram credentials not configured")
        return False

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
    if isinstance(image_path, Path):
        image_path = str(image_path)
    try:
        with open(image_path, "rb") as fp:
            files = {"photo": fp}
            data = {"chat_id": TELEGRAM_CHAT_ID, "caption": caption}
            response = requests.post(url, files=files, data=data, timeout=10)
            response.raise_for_status()
        logging.info("Telegram image sent")
        return True
    except (OSError, requests.exceptions.RequestException) as exc:
        logging.error("Failed sending Telegram image: %s", exc)
        return False


__all__ = ["send_message", "send_image"]
