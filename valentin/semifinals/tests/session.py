from django.test import TestCase
from ..models import Session, SessionStatuses
from django.contrib.auth import get_user_model
from django.utils import timezone


class SessionVisibilityNotPublished(TestCase):
    session_status = SessionStatuses.NOT_PUBLISHED
    allowed_for_staff = True
    allowed_for_all = False

    def setUp(self):
        self.non_staff_user = get_user_model().objects.create(
            username="non_staff_user", is_staff=False
        )
        self.staff_user = get_user_model().objects.create(
            username="staff_user", is_staff=True
        )
        self.session = Session.objects.create(
            display_name="NOTPUS",
            status=self.session_status,
            date_start=timezone.now(),
            date_end=timezone.now(),
            file_upload=False,
            form_allow_review=False,
            contestant_instructions="N/A",
        )

    def test_staff_user(self):
        if self.allowed_for_staff:
            return self.assertIn(
                self.session, Session.get_user_sessions(self.staff_user)
            )
        return self.assertNotIn(
            self.session, Session.get_user_sessions(self.staff_user)
        )

    def test_non_staff_user(self):
        if self.allowed_for_all:
            return self.assertIn(
                self.session, Session.get_user_sessions(self.non_staff_user)
            )
        return self.assertNotIn(
            self.session, Session.get_user_sessions(self.non_staff_user)
        )


class SessionVisibilityTeased(SessionVisibilityNotPublished):
    session_status = SessionStatuses.TEASED
    allowed_for_staff = True
    allowed_for_all = True


class SessionVisibilityOpen(SessionVisibilityNotPublished):
    session_status = SessionStatuses.OPEN
    allowed_for_staff = True
    allowed_for_all = True


class SessionVisibilitySubmissionsClosed(SessionVisibilityNotPublished):
    session_status = SessionStatuses.SUBMISSIONS_CLOSED
    allowed_for_staff = True
    allowed_for_all = True
