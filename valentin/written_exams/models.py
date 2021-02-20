from django.core.files.storage import FileSystemStorage
import os
from django.db import models
from django.contrib.auth import get_user_model
from pathlib import Path


class OverrideStorage(FileSystemStorage):
    OS_OPEN_FLAGS = os.O_CREAT | os.O_WRONLY | getattr(os, "O_BINARY", 0)

    def get_available_name(self, name, max_length=None):
        return name


def get_path(sub, filename):
    id = f"upstream_id_not_found_{sub.user.id}"
    if not (social := sub.user.social_auth.first()) is None:
        id = social.uid
    return Path("exams_submissions") / str(sub.session.id) / f"{str(id)}.pdf"


class Submission(models.Model):
    user = models.ForeignKey(
        to=get_user_model(),
        on_delete=models.CASCADE,
        limit_choices_to={"is_staff": False},
        verbose_name="Utilisateur",
    )
    session = models.ForeignKey(
        to="semifinals.Session", on_delete=models.CASCADE
    )
    last_updated = models.DateTimeField(null=True, blank=True)
    file = models.FileField(upload_to=get_path, storage=OverrideStorage())

    def __str__(self):
        return f"{self.user}@{self.session}"

    class Meta:
        unique_together = [("user", "session")]
        permissions = [
            ("can_export_submissions", "User can export submissions")
        ]
