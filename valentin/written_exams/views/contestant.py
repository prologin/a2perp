from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import (
    ObjectDoesNotExist,
    SuspiciousOperation,
    PermissionDenied,
)
from django.http import HttpResponseBadRequest, Http404
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
from ..models import Submission
from semifinals.models import Session, SessionStatuses
from ..forms import SubmissionForm

from se_forms import views as se_views
from valentin.utils import EnsureStaffMixin


class SubmissionUploadView(LoginRequiredMixin, View):
    http_method_names = ("post",)

    def post(self, request, session_id, *args, **kwargs):
        if request.user.is_staff:
            raise SuspiciousOperation("An organizer is trying to upload submission")

        session = get_object_or_404(
            Session, id=session_id, status=SessionStatuses.OPEN, file_upload=True
        )
        form = SubmissionForm(request.POST, request.FILES)

        if form.is_valid():
            submission = None
            try:
                submission = Submission.objects.get(
                    session=session, user=self.request.user
                )
            except ObjectDoesNotExist:
                submission = Submission(session=session, user=self.request.user)

            submission.file = request.FILES["file"]
            submission.last_updated = timezone.now()
            submission.save()

            return redirect(reverse("semifinals:session-details", args=(session_id,)))
        return HttpResponseBadRequest("Provided File is not Valid")


class FormSubmissionView(se_views.SEEditableFormView):
    template_name = "written_exams/form-questions.html"

    def get_success_url(self):
        return reverse("written_exams:form-questions", args=[self.exam_session.id])

    def get_form_instance(self, id):
        try:
            self.exam_session = Session.get_user_sessions(self.request.user).get(
                id=id, form__isnull=False, status=SessionStatuses.OPEN
            )
        except ObjectDoesNotExist:
            raise Http404

        return self.exam_session.form

    def form_valid(self, form):
        if not self.request.user.is_staff:
            return super().form_valid(form)
        raise PermissionDenied

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["exam_session"] = self.exam_session
        return context


class FormReviewView(FormSubmissionView):
    template_name = "written_exams/form-review.html"
    http_method_names = ("get",)

    def get_form_instance(self, id):
        try:
            self.exam_session = Session.get_user_sessions(self.request.user).get(
                id=id,
                form__isnull=False,
                form_allow_review=True,
                status=SessionStatuses.SUBMISSIONS_CLOSED,
            )
        except ObjectDoesNotExist:
            raise Http404

        return self.exam_session.form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if not self.user_answer.last_updated:
            # user answers is not yet saved <=> user did not submit the form during the exam
            raise Http404
        context["staff"] = self.request.user.is_staff
        return context

    def form_valid(self, form):
        return HttpResponseBadRequest("Form is read only")
