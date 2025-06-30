from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from accounts.models import UserProfile
from datetime import date
from django.http import JsonResponse

from django.utils.timezone import now, localtime
from django.shortcuts import render
from mood.models import MoodEntry, MoodPrediction
from .ai_utils import get_daily_suggestion
from dashboard.ai_utils import get_all_suggestions, get_personalized_suggestions
from django.shortcuts import get_object_or_404
from .models import MoodSuggestion, SuggestionFeedback
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime                                                                                          
import json
from django.utils import timezone
from datetime import timedelta
from django.db import transaction

@login_required(login_url='auth_required')
def dashboard_view(request):
    user = request.user

    # 🕐 Dynamic Greeting
    current_hour = localtime(now()).hour
    if current_hour < 12:
        greeting = "Good Morning"
    elif 12 <= current_hour < 17:
        greeting = "Good Afternoon"
    else:
        greeting = "Good Evening"
    welcome_message = f"👋 {greeting}, {user.first_name or user.username}!"

    # 📊 Get or create user profile
    profile, _ = UserProfile.objects.get_or_create(user=user)

    # 🤖 AI Suggestions (personalized based on user's recent mood)
    suggestions = get_personalized_suggestions(user)

    # 📅 Recent mood entries
    recent_entries = MoodEntry.objects.filter(user=user).order_by('-date')[:5]
    has_mood_today = MoodEntry.objects.filter(user=user, date=date.today()).exists()
    
    feedbacks = SuggestionFeedback.objects.filter(user=user)
    liked_suggestion_ids = feedbacks.filter(liked=True).values_list('suggestion_id', flat=True)
    
    # Check if streak should be reset (missed a day)
    today = timezone.localdate()
    # today = timezone.now().date()
    with transaction.atomic():
        profile = UserProfile.objects.select_for_update().get(user=user)
        
        # Only update streak if last entry wasn't today
        if not MoodEntry.objects.filter(user=user, date=today).exists():
            if profile.last_mood_date:
                if profile.last_mood_date == today - timedelta(days=1):
                    # Consecutive day - increment streak
                    profile.streak_count += 1
                    profile.last_mood_date = today
                    profile.save()
                elif profile.last_mood_date < today - timedelta(days=1):
                    # Broken streak - reset to 0
                    profile.streak_count = 0
                    profile.save()
    
    # Get current streak value after potential update
    current_streak = profile.streak_count


    context = {
        "suggestions": suggestions,  # Dict with keys: quote, tip, video
        "streak": profile.streak_count,
        "profile": profile,
        "recent_entries": recent_entries,
        "show_reminder": not has_mood_today,
        "welcome_message": welcome_message,
        'liked_suggestion_ids': liked_suggestion_ids,
        'current_streak': current_streak,
        'streak_message': get_streak_message(current_streak)
    }

    return render(request, "dashboard/dashboard.html", context)

def get_streak_message(streak_count):
    if streak_count == 0:
        return "Log your mood to start a new streak!"
    elif streak_count == 1:
        return "1 day streak - keep going!"
    elif streak_count == 2:
        return "2 days streak - you're on a roll!"
    elif streak_count >= 7:
        return f"{streak_count} days streak - amazing commitment!"
    else:
        return f"{streak_count} days streak!"

@login_required
def mood_trend(request):
    entries = MoodPrediction.objects.filter(user=request.user).order_by('-timestamp')[:7][::-1]
    return JsonResponse({
        "labels": [e.timestamp.strftime("%d %b") for e in entries],
        "moods": [e.predicted_score for e in entries]
    })


@csrf_exempt  # ✅ Needed if you're sending AJAX from JS (be careful in production)
@login_required
def suggestion_feedback(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            suggestion_id = data.get('suggestion_id')
            feedback_type = data.get('feedback')

            if not suggestion_id or not feedback_type:
                return JsonResponse({"status": "error", "error": "Missing data"}, status=400)

            # Try to update if feedback already exists
            feedback_obj, created = SuggestionFeedback.objects.update_or_create(
                user=request.user,
                suggestion_id=suggestion_id,
                defaults={"feedback": feedback_type}
            )

            return JsonResponse({
                "status": "success",
                "message": "Feedback updated" if not created else "Feedback submitted"
            })

        except Exception as e:
            return JsonResponse({"status": "error", "error": str(e)}, status=500)
    
    return JsonResponse({"status": "error", "error": "Invalid request method"}, status=405)

@login_required
@require_POST
def refresh_suggestion(request):
    profile = request.user.userprofile
    profile.last_suggestion_date = None
    profile.last_suggestion = None
    profile.save()
    return redirect('dashboard')


def custom_login_prompt(request):
    return render(request, 'dashboard/custom_login_prompt.html')
