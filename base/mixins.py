from django.contrib.auth.mixins import UserPassesTestMixin


class StaffMemberRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        user = self.request.user
        return user and user.is_active and user.is_staff


class SuperUserRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        user = self.request.user
        return user and user.is_active and user.is_superuser
