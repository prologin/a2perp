from django.views.generic import ListView, DetailView, View, TemplateView, RedirectView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.http import FileResponse, Http404, HttpResponse
from django.urls import reverse
from django.db.models import Q, F
from django.shortcuts import get_object_or_404
from . import models
from valentin.utils import EnsureStaffMixin
from written_exams.models import Submission

from pathlib import Path

# overseer
from written_exams import models as we_models
from se_forms import models as se_models

class HomeView(LoginRequiredMixin, RedirectView):

    def get_redirect_url(self, *args, **kwargs):
        if self.request.user.is_staff:
            return reverse('semifinals:organizer-home')
        return reverse('semifinals:contestant-home')

class HomeContestant(LoginRequiredMixin, TemplateView):
    template_name = 'semifinals/contestant-home.html'

class HomeOrganizer(EnsureStaffMixin, TemplateView):
    template_name = 'semifinals/organizer-home.html'

class SessionList(LoginRequiredMixin, ListView):
    model = models.Session
    template_name = 'semifinals/session-list.html'

    def get_queryset(self):
        return models.Session.get_user_sessions(self.request.user)

class SessionDetail(LoginRequiredMixin, DetailView):
    model = models.Session
    template_name = 'semifinals/session-details.html'

    def get_queryset(self):
        DETAILS_ALLOWED_STATUSES = (models.SessionStatuses.OPEN, models.SessionStatuses.SUBMISSIONS_CLOSED)
        return models.Session.get_user_sessions(self.request.user).filter(status__in=DETAILS_ALLOWED_STATUSES)

    def get_context_data(self, object, **kwargs):
        context = super().get_context_data(**kwargs)
        submission = None
        try:
            submission = Submission.objects.get(session=object, user=self.request.user)
        except ObjectDoesNotExist:
            pass

        context['submission'] = submission
        if object.form:
            context['form_user_answers'] = object.form.get_user_answers(self.request.user)

        return context

class DownloadSessionSubjectView(LoginRequiredMixin, View):
    http_method_names = ('get',)

    def get_x_accel(self, session):
        res = HttpResponse(status=200)
        res['X-Accel-Redirect'] = Path(settings.APP_X_ACCEL_PATH) / Path(session.subject.path).relative_to(settings.MEDIA_ROOT)
        res['Content-Type'] = ''
        return res

    def get(self, request, pk, **kwargs):
        session = None
        try:
            session = models.Session.get_user_sessions(request.user).get(pk=pk, status=models.SessionStatuses.OPEN)
        except ObjectDoesNotExist:
            raise Http404()

        if not session.subject:
            raise Http404()

        if not request.user.is_staff:
            session.subject_download_count = F('subject_download_count') + 1
            session.save()

        if settings.APP_USE_X_ACCEL_REDIRECT:
            return self.get_x_accel(session)

        return FileResponse(open(session.subject.path, 'rb'), as_attachment=True)

class SessionOverseerList(EnsureStaffMixin, ListView):
    model = models.Session
    template_name = 'semifinals/session-overseer-list.html'

class SessionOverseer(EnsureStaffMixin, TemplateView):
    template_name = 'semifinals/session-overseer.html'

    def get_context_data(self, session_id, **kwargs):
        context = super().get_context_data(**kwargs)
        session = get_object_or_404(models.Session, id=session_id)
        if session.file_upload:
            file_handouts = we_models.Submission.objects.filter(session=session)
            context['nb_file_handouts'] = file_handouts.count()
            context['last_file_handouts'] = file_handouts.order_by('-last_updated')[:15]

        if not session.form is None:
            form_instance = session.form
            answers = se_models.UserAnswers.objects.filter(form=form_instance)
            context['nb_form_handouts'] = answers.count()
            context['last_form_handouts'] = answers.order_by('-last_updated')[:15]
            context['form'] = form_instance

        context['session'] = session

        return context
