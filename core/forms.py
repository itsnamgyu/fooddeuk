from django import forms

from core.models import *


class VoteForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["user"].disabled = True
        self.fields["photo"].disabled = True

    class Meta:
        model = Vote
        fields = ["user", "photo", "selection"]
        widgets = {
            "user": forms.HiddenInput(),
            "photo": forms.HiddenInput(),
        }
