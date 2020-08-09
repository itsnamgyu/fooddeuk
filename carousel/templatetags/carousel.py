import logging

from django import template
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe

from ..models import Carousel

register = template.Library()


@register.simple_tag(takes_context=True)
def carousel(context, identifier):
    try:
        carousel = Carousel.objects.all().get(identifier=identifier)
    except ObjectDoesNotExist:
        carousel = Carousel.objects.create(identifier=identifier)
        logging.info(
            "Carousel {} automatically created while loading {}".format(
                identifier, context.request.get_full_path()
            )
        )
    return carousel
