"""Chart plotting utilities."""
from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path
from typing import Iterable

import matplotlib.pyplot as plt

from config import CRYPTO_DATA_DIR, CHARTS_DIR


def ensure_dirs():
    CHARTS_DIR.mkdir(exist_ok=True, parents=True)


def read_csv(asset: str, days: str, rsi_window: int) -> tuple[list[datetime], list[float], list[float]]:
    path = CRYPTO_DATA_DIR / f"{asset.lower()}_{days}d.csv"
    dates: list[datetime] = []
    prices: list[float] = []
    rsi: list[float] = []
    with path.open("r", encoding="utf-8") as fp:
        reader = csv.DictReader(fp)
        for row in reader:
            try:
                dates.append(datetime.strptime(row["Date"], "%Y-%m-%d %H:%M:%S"))
                prices.append(float(row["Price"]))
                rsi.append(float(row[f"rsi_{rsi_window}"]) if row[f"rsi_{rsi_window}"] else None)
            except (KeyError, ValueError):
                continue
    return dates, prices, rsi


def plot_price_with_rsi(asset: str, days: str = "365", rsi_window: int = 14) -> Path:
    """Generate a price chart with RSI overlay and return the image path."""
    ensure_dirs()
    dates, prices, rsi = read_csv(asset, days, rsi_window)
    if not dates:
        raise ValueError(f"No data for {asset}")

    fig, (ax_price, ax_rsi) = plt.subplots(2, 1, sharex=True, figsize=(8, 6))
    ax_price.plot(dates, prices, label="Price")
    ax_price.set_ylabel("Price (USD)")
    ax_price.legend(loc="upper left")

    ax_rsi.plot(dates, rsi, color="orange", label=f"RSI {rsi_window}")
    ax_rsi.axhline(70, color="red", linestyle="--", linewidth=0.8)
    ax_rsi.axhline(30, color="green", linestyle="--", linewidth=0.8)
    ax_rsi.set_ylabel("RSI")
    ax_rsi.set_xlabel("Date")
    ax_rsi.legend(loc="upper left")

    fig.suptitle(f"{asset} Price and RSI")
    fig.tight_layout()

    out_path = CHARTS_DIR / f"{asset.lower()}_chart.png"
    fig.savefig(out_path)
    plt.close(fig)
    return out_path

__all__ = ["plot_price_with_rsi"]
