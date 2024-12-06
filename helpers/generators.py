import uuid
import random
from helpers.defaults import ITEM_TAX_DEFAULT
from helpers.system_variables import TAXES


def generate_registration_code(code_length: int = 5) -> str:
    return "".join([str(n) for n in random.choices(population=range(100), k=code_length)])


def generate_order_number() -> str:
    order_number = str(uuid.uuid4()).split("-")[-1]
    return order_number


def generate_order_taxes(items_cost: float, tax_percentage: dict = TAXES) -> dict:
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
