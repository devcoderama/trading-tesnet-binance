# exchange/

Binance client factory. Centralizes client creation and testnet toggle.

## Files
- `binance_client.py` — `BinanceClient` wrapping `binance.client.Client`, selecting testnet endpoint based on `settings.TESTNET`. Exposes `get_client()`.