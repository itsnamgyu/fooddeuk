import logging
import stripe

from django.apps import apps
from django.db import models, transaction
from django.utils.translation import gettext_lazy as _
from stripe.api_resources.abstract.listable_api_resource import ListableAPIResource

from . import settings
from .errors import *
from .managers import *

stripe.api_key = settings.SECRET_KEY


# TODO: fix the test console (optional-ize Stripe)
# TODO: create templatetag for StripeJS thing


def list_all(t: ListableAPIResource):
    """Retrieve all objects of type t from Stripe. Should work for
    Product, Plan. SKU.
    """
    objects = []
    last_id = None
    has_more = True

    while has_more:
        response = t.list(limit=100, starting_after=last_id)
        has_more = response.has_more
        objects.append(response.data)
        last_id = objects[-1].id

    return objects


class Customer(models.Model):
    stripe_id = models.CharField(
        _("id"), max_length=128, help_text="Id of Stripe Customer", db_index=True
    )
    name = models.CharField(_("name"), max_length=128, null=True, blank=True)
    email = models.EmailField(_("email"), max_length=254, null=True, blank=True)
    description = models.TextField(
        _("description"), help_text=_("Description for admins"), null=True, blank=True
    )

    SOURCE_NONE = "NA"
    SOURCE_FAILED = "FA"
    SOURCE_AVAILABLE = "AV"
    source_status_choices = [
        (SOURCE_NONE, "None"),
        (SOURCE_FAILED, "Source payment failed"),
        (SOURCE_AVAILABLE, "Source available"),
    ]
    source_status = models.CharField(
        _("source status"),
        max_length=2,
        choices=source_status_choices,
        default=SOURCE_NONE,
    )

    default_source_id = models.CharField(
        _("default source id"), max_length=128, null=True
    )
    default_source_brand = models.TextField(_("default source brand"), null=True)
    default_source_last4 = models.CharField(
        _("default source last 4 digits"), max_length=4, null=True
    )

    def save(self, *args, **kwargs):
        if self._state.adding:  # initial save
            self._create_stripe_object()
        super().save(*args, **kwargs)

    def _create_stripe_object(self):
        stripe_object = stripe.Customer.create(
            email=self.email, name=self.name, description=self.description
        )
        self.stripe_id = stripe_object.id

    def set_source(self, token, **kwargs):
        try:
            customer = stripe.Customer.modify(self.stripe_id, source=token)
            source = customer.sources.data[0]
        except stripe.error.StripeError as e:
            raise DtStripeError.from_stripe_error(e)
        self.source_status = Customer.SOURCE_AVAILABLE
        self.default_source_id = source.id
        self.default_source_brand = source.brand
        self.default_source_last4 = source.last4
        self.save()

    def order(self, sku, token=None, **kwargs):
        try:
            stripe_order = stripe.Order.create(
                customer=self.stripe_id,
                currency=sku.currency,
                items=[{"type": "sku", "parent": sku.stripe_id}],
            )
            if token:
                stripe_order = stripe.Order.pay(stripe_order.id, source=token)
            else:
                stripe_order = stripe.Order.pay(
                    stripe_order.id, customer=self.stripe_id
                )
        except stripe.error.StripeError as e:
            self.source_status = Customer.SOURCE_FAILED
            self.save()
            raise DtStripeError.from_stripe_error(e)
        order = Order(stripe_id=stripe_order.id, customer=self, sku=sku)
        order.save()
        return order

    def subscribe(self, plan):
        # TODO: prevent duplicate subscriptions
        sub = self.get_subscription(plan)
        status = sub.status
        if status == Subscription.SUBSCRIPTION_ACTIVE:
            raise DtStripeError(
                "DUPLICATE_SUBSCRIPTION", "Attempting a duplicate subscription."
            )
        elif status == Subscription.SUBSCRIPTION_CANCEL_AT_PERIOD_END:
            try:
                stripe_sub = stripe.Subscription.modify(
                    sub.stripe_id, cancel_at_period_end=True
                )
            except stripe.error.StripeError as e:
                raise DtStripeError.from_stripe_error(e)
        else:  # CANCELED or NONE
            try:
                stripe_sub = stripe.Subscription.create(
                    customer=self.stripe_id, plan=plan.stripe_id
                )
            except stripe.error.StripeError as e:
                self.source_status = Customer.SOURCE_FAILED
                self.save()
                raise DtStripeError.from_stripe_error(e)
        sub.stripe_id = stripe_sub.id
        sub.status = Subscription.SUBSCRIPTION_ACTIVE
        sub.save()
        return sub

    def cancel_subscription(self, plan):
        sub = self.get_subscription(plan)
        if not sub or sub.status != Subscription.SUBSCRIPTION_ACTIVE:
            raise DtStripeError(
                "NO_ACTIVE_SUBSCRIPTION", "There is no active subscription to cancel."
            )
        try:
            stripe.Subscription.modify(sub.stripe_id, cancel_at_period_end=True)
        except stripe.error.StripeError as e:
            raise DtStripeError.from_stripe_error(e)
        sub.status = Subscription.SUBSCRIPTION_CANCEL_AT_PERIOD_END
        sub.save()
        return sub

    def get_subscription(self, plan):
        obj, created = self.subscriptions.get_or_create(plan=plan)
        return obj

    def get_subscription_status(self, plan):
        return self.get_subscription(plan).status

    def __str__(self):
        try:
            return self.name
        except AttributeError:
            return "Incomplete customer"


