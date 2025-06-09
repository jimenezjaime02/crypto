# Suggested Improvements

This list contains ideas for future work to enhance maintainability and extend the current trading utilities.

1. **Exchange Integration**
   - Connect to a Base network DEX or centralised exchange to place real or paper trades.
   - Include authentication, order placement helpers and basic risk management.

2. **Configuration Cleanup**
   - Expose common settings such as `vs_currency`, `days` and `interval` via a configuration file or command-line arguments.
   - Continue consolidating duplicated logic into utility modules (e.g. log setup, asset loading).

3. **Testing and CI**
   - Increase coverage for `fetcher.py`, `io_utils.py` and new trading functions using mocked HTTP responses.
   - Add a CI workflow to run tests automatically.

4. **Data Storage**
   - Evaluate replacing CSV files with a lightweight database for faster queries and easier backtesting.

5. **Code Quality**
   - Apply a formatter such as `black` and a linter like `flake8` or `ruff` to keep style consistent.
   - Introduce type checking with `mypy`.

6. **Documentation**
   - Expand the README with usage examples, environment setup and how the automation pieces fit together.

These tasks will help transition the project from a data collection toolkit to a more robust trading bot.
