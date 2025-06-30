from django.urls import path
from . import views
from .views import smart_todo_view, neurogoals_view, suggest_goals, toggle_goal_completion
urlpatterns = [
    path('', views.neurobuddy_chat, name='neurobuddy_chat'),
    path('tips/', smart_todo_view, name="smart_todo"),
    path('goals/', neurogoals_view, name='neurogoals'),
    path('suggest-goals/', suggest_goals, name='suggest_goals'),
    path('goal/toggle/<int:progress_id>/', toggle_goal_completion, name='toggle_goal_completion'),


]
