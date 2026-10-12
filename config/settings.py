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
    BOT_TYPE = os.getenv("BOT_TYPE", "Testnet Spot Bot")
    MAX_SYMBOLS = int(os.getenv("MAX_SYMBOLS", "3"))
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
    TELEGRAM_USER_ID = os.getenv("TELEGRAM_USER_ID", "")
    TELEGRAM_CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID", "")
    USE_AI = os.getenv("USE_AI", "false").lower() == "true"
    AI_PROVIDER = os.getenv("AI_PROVIDER", "gemini").lower()
    AI_API_KEY = os.getenv("AI_API_KEY", "")
    SYMBOL = os.getenv("SYMBOL", "")
    SYMBOLS = os.getenv("SYMBOLS", "")  # comma separated
    RISK_LEVEL = os.getenv("RISK_LEVEL", "MEDIUM").upper()
    QUOTE_ASSET = os.getenv("QUOTE_ASSET", "USDT")
    INTERVAL = os.getenv("INTERVAL", "1m")
    QUANTITY = float(os.getenv("QUANTITY", "0.001"))
    DRY_RUN = os.getenv("DRY_RUN", "true").lower() == "true"
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

settings = Settings()
