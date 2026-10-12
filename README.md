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

## Installation

```bash
git clone https://github.com/devcoderama/trading-tesnet-binance.git
cd trading-tesnet-binance
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# edit .env with your Binance TESTNET API keys
```

Get testnet keys at https://testnet.binance.vision/

## Usage

```bash
python main.py
```

Default runs in DRY_RUN=true (no real orders). Set DRY_RUN=false in .env to send orders to testnet.
TESTNET controls whether the testnet endpoint is used.

## Safety
- Default DRY_RUN=true. Never disable dry run on mainnet.
- Bot is for educational purposes.

## License
MIT
```
