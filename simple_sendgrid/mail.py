from typing import List

from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags

from . import settings


def send_mail(
    subject: str,
    html_body: str,
    from_email: str,
    to: List[str],
    categories: List[str] = None,
    reply_to: str = None,
    headers: dict = None,
    preheader: str = None,
    template_id: str = None,
):
    """Send mail using the dynamic template specified by template_id.

    This template should include these variables:
    - Subject: {{ subject }}
    - Preheader: {{ preheader }}
    - Somewhere in the template: {{{ body }}}

    Tip: to display a name for the from_email, use this format:
    - `"Name" <email@address.com>`
    """
    if headers is None:
        headers = dict()
    headers["Reply-To"] = reply_to

    raw_body = strip_tags(html_body)
    mail = EmailMultiAlternatives(
        subject=subject, body=raw_body, from_email=from_email, to=to, headers=headers
    )
    if not template_id:
        template_id = settings.TEMPLATE_ID

    mail.template_id = template_id
    mail.dynamic_template_data = dict(
        body=html_body, subject=subject, preheader=preheader
    )
    if categories:
        mail.categories = categories

    mail.send()
