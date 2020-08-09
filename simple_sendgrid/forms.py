from django import forms
from django.forms.widgets import TextInput
from django_summernote.widgets import SummernoteWidget

from .mail import send_mail


class TestMailForm(forms.Form):
    subject = forms.CharField()
    from_name = forms.CharField(initial="John Doe")
    from_email = forms.CharField()
    to = forms.EmailField()
    body = forms.CharField(widget=SummernoteWidget())
    reply_to = forms.CharField(required=False)

    def send_mail(self):
        f = self.cleaned_data
        subject = f["subject"]
        from_email = '"{name}" <{email}>'.format(
            name=f["from_name"], email=f["from_email"]
        )
        to = [f["to"]]
        body = f["body"]
        reply_to = f["reply_to"]
        if not reply_to:
            reply_to = None

        send_mail(subject, body, from_email, to, reply_to=reply_to)
