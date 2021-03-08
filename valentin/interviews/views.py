from django.views.generic import (
    UpdateView,
    ListView,
    FormView,
    DetailView,
    RedirectView,
)
from django.core.mail import send_mail
from itertools import groupby
from valentin.utils import EnsureStaffMixin
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.http import HttpResponseGone, HttpResponseNotFound, Http404
from django.urls import reverse_lazy
from django.core.exceptions import SuspiciousOperation, PermissionDenied
from django.db import transaction
from django.template import loader as template_loader
from . import forms, models, mixins


class InterviewerProfileEditView(EnsureStaffMixin, UpdateView):
    form_class = forms.InterviewerProfile
    model = models.Interviewer
    template_name = "interviews/profile-edit.html"
    success_url = reverse_lazy("interviews:profile")

    def get_object(self, queryset=None):
        try:
            if queryset is None:
                return self.model.objects.get(user=self.request.user)
            return queryset.get(id=self.request.user.id)
        except ObjectDoesNotExist:
            return self.model(user=self.request.user)


class SessionListView(LoginRequiredMixin, ListView):
    template_name = "interviews/sessions-list.html"

    def get_queryset(self, *args, **kwargs):
        return models.Session.get_my_sessions(self.request.user)


class InterviewerDispoSelect(
    mixins.SessionObjectMixin, mixins.EnsureInterviewerMixin, FormView
):
    template_name = "interviews/interviewer-dispos-select.html"
    form_class = forms.IntervierwerDispoSelection
    session_passes_test = (
        lambda _, session: session.in_phase_1 or session.in_phase_2
    )

    def get_success_url(self, *args, **kwargs):
        return reverse_lazy("interviews:dispo-select", args=[self.session.id])

    def get_initial(self):
        initial = super().get_initial()
        user_slots = models.SlotInstance.objects.filter(
            slot__session=self.session, interviewer=self.interviewer
        )
        initial["slot_choices"] = tuple(sloti.slot_id for sloti in user_slots)
        return initial

    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()
        self.slot_choices = tuple(
            slot
            for slot in models.Slot.objects.filter(
                session=self.session
            ).order_by("date_start")
        )
        form_kwargs["slot_choices"] = tuple(
            (slot.id, slot.local_display) for slot in self.slot_choices
        )
        return form_kwargs

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        # Because of a weird django thing we are obliged to evaluate :(
        context["grouped_slot_choices"] = tuple(
            (i, list(j))
            for i, j in groupby(
                self.slot_choices, lambda d: d.date_start.date()
            )
        )
        context["session"] = self.session
        context["interviewer"] = self.interviewer
        return context

    def form_valid(self, form=None):
        if form.has_changed():
            initial, old_choices = self.get_initial(), set()
            new_choices = set(
                int(c) for c in form.cleaned_data["slot_choices"]
            )
            if initial and (slot_choices := initial.get("slot_choices")):
                old_choices = set(int(c) for c in slot_choices)

            deleted, added = tuple(old_choices - new_choices), tuple(
                new_choices - old_choices
            )
            with transaction.atomic():
                if self.session.in_phase_1:
                    models.SlotInstance.objects.filter(
                        interviewer=self.interviewer, slot_id__in=deleted
                    ).delete()
                for slot_id in added:
                    models.SlotInstance.objects.create(
                        interviewer=self.interviewer, slot_id=slot_id
                    )
        return super().form_valid(form)


