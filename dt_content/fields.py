from django import forms
from django.db import models
from django_summernote.widgets import SummernoteWidget


class SummernoteField(models.TextField):
    def __init__(self, *args, **kwargs):
        super(SummernoteField, self).__init__(*args, **kwargs)

    def formfield(self, **kwargs):
        defaults = {"form_class": self._get_form_class()}
        defaults.update(kwargs)
        return super(SummernoteField, self).formfield(**defaults)

    @staticmethod
    def _get_form_class():
        return SummernoteFormField


class SummernoteFormField(forms.fields.CharField):
    def __init__(self, *args, **kwargs):
        kwargs.update({"widget": SummernoteWidget()})
        super(SummernoteFormField, self).__init__(*args, **kwargs)
