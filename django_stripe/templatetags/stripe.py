from django import template
from django.utils.safestring import mark_safe

from django_stripe import settings
from django_stripe.models import *

OPEN_TAG = "<script>"

CLOSE_TAG = "</script>"

INIT_TEMPLATE = """
var stripe = Stripe('{STRIPE_PUBLIC_KEY}');
"""

BUTTON_TEMPLATE = """
$('{button_selector}').click(function() {{
    stripe.redirectToCheckout({{
        sessionId: '{checkout_session_id}'
    }}).then(function (result) {{
        $('{error_selector}').html(result.error.message);
    }});
}});
"""

register = template.Library()


def _get_stripe_import_element():
    element = '<script src="https://js.stripe.com/v3/"></script>'
    return element


def _get_stripe_init_script():
    script = INIT_TEMPLATE.format(STRIPE_PUBLIC_KEY=settings.PUBLIC_KEY)
    return script


def _get_stripe_button_script(checkout_session, button_selector, error_selector):
    script = BUTTON_TEMPLATE.format(
        button_selector=button_selector,
        checkout_session_id=checkout_session.stripe_session_id,
        error_selector=error_selector,
    )
    return script


@register.simple_tag()
def stripe_import():
    return mark_safe(_get_stripe_import_element())


@register.simple_tag()
def stripe_init():
    script = _get_stripe_init_script()
    element = "\n".join((OPEN_TAG, script, CLOSE_TAG))
    return mark_safe(element)


@register.simple_tag()
def stripe_button(checkout_session, button_selector, error_selector):
    script = _get_stripe_button_script(
        checkout_session, button_selector, error_selector
    )
    element = "\n".join((OPEN_TAG, script, CLOSE_TAG))
    return mark_safe(element)


@register.simple_tag()
def stripe_standalone(checkout_session, button_selector, error_selector):
    import_element = _get_stripe_import_element()

    init_script = _get_stripe_init_script()
    button_script = _get_stripe_button_script(
        checkout_session, button_selector, error_selector
    )
    element = "\n".join((OPEN_TAG, init_script, button_script, CLOSE_TAG))
    html = "\n".join((import_element, element))

    return mark_safe(html)
