from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist, SuspiciousOperation, PermissionDenied
from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
from .models import Submission
from semifinals.models import Session, SessionStatuses
from .forms import SubmissionForm


class SubmissionUploadView(LoginRequiredMixin, View):
    http_method_names = ('post',)

    def post(self, request, session_id, *args, **kwargs):
        if request.user.is_staff:
            raise SuspiciousOperation('An organizer is trying to upload submission')

        session = get_object_or_404(Session, id=session_id, status=SessionStatuses.OPEN)
        print(request.FILES)
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