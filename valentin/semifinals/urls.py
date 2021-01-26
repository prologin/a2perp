from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from . import views

app_name = 'semifinals'

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='/'), name='logout'),
    path('sessions/', views.SessionList.as_view(), name='session-list'),
    path('session/<uuid:pk>/', views.SessionDetail.as_view(), name='session-details'),
    path('session/<uuid:pk>/subject', views.DownloadSessionSubjectView.as_view(), name='download-subject'),

    path('overseer/', views.SessionOverseerList.as_view(), name='session-overseer-list'),
    path('overseer/<uuid:session_id>/', views.SessionOverseer.as_view(), name='session-overseer'),

    path('contestant/', views.HomeContestant.as_view(), name='contestant-home'),
    path('organizer/', views.HomeOrganizer.as_view(), name='organizer-home'),
    path('', views.HomeView.as_view(), name='home'),
]
