from django.conf import settings

PUBLIC_KEY: str = getattr(settings, "STRIPE_PUBLIC_KEY", None)
SECRET_KEY: str = getattr(settings, "STRIPE_SECRET_KEY", None)
WEBHOOK_SIGNING_SECRET: str = getattr(settings, "STRIPE_WEBHOOK_SIGNING_SECRET", None)

SUPPORT_EMAIL: str = getattr(settings, "STRIPE_SUPPORT_EMAIL", None)
