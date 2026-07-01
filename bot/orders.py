"""
orders.py

Order placement logic: takes a validated OrderRequest, submits it via the
client layer, and formats a clean summary for CLI output. This module
knows nothing about argparse or raw user input -- that's the CLI's job.
"""

import logging

from bot.client import BinanceFuturesTestnetClient, BinanceClientError
from bot.validators import OrderRequest

logger = logging.getLogger("trading_bot")


class OrderExecutionError(Exception):
    """Raised when an order could not be placed, wrapping the root cause."""


def print_request_summary(order: OrderRequest) -> None:
    print("\n--- Order Request ---")
    print(f"  Symbol     : {order.symbol}")
    print(f"  Side       : {order.side}")
    print(f"  Type       : {order.order_type}")
    print(f"  Quantity   : {order.quantity}")
    if order.order_type == "LIMIT":
        print(f"  Price      : {order.price}")
    print("----------------------\n")


def print_response_summary(response: dict) -> None:
    print("--- Order Response ---")
    print(f"  Order ID     : {response.get('orderId')}")
    print(f"  Status       : {response.get('status')}")
    print(f"  Executed Qty : {response.get('executedQty')}")
    # avgPrice is only meaningful/non-zero once a MARKET order fills,
    # or for a partially/fully filled LIMIT order
    avg_price = response.get("avgPrice")
    if avg_price is not None:
        print(f"  Avg Price    : {avg_price}")
    print("-----------------------\n")


def place_order(client: BinanceFuturesTestnetClient, order: OrderRequest) -> dict:
    """
    Places the given order via the client and returns Binance's response.
    Prints request/response summaries and success/failure messages.
    Raises OrderExecutionError on failure (already logged by the client layer).
    """
    print_request_summary(order)

    try:
        response = client.create_order(
            symbol=order.symbol,
            side=order.side,
            order_type=order.order_type,
            quantity=order.quantity,
            price=order.price,
        )
    except BinanceClientError as exc:
        print(f"FAILED: order was not placed. Reason: {exc}\n")
        raise OrderExecutionError(str(exc)) from exc

    print_response_summary(response)
    print(f"SUCCESS: {order.order_type} {order.side} order placed for {order.symbol}.\n")
    return response
