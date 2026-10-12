from binance.client import Client
from config.settings import settings

class BinanceClient:
    def __init__(self):
        self.client = Client(settings.API_KEY, settings.API_SECRET, testnet=settings.TESTNET)

    def get_client(self):
        return self.client
