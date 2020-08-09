from django.contrib.auth.mixins import UserPassesTestMixin
from django.urls import reverse_lazy


class StaffMemberRequiredMixin(UserPassesTestMixin):
    login_url = reverse_lazy("admin:login")

    def test_func(self):
        user = self.request.user
        return user and user.is_active and user.is_staff


class SuperUserRequiredMixin(UserPassesTestMixin):
    login_url = reverse_lazy("admin:login")

    def test_func(self):
        user = self.request.user
        return user and user.is_active and user.is_superuser