class Product(models.Model):
    stripe_id = models.CharField(
        _("id"), max_length=128, help_text="Id of Stripe Product", db_index=True
    )
    name = models.CharField(_("name"), max_length=128)
    description = models.TextField(
        _("description"),
        help_text=_(
            "Description to be shown to the user. Only for products of type 'good'."
        ),
        null=True,
        blank=True,
    )

    GOOD = "good"
    SERVICE = "service"
    TYPE_CHOICES = [(GOOD, "Good"), (SERVICE, "Service")]
    product_type = models.CharField(_("type"), max_length=16, choices=TYPE_CHOICES)

    SYNC_FIELDS = ["name", "description"]

    objects = models.Manager()
    services = ServiceManager()
    goods = GoodManager()

    def save(self, *args, **kwargs):
        if self._state.adding:  # initial save
            self._create_stripe_object()
        super().save(*args, **kwargs)

    def _create_stripe_object(self):
        if self.product_type == "good":
            stripe_object = stripe.Product.create(
                name=self.name, type=self.product_type, shippable=False
            )
        else:
            stripe_object = stripe.Product.create(
                name=self.name, type=self.product_type
            )
        self.stripe_id = stripe_object.id

    @classmethod
    def sync(cls, product):
        """Update or create internal Product object according to product object
        from stripe API.
        """
        try:
            local_product = Product.get(stripe_id=product.id)
        except Product.DoesNotExist:
            local_product = Product

        local_product.product_type = product.type
        for field in cls.SYNC_FIELDS:
            setattr(local_plan, field, getattr(plan, field))
        local_plan.save()

        return local_plan

    @staticmethod
    def sync_all():
        products = list_all(stripe.Product)
        for product in products:
            Product.sync(product)

    def __str__(self):
        try:
            return self.name
        except AttributeError:
            return "Incomplete product"


class Plan(models.Model):
    stripe_id = models.CharField(
        _("id"), max_length=128, help_text=_("Id of Stripe Plan"), db_index=True
    )

    DAILY = "day"
    WEEKLY = "week"
    MONTHLY = "month"
    YEARLY = "year"
    INTERVAL_CHOICES = [
        (DAILY, "Daily"),
        (WEEKLY, "Weekly"),
        (MONTHLY, "Monthly"),
        (YEARLY, "Yearly"),
    ]

    product = models.ForeignKey(Product, on_delete="CASCADE", related_name="plans")
    amount = models.IntegerField(_("amount"))
    currency = models.CharField(_("currency"), max_length=3, default="usd")
    interval = models.CharField(_("interval"), max_length=16, choices=INTERVAL_CHOICES)
    interval_count = models.IntegerField(
        _("count"),
        default=1,
        help_text=_(
            "Number of intervals per billing cycle. I.e., interval=month and interval_count=3 for 3 months."
        ),
    )

    name = models.CharField(
        _("name"),
        help_text=_("Local name for use by admins"),
        max_length=128,
        null=True,
    )
    description = models.TextField(
        _("description"),
        help_text=_("Local description for use by admins"),
        null=True,
        blank=True,
    )

    SYNC_FIELD = ["amount", "currency", "interval", "interval_count"]

    objects = PlanManager()

    @staticmethod
    def create(product: Product, name: str = None, **kwargs):
        raise NotImplementedError()

    def save(self, *args, **kwargs):
        if self._state.adding:  # initial save
            self._create_stripe_object()
        super().save(*args, **kwargs)

    def _create_stripe_object(self):
        stripe_object = stripe.Plan.create(
            product=self.product.stripe_id,
            amount=self.amount,
            currency=self.currency,
            interval=self.interval,
            interval_count=self.interval_count,
        )
        self.stripe_id = stripe_object.id

    @classmethod
    def sync(cls, plan):
        """Update or create internal Plan object according to plan object
        from stripe API.
        """
        try:
            product = Product.get(stripe_id=plan.product)
        except Product.DoesNotExist:
            logging.warning(
                "Product associated to Stripe Plan object does not exist in local DB. Skipping retrieval of Plan."
            )
            return

        try:
            local_plan = Plan.get(stripe_id=plan.id)
        except Plan.DoesNotExist:
            local_plan = Plan()

        local_plan.product = product
        for field in cls.SYNC_FIELDS:
            setattr(local_plan, field, getattr(plan, field))
        local_plan.save()

        return local_plan

    @staticmethod
    def sync_all():
        plans = list_all(stripe.Plan)
        for plan in plans:
            Plan.sync(plan)

    def __str__(self):
        try:
            base = getattr(self, "name", "Plan")
            if self.currency == "usd":
                amount = "${:.2f}".format(self.amount / 100)
            else:
                amount = "{}{}".format(self.amount, self.currency.upper())
            return "{base} for {product} ({amount}/{interval_count}{interval})".format(
                base=base,
                product=self.product.name,
                amount=amount,
                interval_count="" if self.interval_count == 1 else self.interval_count,
                interval=self.interval[:1],
            )
        except AttributeError:
            return "Incomplete plan"


