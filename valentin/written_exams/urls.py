from django.urls import path
from . import views

app_name = 'written_exams'

urlpatterns = [
    path('submission/<uuid:session_id>/', views.SubmissionUploadView.as_view(), name='submit-file'),
]