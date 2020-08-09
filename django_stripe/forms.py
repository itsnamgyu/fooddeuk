from django import forms

from django_stripe.models import Checkout


class TestCheckoutForm(forms.ModelForm):
    class Meta:
        model = Checkout
        fields = ("amount", "name", "description", "prefilled_email")
