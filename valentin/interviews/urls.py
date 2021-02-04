from django.urls import path
from . import views

app_name = "interviews"

urlpatterns = [
    path(
        "profile/", views.InterviewerProfileEditView.as_view(), name="profile"
    ),
    path("sessions/", views.SessionListView.as_view(), name="list"),
    path(
        "<uuid:session_id>/dispo-select/",
        views.InterviewerDispoSelect.as_view(),
        name="dispo-select",
    ),
    path(
        "<uuid:session_id>/slot-select/",
        views.ContestantSlotSelect.as_view(),
        name="slot-select",
    ),
    path(
        "<uuid:session_id>/recap/",
        views.InterviewRecapView.as_view(),
        name="contestant-recap",
    ),
    path(
        "<uuid:session_id>/my-itw/",
        views.ContestantInterviewPortal.as_view(),
        name="contestant-portal",
    ),
    path(
        "<uuid:session_id>/my-itws/",
        views.InterviewerSlotsList.as_view(),
        name="interviewer-interviews",
    ),
    path(
        "<uuid:session_id>/grading/<int:contestant_id>/",
        views.ContestantGrading.as_view(),
        name="contestant-grading",
    ),
]
