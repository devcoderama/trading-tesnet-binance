import json
import os

class SymbolDiscovery:
    def __init__(self, client, path="data/symbols.json"):
        self.client = client
        self.path = path

    def fetch_and_save(self):
        info = self.client.get_exchange_info()
        symbols = [s["symbol"] for s in info["symbols"] if s["status"] == "TRADING"]
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        with open(self.path, "w") as f:
            json.dump({"symbols": symbols, "count": len(symbols)}, f, indent=2)
        return symbols

    def load(self):
        if not os.path.exists(self.path):
            return self.fetch_and_save()
        with open(self.path) as f:
            return json.load(f)["symbols"]
