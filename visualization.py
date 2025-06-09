"""Plot price chart and RSI indicators for assets."""
from __future__ import annotations

import csv
import logging
from datetime import datetime
from pathlib import Path
from typing import Iterable, List

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from config import CRYPTO_DATA_DIR
from utils import load_assets

logger = logging.getLogger(__name__)


def _read_csv(path: Path) -> tuple[List[datetime], List[float], List[float], List[float], List[float]]:
    dates: List[datetime] = []
    prices: List[float] = []
    rsi7: List[float] = []
    rsi14: List[float] = []
    rsi21: List[float] = []
    try:
        with path.open(newline="", encoding="utf-8") as fp:
            reader = csv.DictReader(fp)
            for row in reader:
                if not row.get("Price"):
                    continue
                try:
                    dates.append(datetime.strptime(row["Date"], "%Y-%m-%d %H:%M:%S"))
                    prices.append(float(row["Price"]))
                    rsi7.append(float(row.get("rsi_7", 0) or 0))
                    rsi14.append(float(row.get("rsi_14", 0) or 0))
                    rsi21.append(float(row.get("rsi_21", 0) or 0))
                except ValueError:
                    continue
    except OSError as exc:
        logger.error("Failed reading %s: %s", path, exc)
    return dates, prices, rsi7, rsi14, rsi21


def plot_asset(symbol: str, days: str = "365", csv_path: Path | None = None) -> Path:
    """Generate a PNG chart for *symbol* and return the path."""
    path = csv_path or CRYPTO_DATA_DIR / f"{symbol.lower()}_{days}d.csv"
    if not path.exists():
        raise FileNotFoundError(path)

    dates, prices, rsi7, rsi14, rsi21 = _read_csv(path)
    if not dates:
        raise ValueError(f"No data in {path}")

    fig, ax_price = plt.subplots(figsize=(8, 4))
    ax_price.plot(dates, prices, label="Price", color="blue")
    ax_price.set_ylabel("Price")

    ax_rsi = ax_price.twinx()
    ax_rsi.plot(dates, rsi7, label="RSI 7", color="orange")
    ax_rsi.plot(dates, rsi14, label="RSI 14", color="green")
    ax_rsi.plot(dates, rsi21, label="RSI 21", color="red")
    ax_rsi.set_ylabel("RSI")
    ax_rsi.axhline(70, color="grey", ls="--", lw=0.8)
    ax_rsi.axhline(30, color="grey", ls="--", lw=0.8)

    lines1, labels1 = ax_price.get_legend_handles_labels()
    lines2, labels2 = ax_rsi.get_legend_handles_labels()
    ax_price.legend(lines1 + lines2, labels1 + labels2, loc="upper left")

    fig.autofmt_xdate()
    out_path = CRYPTO_DATA_DIR / f"{symbol.lower()}_{days}.png"
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    logger.info("Saved plot %s", out_path)
    return out_path


def plot_all(days: str = "365") -> List[Path]:
    assets = load_assets()
    paths: List[Path] = []
    for sym in assets.keys():
        try:
            paths.append(plot_asset(sym, days))
        except Exception as exc:
            logger.error("Plot failed for %s: %s", sym, exc)
    return paths

__all__ = ["plot_asset", "plot_all"]
