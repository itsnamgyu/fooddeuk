from django import template

from .. import models
from ..models import ContentSection, ContentBlock

register = template.Library()


@register.simple_tag(takes_context=True)
def content_section(context, key):
    url = context.request.path
    section, created = ContentSection.objects.get_or_create(
        key=key, defaults=dict(static_location=url)
    )
    return section


@register.simple_tag(takes_context=True)
def content_block(context, key, block_type):
    url = context.request.path
    BlockClass = models.content_block_classes[block_type]
    block, created = BlockClass.objects.get_or_create(
        key=key, defaults=dict(static_location=url)
    )
    return block


@register.simple_tag(takes_context=False)
def content_block_classes():
    return list(models.content_block_classes.values())
