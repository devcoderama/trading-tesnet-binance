import pandas as pd

class MarketData:
    def __init__(self, client):
        self.client = client

    def get_klines(self, symbol, interval, limit=100):
        raw = self.client.get_klines(symbol=symbol, interval=interval, limit=limit)
        df = pd.DataFrame(raw, columns=[
            "open_time","open","high","low","close","volume",
            "close_time","quote_asset_volume","num_trades",
            "taker_buy_base","taker_buy_quote","ignore"
        ])
        for col in ["open","high","low","close","volume"]:
            df[col] = df[col].astype(float)
        df["open_time"] = pd.to_datetime(df["open_time"], unit="ms")
        return df

    def latest_price(self, symbol):
        ticker = self.client.get_symbol_ticker(symbol=symbol)
        return float(ticker["price"])
