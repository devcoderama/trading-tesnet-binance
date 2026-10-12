import time
from config.settings import settings
from exchange.binance_client import BinanceClient
from market.data import MarketData
from market.symbols import SymbolDiscovery
from strategy.strategy import SimpleStrategy
from risk.risk_manager import RiskManager
from execution.executor import Executor
from utils.logger import setup_logger

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
    logger.info(f"Bot started. Symbol={symbol} TESTNET={settings.TESTNET} DRY_RUN={settings.DRY_RUN} RISK={settings.RISK_LEVEL}")

    while True:
        try:
            df = market.get_klines(symbol, settings.INTERVAL, limit=50)
            sig = strategy.signal(df)
            price = market.latest_price(symbol)
            logger.info(f"Price={price} Signal={sig}")
            if sig == "BUY":
                bal = float(client.get_asset_balance(asset=settings.QUOTE_ASSET)["free"])
                qty = risk.position_size(bal, price)
                if qty > 0:
                    executor.market_buy(symbol, qty)
            elif sig == "SELL":
                base = symbol.replace(settings.QUOTE_ASSET, "")
                bal = float(client.get_asset_balance(asset=base)["free"])
                if bal > 0:
                    executor.market_sell(symbol, round(bal, 6))
            time.sleep(60)
        except Exception as e:
            logger.error(f"Error: {e}")
            time.sleep(10)

if __name__ == "__main__":
    main()