class SKU(models.Model):
    stripe_id = models.CharField(
        _("id"), max_length=128, help_text=_("Id of Stripe SKU"), db_index=True
    )
    product = models.ForeignKey(Product, on_delete="CASCADE", related_name="skus")
    price = models.IntegerField(_("price"))
    currency = models.CharField(_("currency"), max_length=3, default="usd")

    name = models.CharField(
        _("name"),
        help_text=_("Local name for use by admins"),
        max_length=128,
        null=True,
    )
    description = models.TextField(
        _("description"),
        help_text=_("Local description for use by admins"),
        null=True,
        blank=True,
    )

    INFINITE_INVENTORY = {"type": "infinite"}
    SYNC_FIELDS = ["price", "currency"]

    def save(self, *args, **kwargs):
        if self._state.adding:  # initial save
            self._create_stripe_object()
        super().save(*args, **kwargs)

    def _create_stripe_object(self):
        stripe_object = stripe.SKU.create(
            product=self.product.stripe_id,
            price=self.price,
            currency=self.currency,
            inventory=SKU.INFINITE_INVENTORY,
        )
        self.stripe_id = stripe_object.id

    @classmethod
    def sync(cls, sku):
        """Update or create internal SKU object according to SKU object
        from stripe API.
        """
        try:
            product = Product.get(stripe_id=sku.product)
        except Product.DoesNotExist:
            logging.warning(
                "Product associated to Stripe SKU object does not exist in local DB. Skipping retrieval of SKU."
            )
            return

        try:
            local_sku = SKU.get(stripe_id=sku.id)
        except SKU.DoesNotExist:
            local_sku = SKU()

        local_sku.product = product
        for field in cls.SYNC_FIELDS:
            setattr(local_sku, field, getattr(sku, field))
        local_sku.save()

        return local_sku

    @staticmethod
    def sync_all():
        skus = list_all(stripe.SKU)
        for sku in skus:
            SKU.sync(sku)

    def __str__(self):
        try:
            base = getattr(self, "name", "SKU")
            if self.currency == "usd":
                price = "${:.2f}".format(self.price / 100)
            else:
                price = "{}{}".format(self.price, self.currency.upper())
            return "{base} for {product} ({price})".format(
                base=base, product=self.product.name, price=price
            )
        except AttributeError:
            return "Incomplete SKU"


class Subscription(models.Model):
    stripe_id = models.CharField(
        _("id"), max_length=128, help_text=_("Id of Stripe Subscription"), db_index=True
    )
    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE, related_name="subscriptions"
    )
    plan = models.ForeignKey(
        Plan, on_delete=models.CASCADE, related_name="subscriptions"
    )

    SUBSCRIPTION_NONE = "NA"
    SUBSCRIPTION_ACTIVE = "AV"
    SUBSCRIPTION_CANCEL_AT_PERIOD_END = "CE"
    SUBSCRIPTION_CANCELED_BY_EXPIRY = "CX"
    SUBSCRIPTION_CANCELED_BY_PAYMENT_ISSUE = "CP"
    status_choices = [
        (SUBSCRIPTION_NONE, "No subscription"),
        (SUBSCRIPTION_ACTIVE, "Active"),
        (SUBSCRIPTION_CANCEL_AT_PERIOD_END, "Active until end of billing cycle)"),
        (SUBSCRIPTION_CANCELED_BY_EXPIRY, "Canceled due to expiry"),
        (SUBSCRIPTION_CANCELED_BY_PAYMENT_ISSUE, "Canceled due to payment issue"),
    ]
    status = models.CharField(
        _("status"), max_length=2, choices=status_choices, default=SUBSCRIPTION_NONE
    )

    def __str__(self):
        try:
            plan = getattr(self.plan, "name", self.plan.product.name)
            customer = getattr(self.customer, "name", self.customer.stripe_id)
            status = self.get_status_display()
            return "Subscription to {plan} by {customer} ({status})".format(
                plan=plan, customer=customer, status=status
            )
        except AttributeError:
            return "Incomplete subscription"


class Order(models.Model):
    stripe_id = models.CharField(
        _("id"), max_length=128, help_text=_("Id of Stripe Order"), db_index=True
    )
    date_created = models.DateTimeField(_("date created"), auto_now_add=True)
    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE, related_name="orders"
    )
    sku = models.ForeignKey(SKU, on_delete=models.CASCADE, related_name="orders")

    def __str__(self):
        try:
            sku = getattr(self.sku, "name", self.sku.product.name)
            customer = getattr(self.customer, "name", self.customer.stripe_id)
            return "Order for {plan} by {customer}".format(plan=plan, customer=customer)
        except AttributeError:
            return "Incomplete subscription"
