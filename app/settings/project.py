"""Add project specific settings here.

This way, you only need to update `base.py` when you fetch changes from
`django-template`. Settings that may change between different deployments
should be defined in .env.
"""
from .env_loader import fetch_env

# Prepended to base settings
# TODO: change APP
DJANGO_ENV = fetch_env("DJANGO_FD_ENV", default="DEV")
# TODO: change defaults
SITE_DOMAIN = fetch_env("SITE_DOMAIN", default="food.namgyu.io")
SITE_NAME = fetch_env("SITE_NAME", default="Food Selector")
SUPPORT_EMAIL = "its@namgyu.io"

# Appended to base settings
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True
ACCOUNT_LOGIN_ON_PASSWORD_RESET = True
ACCOUNT_EMAIL_VERIFICATION = fetch_env("ACCOUNT_EMAIL_VERIFICATION", "none")
