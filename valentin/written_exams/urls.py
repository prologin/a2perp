from django.urls import path
from . import views

app_name = 'written_exams'

contestant_urls = [
    path('submission/<uuid:session_id>/', views.contestant.SubmissionUploadView.as_view(), name='submit-file'),
    path('form/<uuid:id>/', views.contestant.FormSubmissionView.as_view(), name='form-questions'),
    path('form/<uuid:id>/review/', views.contestant.FormReviewView.as_view(), name='form-review'),
]

staff_urls = [
    path('staff/form/', views.staff.FormInstanceListView.as_view(), name='form-list'),
    path('staff/form/<uuid:id>/test', views.staff.FormTestingView.as_view(), name='form-testing'),
    path('staff/form/<uuid:id>/answers', views.staff.FormAnswersListView.as_view(), name='form-answers-list'),
    path('staff/form/<uuid:id>/export', views.staff.FormGlobalExportView.as_view(), name='form-export'),
    path('staff/form-answer/<int:id>', views.staff.FormAnswersDetailView.as_view(), name='form-answers'),
]

urlpatterns = contestant_urls + staff_urls
