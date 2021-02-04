from . import models
from django.core.exceptions import ObjectDoesNotExist


class FormInitialUserAnswersMixin:
    def get_user_answer(self, form_instance, user):
        try:
            return models.UserAnswers.objects.get(form=form_instance, user=user)
        except ObjectDoesNotExist:
            return models.UserAnswers(user=user, form=form_instance)

    def get_initial(self):
        if getattr(self, "user_answer", None):
            return self.user_answer.answers
        self.user_answer = self.get_user_answer(self.form_instance, self.request.user)
        return self.user_answer.answers

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user_answer"] = self.user_answer
        return context


class FormSubmitUserAnswerMixin(FormInitialUserAnswersMixin):
    def form_valid(self, form):
        self.user_answer.answers = form.cleaned_data
        self.user_answer.save()
        return super().form_valid(form)
