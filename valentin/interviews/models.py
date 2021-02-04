from django.contrib.auth import get_user_model
from django.template.defaultfilters import date as format_date
from django.db import models
from datetime import timedelta
from django.utils import timezone
from django.conf import settings
from django.core import validators
import uuid


class SessionStatuses(models.IntegerChoices):
    NOT_PUBLISHED = 0
    SLOT_INSTANCIATION = 1
    CONTESTANT_CHOICE = 2
    LOCKED = 3


class Session(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=70)
    status = models.IntegerField(choices=SessionStatuses.choices)
    upstream_id = models.IntegerField(null=True, blank=True)
    description = models.TextField(max_length=240)

    @property
    def in_phase_0(self):
        return self.status == SessionStatuses.NOT_PUBLISHED

    @property
    def in_phase_1(self):
        return self.status == SessionStatuses.SLOT_INSTANCIATION

    @property
    def in_phase_2(self):
        return self.status == SessionStatuses.CONTESTANT_CHOICE

    @property
    def in_phase_3(self):
        return self.status == SessionStatuses.LOCKED

    @classmethod
    def get_my_sessions(cls, user):
        if user.is_staff:
            return cls.objects.filter(
                status__in=(
                    SessionStatuses.SLOT_INSTANCIATION,
                    SessionStatuses.CONTESTANT_CHOICE,
                    SessionStatuses.LOCKED,
                )
            )
        return cls.objects.filter(
            status__in=(SessionStatuses.CONTESTANT_CHOICE, SessionStatuses.LOCKED)
        )

    def __str__(self):
        return self.name


class Slot(models.Model):
    session = models.ForeignKey(to="interviews.Session", on_delete=models.CASCADE)
    date_start = models.DateTimeField()
    date_end = models.DateTimeField()

    @property
    def local_display(self):
        start = format_date(self.date_start, "D d N Y - H:i")
        end = None
        if self.date_start.date() == self.date_end.date():
            end = format_date(self.date_end, "H:i")
        else:
            end = format_date(self.date_end, "D d N Y - H:i")
        return f"{start} à {end}"

    def __str__(self):
        return f"{self.session} : {self.local_display}"


class Interviewer(models.Model):
    user = models.OneToOneField(
        to=get_user_model(),
        primary_key=True,
        limit_choices_to={"is_staff": True},
        on_delete=models.CASCADE,
    )
    meet_link = models.URLField(verbose_name="Google Meet link", null=True, blank=True)

    def grading_targets_queryset(self, session):
        return SlotInstance.objects.filter(slot__session=session, interviewer=self)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"


class SlotInstance(models.Model):
    slot = models.ForeignKey(
        to="interviews.Slot", related_name="instances", on_delete=models.CASCADE
    )
    interviewer = models.ForeignKey(
        to="interviews.Interviewer", on_delete=models.CASCADE
    )
    contestant = models.ForeignKey(
        to=get_user_model(),
        limit_choices_to={"is_staff": False},
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    @property
    def can_see_meet_link(self):
        return (
            (
                self.slot.date_start
                - timedelta(minutes=settings.APP_ITW_MEET_UNLOCK_BEFORE)
            )
            <= timezone.now()
            <= self.slot.date_end
        )

    @property
    def contestant_full_name(self):
        if self.contestant:
            return f"{self.contestant.first_name} {self.contestant.last_name}"
        return "N/A"

    class Meta:
        unique_together = (("slot", "contestant"), ("interviewer", "slot"))

    def __str__(self):
        if self.contestant:
            return f"""
            Entretien de {self.contestant_full_name}
            avec  {self.interviewer} ({self.slot})
            """

        return f"Créneau {self.slot} avec {self.interviewer}"


class InterviewScore(models.Model):
    session = models.ForeignKey(to="interviews.Session", on_delete=models.CASCADE)
    contestant = models.ForeignKey(
        to=get_user_model(),
        limit_choices_to={"is_staff": False},
        on_delete=models.CASCADE,
    )
    grade = models.IntegerField(
        verbose_name="Note",
        help_text="Entier compris entre 0 et 5",
        validators=[validators.MinValueValidator(0), validators.MaxValueValidator(5)],
    )
    comments = models.TextField(
        verbose_name="Commentaires sur l'entretien", max_length=400
    )

    class Meta:
        unique_together = (("session", "contestant"),)

    @property
    def contestant_full_name(self):
        return f"{self.contestant.first_name} {self.contestant.last_name}"

    def __str__(self):
        return f"{self.session} {self.contestant_full_name}"
