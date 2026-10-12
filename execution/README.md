# execution/

Order execution wrapper around Binance client.

## Files
- `executor.py` — `Executor` with `market_buy` and `market_sell`. Honors `DRY_RUN` to avoid real orders.