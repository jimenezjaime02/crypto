# Crypto Data Utilities

A lightweight, pure-Python toolkit for fetching cryptocurrency market data from
CoinGecko, calculating popular technical indicators, and saving results to CSV
files for further analysis.

## Directory layout

```
.
├── cli.py            # Command-line entry-point
├── config.py         # Centralised settings / constants
├── fetcher.py        # HTTP layer (rate-limited, with retry)
├── indicators.py     # Indicator maths (SMA, EMA, RSI, MACD…)
├── io_utils.py       # CSV / knowledge-base helpers
├── processing.py     # Raw-JSON → enriched-records pipeline
├── data/             # (auto-created) per-asset historical CSVs
└── knowledgebase.csv # (auto) last snapshot for each asset
```

## Installation

```bash
python -m venv .venv
source .venv/bin/activate        # On Windows use: .venv\Scripts\activate
python -m pip install -r requirements.txt
```

`requirements.txt` is minimal – **only** `requests` for HTTP and `pytest` for
tests. Everything else is in the standard library.

## Configuration

Edit `cryptos.json` to list the assets you want to track. Each entry must
contain a `coingecko_id` field pointing at the
`/api/v3/coins/<coin>/market_chart` endpoint, e.g.

```json
{
  "BTC": {
    "coingecko_id": "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart"
  }
}
```

Optional environment variables can be set for Telegram notifications, but the
messaging feature is currently disabled in the code.

## Running the pipeline

```bash
python cli.py              # Fetches 365 days of daily OHLC data for every asset
```

The script will:

1. Load your asset list from `cryptos.json`.
2. Rate-limit and download each asset’s data from CoinGecko.
3. Compute SMA, EMA, RSI, Bollinger Bands, MACD, Momentum, Log-returns and OBV.
4. Write a per-asset CSV in `data/<symbol>_365d.csv`.
5. Append the latest snapshot for each asset to `knowledgebase.csv`.

## Running tests

```bash
pytest -q
```

## Extending

* **More indicators** – add functions to `indicators.py` and import them in
  `processing.py`.
* **Different time-frames** – call `process_asset` from your own script and pass
  different `days`/`interval` arguments.
* **Real-time alerts** – re-enable the Telegram helper (see the original
  commented-out code) and schedule `cli.py` with `cron` or Windows Task
  Scheduler.
