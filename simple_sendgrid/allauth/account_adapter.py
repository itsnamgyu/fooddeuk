from allauth.account.adapter import DefaultAccountAdapter
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.template.defaultfilters import linebreaksbr
from django.template.exceptions import TemplateDoesNotExist
from django.template.loader import render_to_string

from .. import settings


class AccountAdapter(DefaultAccountAdapter):
    def render_mail(self, template_prefix, email, context):
        """
            Renders an e-mail to `email`.  `template_prefix` identifies the
            e-mail that is to be sent, e.g. "account/email/email_confirmation"
            """
        subject = render_to_string("{0}_subject.txt".format(template_prefix), context)
        # remove superfluous line breaks
        subject = " ".join(subject.splitlines()).strip()
        subject = self.format_email_subject(subject)

        from_email = self.get_from_email()

        bodies = {}
        for ext in ["html", "txt"]:
            try:
                template_name = "{0}_message.{1}".format(template_prefix, ext)
                bodies[ext] = render_to_string(template_name, context).strip()
            except TemplateDoesNotExist:
                if ext == "txt" and not bodies:
                    # We need at least one body
                    raise
        if "txt" in bodies:
            msg = EmailMultiAlternatives(subject, bodies["txt"], from_email, [email])
            if "html" in bodies:
                msg.attach_alternative(bodies["html"], "text/html")
                html_body = bodies["html"]
            else:
                html_body = linebreaksbr(bodies["txt"])
        else:
            msg = EmailMessage(subject, bodies["html"], from_email, [email])
            msg.content_subtype = "html"  # Main content is now text/html
            body = bodies["html"]

        msg.template_id = settings.TEMPLATE_ID
        msg.dynamic_template_data = dict(body=html_body, subject=subject)
        return msg

    def send_mail(self, template_prefix, email, context):
        msg = self.render_mail(template_prefix, email, context)
        msg.send()
