import os

def _load_env(path=".env"):
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())

_load_env()

class Settings:
    API_KEY = os.getenv("BINANCE_API_KEY", "")
    API_SECRET = os.getenv("BINANCE_API_SECRET", "")
    TESTNET = os.getenv("TESTNET", "true").lower() == "true"
    SYMBOL = os.getenv("SYMBOL", "")
    RISK_LEVEL = os.getenv("RISK_LEVEL", "MEDIUM").upper()
    QUOTE_ASSET = os.getenv("QUOTE_ASSET", "USDT")
    INTERVAL = os.getenv("INTERVAL", "1m")
    QUANTITY = float(os.getenv("QUANTITY", "0.001"))
    DRY_RUN = os.getenv("DRY_RUN", "true").lower() == "true"
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

settings = Settings()
