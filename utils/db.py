import os, sqlite3, json

DB_PATH = "data/trading.db"

def init_db():
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS trades (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        time TEXT, side TEXT, symbol TEXT, qty REAL, status TEXT, price REAL
    )""")
    cur.execute("""CREATE TABLE IF NOT EXISTS config (
        key TEXT PRIMARY KEY,
        value TEXT
    )""")
    # remove telegram secrets from DB (stored in .env)
    for k in ("TELEGRAM_BOT_TOKEN", "TELEGRAM_USER_ID", "TELEGRAM_CHANNEL_ID"):
        cur.execute("DELETE FROM config WHERE key=?", (k,))
    conn.commit()
    cur.execute("SELECT COUNT(*) FROM config")
    if cur.fetchone()[0] == 0:
        defaults = {
            "MAX_SYMBOLS": os.getenv("MAX_SYMBOLS", "3"),
            "USE_AI": os.getenv("USE_AI", "false"),
            "AI_PROVIDER": os.getenv("AI_PROVIDER", "gemini"),
            "AI_API_KEY": os.getenv("AI_API_KEY", ""),
            "SYMBOL": os.getenv("SYMBOL", ""),
            "RISK_LEVEL": os.getenv("RISK_LEVEL", "MEDIUM"),
            "QUOTE_ASSET": os.getenv("QUOTE_ASSET", "USDT"),
            "INTERVAL": os.getenv("INTERVAL", "1m"),
            "QUANTITY": os.getenv("QUANTITY", "0.001"),
            "DRY_RUN": os.getenv("DRY_RUN", "true"),
            "LOG_LEVEL": os.getenv("LOG_LEVEL", "INFO"),
            "BOT_TYPE": os.getenv("BOT_TYPE", "Testnet Spot Bot"),
        }
        for k, v in defaults.items():
            cur.execute("INSERT INTO config (key,value) VALUES (?,?)", (k, str(v)))
        conn.commit()
    conn.close()

def save_trade(row):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("INSERT INTO trades (time, side, symbol, qty, status, price) VALUES (?,?,?,?,?,?)", row)
    conn.commit()
    conn.close()

def load_trades(limit=50):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT time, side, symbol, qty, status FROM trades ORDER BY id DESC LIMIT ?", (limit,))
    rows = cur.fetchall()
    conn.close()
    return [list(r) for r in reversed(rows)]

def get_config(key, default=None):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT value FROM config WHERE key=?", (key,))
    r = cur.fetchone()
    conn.close()
    return r[0] if r else default

def set_config(key, value):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("INSERT INTO config (key,value) VALUES (?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value", (key, str(value)))
    conn.commit()
    conn.close()
