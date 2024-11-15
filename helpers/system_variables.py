import os
from django.apps import apps
from dotenv import load_dotenv

load_dotenv(".env")

TAX_PERCENTAGE = 0
UNREGISTERED_USER_PASSWORD = os.getenv("UNREGISTERED_USER_PASSWORD")
UNREGISTERED_USER_EMAIL = "unregistereduser.verbs@gmail.com"

PROMO_CODE_STATUS_CHOICES = {
    ("invalid", "Invalid"),
    ("valid", "Valid")
}

TAXES = {
    "VAT": 0,
}