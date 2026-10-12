import hashlib, hmac, json, time, urllib.parse, urllib.request

class BinanceClient:
    def __init__(self):
        from config.settings import settings
        self.settings = settings
        self.api_key = settings.API_KEY
        self.api_secret = settings.API_SECRET
        self.base = "https://testnet.binance.vision" if settings.TESTNET else "https://api.binance.com"

    def get_client(self):
        return self

    def _signed_params(self, params):
        params = dict(params)
        params["timestamp"] = int(time.time() * 1000)
        qs = urllib.parse.urlencode(params)
        sig = hmac.new(self.api_secret.encode(), qs.encode(), hashlib.sha256).hexdigest()
        params["signature"] = sig
        return params

    def _request(self, method, path, params=None, signed=False):
        params = params or {}
        if signed:
            params = self._signed_params(params)
        url = self.base + path
        if method == "GET":
            if params:
                url += "?" + urllib.parse.urlencode(params)
            req = urllib.request.Request(url, headers={"X-MBX-APIKEY": self.api_key})
        else:
            data = urllib.parse.urlencode(params).encode()
            req = urllib.request.Request(url, data=data, method=method, headers={"X-MBX-APIKEY": self.api_key})
        with urllib.request.urlopen(req) as r:
            return json.loads(r.read().decode())

    def get_exchange_info(self):
        return self._request("GET", "/api/v3/exchangeInfo")

    def get_klines(self, symbol, interval, limit=100):
        return self._request("GET", "/api/v3/klines", {"symbol": symbol, "interval": interval, "limit": limit})

    def get_symbol_ticker(self, symbol):
        return self._request("GET", "/api/v3/ticker/price", {"symbol": symbol})

    def get_asset_balance(self, asset):
        acc = self._request("GET", "/api/v3/account", signed=True)
        for b in acc.get("balances", []):
            if b["asset"] == asset:
                return {"free": b["free"], "locked": b["locked"]}
        return {"free": "0", "locked": "0"}

    def order_market_buy(self, symbol, quantity):
        params = {"symbol": symbol, "side": "BUY", "type": "MARKET", "quantity": quantity}
        return self._request("POST", "/api/v3/order", params, signed=True)

    def order_market_sell(self, symbol, quantity):
        params = {"symbol": symbol, "side": "SELL", "type": "MARKET", "quantity": quantity}
        return self._request("POST", "/api/v3/order", params, signed=True)
