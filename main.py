import json, os, time
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

logger = setup_logger(settings.LOG_LEVEL)
HISTORY_PATH = "data/trade_history.json"

def load_history():
    if os.path.exists(HISTORY_PATH):
        try:
            with open(HISTORY_PATH) as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_history(history):
    os.makedirs(os.path.dirname(HISTORY_PATH), exist_ok=True)
    with open(HISTORY_PATH, "w") as f:
        json.dump(history, f, indent=2)

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
    client = BinanceClient().get_client()
    market = MarketData(client)
    strategy = SimpleStrategy()
    risk = RiskManager()
    executor = Executor(client)
    discovery = SymbolDiscovery(client)

    if settings.SYMBOLS:
        symbols = [s.strip() for s in settings.SYMBOLS.split(",") if s.strip()]
    elif settings.SYMBOL:
        symbols = [settings.SYMBOL]
    else:
        symbols = auto_symbols(discovery, settings.MAX_SYMBOLS)

    info = {
        "Bot Type": settings.BOT_TYPE,
        "Exchange": "Binance",
        "Symbols": ", ".join(symbols),
        "Profit Currency": settings.QUOTE_ASSET,
        "Risk Level": settings.RISK_LEVEL,
        "Interval": settings.INTERVAL,
        "Dry Run": settings.DRY_RUN,
        "Testnet": settings.TESTNET,
        "Indicators": "SMA crossover (fast/slow)",
    }

    last_orders = {s: {"buy": "-", "sell": "-"} for s in symbols}
    history = load_history()
    prev_bal = None

    while True:
        rows = []
        for symbol in symbols:
            try:
                closes = market.get_closes(symbol, settings.INTERVAL, limit=50)
                sig = strategy.signal(closes)
                ind = strategy.indicators(closes)
                price = market.latest_price(symbol)
                cur_bal = float(client.get_asset_balance(asset=settings.QUOTE_ASSET)["free"])
                if sig == "BUY":
                    qty = risk.position_size(cur_bal, price)
                    if qty > 0:
                        res = executor.market_buy(symbol, qty)
                        last_orders[symbol]["buy"] = res.get("orderId", "dry")
                        history.append([datetime.now().strftime("%H:%M:%S"), "BUY", symbol, qty, res.get("status")])
                        save_history(history)
                elif sig == "SELL":
                    base = symbol.replace(settings.QUOTE_ASSET, "")
                    bal = float(client.get_asset_balance(asset=base)["free"])
                    if bal > 0:
                        qty = round(bal, 6)
                        res = executor.market_sell(symbol, qty)
                        last_orders[symbol]["sell"] = res.get("orderId", "dry")
                        history.append([datetime.now().strftime("%H:%M:%S"), "SELL", symbol, qty, res.get("status")])
                        save_history(history)
                rows.append({
                    "symbol": symbol,
                    "interval": settings.INTERVAL,
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
