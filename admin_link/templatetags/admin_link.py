"""Based on the [Django template tag for admin urls](django/django/contrib/admin/templatetags/admin_urls.py).
"""

from django import template
from django.template.loader import render_to_string
from django.urls import reverse

from .. import utils

register = template.Library()

ACTIONS = ("changelist", "add", "change", "delete")


@register.simple_tag(takes_context=True)
def admin_link_url(context, instance, action: str, require_permission=True):
    user = context.request.user
    has_permission = utils.has_permission(context, instance, action)

    if require_permission and not has_permission:
        return None

    return utils.get_admin_link_url(context, instance, action)


@register.simple_tag(takes_context=True)
def admin_link(
    context, instance, action: str, label: str = None, require_permission=True
):
    url = admin_link_url(context, instance, action, require_permission)

    try:
        app_label = instance._meta.app_label.replace("_", " ")
        model_name = instance._meta.model_name.replace("_", " ")
    except AttributeError:
        return ""

    local_context = dict(
        url=url, label=label, app_label=app_label, model_name=model_name
    )

    if url:
        return render_to_string(
            "admin_link/{}.html".format(action), context=local_context
        )
    else:
        return ""
