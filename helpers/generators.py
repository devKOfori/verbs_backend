import uuid

def generate_order_number() -> str:
    order_number = str(uuid.uuid4()).split("-")[-1]
    return order_number

def generate_tax(item_price: float, tax_percentage: float) -> float:
    return (1 + (tax_percentage / 100)) * float(item_price)

def generate_reset_password_token() -> str:
    reset_password_token = str(uuid.uuid4()).split("-")[-1]
    return reset_password_token