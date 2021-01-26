from django.urls import path
from . import views

app_name = 'written_exams'

contestant_urls = [
    path('submission/<uuid:session_id>/', views.contestant.SubmissionUploadView.as_view(), name='submit-file'),
    path('form/<uuid:id>/', views.contestant.FormSubmissionView.as_view(), name='form-questions'),
    path('form/<uuid:id>/review/', views.contestant.FormReviewView.as_view(), name='form-review'),
]

staff_urls = [
    path('staff/form-test/', views.staff.FormTestingListView.as_view(), name='form-testing-list'),
    path('staff/form-test/<uuid:id>/', views.staff.FormTestingView.as_view(), name='form-testing'),
]

urlpatterns = contestant_urls + staff_urls
