import csv

import plot_utils


def test_plot_price_with_rsi(tmp_path, monkeypatch):
    csv_path = tmp_path / "foo_365d.csv"
    with csv_path.open("w", newline="") as fp:
        writer = csv.DictWriter(fp, fieldnames=["Date", "Price", "rsi_14"])
        writer.writeheader()
        writer.writerow({"Date": "2020-01-01 00:00:00", "Price": "1", "rsi_14": "50"})
        writer.writerow({"Date": "2020-01-02 00:00:00", "Price": "2", "rsi_14": "55"})

    monkeypatch.setattr(plot_utils, "CRYPTO_DATA_DIR", tmp_path)
    monkeypatch.setattr(plot_utils, "CHARTS_DIR", tmp_path)

    img = plot_utils.plot_price_with_rsi("foo", days="365", rsi_window=14)
    assert img.is_file()
