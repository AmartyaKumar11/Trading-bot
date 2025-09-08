# Binance Futures Trading Bot (Python)

## Overview
This is a Python-based trading bot for **Binance USDT-M Futures Testnet**. It allows you to place crypto futures trades using a command-line interface (CLI) or interactive menu. The bot uses the `python-binance` library and supports market, limit, and stop orders, with proper quantity/price validation.

---

## Features
- Connects to Binance Futures Testnet (safe for practice)
- Place BUY/SELL orders for popular crypto pairs (e.g., BTCUSDT, ETHUSDT, LINKUSDT)
- Supports Market, Limit, and Stop orders
- Interactive CLI with menu and prompts
- Quantity/price rounding based on Binance exchange filters
- Minimum $5 order value enforced
- Logging and error handling
- Secure API key management via `.env` file

---

## What You Can Trade
- **Crypto futures pairs only** (e.g., BTCUSDT, ETHUSDT, LINKUSDT)
- **NOT for stocks** (Microsoft, Tata Steel, etc.)

---

## Setup Instructions

### 1. Clone or Download
Place all files in a folder, e.g. `Trading bot`

### 2. Create a Virtual Environment
```
python -m venv .venv
```
Activate it:
- Windows: `.venv\Scripts\activate`
- Linux/Mac: `source .venv/bin/activate`

### 3. Install Requirements
```
pip install python-binance python-dotenv
```

### 4. Add Your API Keys
Create a `.env` file in the project folder:
```
API_KEY=your_testnet_api_key
API_SECRET=your_testnet_api_secret
```
Get keys from https://testnet.binancefuture.com

### 5. Run the Bot
- **Interactive CLI:**
  ```
  python interactive_trade.py
  ```
- **Quick CLI:**
  ```
  python trade.py buy BTCUSDT 0.01
  ```

---

## Files
- `interactive_trade.py` — Main interactive CLI bot
- `trade.py` — Quick command-line bot
- `bot.py` — Original implementation
- `.env` — API credentials (not shared)
- `check_precision.py` / `test_rounding.py` — Utility scripts for debugging

---

## Notes
- This bot is for **educational and testing purposes** only.
- It does NOT trade stocks or real money.
- For live trading, use the mainnet and real API keys (at your own risk).

---

## License
MIT License

---

## Author
Created by Amartya Kumar
