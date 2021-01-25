from . import models

class FormInitialUserAnswersMixin():

    def get_user_answer(self, form_instance, user):
        try:
            return models.UserAnswers.objects.get(form=form_instance, user=user)
        except ObjectDoesNotExist:
            return models.UserAnswers(user=request.user, form=form_instance)

    def get_initial(self):
        self.user_answer = self.get_user_answer(self.form_instance, self.request.user)
        return self.user_answer.answers

    def get_context_data(self):
        context = super().get_context_data()
        context['user_answer'] = self.user_answer
        return context

class FormSubmitUserAnswerMixin(FormInitialUserAnswersMixin):

    def form_valid(self, form):
        self.user_answer.answers = form.cleaned_data
        self.user_answer.save()
        return super().form_valid(form)
