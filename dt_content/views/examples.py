from django.urls import reverse_lazy
from django.views.generic import RedirectView
from django.views.generic.base import TemplateView

from ..mixins import PreviewModeMixin, StaffMemberRequiredMixin
from .core import PageView


class ExampleSiteIndexView(StaffMemberRequiredMixin, PageView):
    template_name = "dt_content/example/site/index.html"
    menu_base_url = reverse_lazy("dt-content:example-site-page-base")


class ExampleSitePageView(StaffMemberRequiredMixin, PageView):
    template_name = "dt_content/example/site/page.html"
    menu_base_url = reverse_lazy("dt-content:example-site-page-base")


class ExampleStaticBlockView(StaffMemberRequiredMixin, PreviewModeMixin, TemplateView):
    template_name = "dt_content/example/static_block.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["dt_content_preview_mode"] = self.get_preview_mode()
        return context


class ExampleStaticSectionView(
    StaffMemberRequiredMixin, PreviewModeMixin, TemplateView
):
    template_name = "dt_content/example/static_section.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["dt_content_preview_mode"] = self.get_preview_mode()
        return context


class ExampleBlurbView(StaffMemberRequiredMixin, PreviewModeMixin, TemplateView):
    template_name = "dt_content/example/blurb.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["dt_content_preview_mode"] = self.get_preview_mode()
        return context


class ExampleImageBlurbView(StaffMemberRequiredMixin, PreviewModeMixin, TemplateView):
    template_name = "dt_content/example/image_blurb.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["dt_content_preview_mode"] = self.get_preview_mode()
        return context
