from django.core.checks import register, Error

from . import settings


@register()
def check_template_id(app_configs, **kwargs):
    errors = []

    if app_configs is None or "sendgrid" in app_configs:
        if settings.TEMPLATE_ID is None:
            errors.append(
                Error(
                    "settings.SENDGRID_TEMPLATE_ID is not set.",
                    id="simple_sendgird.E001",
                )
            )

    return errors
