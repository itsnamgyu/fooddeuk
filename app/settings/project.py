"""Add project specific settings here.

This way, you only need to update `base.py` when you fetch changes from
`django-template`. Settings that may change between different deployments
should be defined in .env.
"""
from .env_loader import fetch_env

# Prepended to base settings
# TODO: change APP
DJANGO_ENV = fetch_env("DJANGO_APP_ENV", default="DEV")
# TODO: change defaults
SITE_DOMAIN = fetch_env("SITE_DOMAIN", default="example.com")
SITE_NAME = fetch_env("SITE_NAME", default="Example Site")
SUPPORT_EMAIL = "support@" + SITE_DOMAIN

# Appended to base settings
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True
ACCOUNT_LOGIN_ON_PASSWORD_RESET = True
ACCOUNT_EMAIL_VERIFICATION = fetch_env("ACCOUNT_EMAIL_VERIFICATION", "mandatory")
