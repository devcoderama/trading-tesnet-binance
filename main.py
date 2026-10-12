import time
from config.settings import settings
from exchange.binance_client import BinanceClient
from market.data import MarketData
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

    logger.info(f"Bot started. Symbol={settings.SYMBOL} TESTNET={settings.TESTNET} DRY_RUN={settings.DRY_RUN}")
    while True:
        try:
            df = market.get_klines(settings.SYMBOL, settings.INTERVAL, limit=50)
            sig = strategy.signal(df)
            price = market.latest_price(settings.SYMBOL)
            logger.info(f"Price={price} Signal={sig}")
            if sig == "BUY":
                bal = float(client.get_asset_balance(asset="USDT")["free"])
                qty = risk.position_size(bal, price)
                if qty > 0:
                    executor.market_buy(settings.SYMBOL, qty)
            elif sig == "SELL":
                bal = float(client.get_asset_balance(asset=settings.SYMBOL.replace("USDT",""))["free"])
                if bal > 0:
                    executor.market_sell(settings.SYMBOL, round(bal, 6))
            time.sleep(60)
        except Exception as e:
            logger.error(f"Error: {e}")
            time.sleep(10)

if __name__ == "__main__":
    main()
