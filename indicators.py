"""Technical indicator calculations.

All pure-python calculations used by the rest of the code-base live here so that
there are *zero* external dependencies (NumPy/Pandas/etc.). Each function
returns a list of the same length as the input *prices* list, filled with
``None`` for indices where the value is undefined.
"""
from __future__ import annotations

import math
from typing import List, Optional, Tuple

# ---------------------------------------------------------------------------
# Simple/Exponential Moving Averages
# ---------------------------------------------------------------------------

def compute_sma(prices: List[float], window: int) -> List[Optional[float]]:
    """Simple moving average (unweighted)."""
    sma: list[Optional[float]] = [None] * len(prices)
    if window <= 0:
        raise ValueError("window must be positive")
    for idx in range(window - 1, len(prices)):
        sma[idx] = sum(prices[idx - window + 1 : idx + 1]) / window
    return sma


def compute_ema(prices: List[float], window: int) -> List[Optional[float]]:
    """Exponential moving average using the standard 2/(n+1) smoothing."""
    ema: list[Optional[float]] = [None] * len(prices)
    if window <= 0:
        raise ValueError("window must be positive")
    if len(prices) < window:
        return ema
    alpha = 2 / (window + 1)
    ema[window - 1] = sum(prices[:window]) / window  # initial SMA seed
    for i in range(window, len(prices)):
        ema[i] = prices[i] * alpha + ema[i - 1] * (1 - alpha)
    return ema

# ---------------------------------------------------------------------------
# RSI
# ---------------------------------------------------------------------------

def compute_rsi(prices: List[float], window: int) -> List[Optional[float]]:
    """Relative Strength Index (RSI)."""
    rsi: list[Optional[float]] = [None] * len(prices)
    if window <= 0:
        raise ValueError("window must be positive")
    if len(prices) <= window:
        return rsi

    # Price changes
    changes = [0.0] * len(prices)
    for i in range(1, len(prices)):
        changes[i] = prices[i] - prices[i - 1]

    gains = sum(c for c in changes[1 : window + 1] if c > 0) / window
    losses = sum(-c for c in changes[1 : window + 1] if c < 0) / window

    rsi[window] = 100.0 if losses == 0 else 100.0 - 100.0 / (1 + gains / losses)

    for i in range(window + 1, len(prices)):
        delta = changes[i]
        gain = delta if delta > 0 else 0.0
        loss = -delta if delta < 0 else 0.0
        gains = (gains * (window - 1) + gain) / window
        losses = (losses * (window - 1) + loss) / window
        rsi[i] = 100.0 if losses == 0 else 100.0 - 100.0 / (1 + gains / losses)

    return rsi


def compute_multiple_rsi(prices: List[float], windows: List[int]) -> dict[int, List[Optional[float]]]:
    """Compute RSI for multiple windows in one shot (convenience wrapper)."""
    return {w: compute_rsi(prices, w) for w in windows}

# ---------------------------------------------------------------------------
# Bollinger Bands
# ---------------------------------------------------------------------------

def compute_bollinger_bands(
    prices: List[float],
    window: int,
    num_std_dev: float = 2,
) -> Tuple[List[Optional[float]], List[Optional[float]], List[Optional[float]]]:
    mid = compute_sma(prices, window)
    stds: list[Optional[float]] = [None] * len(prices)

    for i in range(window - 1, len(prices)):
        window_slice = prices[i - window + 1 : i + 1]
        mean = mid[i]
        if mean is not None:
            var = sum((p - mean) ** 2 for p in window_slice) / window
            stds[i] = math.sqrt(var)

    upper = [m + num_std_dev * s if m is not None and s is not None else None for m, s in zip(mid, stds)]
    lower = [m - num_std_dev * s if m is not None and s is not None else None for m, s in zip(mid, stds)]
    return mid, upper, lower

# ---------------------------------------------------------------------------
# MACD
# ---------------------------------------------------------------------------

def compute_macd(
    prices: List[float],
    short_window: int = 12,
    long_window: int = 26,
    signal_window: int = 9,
) -> Tuple[List[Optional[float]], List[Optional[float]], List[Optional[float]]]:
    ema_short = compute_ema(prices, short_window)
    ema_long = compute_ema(prices, long_window)

    macd_line = [s - l if s is not None and l is not None else None for s, l in zip(ema_short, ema_long)]
    signal_line: list[Optional[float]] = [None] * len(prices)

    alpha = 2 / (signal_window + 1)

    # Seed signal with SMA of the first *signal_window* macd values that are defined
    first_defined = next((idx for idx, v in enumerate(macd_line) if v is not None), None)
    if first_defined is not None:
        start = first_defined + signal_window - 1
        sample = macd_line[first_defined : first_defined + signal_window]
        if len(sample) == signal_window and all(x is not None for x in sample):
            signal_line[start] = sum(sample) / signal_window
            for i in range(start + 1, len(prices)):
                if macd_line[i] is not None and signal_line[i - 1] is not None:
                    signal_line[i] = macd_line[i] * alpha + signal_line[i - 1] * (1 - alpha)

    hist = [m - s if m is not None and s is not None else None for m, s in zip(macd_line, signal_line)]
    return macd_line, signal_line, hist

# ---------------------------------------------------------------------------
# Momentum / Log-returns / OBV / Volatility
# ---------------------------------------------------------------------------

def compute_momentum(prices: List[float], window: int) -> List[Optional[float]]:
    momentum: list[Optional[float]] = [None] * len(prices)
    for idx in range(window, len(prices)):
        momentum[idx] = prices[idx] - prices[idx - window]
    return momentum


def compute_log_return(prices: List[float], window: int) -> List[Optional[float]]:
    log_r: list[Optional[float]] = [None] * len(prices)
    for idx in range(window, len(prices)):
        prev = prices[idx - window]
        if prev:
            log_r[idx] = math.log(prices[idx] / prev)
    return log_r


def compute_obv(prices: List[float], volumes: List[float]) -> List[Optional[float]]:
    obv: list[Optional[float]] = [None] * len(prices)
    running = 0.0
    obv[0] = 0.0
    for idx in range(1, len(prices)):
        sign = 1 if prices[idx] > prices[idx - 1] else -1 if prices[idx] < prices[idx - 1] else 0
        running += sign * volumes[idx]
        obv[idx] = running
    return obv


__all__ = [
    "compute_sma",
    "compute_ema",
    "compute_rsi",
    "compute_multiple_rsi",
    "compute_bollinger_bands",
    "compute_macd",
    "compute_momentum",
    "compute_log_return",
    "compute_obv",
]
