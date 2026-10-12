import time
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

def main():
    client = BinanceClient().get_client()
    market = MarketData(client)
    strategy = SimpleStrategy()
    risk = RiskManager()
    executor = Executor(client)
    discovery = SymbolDiscovery(client)

    symbols = discovery.load()
    symbol = settings.SYMBOL or risk.select_symbol(symbols, settings.QUOTE_ASSET, settings.RISK_LEVEL)

    history = []
    prev_bal = None
    while True:
        try:
            closes = market.get_closes(symbol, settings.INTERVAL, limit=50)
            sig = strategy.signal(closes)
            price = market.latest_price(symbol)
            cur_bal = float(client.get_asset_balance(asset=settings.QUOTE_ASSET)["free"])
            if sig == "BUY":
                qty = risk.position_size(cur_bal, price)
                if qty > 0:
                    res = executor.market_buy(symbol, qty)
                    history.append([datetime.now().strftime("%H:%M:%S"), "BUY", symbol, qty, res.get("status")])
            elif sig == "SELL":
                base = symbol.replace(settings.QUOTE_ASSET, "")
                bal = float(client.get_asset_balance(asset=base)["free"])
                if bal > 0:
                    qty = round(bal, 6)
                    res = executor.market_sell(symbol, qty)
                    history.append([datetime.now().strftime("%H:%M:%S"), "SELL", symbol, qty, res.get("status")])
            render_dashboard(symbol, settings.RISK_LEVEL, settings.INTERVAL, price, sig, cur_bal, prev_bal,
                             settings.DRY_RUN, settings.TESTNET, history)
            prev_bal = cur_bal
            time.sleep(10)
        except Exception as e:
            logger.error(f"Error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
