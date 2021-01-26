from se_forms import views as se_views
from se_forms import models as se_models
from valentin.utils import EnsureStaffMixin
from django.http import JsonResponse
from django.urls import reverse
from django.views.generic import ListView

class FormTestingView(EnsureStaffMixin, se_views.BaseSEFormView):
    template_name = 'written_exams/form-testing.html'

    def get_success_url(self):
        return reverse('written_exams:form-testing', args=[self.form_instance.id])

class FormTestingListView(EnsureStaffMixin, ListView):
    model = se_models.FormInstance
    template_name = 'written_exams/form-testing-list.html'
