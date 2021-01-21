from django.db import models
from pathlib import Path
import uuid

def get_session_subject_path(obj, filename):
    return Path('session_subjects') / str(obj.id) / str(filename)

class SessionStatuses(models.IntegerChoices):
    NOT_PUBLISHED = 0
    TEASED = 1
    OPEN = 2
    SUBMISSIONS_CLOSED = 3

class Session(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, verbose_name='ID')
    upstream_id = models.IntegerField(help_text='ID de l\'ER sur le site Prologin', null=True, blank=True)
    display_name = models.CharField(max_length=100, help_text='Nom affiché de la session')
    date_start = models.DateTimeField(verbose_name='Début')
    date_end = models.DateTimeField(verbose_name='Fin')
    status = models.IntegerField(choices=SessionStatuses.choices, verbose_name='Statut')
    subject = models.FileField(upload_to=get_session_subject_path, null=True, blank=True)
    contestant_instructions = models.TextField(max_length=1000)

    def __str__(self):
        return self.display_name