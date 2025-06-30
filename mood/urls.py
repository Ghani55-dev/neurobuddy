from django.urls import path
from . import views

urlpatterns = [
    path('submit/', views.mood_submit_view, name='submit_mood'),
    path('history/', views.mood_history_view, name='mood_history'),
    path('chart/', views.mood_chart_view, name='mood_chart'),
    path('gpt-summary/', views.gpt_mood_summary_view, name='gpt_summary'),
    path('submit/', views.mood_submit, name='mood_submit'),
    path('cancel-alert/', views.cancel_alert, name='cancel_alert'),

]
