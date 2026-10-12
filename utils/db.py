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
    cur.execute("""CREATE TABLE IF NOT EXISTS audit_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        time TEXT,
        action TEXT,
        detail TEXT
    )""")
    cur.execute("""CREATE TABLE IF NOT EXISTS miniapp_users (
        username TEXT PRIMARY KEY,
        password_hash TEXT
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


def save_audit(action, detail):
    init_db()
    import datetime
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("INSERT INTO audit_log (time, action, detail) VALUES (?,?,?)", (datetime.datetime.now().isoformat(), action, str(detail)))
    conn.commit()
    conn.close()

def load_audit(limit=20):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT time, action, detail FROM audit_log ORDER BY id DESC LIMIT ?", (limit,))
    rows = cur.fetchall()
    conn.close()
    return [list(r) for r in rows]


import hashlib

def _hash_pw(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

def create_miniapp_user(username, password):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("INSERT INTO miniapp_users (username,password_hash) VALUES (?,?) ON CONFLICT(username) DO UPDATE SET password_hash=excluded.password_hash", (username, _hash_pw(password)))
    conn.commit()
    conn.close()

def verify_miniapp_user(username, password):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT password_hash FROM miniapp_users WHERE username=?", (username,))
    r = cur.fetchone()
    conn.close()
    return bool(r and r[0] == _hash_pw(password))

def list_miniapp_users():
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT username FROM miniapp_users")
    rows = [r[0] for r in cur.fetchall()]
    conn.close()
    return rows
