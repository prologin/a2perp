from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ObjectDoesNotExist
from pathlib import Path
from semifinals.models import Session, SessionStatuses

import tarfile


class Command(BaseCommand):
    """
    This commands makes a lazy tarball of exams submissions
    """

    help = "Exports the tarball of file submissions for specified exam"

    def add_arguments(self, parser):
        parser.add_argument("session_id")
        parser.add_argument("tarball_path")

    def handle(self, *args, **options):
        session_id, tarball_path = (
            options["session_id"],
            options["tarball_path"],
        )

        try:
            session = Session.objects.get(id=session_id)
        except ObjectDoesNotExist:
            raise CommandError(f"No session with id {session_id}")

        if session.status not in (
            SessionStatuses.NOT_PUBLISHED,
            SessionStatuses.SUBMISSIONS_CLOSED,
        ):
            raise CommandError(
                "To continue, session must be either closed or not published"
            )

        base_path = (
            Path(settings.MEDIA_ROOT) / "exams_submissions" / str(session.id)
        )

        if not base_path.exists():
            raise CommandError("No submissions yet for this session")

        if not base_path.is_dir():
            raise CommandError(
                "Somebody has done something stupid, Contact a Prologin root"
            )

        with tarfile.open(tarball_path, "w:xz") as tar:
            tar.add(base_path, arcname=base_path.name)

        self.stdout.write(self.style.SUCCESS(f"Tarball at {tarball_path}"))
