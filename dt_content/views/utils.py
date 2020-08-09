import logging

from django.urls import reverse
from django.views.generic import RedirectView

from ..mixins import SuperUserRequiredMixin


class TogglePreviewModeView(SuperUserRequiredMixin, RedirectView):
    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)

        target_mode = request.GET.get("mode", None)
        if target_mode:
            # Set to specific mode
            self.request.session["dt_content_preview_mode"] = target_mode == "true"
        else:
            # Toggle
            previous_mode = self.request.session.get("dt_content_preview_mode", False)
            self.request.session.set("dt_content_preview_mode", not previous_mode)

        self.next_url = request.GET.get("next", None)
        if not self.next_url:
            logging.warning("Accessing preview mode toggle view without next url")

    def get_redirect_url(self, *args, **kwargs):
        return self.next_url or reverse("dt-content:index")

