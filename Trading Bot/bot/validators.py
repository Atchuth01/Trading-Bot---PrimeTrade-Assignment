
import re

VALID_SIDES = {"BUY", "SELL"}
VALID_TYPES = {"MARKET", "LIMIT", "STOP"}
SYMBOL_RE = re.compile(r"^[A-Z0-9]{5,20}$")


class ValidationError(Exception):
    pass


def validate_symbol(symbol: str) -> str:
    if symbol is None:
        raise ValidationError("Symbol is required.")
    symbol = symbol.strip().upper()
    if not SYMBOL_RE.match(symbol):
        raise ValidationError(
            f"Invalid symbol '{symbol}'. Expected a format like BTCUSDT."
        )
    return symbol


def validate_side(side: str) -> str:
    if side is None:
        raise ValidationError("Side is required.")
    side = side.strip().upper()
    if side not in VALID_SIDES:
        raise ValidationError(f"Invalid side '{side}'. Must be one of {sorted(VALID_SIDES)}.")
    return side


def validate_order_type(order_type: str) -> str:
    if order_type is None:
        raise ValidationError("Order type is required.")
    order_type = order_type.strip().upper()
    if order_type not in VALID_TYPES:
        raise ValidationError(
            f"Invalid order type '{order_type}'. Must be one of {sorted(VALID_TYPES)}."
        )
    return order_type


def validate_quantity(quantity) -> float:
    try:
        quantity = float(quantity)
    except (TypeError, ValueError):
        raise ValidationError(f"Quantity must be a number, got '{quantity}'.")
    if quantity <= 0:
        raise ValidationError("Quantity must be greater than 0.")
    return quantity


def validate_price(price, order_type: str):
    """Price is required for LIMIT and STOP (stop-limit) orders, ignored for MARKET."""
    if order_type in ("LIMIT", "STOP"):
        if price is None:
            raise ValidationError(f"Price is required for {order_type} orders.")
        try:
            price = float(price)
        except (TypeError, ValueError):
            raise ValidationError(f"Price must be a number, got '{price}'.")
        if price <= 0:
            raise ValidationError("Price must be greater than 0.")
        return price
    return None


def validate_stop_price(stop_price, order_type: str):
    """Stop (trigger) price is required for STOP orders only."""
    if order_type == "STOP":
        if stop_price is None:
            raise ValidationError("Stop price is required for STOP orders.")
        try:
            stop_price = float(stop_price)
        except (TypeError, ValueError):
            raise ValidationError(f"Stop price must be a number, got '{stop_price}'.")
        if stop_price <= 0:
            raise ValidationError("Stop price must be greater than 0.")
        return stop_price
    return None
