
"""
CLI entry point for the simplified Binance Futures Testnet trading bot.

Examples:
    python cli.py --symbol BTCUSDT --side BUY  --type MARKET --quantity 0.01
    python cli.py --symbol BTCUSDT --side SELL --type LIMIT  --quantity 0.01 --price 60000
    python cli.py --symbol BTCUSDT --side SELL --type STOP   --quantity 0.01 --stop-price 61000 --price 60900
"""
import argparse
import os
import sys

from bot.client import DEFAULT_BASE_URL, BinanceAPIError, BinanceFuturesClient
from bot.logging_config import setup_logging
from bot.orders import OrderRequest, place_order
from bot.validators import ValidationError


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cli.py",
        description="Place MARKET/LIMIT orders on Binance Futures Testnet (USDT-M).",
    )
    parser.add_argument("--symbol", required=True, help="e.g. BTCUSDT")
    parser.add_argument(
        "--side", required=True, choices=["BUY", "SELL", "buy", "sell"]
    )
    parser.add_argument(
        "--type",
        dest="order_type",
        required=True,
        choices=["MARKET", "LIMIT", "STOP", "market", "limit", "stop"],
    )
    parser.add_argument("--quantity", required=True, help="order quantity")
    parser.add_argument("--price", help="required for LIMIT and STOP orders")
    parser.add_argument(
        "--stop-price",
        dest="stop_price",
        help="trigger price, required for STOP (stop-limit) orders",
    )
    parser.add_argument(
        "--base-url",
        default=DEFAULT_BASE_URL,
        help=f"API base URL (default: {DEFAULT_BASE_URL})",
    )
    return parser


def main(argv=None) -> int:
    logger = setup_logging()
    args = build_parser().parse_args(argv)

    api_key = os.environ.get("BINANCE_API_KEY")
    api_secret = os.environ.get("BINANCE_API_SECRET")
    if not api_key or not api_secret:
        print(
            "ERROR: BINANCE_API_KEY and BINANCE_API_SECRET environment "
            "variables must be set. See README.md."
        )
        return 1

    try:
        order = OrderRequest(
            symbol=args.symbol,
            side=args.side,
            order_type=args.order_type,
            quantity=args.quantity,
            price=args.price,
            stop_price=args.stop_price,
        )
    except ValidationError as exc:
        logger.error("Validation failed: %s", exc)
        print(f"Invalid input: {exc}")
        return 1

    client = BinanceFuturesClient(api_key, api_secret, base_url=args.base_url)

    try:
        place_order(client, order)
    except BinanceAPIError:
        return 1
    except Exception as exc:
        logger.exception("Unexpected error placing order")
        print(f"Unexpected error: {exc}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
