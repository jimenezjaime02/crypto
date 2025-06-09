import os
import sys
from pathlib import Path
import csv
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from visualization import plot_asset


def test_plot_asset(tmp_path: Path):
    csv_path = tmp_path / "sample.csv"
    with csv_path.open("w", newline="") as fp:
        writer = csv.writer(fp)
        writer.writerow([
            "Date",
            "Price",
            "rsi_7",
            "rsi_14",
            "rsi_21",
            "sma_20",
            "ema_20",
            "bb_upper",
            "bb_lower",
        ])
        writer.writerow([
            "2024-01-01 00:00:00",
            "1",
            "10",
            "20",
            "30",
            "1",
            "1",
            "1.2",
            "0.8",
        ])
        writer.writerow([
            "2024-01-02 00:00:00",
            "2",
            "11",
            "21",
            "31",
            "1.5",
            "1.4",
            "1.7",
            "1.3",
        ])
    out = plot_asset("sample", days="test", csv_path=csv_path)
    assert out.exists()
