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
