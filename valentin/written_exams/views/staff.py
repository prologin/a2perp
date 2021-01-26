from se_forms import views as se_views
from django.core.exceptions import ObjectDoesNotExist
from se_forms import models as se_models
from valentin.utils import EnsureStaffMixin
from django.http import JsonResponse, Http404
from django.urls import reverse
from django.views.generic import ListView

class FormTestingView(EnsureStaffMixin, se_views.BaseSEFormView):
    template_name = 'written_exams/form-testing.html'

    def form_valid(self, form):
        return JsonResponse({'is_valid': True, 'cleaned_data': form.cleaned_data })

    def form_invalid(self, form):
        dic = {
            'is_valid': False,
            'data': form.data,
            'errors': form.errors,
        }
        return JsonResponse(dic)

    def get_success_url(self):
        return reverse('written_exams:form-testing', args=[self.form_instance.id])

class FormInstanceListView(EnsureStaffMixin, ListView):
    model = se_models.FormInstance
    template_name = 'written_exams/form-list.html'


class FormAnswersListView(EnsureStaffMixin, ListView):
    template_name = 'written_exams/form-answers-list.html'

    def get_queryset(self):
        try:
            self.form_instance = se_models.FormInstance.objects.get(id=self.kwargs['id'])
        except (ObjectDoesNotExist):
            raise Http404
        return self.form_instance.user_answers.all().order_by('-last_updated')

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['form_instance'] = self.form_instance
        return context
