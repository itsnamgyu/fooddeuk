import logging

from django.contrib.auth import logout
from django.contrib.auth.mixins import UserPassesTestMixin
from django.urls import reverse_lazy
from django.views import View


class SuperUserRequiredMixin(UserPassesTestMixin):
    login_url = reverse_lazy("admin:login")
    auto_logout = True

    def test_func(self):
        user = self.request.user
        if user.is_active and user.is_superuser:
            return True
        if self.auto_logout:
            logout(self.request)
        return False


class StaffMemberRequiredMixin(UserPassesTestMixin):
    login_url = reverse_lazy("admin:login")
    auto_logout = True

    def test_func(self):
        user = self.request.user
        if user.is_active and user.is_staff:
            return True
        if self.auto_logout:
            logout(self.request)
        return False


class PreviewModeMixin:
    def get_preview_mode(self, request=None):
        if not request:
            try:
                request = self.request
            except KeyError:
                logging.warning(
                    "PreviewMixin.get_preview_mode called before self.request has been set"
                )
                return False
        return request.session.get("dt_content_preview_mode", False)
