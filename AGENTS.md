# AGENT WORKFLOW OVERVIEW

This repository contains utilities for fetching cryptocurrency market data, computing technical indicators and generating trading signals. The goal is to automate trading using these signals to maximize profits. Agents coordinating in this repo should follow the outline below.

## Modules
- `fetcher.py` downloads OHLC data from CoinGecko with retry and rate limiting.
- `processing.py` transforms raw JSON into per-record dictionaries and enriches them with indicators defined in `indicators.py`.
- `decision_maker.py` labels each asset as BUY, SELL or HOLD based on indicator values.
- `io_utils.py` manages per-asset CSVs and the `knowledgebase.csv` snapshot.
- `master.py` orchestrates the workflow and optionally interacts with Telegram via `telegram_utils.py`.

## Desired Agentic Workflow
1. **Data Fetch Agent** – regularly calls `fetcher.py` to keep local data up to date.
2. **Indicator Agent** – processes fetched data to compute indicators and update CSVs.
3. **Signal Agent** – reads the latest snapshot and runs `decision_maker.decide` to produce trading signals.
4. **Trading Agent** – converts signals into actual trades on a chosen exchange or smart contract, applying risk management rules.
5. **Monitoring Agent** – tracks portfolio state, logs results and raises alerts.

Agents should share state via the CSV files and knowledge base, coordinating so that each step has fresh data. Credentials such as Telegram tokens must be provided through environment variables or private configuration files, never hard-coded in the repository.

Run `pytest -q` to ensure tests pass before committing changes. Execute the full pipeline with `python master.py`.
