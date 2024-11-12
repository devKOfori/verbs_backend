from django.core.exceptions import ValidationError

def validate_shipping_cost_percentage(percentage: float):
    if percentage > 100:
        raise ValidationError(f"{percentage} cannot be greater than 100")
    

def validate_password(password: str):
    return password