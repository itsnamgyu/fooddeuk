from django.conf import settings

TEMPLATE_ID: str = getattr(settings, "SENDGRID_TEMPLATE_ID", None)
