import datetime
import logging
import uuid
from urllib.parse import urljoin

import stripe
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.contrib import admin
from django.contrib.sites.models import Site
from django.utils.translation import gettext_lazy as _
from django.views.generic.edit import ModelFormMixin

from django_stripe import settings

logger = logging.getLogger(__name__)
ADMIN_TEST_CHECKOUT_KEY = "ADMIN_TEST_CHECKOUT"


class TestCheckoutManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(key=ADMIN_TEST_CHECKOUT_KEY)


class Checkout(models.Model):
    COMPLETE = "CO"
    INCOMPLETE = "IC"
    MULTIPLE_CHARGES = "MC"
    status_choices = (
        (COMPLETE, "Complete"),
        (INCOMPLETE, "Incomplete"),
        (MULTIPLE_CHARGES, "Multiple Charges"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    date_created = models.DateTimeField(_("date created"), auto_now_add=True)
    date_status_modified = models.DateTimeField(
        _("date status modified"), auto_now=True
    )
    status = models.CharField(
        _("status"), max_length=2, choices=status_choices, default=INCOMPLETE
    )
    amount = models.IntegerField(_("price amount"))
    currency = models.CharField(_("currency"), max_length=3, default="usd")
    quantity = models.IntegerField(_("quantity"), default=1)

    name = models.TextField(_("name"))
    description = models.TextField(_("description"), null=True, blank=True)
    key = models.CharField(_("key"), max_length=256, null=True, blank=True)
    prefilled_email = models.EmailField(_("prefilled email"), null=True, blank=True)

    objects = models.Manager()
    checkouts = models.Manager()
    test_checkouts = TestCheckoutManager()

    class Meta:
        indexes = [models.Index(fields=["key"])]

    def get_session(
        self, cancel_url, success_url, reuse_threshold=datetime.timedelta(hours=12)
    ):
        session = None
        try:
            latest_session = self.checkout_set.latest("date_created")
            reuse = True
            reuse = reuse and (latest_session.cancel_url == cancel_url)
            reuse = reuse and (latest_session.success_url == success_url)
            expired = latest_session.date_created < timezone.now() - reuse_threshold
            reuse = reuse and not expired
            if reuse:
                session = latest_session
        except ObjectDoesNotExist:
            pass

        if not session:
            session = CheckoutSession.init_session(self, cancel_url, success_url)

        return session


@admin.register(Checkout)
class CheckoutAdmin(admin.ModelAdmin):
    list_display = ("key", "name", "status", "date_created")
    ordering = ("-date_created",)


class CheckoutSession(models.Model):
    checkout = models.ForeignKey(
        Checkout, on_delete=models.SET_NULL, related_name="checkout_set", null=True
    )
    stripe_session_id = models.CharField(
        _("stripe checkout id"), max_length=128, null=True, blank=True
    )
    date_created = models.DateTimeField(_("date created"), auto_now_add=True)
    date_completed = models.DateTimeField(_("date completed"), null=True, blank=True)
    completed = models.BooleanField(_("completed"), default=False)

    cancel_url = models.URLField(_("cancel url"))
    success_url = models.URLField(_("success_url"))

    class Meta:
        indexes = [
            models.Index(fields=["stripe_session_id", "date_created"]),
            models.Index(fields=["date_created"]),
        ]

    @staticmethod
    def verify(stripe_session_id):
        session = CheckoutSession.objects.filter(
            stripe_session_id=stripe_session_id
        ).first()
        if session:
            if session.completed:
                logger.warning("duplicate verification of checkout session ")
            else:
                session.completed = True
                session.save()
                checkout = session.checkout
                if checkout.status == Checkout.INCOMPLETE:
                    checkout.status = Checkout.COMPLETE
                elif checkout.status == Checkout.COMPLETE:
                    checkout.status = Checkout.MULTIPLE_CHARGES
                checkout.save()
            return True
        else:
            return False

    @staticmethod
    def init_session(checkout: Checkout, cancel_url, success_url):
        session = CheckoutSession(
            checkout=checkout, cancel_url=cancel_url, success_url=success_url
        )
        session.save()

        stripe_success_url = urljoin(
            settings.STATIC_HOST,
            reverse("django_stripe:checkout_success") + "?id={}".format(session.id),
        )
        print(stripe_success_url)

        if checkout.description:
            description = checkout.description
        else:
            description = None

        if checkout.prefilled_email:
            customer_email = checkout.prefilled_email
        else:
            customer_email = None

        stripe.api_key = settings.SECRET_KEY
        stripe_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                dict(
                    name=checkout.name,
                    description=description,
                    amount=checkout.amount,
                    currency=checkout.currency,
                    quantity=checkout.quantity,
                )
            ],
            success_url=stripe_success_url,
            cancel_url=cancel_url,
            customer_email=customer_email,
        )
        session.stripe_session_id = stripe_session.id
        session.save()

        return session


@admin.register(CheckoutSession)
class CheckoutSessionAdmin(admin.ModelAdmin):
    list_display = ("id", "checkout", "date_created")
    ordering = ("-date_created",)
