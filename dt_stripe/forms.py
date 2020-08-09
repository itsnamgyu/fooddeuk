from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from .models import *


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ["name", "email", "description"]
        widgets = {"description": forms.Textarea(attrs={"rows": 3})}


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ["name", "description", "product_type"]
        widgets = {"description": forms.Textarea(attrs={"rows": 3})}

    def clean(self):
        super().clean()

        if self.cleaned_data.get(
            "product_type"
        ) == Product.SERVICE and self.cleaned_data.get("description"):
            raise ValidationError(
                _("You can't set description for services"), "service_description"
            )


class PlanForm(forms.ModelForm):
    product = forms.ModelChoiceField(queryset=Product.services)

    class Meta:
        model = Plan
        fields = [
            "name",
            "description",
            "product",
            "amount",
            "interval",
            "interval_count",
            "currency",
        ]
        widgets = {"description": forms.Textarea(attrs={"rows": 3})}


class SKUForm(forms.ModelForm):
    product = forms.ModelChoiceField(queryset=Product.goods)

    class Meta:
        model = SKU
        fields = ["name", "description", "product", "price", "currency"]
        widgets = {"description": forms.Textarea(attrs={"rows": 3})}


class SubscribeForm(forms.Form):
    plan = forms.ModelChoiceField(
        queryset=None, empty_label="Select a plan", label="Plan"
    )
    token = forms.CharField(
        max_length=128,
        required=False,
        help_text="Stripe.js token used to reset the source on the customer",
    )

    def __init__(self, *args, customer: Customer, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["plan"].queryset = Plan.objects.not_subscribed_by(customer)

    def subscribe(self, customer: Customer):
        if not hasattr(self, "cleaned_data"):
            raise Exception(
                "cleaned_data is undefined. Maybe you forgot to call `is_valid()`?."
            )
        token = self.cleaned_data.get("token", None)
        plan = self.cleaned_data["plan"]
        if token:
            customer.set_source(token)
        customer.subscribe(plan)


class UnsubscribeForm(forms.Form):
    plan = forms.ModelChoiceField(
        queryset=None, empty_label="Select a plan", label="Plan"
    )

    def __init__(self, *args, customer: Customer, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["plan"].queryset = Plan.objects.subscribed_by(customer)

    def unsubscribe(self, customer: Customer):
        if not hasattr(self, "cleaned_data"):
            raise Exception(
                "cleaned_data is undefined. Maybe you forgot to call `is_valid()`?."
            )
        plan = self.cleaned_data["plan"]
        customer.cancel_subscription(plan)


class OrderForm(forms.Form):
    sku = forms.ModelChoiceField(SKU.objects, empty_label="Select an SKU", label="SKU")
    token = forms.CharField(
        max_length=128,
        required=False,
        help_text="Stripe.js token used to reset the source on the customer",
    )
    save_source = forms.BooleanField(
        required=False, label="Use this card for future payments"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        save_source = self.cleaned_data["save_source"]
        token = self.cleaned_data["token"]

        if save_source and not token:
            raise forms.ValidationError(
                "You must provide card info to save if for later use"
            )

    def order(self, customer: Customer):
        if not hasattr(self, "cleaned_data"):
            raise Exception(
                "cleaned_data is undefined. Maybe you forgot to call `is_valid()`?."
            )
        sku = self.cleaned_data["sku"]
        save_source = self.cleaned_data["save_source"]
        token = self.cleaned_data["token"]

        if save_source:
            customer.set_source(token)
            token = None
        customer.order(sku, token)
