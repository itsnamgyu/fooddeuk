import hashlib

from django import forms
from django.utils.translation import gettext_lazy as _
import allauth


class SignupForm(allauth.account.forms.SignupForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["first_name"] = forms.fields.CharField(
            label=_("First name"), max_length=30
        )
        self.fields["last_name"] = forms.fields.CharField(
            label=_("Last name"), max_length=150
        )
        self.fields["secret"] = forms.fields.CharField(
            label=_("Secret Key"), max_length=150
        )

    def clean_secret(self):
        data = self.cleaned_data['secret']
        hashed = hashlib.sha256(str.encode(data)).hexdigest()
        answer = '6e73edb1ca687aba0fc1247c2215b3f6106ca16835677d63cd29a2049c8fc7be'
        if hashed != answer:
            raise forms.ValidationError("Incorrect secret key!")
        return data

    def save(self, request):
        user = super().save(request)
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.save()
        return user
