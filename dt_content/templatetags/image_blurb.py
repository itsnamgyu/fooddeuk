import logging

from django import template
from django.conf import settings
from ..models import ImageBlurb

register = template.Library()


@register.simple_tag(takes_context=True)
def image_blurb(context, identifier, placeholder=None):
    # identifier should be in the form of '<page>:<name>'
    try:
        ib = ImageBlurb.objects.all().get(identifier=identifier)
    except ImageBlurb.DoesNotExist:
        ib = ImageBlurb.objects.create(
            identifier=identifier,
            last_known_location=context.request.path,
            placeholder=placeholder,
        )

    return ib
