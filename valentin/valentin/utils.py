from django.contrib.auth.mixins import UserPassesTestMixin


class EnsureStaffMixin(UserPassesTestMixin):
    def test_func(self):
        return (
            self.request.user.is_authenticated and self.request.user.is_staff
        )
