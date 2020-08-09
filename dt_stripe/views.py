from click import get_current_context
from django.http import (
    Http404,
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponseNotFound,
    HttpResponseRedirect,
)
from django.shortcuts import get_object_or_404, render
from django.urls import reverse, reverse_lazy
from django.views.generic import *

from .forms import *
from .models import *


class IndexView(TemplateView):
    template_name = "dt_stripe/index.html"


class CustomerListView(ListView):
    model = Customer


class CustomerCreateView(FormView):
    template_name = "dt_stripe/customer_create.html"
    form_class = CustomerForm
    success_url = reverse_lazy("dt-stripe:customer-list")

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


class CustomerDetailView(View):
    # TODO: redirect via GET when POST is successful to prevent duplicate POSTS on refresh
    template_name = "dt_stripe/customer_detail.html"

    def get(self, request, customer_id):
        customer = get_object_or_404(Customer, id=customer_id)
        context = {}
        context["customer"] = customer

        context["subscribe_form"] = SubscribeForm(customer=customer)
        context["unsubscribe_form"] = UnsubscribeForm(customer=customer)
        context["order_form"] = OrderForm()

        return render(request, CustomerDetailView.template_name, context=context)

    def post(self, request, customer_id):
        customer = get_object_or_404(Customer, id=customer_id)
        action = request.GET.get("action", None)
        if not action:
            raise Http404()

        context = {}
        context["customer"] = customer
        context["subscribe_form"] = SubscribeForm(customer=customer)
        context["unsubscribe_form"] = UnsubscribeForm(customer=customer)
        context["order_form"] = OrderForm()

        if action == "subscribe":
            subscribe_form = SubscribeForm(request.POST, customer=customer)
            if subscribe_form.is_valid():
                try:
                    subscribe_form.subscribe(customer)
                    context["subscribe_success"] = True
                except DtStripeError as e:
                    context["subscribe_error"] = e.message
            else:
                context["subscribe_form"] = subscribe_form
        elif action == "unsubscribe":
            unsubscribe_form = UnsubscribeForm(request.POST, customer=customer)
            if unsubscribe_form.is_valid():
                try:
                    unsubscribe_form.unsubscribe(customer)
                    context["unsubscribe_success"] = True
                except DtStripeError as e:
                    context["unsubscribe_error"] = e.message
            else:
                context["unsubscribe_form"] = unsubscribe_form
        elif action == "order":
            order_form = OrderForm(request.POST)
            if order_form.is_valid():
                try:
                    order_form.order(customer)
                    context["order_success"] = True
                except DtStripeError as e:
                    context["order_error"] = e.message
            else:
                context["order_form"] = order_form

        return render(request, CustomerDetailView.template_name, context=context)


class CustomerSubscribe(View):
    def post(self, request, customer_id, plan_id):
        redirect_url = reverse("dt-stripe:customer-detail", args=[customer_id])
        customer: Customer = get_object_or_404(Customer, id=customer_id)
        plan: Plan = get_object_or_404(Plan, id=plan_id)

        try:
            customer.subscribe(plan)
        except DtStripeError as e:
            return HttpResponseRedirect("{}?error={}".format(redirect_url, e.message))
        else:
            return HttpResponseRedirect(redirect_url)


class CustomerCancelSubscription(View):
    def post(self, request, customer_id, plan_id):
        redirect_url = reverse("dt-stripe:customer-detail", args=[customer_id])
        customer: Customer = get_object_or_404(Customer, id=customer_id)
        plan: Plan = get_object_or_404(Plan, id=plan_id)

        try:
            customer.cancel_subscription(plan)
        except DtStripeError as e:
            return HttpResponseRedirect("{}?error={}".format(redirect_url, e.message))
        else:
            return HttpResponseRedirect(redirect_url)


class CustomerOrder(View):
    def post(self, request, customer_id, sku_id):
        redirect_url = reverse("dt-stripe:customer-detail", args=[customer_id])
        customer: Customer = get_object_or_404(Customer, id=customer_id)
        sku: SKU = get_object_or_404(SKU, id=sku_id)

        try:
            from_token = request.POST.from_token
            if from_token:
                token = request.POST.token
                set_source = request.POST.set_source
            else:
                token = None
        except AttributeError:
            raise Http404()

        try:
            if set_source:
                customer.set_source(token)
                token = None
            customer.order(sku, token)
        except DtStripeError as e:
            return HttpResponseRedirect("{}?error={}".format(redirect_url, e.message))
        else:
            return HttpResponseRedirect(redirect_url)


class ProductListView(ListView):
    model = Product


class ProductCreateView(FormView):
    template_name = "dt_stripe/product_create.html"
    form_class = ProductForm
    success_url = reverse_lazy("dt-stripe:product-list")

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


class PlanListView(ListView):
    model = Plan


class PlanCreateView(FormView):
    template_name = "dt_stripe/plan_create.html"
    form_class = PlanForm
    success_url = reverse_lazy("dt-stripe:plan-list")

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


class SKUListView(ListView):
    model = SKU


class SKUCreateView(FormView):
    template_name = "dt_stripe/sku_create.html"
    form_class = SKUForm
    success_url = reverse_lazy("dt-stripe:sku-list")

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)
