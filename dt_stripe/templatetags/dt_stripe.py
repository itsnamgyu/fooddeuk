from email import contentmanager

from django import template
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe

from .. import settings

register = template.Library()


def _tag_script(safe_html):
    script_html = "<script>"
    script_html += "\n"
    script_html += safe_html
    script_html += "\n"
    script_html += "</script>"
    return mark_safe(script_html)


@register.simple_tag()
def dt_stripe_init():
    html_for_stripe_js = '<script src="https://js.stripe.com/v3/"></script>'

    context = dict()
    context["stripe_public_key"] = settings.PUBLIC_KEY
    script = render_to_string("dt_stripe/js/init.js", context=context)
    html_for_dt_stripe = _tag_script(script)

    html = "\n".join([html_for_stripe_js, html_for_dt_stripe])
    return mark_safe(html)


@register.simple_tag()
def dt_stripe_mount_card_element(form_id, element_id, errors_id):
    context = dict()
    context["form_id"] = form_id
    context["element_id"] = element_id
    context["errors_id"] = errors_id
    script = render_to_string("dt_stripe/js/mount_card_element.js", context=context)
    return _tag_script(script)


@register.simple_tag()
def dt_stripe(form_id, element_id, errors_id):
    init = dt_stripe_init()
    mount = dt_stripe_mount_card_element(form_id, element_id, errors_id)

    html = "\n".join([init, mount])
    return mark_safe(html)
