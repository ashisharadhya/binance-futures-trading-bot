"""
cli.py

Command-line entry point for the trading bot.

Examples:
    # Market order
    python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.01

    # Limit order
    python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.01 --price 60000

Credentials can be supplied via environment variables (recommended):
    export BINANCE_TESTNET_API_KEY="your_key"
    export BINANCE_TESTNET_API_SECRET="your_secret"

...or via --api-key / --api-secret flags (not recommended, ends up in shell history).
"""

import argparse
import os
import sys

from bot.client import BinanceFuturesTestnetClient, BinanceClientError
from bot.logging_config import setup_logging
from bot.orders import place_order, OrderExecutionError
from bot.validators import build_order_request, ValidationError

logger = setup_logging()


def parse_args(argv=None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Place MARKET or LIMIT orders on Binance Futures Testnet (USDT-M)."
    )
    parser.add_argument("--symbol", required=True, help="Trading pair, e.g. BTCUSDT")
    parser.add_argument("--side", required=True, choices=["BUY", "SELL", "buy", "sell"],
                         help="Order side")
    parser.add_argument("--type", required=True, dest="order_type",
                         choices=["MARKET", "LIMIT", "market", "limit"],
                         help="Order type")
    parser.add_argument("--quantity", required=True, type=float,
                         help="Order quantity (base asset units)")
    parser.add_argument("--price", required=False, type=float, default=None,
                         help="Limit price (required for LIMIT orders only)")
    parser.add_argument("--api-key", required=False, default=None,
                         help="Binance Futures Testnet API key (or set BINANCE_TESTNET_API_KEY)")
    parser.add_argument("--api-secret", required=False, default=None,
                         help="Binance Futures Testnet API secret (or set BINANCE_TESTNET_API_SECRET)")

    return parser.parse_args(argv)


def main(argv=None) -> int:
    args = parse_args(argv)

    # 1. Validate input
    try:
        order = build_order_request(
            symbol=args.symbol,
            side=args.side,
            order_type=args.order_type,
            quantity=args.quantity,
            price=args.price,
        )
    except ValidationError as exc:
        logger.error("Input validation failed: %s", exc)
        print(f"FAILED: invalid input. {exc}")
        return 1

    # 2. Resolve credentials (CLI args take priority over env vars)
    api_key = args.api_key or os.environ.get("BINANCE_TESTNET_API_KEY")
    api_secret = args.api_secret or os.environ.get("BINANCE_TESTNET_API_SECRET")

    # 3. Build client and place order
    try:
        client = BinanceFuturesTestnetClient(api_key, api_secret)
        place_order(client, order)
    except BinanceClientError as exc:
        logger.error("Client initialization failed: %s", exc)
        print(f"FAILED: {exc}")
        return 1
    except OrderExecutionError:
        # Already logged and printed inside place_order/client layer
        return 1
    except Exception as exc:
        logger.exception("Unexpected error in CLI execution")
        print(f"FAILED: unexpected error. {exc}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
