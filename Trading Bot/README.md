# Simplified Trading Bot — Binance Futures Testnet

A small CLI application that places MARKET, LIMIT, and Stop-Limit orders
on Binance Futures Testnet (USDT-M), with input validation, structured
logging, and separated client/CLI layers.

## Project structure

```
trading_bot/
├── bot/
│   ├── __init__.py
│   ├── client.py          # Binance REST client (signing, requests, error handling)
│   ├── orders.py          # OrderRequest + place_order()
│   ├── validators.py      # input validation
│   └── logging_config.py  # rotating file + console logging setup
├── cli.py                 # CLI entry point (argparse)
├── requirements.txt
├── .env.example
└── logs/                  # trading_bot.log is written here at runtime
```

## Setup

1. **Create a Binance Futures Testnet account** at
   https://testnet.binancefuture.com and generate an API key/secret.

2. **Install dependencies** (Python 3.9+):
   ```bash
   python3 -m venv venv
   source venv/bin/activate      # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Set credentials** as environment variables (copy `.env.example` to
   `.env` and load it, or export directly):
   ```bash
   export BINANCE_API_KEY="your_testnet_api_key"
   export BINANCE_API_SECRET="your_testnet_api_secret"
   ```

## Running it

Market order:
```bash
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.01
```

Limit order:
```bash
python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.01 --price 60000
```

Stop-Limit order (bonus feature — rests as a LIMIT order once the market
trades at `--stop-price`):
```bash
python cli.py --symbol BTCUSDT --side SELL --type STOP --quantity 0.01 --stop-price 61000 --price 60900
```

Each run prints the order request, the order response (`orderId`,
`status`, `executedQty`, `avgPrice`), and a success/failure message, and
appends the same information to `logs/trading_bot.log`.

## Assumptions

- **Bonus implemented: Stop-Limit (`--type STOP`)**. It requires both
  `--stop-price` (the trigger) and `--price` (the limit price the order
  rests at once triggered), matching Binance's `STOP` order type, which
  needs both fields plus a `timeInForce`.
- `timeInForce` for LIMIT and STOP orders defaults to `GTC` since the
  spec doesn't specify one.
- Credentials are read from environment variables rather than a config
  file or CLI flags, to avoid ever writing a secret to disk or a log.
- `--base-url` defaults to the Futures Testnet
  (`https://testnet.binancefuture.com`) but is overridable for testing
  against a different environment.
- The request signature is redacted from log output; everything else
  (params, response body) is logged as-is.

## Note on the log-file deliverable

The task asks for log files from at least one MARKET and one LIMIT
order. Those have to come from an actual run against your own Testnet
account/credentials — `logs/trading_bot.log` will be created the first
time you run `cli.py` successfully, and will contain both once you've
placed one order of each type.
