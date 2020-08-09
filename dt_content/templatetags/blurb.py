import logging

from django import template
from django.conf import settings
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from django.urls import reverse
from django.utils.html import escape, format_html
from django.utils.safestring import mark_safe

from ..models import Blurb

register = template.Library()


@register.simple_tag(takes_context=True)
def blurb(context, identifier, plain_text=False):
    # identifier should be in the form of '.../.../...'
    try:
        blurb = Blurb.objects.all().get(identifier=identifier)
        if blurb.plain_text != plain_text:
            blurb.plain_text = plain_text
            blurb.save()
            logging.warning(
                "Auto-correcting blurb type of {} to plain_text={}".format(
                    blurb.display_name, plain_text
                )
            )
    except ObjectDoesNotExist:
        blurb = Blurb.objects.create(
            identifier=identifier,
            content=None,
            plain_text=plain_text,
            last_known_location=context.request.path,
        )

    return blurb
