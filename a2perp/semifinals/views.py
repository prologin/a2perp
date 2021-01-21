from django.views.generic import ListView, DetailView, View, TemplateView, RedirectView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from django.http import FileResponse, Http404
from django.urls import reverse
from django.db.models import Q
from . import models
from a2perp.utils import EnsureStaffMixin
from written_exams.models import Submission

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
        return models.Session.objects.filter(status__in=(models.SessionStatuses.TEASED, models.SessionStatuses.OPEN, models.SessionStatuses.SUBMISSIONS_CLOSED))

class SessionDetail(LoginRequiredMixin, DetailView):
    model = models.Session
    template_name = 'semifinals/session-details.html'

    def get_queryset(self):
        return models.Session.objects.filter(status__in=(models.SessionStatuses.OPEN, models.SessionStatuses.SUBMISSIONS_CLOSED))
    
    def get_context_data(self, object, **kwargs):
        context = super().get_context_data(**kwargs)
        submission = None
        try:
            submission = Submission.objects.get(session=object, user=self.request.user)
        except ObjectDoesNotExist:
            pass
        context['submission'] = submission

        return context

class DownloadSessionSubjectView(View):
    http_method_names = ('get',)

    def get(self, request, pk, **kwargs):
        session = get_object_or_404(models.Session, id=pk, status=models.SessionStatuses.OPEN)
        if not session.subject:
            raise Http404()
        return FileResponse(open(session.subject.path, 'rb'), as_attachment=True)

class SessionOverseerList(EnsureStaffMixin, ListView):
    model = models.Session
    template_name = 'semifinals/session-overseer-list.html'