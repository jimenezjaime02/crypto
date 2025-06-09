# Development Notes

This repository currently fetches cryptocurrency market data, calculates indicators, and logs simple "BUY/SELL/HOLD" signals. It does not automate trading or integrate with an exchange API.

## Summary of Next Steps

1. **Exchange Integration**
   - Research APIs (Binance, Coinbase, etc.) to place orders.
   - Investigate authentication, order types, and error handling.

2. **Notification and Automation**
   - Optionally re-enable Telegram notifications or add other alert channels.
   - Schedule the pipeline for regular runs (cron or a long-running process).

3. **Improve Decision Logic**
   - Expand beyond RSI and MACD histogram thresholds.
   - Explore additional technical indicators or machine-learning approaches.

4. **Data Storage & Efficiency**
   - Consider using a database instead of CSV for historical records and backtesting.

5. **Risk Management & Order Tracking**
   - Implement position sizing, stop-loss, take-profit, and log all trades.

6. **Testing & Reliability**
   - Increase test coverage, mock network responses, and add tests for new features.

7. **Deployment & Configuration**
   - Manage credentials via environment variables or a secrets manager.
   - Evaluate Docker and CI/CD for consistent deployments.

8. **Security & Compliance**
   - Secure API keys, handle errors gracefully, and research regulatory requirements.

## Current Status of Automation

The decision logic in `decision_maker.py` returns only strings and does not trigger trades:

```python
def decide(row: Dict[str, str]) -> str:
    if rsi < 30 and macd_hist > 0:
        return "BUY"
    if rsi > 70 and macd_hist < 0:
        return "SELL"
    return "HOLD"
```

`master.py` runs the pipeline and can send an optional Telegram summary, but no orders are executed. Integrating an exchange API and an order-management layer would be required to fully automate trading.
