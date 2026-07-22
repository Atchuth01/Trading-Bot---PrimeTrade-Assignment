
import logging

from .client import BinanceAPIError, BinanceFuturesClient
from .validators import (
    validate_order_type,
    validate_price,
    validate_quantity,
    validate_side,
    validate_stop_price,
    validate_symbol,
)

logger = logging.getLogger("trading_bot.orders")


ALGO_ORDER_TYPES = {"STOP", "STOP_MARKET", "TAKE_PROFIT", "TAKE_PROFIT_MARKET", "TRAILING_STOP_MARKET"}


class OrderRequest:
    def __init__(self, symbol, side, order_type, quantity, price=None, stop_price=None):
        self.symbol = validate_symbol(symbol)
        self.side = validate_side(side)
        self.order_type = validate_order_type(order_type)
        self.quantity = validate_quantity(quantity)
        self.price = validate_price(price, self.order_type)
        self.stop_price = validate_stop_price(stop_price, self.order_type)

    @property
    def is_algo_order(self) -> bool:
        return self.order_type in ALGO_ORDER_TYPES

    def to_api_params(self) -> dict:
        if self.is_algo_order:
        
            params = {
                "algoType": "CONDITIONAL",
                "symbol": self.symbol,
                "side": self.side,
                "type": self.order_type,
                "quantity": self.quantity,
                "price": self.price,
                "triggerPrice": self.stop_price,
                "timeInForce": "GTC",
            }
            return params

        params = {
            "symbol": self.symbol,
            "side": self.side,
            "type": self.order_type,
            "quantity": self.quantity,
        }
        if self.order_type == "LIMIT":
            params["price"] = self.price
            params["timeInForce"] = "GTC"
        return params

    def summary(self) -> str:
        if self.order_type == "LIMIT":
            return (
                f"{self.side} {self.quantity} {self.symbol} @ {self.price} "
                f"({self.order_type})"
            )
        if self.order_type == "STOP":
            return (
                f"{self.side} {self.quantity} {self.symbol} "
                f"trigger @ {self.stop_price} -> limit @ {self.price} "
                f"({self.order_type})"
            )
        return f"{self.side} {self.quantity} {self.symbol} ({self.order_type})"


def place_order(client: BinanceFuturesClient, order: OrderRequest) -> dict:
    logger.info("Submitting order: %s", order.summary())
    print(f"\nOrder request : {order.summary()}")

    place = client.new_algo_order if order.is_algo_order else client.new_order
    try:
        response = place(**order.to_api_params())
    except BinanceAPIError as exc:
        print(f"FAILED: Binance rejected the order -> {exc.payload}")
        raise
    except Exception as exc:
        print(f"FAILED: {exc}")
        raise

    print("Order response:")
    if order.is_algo_order:
       
        print(f"  algoId       : {response.get('algoId')}")
        print(f"  algoStatus   : {response.get('algoStatus')}")
        print(f"  triggerPrice : {response.get('triggerPrice')}")
    else:
        print(f"  orderId      : {response.get('orderId')}")
        print(f"  status       : {response.get('status')}")
        print(f"  executedQty  : {response.get('executedQty')}")
        if response.get("avgPrice") is not None:
            print(f"  avgPrice     : {response.get('avgPrice')}")
    print("SUCCESS: order accepted by Binance Futures Testnet\n")

    return response
