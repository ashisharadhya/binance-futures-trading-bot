"""
client.py

Thin wrapper around python-binance's Client, pinned to the Binance
Futures Testnet (USDT-M). Keeps all API-connection concerns (auth,
base URL, low-level error translation) out of the CLI and order logic.
"""

import logging
from typing import Optional

from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceOrderException, BinanceRequestException

logger = logging.getLogger("trading_bot")

FUTURES_TESTNET_BASE_URL = "https://testnet.binancefuture.com/fapi"


class BinanceClientError(Exception):
    """Wraps any low-level API/network error into a single app-level exception."""


class BinanceFuturesTestnetClient:
    """
    Wraps python-binance's Client, forced onto the Futures Testnet.

    Usage:
        client = BinanceFuturesTestnetClient(api_key, api_secret)
        response = client.create_order(symbol="BTCUSDT", side="BUY",
                                        order_type="MARKET", quantity=0.01)
    """

    def __init__(self, api_key: str, api_secret: str):
        if not api_key or not api_secret:
            raise BinanceClientError(
                "API key/secret not provided. Set BINANCE_TESTNET_API_KEY and "
                "BINANCE_TESTNET_API_SECRET environment variables, or pass --api-key/--api-secret."
            )
        try:
            # python-binance's `testnet=True` flag configures the client for
            # Spot testnet by default; for Futures we explicitly override the
            # FUTURES_URL to guarantee we hit the Futures Testnet regardless
            # of library version behaviour.
            self._client = Client(api_key, api_secret, testnet=True)
            self._client.FUTURES_URL = FUTURES_TESTNET_BASE_URL
            logger.debug("Initialized Binance client against %s", FUTURES_TESTNET_BASE_URL)
        except Exception as exc:  # covers unexpected init-time failures
            logger.exception("Failed to initialize Binance client")
            raise BinanceClientError(f"Failed to initialize Binance client: {exc}") from exc

    def create_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        quantity: float,
        price: Optional[float] = None,
    ) -> dict:
        """
        Place a MARKET or LIMIT order on Futures Testnet.
        Returns the raw JSON response dict from Binance on success.
        Raises BinanceClientError on any API/network/order failure.
        """
        order_kwargs = {
            "symbol": symbol,
            "side": side,
            "type": order_type,
            "quantity": quantity,
        }
        if order_type == "LIMIT":
            order_kwargs["price"] = price
            order_kwargs["timeInForce"] = "GTC"  # Good-Til-Cancelled, required for LIMIT

        logger.info("Sending order request: %s", order_kwargs)

        try:
            response = self._client.futures_create_order(**order_kwargs)
            logger.info("Order response received: %s", response)
            return response

        except BinanceOrderException as exc:
            logger.error("Order rejected by Binance: %s", exc)
            raise BinanceClientError(f"Order rejected: {exc}") from exc

        except BinanceAPIException as exc:
            # Raised for API-level errors, e.g. bad symbol, insufficient margin,
            # invalid precision, rate limits, auth failures, etc.
            logger.error("Binance API error (code=%s): %s", getattr(exc, "code", "?"), exc)
            raise BinanceClientError(f"Binance API error: {exc}") from exc

        except BinanceRequestException as exc:
            # Raised for malformed responses / non-JSON payloads
            logger.error("Binance request error: %s", exc)
            raise BinanceClientError(f"Binance request error: {exc}") from exc

        except (ConnectionError, TimeoutError) as exc:
            logger.error("Network error while contacting Binance: %s", exc)
            raise BinanceClientError(f"Network error: {exc}") from exc

        except Exception as exc:  # final safety net, still logged with traceback
            logger.exception("Unexpected error while placing order")
            raise BinanceClientError(f"Unexpected error: {exc}") from exc
