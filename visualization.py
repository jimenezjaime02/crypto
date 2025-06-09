"""Plot price and RSI charts for assets."""
from __future__ import annotations

import csv
import logging
from datetime import datetime
from pathlib import Path
from typing import Iterable, List, Tuple

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from config import CRYPTO_DATA_DIR
from utils import load_assets

logger = logging.getLogger(__name__)


def _read_csv(
    path: Path,
) -> Tuple[
    List[datetime],
    List[float],
    List[float],
    List[float],
    List[float],
    List[float],
    List[float],
    List[float],
    List[float],
]:
    dates: List[datetime] = []
    prices: List[float] = []
    rsi7: List[float] = []
    rsi14: List[float] = []
    rsi21: List[float] = []
    sma20: List[float] = []
    ema20: List[float] = []
    bb_upper: List[float] = []
    bb_lower: List[float] = []
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
                    sma20.append(float(row.get("sma_20", 0) or 0))
                    ema20.append(float(row.get("ema_20", 0) or 0))
                    bb_upper.append(float(row.get("bb_upper", 0) or 0))
                    bb_lower.append(float(row.get("bb_lower", 0) or 0))
                except ValueError:
                    continue
    except OSError as exc:
        logger.error("Failed reading %s: %s", path, exc)
    return (
        dates,
        prices,
        rsi7,
        rsi14,
        rsi21,
        sma20,
        ema20,
        bb_upper,
        bb_lower,
    )


def plot_asset(symbol: str, days: str = "365", csv_path: Path | None = None) -> Path:
    """Generate a PNG chart for *symbol* and return the path.

    The output image contains two panels: the top shows the price history and
    the bottom displays RSI 7, 14 and 21 curves.
    """
    path = csv_path or CRYPTO_DATA_DIR / f"{symbol.lower()}_{days}d.csv"
    if not path.exists():
        raise FileNotFoundError(path)

    (
        dates,
        prices,
        rsi7,
        rsi14,
        rsi21,
        sma20,
        ema20,
        bb_upper,
        bb_lower,
    ) = _read_csv(path)
    if not dates:
        raise ValueError(f"No data in {path}")

    fig, (ax_price, ax_rsi) = plt.subplots(
        2, 1, figsize=(9, 6), sharex=True, gridspec_kw={"height_ratios": [2, 1]}
    )
    fig.suptitle(f"{symbol} – last {days} days")

    # Price panel
    ax_price.plot(dates, prices, label="Price", color="blue")
    if any(sma20):
        ax_price.plot(dates, sma20, label="SMA 20", color="purple", linewidth=0.9)
    if any(ema20):
        ax_price.plot(dates, ema20, label="EMA 20", color="brown", linewidth=0.9)
    if any(bb_upper) and any(bb_lower):
        ax_price.fill_between(
            dates,
            bb_lower,
            bb_upper,
            color="lightgrey",
            alpha=0.3,
            label="Bollinger",
        )
    ax_price.set_ylabel("Price")
    ax_price.legend(loc="upper left")
    ax_price.grid(True, linestyle="--", alpha=0.5)

    # RSI panel
    ax_rsi.plot(dates, rsi7, label="RSI 7", color="orange")
    ax_rsi.plot(dates, rsi14, label="RSI 14", color="green")
    ax_rsi.plot(dates, rsi21, label="RSI 21", color="red")
    ax_rsi.set_ylabel("RSI")
    ax_rsi.axhline(70, color="grey", ls="--", lw=0.8)
    ax_rsi.axhline(30, color="grey", ls="--", lw=0.8)
    ax_rsi.legend(loc="upper left")
    ax_rsi.grid(True, linestyle="--", alpha=0.5)

    fig.autofmt_xdate()
    out_path = CRYPTO_DATA_DIR / f"{symbol.lower()}_{days}.png"
    fig.tight_layout(rect=[0, 0, 1, 0.96])
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
