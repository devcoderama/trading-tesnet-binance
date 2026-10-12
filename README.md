# Binance Testnet Trading Bot (Python, Modular)

Modular trading bot for Binance **testnet** using python-binance. Each folder has a single responsibility and its own README.md.

## Folder structure

```
trading-bot/
├── main.py                 # Entry point / orchestration loop
├── config/
│   ├── settings.py         # Env-based configuration
│   └── README.md
├── exchange/
│   ├── binance_client.py   # Binance client factory (testnet toggle)
│   └── README.md
├── market/
│   ├── data.py             # Klines / price data
│   └── README.md
├── strategy/
│   ├── strategy.py         # Signal logic (SMA crossover)
│   └── README.md
├── risk/
│   ├── risk_manager.py     # Position sizing & stop loss
│   └── README.md
├── execution/
│   ├── executor.py         # Order execution (dry-run by default)
│   └── README.md
├── utils/
│   ├── logger.py           # Logging setup
│   └── README.md
├── requirements.txt
├── .env.example
└── README.md
```

## RISK_LEVEL (pilih level risiko)
- `LOW`    : pilih koin lebih "besar"/likuid (posisi indeks 25% dari daftar).
- `MEDIUM` : default, pilih tengah daftar.
- `HIGH`   : pilih koin lebih kecil/volatil (indeks 75%).

Set di `.env` sebagai `RISK_LEVEL=LOW|MEDIUM|HIGH`. Jika `SYMBOL` diisi, level ini diabaikan.

## Membuat API Key & Secret (Binance TESTNET)
1. Buka https://testnet.binance.vision/ dan login (GitHub).
2. Klik "Generate HMAC_SHA256 Key".
3. Simpan API Key dan Secret Key (secret hanya ditampilkan sekali).
4. Isi ke `.env`: `BINANCE_API_KEY=...`, `BINANCE_API_SECRET=...`.

## Sistem Operasi yang Didukung
- Linux, macOS, Windows (Python 3.10+). Disarankan Linux/macOS.

## Instalasi
```bash
git clone https://github.com/devcoderama/trading-tesnet-binance.git
cd trading-tesnet-binance
python -m venv .venv
# Linux/macOS:
source .venv/bin/activate
# Windows:
# .venv\\Scripts\\activate
pip install -r requirements.txt
cp .env.example .env
# edit .env
```

## Cara Penggunaan
```bash
python main.py
```
- Jika `SYMBOL` kosong, bot fetch semua simbol dan simpan ke `data/symbols.json`, lalu pilih berdasarkan RISK_LEVEL.
- Default `DRY_RUN=true`: tidak kirim order nyata. Set `DRY_RUN=false` untuk testnet.
- Log tersimpan di `logs/bot.log`.

## Safety
- Default DRY_RUN=true. Never disable dry run on mainnet.
- Bot is for educational purposes.

## License
MIT
```
