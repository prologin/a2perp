from se_forms import views as se_views
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.mixins import PermissionRequiredMixin
from se_forms import models as se_models
from valentin.utils import EnsureStaffMixin
from django.http import JsonResponse, Http404
from django.urls import reverse
from django.views.generic import ListView, View
from django.db import transaction
from django.utils import timezone
from .. import models
from semifinals.models import Session
from django.conf import settings
from django.http import FileResponse, HttpResponse
from pathlib import Path


class FormTestingView(EnsureStaffMixin, se_views.BaseSEFormView):
    template_name = "written_exams/form-testing.html"

    def form_valid(self, form):
        return JsonResponse(
            {"is_valid": True, "cleaned_data": form.cleaned_data}
        )

    def form_invalid(self, form):
        dic = {
            "is_valid": False,
            "data": form.data,
            "errors": form.errors,
        }
        return JsonResponse(dic)

    def get_success_url(self):
        return reverse(
            "written_exams:form-testing", args=[self.form_instance.id]
        )


class FormInstanceListView(EnsureStaffMixin, ListView):
    model = se_models.FormInstance
    template_name = "written_exams/form-list.html"


class FormAnswersListView(EnsureStaffMixin, ListView):
    template_name = "written_exams/form-answers-list.html"

    def get_queryset(self):
        try:
            self.form_instance = se_models.FormInstance.objects.get(
                id=self.kwargs["id"]
            )
        except (ObjectDoesNotExist):
            raise Http404
        return self.form_instance.user_answers.all().order_by("-last_updated")

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["form_instance"] = self.form_instance
        return context


class FormAnswersDetailView(EnsureStaffMixin, se_views.SEFormView):
    template_name = "written_exams/form-review.html"
    http_method_names = ("get",)

    def get_extracted_form(self):
        try:
            self.user_answer = se_models.UserAnswers.objects.get(
                id=self.kwargs.pop("id")
            )
        except ObjectDoesNotExist:
            raise Http404
        self.form_instance = self.user_answer.form
        return self.form_instance.get_form()

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["staff"] = True
        if not (social := self.user_answer.user.social_auth.first()) is None:
            context["target_uid"] = social.uid
        return context


class FileSubmissionsListView(
    PermissionRequiredMixin, EnsureStaffMixin, ListView
):
    permission_required = ("written_exams.can_export_submissions",)
    template_name = "written_exams/submissions-list.html"

    def get_queryset(self):
        try:
            self.session = Session.objects.get(id=self.kwargs["session_id"])
            return models.Submission.objects.filter(
                session_id=self.session.id
            ).order_by("-last_updated")
        except ObjectDoesNotExist:
            raise Http404

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["session"] = self.session
        return context


class FileSubmissionDownloadView(
    PermissionRequiredMixin, EnsureStaffMixin, View
):
    permission_required = ("written_exams.can_export_submissions",)
    http_method_names = ("get",)

    def get_x_accel(self, submission):
        res = HttpResponse(status=200)
        res["X-Accel-Redirect"] = Path(settings.APP_X_ACCEL_PATH) / Path(
            submission.file.path
        ).relative_to(settings.MEDIA_ROOT)
        res["Content-Type"] = ""
        return res

    def get(self, request, submission_id, **kwargs):
        submission = None
        try:
            submission = models.Submission.objects.get(id=submission_id)
        except ObjectDoesNotExist:
            raise Http404

        if settings.APP_USE_X_ACCEL_REDIRECT:
            return self.get_x_accel(submission)

        return FileResponse(open(submission.file.path, "rb"))


class FormGlobalExportView(EnsureStaffMixin, View):
    http_method_names = ("get",)

    def get(self, request, id, *args, **kwargs):
        with transaction.atomic():
            try:
                form_instance = se_models.FormInstance.objects.get(id=id)
            except ObjectDoesNotExist:
                raise Http404

            dic = {}
            dic["id"] = form_instance.id
            dic["display_name"] = form_instance.display_name
            dic["answers"] = []

            for user_answer in form_instance.user_answers.filter(
                user__is_staff=False
            ):
                res = {
                    "user": {"has_social_auth": False, "prologin_uid": None}
                }
                res["user"]["first_name"] = user_answer.user.first_name
                res["user"]["last_name"] = user_answer.user.last_name
                res["user"]["email"] = user_answer.user.email

                if (
                    not (social := user_answer.user.social_auth.first())
                    is None
                ):
                    res["user"]["has_social_auth"] = True
                    res["user"]["prologin_uid"] = social.uid

                res["answers"] = user_answer.answers
                res["last_updated"] = user_answer.last_updated

                dic["answers"].append(res)

            dic["export_date"] = timezone.now()
            date_filename = dic["export_date"].strftime("%Y-%m-%d-%Hh-%Mm-%Ss")

            response = JsonResponse(dic)
            response[
                "Content-Disposition"
            ] = f"attachment; filename={form_instance.id}_{date_filename}.json;"  # noqa
            return response
