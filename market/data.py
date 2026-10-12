class MarketData:
    def __init__(self, client):
        self.client = client

    def get_closes(self, symbol, interval, limit=100):
        raw = self.client.get_klines(symbol=symbol, interval=interval, limit=limit)
        return [float(row[4]) for row in raw]

    def latest_price(self, symbol):
        ticker = self.client.get_symbol_ticker(symbol=symbol)
        return float(ticker["price"])
