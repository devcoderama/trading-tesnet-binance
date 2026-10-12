import time, os
from utils.db import init_db, save_trade, load_trades, get_config
from utils.telegram import send_telegram, start_telegram_polling
from utils.telethon_bot import start_telethon
from datetime import datetime
from config.settings import settings
from exchange.binance_client import BinanceClient
from market.data import MarketData
from market.symbols import SymbolDiscovery
from strategy.strategy import SimpleStrategy
from risk.risk_manager import RiskManager
from execution.executor import Executor
from utils.logger import setup_logger
from ui.dashboard import render_dashboard
from utils.ai import get_ai_signal

logger = setup_logger(settings.LOG_LEVEL)

def auto_symbols(discovery, n=3):
    syms = [s for s in discovery.load() if s.endswith(settings.QUOTE_ASSET)]
    syms = sorted(set(syms))
    if not syms:
        return []
    idxs = [int((len(syms)-1)*p) for p in (0.25, 0.5, 0.75)]
    out = []
    for i in idxs:
        if syms[i] not in out:
            out.append(syms[i])
    return out[:n]

def main():
    init_db()
    if not start_telethon():
        start_telegram_polling()
    client = BinanceClient().get_client()
    market = MarketData(client)
    strategy = SimpleStrategy()
    risk = RiskManager()
    executor = Executor(client)
    discovery = SymbolDiscovery(client)

    cfg_symbols = get_config("SYMBOLS", settings.SYMBOLS) or ""
    cfg_symbol = get_config("SYMBOL", settings.SYMBOL) or ""
    cfg_interval = get_config("INTERVAL", settings.INTERVAL) or settings.INTERVAL

    if cfg_symbols:
        symbols = [s.strip() for s in cfg_symbols.split(",") if s.strip()]
    elif cfg_symbol:
        symbols = [cfg_symbol]
    else:
        max_sym = int(get_config("MAX_SYMBOLS", settings.MAX_SYMBOLS) or settings.MAX_SYMBOLS)
        symbols = auto_symbols(discovery, max_sym)

    info = {
        "Bot Type": settings.BOT_TYPE,
        "Exchange": "Binance",
        "Symbols": ", ".join(symbols),
        "Profit Currency": settings.QUOTE_ASSET,
        "Risk Level": get_config("RISK_LEVEL", settings.RISK_LEVEL),
        "Interval": cfg_interval,
        "Dry Run": settings.DRY_RUN,
        "Testnet": settings.TESTNET,
        "Indicators": "AI multi-provider" if settings.USE_AI else "SMA crossover (fast/slow)",
        "AI Mode": "ON" if settings.USE_AI else "OFF",
        "AI Providers": settings.AI_PROVIDERS if settings.USE_AI else "-",
    }

    info["Balance"] = float(client.get_asset_balance(asset=settings.QUOTE_ASSET)["free"])
    last_orders = {s: {"buy": "-", "sell": "-"} for s in symbols}
    history = load_trades()
    prev_bal = None

    while True:
        if get_config("BOT_PAUSED", "false").lower() == "true":
            time.sleep(5)
            continue
        rows = []
        for symbol in symbols:
            try:
                closes = market.get_closes(symbol, cfg_interval, limit=50)
                if settings.USE_AI:
                    sig, ai_used = get_ai_signal(closes, symbol)
                else:
                    sig = strategy.signal(closes)
                    ai_used = "SMA"
                ind = strategy.indicators(closes)
                price = market.latest_price(symbol)
                cur_bal = float(client.get_asset_balance(asset=settings.QUOTE_ASSET)["free"])
                if sig == "BUY":
                    qty = risk.position_size(cur_bal, price)
                    if qty > 0:
                        res = executor.market_buy(symbol, qty)
                        last_orders[symbol]["buy"] = res.get("orderId", "dry")
                        row = [datetime.now().strftime("%H:%M:%S"), "BUY", symbol, qty, res.get("status"), price]
                        history.append(row[:5])
                        save_trade(row)
                        send_telegram(f"BUY {symbol} qty={qty} price={price} via {ai_used}")
                elif sig == "SELL":
                    base = symbol.replace(settings.QUOTE_ASSET, "")
                    bal = float(client.get_asset_balance(asset=base)["free"])
                    if bal > 0:
                        qty = round(bal, 6)
                        res = executor.market_sell(symbol, qty)
                        last_orders[symbol]["sell"] = res.get("orderId", "dry")
                        row = [datetime.now().strftime("%H:%M:%S"), "SELL", symbol, qty, res.get("status"), price]
                        history.append(row[:5])
                        save_trade(row)
                        send_telegram(f"SELL {symbol} qty={qty} price={price} via {ai_used}")
                rows.append({
                    "symbol": symbol,
                    "interval": cfg_interval,
                    "indicators": ind,
                    "price": price,
                    "signal": sig,
                    "last_buy": last_orders[symbol]["buy"],
                    "last_sell": last_orders[symbol]["sell"],
                    "fast": strategy.fast,
                    "slow": strategy.slow,
                })
                prev_bal = cur_bal
            except Exception as e:
                logger.error(f"{symbol}: {e}")
        render_dashboard(info, rows, history)
        time.sleep(10)

if __name__ == "__main__":
    main()