class ContestantSlotSelect(
    LoginRequiredMixin, mixins.SessionObjectMixin, FormView
):
    template_name = "interviews/contestant-slot-select.html"
    form_class = forms.ContestantSlotSelection
    success_url = reverse_lazy("interviews:list")

    def session_passes_test(self, session):
        if self.request.user.is_staff:
            raise SuspiciousOperation(
                "Staff is trying to sign up as contestant in phase2"
            )
        if not session.status == models.SessionStatuses.CONTESTANT_CHOICE:
            return False
        if models.SlotInstance.objects.filter(
            contestant=self.request.user, slot__session=session
        ).exists():
            return False
        self.available_slots = tuple(
            filter(
                lambda x: x.instances.filter(contestant__isnull=True).exists(),
                models.Slot.objects.filter(session=self.session).order_by(
                    "date_start"
                ),
            )
        )
        return True

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["session"] = self.session
        context["grouped_slot_choices"] = tuple(
            (i, list(j))
            for i, j in groupby(
                self.available_slots, lambda d: d.date_start.date()
            )
        )

        return context

    def get_form_kwargs(self, *args, **kwargs):
        form_kwargs = super().get_form_kwargs(*args, **kwargs)
        form_kwargs["slot_choices"] = tuple(
            (
                slot.id,
                f"{slot.local_display} ({slot.instances.filter(contestant__isnull=True).count()} en stock)",  # noqa
            )
            for slot in self.available_slots
        )
        return form_kwargs

    def form_valid(self, form=None):
        with transaction.atomic():
            try:
                sloti = (
                    models.SlotInstance.objects.select_for_update()
                    .filter(
                        slot=form.cleaned_data["slot_choice"],
                        contestant__isnull=True,
                    )
                    .first()
                )
                sloti.contestant = self.request.user
                sloti.save()
                if sloti.interviewer.email_notifications:
                    send_mail(
                        "[ER][ITW] Nouvel entretien avec %s"
                        % (sloti.contestant_full_name,),
                        (
                            f"""
Bonjour {sloti.interviewer},

Votre créneau du {sloti.slot.local_display} a été assigné au
candidat {sloti.contestant_full_name}.

Cordialement,

Pensez à l'environnement, imprimez cet email sur du papier recyclé
uniquement.

--
Département Entretiens
Service des Épreuves Régionales
Association Prologin
"""
                        ),
                        None,
                        [sloti.interviewer.user.email],
                        fail_silently=True,
                    )
                return super().form_valid(form)
            except ObjectDoesNotExist:
                return HttpResponseGone(
                    content_type="text/plain",
                    content="The requested slot is out of order",
                )


class InterviewRecapView(
    mixins.SessionObjectMixin, LoginRequiredMixin, DetailView
):
    template_name = "interviews/my-interview.html"

    def session_passes_test(self, session):
        if self.request.user.is_staff:
            return False
        if not (session.in_phase_2 or session.in_phase_3):
            return False
        return True

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["session"] = self.session
        return context

    def render_detailed_404(self):
        content = template_loader.render_to_string(
            "interviews/no-interview.html", {}, self.request
        )
        res = HttpResponseNotFound(content, "text/html")
        return res

    def get_object(self, *args, **kwargs):
        return self.sloti

    def get(self, request, *args, **kwargs):
        try:
            self.sloti = models.SlotInstance.objects.get(
                slot__session=self.session, contestant=request.user
            )
            return super().get(request, *args, **kwargs)
        except MultipleObjectsReturned:
            raise Exception(
                f"{request.user.first_name} {request.user.last_name} has multiple slot instance assignations."  # noqa
            )
        except ObjectDoesNotExist:
            if self.session.in_phase_2:
                raise Http404
            return self.render_detailed_404()


class ContestantInterviewPortal(
    mixins.SessionObjectMixin, LoginRequiredMixin, RedirectView
):
    def get_redirect_url(self, *args, **kwargs):
        if (
            models.SlotInstance.objects.filter(
                slot__session=self.session, contestant=self.request.user
            ).exists()
            or self.session.in_phase_3
        ):
            return reverse_lazy(
                "interviews:contestant-recap", args=[self.session.id]
            )
        return reverse_lazy("interviews:slot-select", args=[self.session.id])

    def session_passes_test(self, session):
        if self.request.user.is_staff:
            return False
        if session.in_phase_0 or session.in_phase_1:
            return False

        return True


class InterviewerSlotsList(
    mixins.SessionObjectMixin, mixins.EnsureInterviewerMixin, ListView
):
    template_name = "interviews/interviews-list.html"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["session"] = self.session
        return context

    def session_passes_test(self, session):
        return session.in_phase_2 or session.in_phase_3

    def get_queryset(self):
        return models.SlotInstance.objects.filter(
            slot__session=self.session,
            contestant__isnull=False,
            interviewer=self.interviewer,
        ).order_by("slot__date_start")


class ContestantGrading(
    mixins.SessionObjectMixin, mixins.EnsureInterviewerMixin, UpdateView
):
    template_name = "interviews/contestant-grading.html"
    form_class = forms.GradingForm

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["session"] = self.session
        return context

    def form_valid(self, form):
        self.object = form.save()
        return self.render_to_response(self.get_context_data(form=form))

    def session_passes_test(self, session):
        return session.in_phase_3 or session.in_phase_2

    def get_object(self, *args, **kwargs):
        target_uid = self.kwargs.pop("contestant_id")
        contestant = None
        try:
            contestant = get_user_model().objects.get(id=target_uid)
        except ObjectDoesNotExist:
            raise Http404

        if not (contestant.id,) in self.interviewer.grading_targets_queryset(
            self.session
        ).values_list("contestant"):
            raise PermissionDenied

        qs = models.InterviewScore.objects.filter(session=self.session)
        try:
            return qs.get(contestant=contestant)
        except ObjectDoesNotExist:
            return models.InterviewScore(
                session=self.session, contestant=contestant
            )
