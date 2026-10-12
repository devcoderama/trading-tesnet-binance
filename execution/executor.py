from config.settings import settings
from utils.logger import setup_logger

logger = setup_logger()

class Executor:
    def __init__(self, client):
        self.client = client

    def market_buy(self, symbol, quantity):
        if settings.DRY_RUN:
            logger.info(f"[DRY_RUN] MARKET BUY {symbol} qty={quantity}")
            return {"status": "dry_run", "side": "BUY", "qty": quantity}
        return self.client.order_market_buy(symbol=symbol, quantity=quantity)

    def market_sell(self, symbol, quantity):
        if settings.DRY_RUN:
            logger.info(f"[DRY_RUN] MARKET SELL {symbol} qty={quantity}")
            return {"status": "dry_run", "side": "SELL", "qty": quantity}
        return self.client.order_market_sell(symbol=symbol, quantity=quantity)
