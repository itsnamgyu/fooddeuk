from django.urls import path
from django.views.generic import TemplateView

from django_stripe import views
from django_stripe.views import checkout_completed_webhook

app_name = "django_stripe"
urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path(
        "test_checkout/create",
        views.TestCheckoutCreateView.as_view(),
        name="test_checkout_create",
    ),
    path(
        "test_checkout/payment/<str:id>",
        views.TestCheckoutPaymentView.as_view(),
        name="test_checkout_payment",
    ),
    path(
        "webhooks/checkout-completed",
        views.checkout_completed_webhook,
        name="webhook_checkout_completed",
    ),
    path("checkout-success", views.checkout_success, name="checkout_success"),
]
