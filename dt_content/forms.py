from django import forms
from django_summernote.widgets import SummernoteInplaceWidget

from .fields import SummernoteFormField
from .models import *


class MenuForm(forms.ModelForm):
    parent = forms.ModelChoiceField(
        Menu.objects.filter(parent=None),
        disabled=True,
        required=False,
        initial=None,
        widget=forms.HiddenInput(),
    )

    class Meta:
        fields = ["title", "url_slug", "disabled", "redirect_to", "parent"]
        model = Menu


class SubmenuForm(forms.ModelForm):
    parent = forms.ModelChoiceField(
        Menu.objects.filter(parent=None), disabled=True, widget=forms.HiddenInput()
    )

    class Meta:
        model = Menu
        fields = ["title", "url_slug", "disabled", "redirect_to", "parent"]


class RichTextBlockCreateForm(forms.ModelForm):
    section = forms.ModelChoiceField(
        ContentSection.objects.get_queryset(), disabled=True
    )

    class Meta:
        model = RichTextBlock
        fields = ["content", "section"]


class BlurbForm(forms.ModelForm):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if "instance" in kwargs and kwargs["instance"].plain_text:
            self.fields["content"] = forms.CharField(
                widget=forms.Textarea(attrs=dict(rows=3))
            )
        else:
            self.fields["content"] = SummernoteFormField()

    class Meta:
        model = Blurb
        fields = ["content"]


class ImageBlurbForm(forms.ModelForm):
    class Meta:
        model = ImageBlurb
        fields = ["image"]
