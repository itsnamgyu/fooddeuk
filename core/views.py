from django.apps import apps
from django.shortcuts import render
from django.urls import reverse_lazy

from dt_content.views.core import PageView as BasePageView


class IndexView(BasePageView):
    template_name = "core/index.html"
    menu_base_url = reverse_lazy("core:page-base")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["dt_stripe"] = apps.is_installed("dt_stripe")
        context["simple_sendgrid"] = apps.is_installed("simple_sendgrid")
        return context


class PageView(BasePageView):
    template_name = "core/page.html"
    menu_base_url = reverse_lazy("core:page-base")
