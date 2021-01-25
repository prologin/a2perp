from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
import uuid
from . import file_forms, validators

class FormInstance(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    subject_path = models.CharField(
        max_length=200,
        help_text='Path to the subject relative to PROLOGIN_FORMS_REPOSITORY',
        validators=(validators.validate_form,)
    )
    display_name = models.CharField(max_length=80, unique=True)

    def __str__(self):
        return self.display_name

    def get_user_answers(self, user):
        try:
            return UserAnswers.objects.get(user=user, form=self)
        except ObjectDoesNotExist:
            return None

    def get_form(self):
        with open(file_forms.get_full_subject_path(self.subject_path)) as f:
            return file_forms.FormBuilder.load_yaml(f).build()

class UserAnswers(models.Model):
    user = models.ForeignKey(to=get_user_model(), on_delete=models.CASCADE)
    form = models.ForeignKey(to='se_forms.FormInstance', on_delete=models.CASCADE)
    answers = models.JSONField()
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (('user', 'form'),)
        verbose_name = 'user answers'
        verbose_name_plural = 'user answers'

    def __str__(self):
        return f'{self.user}@{self.form}'
