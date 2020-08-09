import logging
import traceback

import stripe
from allauth.utils import build_absolute_uri
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View

from django_stripe import session_status, settings
from django_stripe.forms import *
from django_stripe.models import *
from django_stripe.mixins import *

logger = logging.getLogger(__name__)


class IndexView(SuperUserRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        context = dict()
        context["url_webhook_checkout_completed"] = request.build_absolute_uri(
            reverse("django_stripe:webhook_checkout_completed")
        )
        context["test_checkouts"] = Checkout.test_checkouts.all()
        return render(request, "django_stripe/index.html", context=context)


class TestCheckoutCreateView(SuperUserRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        context = dict()
        context["checkout_form"] = TestCheckoutForm()
        return render(
            request, "django_stripe/test_checkout/create.html", context=context
        )

    def post(self, request, *args, **kwargs):
        checkout = Checkout(key=ADMIN_TEST_CHECKOUT_KEY)
        form = TestCheckoutForm(request.POST, instance=checkout)
        if form.is_valid():
            form.save()
            return redirect("django_stripe:index")
        else:
            context = dict()
            context["checkout_form"] = form
            return render(
                request, "django_stripe/test_checkout/create.html", context=context
            )


class TestCheckoutPaymentView(SuperUserRequiredMixin, View):
    def get(self, request, id, *args, **kwargs):
        checkout: Checkout = get_object_or_404(Checkout.test_checkouts, id=id)
        cancel_url = request.build_absolute_uri(
            reverse("django_stripe:test_checkout_payment", args=(id,))
        )
        success_url = request.build_absolute_uri(
            reverse("django_stripe:test_checkout_payment", args=(id,))
        )
        context = dict()
        context["checkout"] = checkout
        context["checkout_session"] = checkout.get_session(cancel_url, success_url)

        return render(
            request, "django_stripe/test_checkout/payment.html", context=context
        )


def checkout_success(request):
    try:
        id = request.GET["id"]
        session = CheckoutSession.objects.get(id=id)
    except (KeyError, ObjectDoesNotExist):
        raise Http404()

    if session.completed:
        if session.checkout.status == Checkout.COMPLETE:
            status = session_status.COMPLETE
        elif session.checkout.status == Checkout.MULTIPLE_CHARGES:
            status = session_status.MULTIPLE_CHARGES
        else:
            try:
                raise AssertionError("session is complete but checkout in incomplete")
            except AssertionError as e:
                logger.error(traceback.format_exc())
    else:
        status = session_status.INCOMPLETE

    redirect_url = session.success_url + "?status={}".format(status)
    return redirect(redirect_url)


@csrf_exempt
def checkout_completed_webhook(request):
    stripe.api_key = settings.SECRET_KEY
    endpoint_secret = settings.WEBHOOK_SIGNING_SECRET
    payload = request.body
    sig_header = request.META["HTTP_STRIPE_SIGNATURE"]

    event = None
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except ValueError as e:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        return HttpResponse(status=400)

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        if CheckoutSession.verify(session.id):
            return HttpResponse(status=200)
        else:
            return HttpResponse(status=400)
    else:
        logger.warning(
            "invalid webhook type {} sent to checkout.session.completed endpoint".format(
                event["type"]
            )
        )
        return HttpResponse(status=400)
