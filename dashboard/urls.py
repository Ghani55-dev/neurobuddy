from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path("suggestion-feedback/", views.suggestion_feedback, name="suggestion_feedback"),
    path('refresh-suggestion/', views.refresh_suggestion, name='refresh_suggestion'),
    path('auth-required/', views.custom_login_prompt, name='auth_required'),



]
