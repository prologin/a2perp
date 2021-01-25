from django.contrib.auth.mixins import LoginRequiredMixin
from . import mixins
from django.views.generic import FormView
from .file_forms import DynamicForm

class BaseSEFormView(LoginRequiredMixin, FormView):

    def get_form_instance(self, id):
        try:
            return form_models.FormInstance.objects.get(id=id)
        except ObjectDoesNotExist:
            raise Http404

    def get_extracted_form(self):
        self.form_instance = self.get_form_instance(self.kwargs.pop('id'))
        return self.form_instance.get_form()

    def get_form_class(self):
        return DynamicForm

    def get_form_kwargs(self):
        self.extracted_form = self.get_extracted_form()
        kwargs = super().get_form_kwargs()
        kwargs['extracted_fields'] = self.extracted_form.questions
        return kwargs

    def get_context_data(self):
        context = super().get_context_data()
        context['form_instance'] = self.form_instance
        context['extracted_form'] = self.extracted_form
        return context

class SEFormView(mixins.FormInitialUserAnswersMixin, BaseSEFormView):
    pass

class SEEditableFormView(mixins.FormSubmitUserAnswerMixin, BaseSEFormView):
    pass
