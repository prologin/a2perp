from django.views.generic import View, FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist, SuspiciousOperation, PermissionDenied
from django.http import HttpResponseBadRequest, Http404
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
from .models import Submission
from semifinals.models import Session, SessionStatuses
from .forms import SubmissionForm

from se_forms import models as form_models
from se_forms import file_forms


class SubmissionUploadView(LoginRequiredMixin, View):
    http_method_names = ('post',)

    def post(self, request, session_id, *args, **kwargs):
        if request.user.is_staff:
            raise SuspiciousOperation('An organizer is trying to upload submission')

        session = get_object_or_404(Session, id=session_id, status=SessionStatuses.OPEN, file_upload=True)
        form = SubmissionForm(request.POST, request.FILES)

        if form.is_valid():
            submission = None
            try:
                submission = Submission.objects.get(session=session, user=self.request.user)
            except ObjectDoesNotExist:
                submission = Submission(session=session, user=self.request.user)

            submission.file = request.FILES['file']
            submission.last_updated = timezone.now()
            submission.save()

            return redirect(reverse('semifinals:session-details', args=(session_id,)))
        return HttpResponseBadRequest('Provided File is not Valid')


class FormSubmissionView(FormView):
    template_name = 'written_exams/form-questions.html'

    def authorization(self, request):
        pass

    def get_success_url(self):
        return reverse('written_exams:form-questions', args=[self.exam_session.id])

    def dispatch(self, request, session_id, *args, **kwargs):
        if not request.user.is_authenticated:
            raise PermissionDenied

        try:
            self.exam_session = Session.get_user_sessions(request.user).get(id=session_id, form__isnull=False, status=SessionStatuses.OPEN)
        except ObjectDoesNotExist:
            raise Http404

        self.authorization(request)
        self.form_instance = self.exam_session.form
        self.extracted_form = self.form_instance.get_form()
        self.user_answers = self.get_user_answers()

        return super().dispatch(request, *args, **kwargs)

    def get_user_answers(self):
        try:
            return form_models.UserAnswers.objects.get(form=self.form_instance, user=self.request.user)
        except ObjectDoesNotExist:
            return form_models.UserAnswers(user=self.request.user, form=self.form_instance)

    def get_initial(self):
        if bool(self.user_answers.answers):
            return self.user_answers.answers
        return super().get_initial()

    def get_form(self, form_class=None):
        return file_forms.DynamicForm(self.extracted_form.questions, **self.get_form_kwargs())

    def get_context_data(self):
        context = super().get_context_data()
        context['form_instance'] = self.form_instance
        context['extracted_form'] = self.extracted_form
        context['exam_session'] = self.exam_session
        context['user_answer'] = self.user_answers
        return context

    def form_valid(self, form):
        self.user_answers.answers = form.cleaned_data
        self.user_answers.save()

        return super().form_valid(form)
