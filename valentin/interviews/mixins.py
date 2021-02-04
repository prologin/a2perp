from valentin.utils import EnsureStaffMixin
from django.http import Http404
from django.core.exceptions import ObjectDoesNotExist
from . import models


class EnsureInterviewerMixin(EnsureStaffMixin):
    def test_func(self):
        if super().test_func():
            try:
                self.interviewer = models.Interviewer.objects.get(
                    user=self.request.user
                )
                return True
            except ObjectDoesNotExist:
                return False
        return False


class SessionObjectMixin:
    def session_passes_test(self, session):
        return True

    def dispatch(self, request, session_id, *args, **kwargs):
        try:
            self.session = models.Session.get_my_sessions(request.user).get(
                id=session_id
            )
            if not self.session_passes_test(self.session):
                raise Http404
        except ObjectDoesNotExist:
            raise Http404
        return super().dispatch(request, *args, **kwargs)
