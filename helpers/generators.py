import uuid
from helpers.defaults import ITEM_TAX_DEFAULT


def generate_order_number() -> str:
    order_number = str(uuid.uuid4()).split("-")[-1]
    return order_number


def generate_order_taxes(
    items_cost: float, tax_percentage: dict = ITEM_TAX_DEFAULT
) -> float:
    taxes = {}
    for tax, percentage in tax_percentage.items():
        taxes[tax] = (percentage / 100) * float(items_cost)
    return taxes


def generate_reset_password_token() -> str:
    reset_password_token = str(uuid.uuid4()).split("-")[-1]
    return reset_password_token


def generate_shipping_cost() -> float:
    """
    this function returns the evaluated price of an order
    """
    return 0
