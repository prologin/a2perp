from django.db import models
from django.contrib.auth import get_user_model
from pathlib import Path

def get_path(sub, filename):
        return (
            Path('exams_submissions') /
            str(sub.session.id) /
            str(sub.user.social_auth.first().uid) /
            filename
        )

class Submission(models.Model):
    user = models.ForeignKey(to=get_user_model(), on_delete=models.CASCADE, verbose_name='Utilisateur')
    session = models.ForeignKey(to='semifinals.Session', on_delete=models.CASCADE)
    last_updated = models.DateTimeField(null=True, blank=True)
    file = models.FileField(upload_to=get_path)

    def __str__(self):
        return f'{self.user}@{self.session}'

    class Meta:
        unique_together = [('user', 'session')]
