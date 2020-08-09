from django.apps import apps
from django.db import models


class ServiceManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(product_type="service")


class GoodManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(product_type="good")


class PlanManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset()

    def subscribed_by(self, customer):
        Subscription = apps.get_model("dt_stripe", "Subscription")
        return self.get_queryset().filter(
            subscriptions__in=Subscription.objects.filter(
                customer=customer, status=Subscription.SUBSCRIPTION_ACTIVE
            )
        )

    def not_subscribed_by(self, customer):
        Subscription = apps.get_model("dt_stripe", "Subscription")
        return self.get_queryset().exclude(
            subscriptions__in=Subscription.objects.filter(
                customer=customer, status=Subscription.SUBSCRIPTION_ACTIVE
            )
        )
