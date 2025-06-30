from datetime import timedelta
from django.utils import timezone
from .models import UserProfile

def update_streak(user):
    today = timezone.now().date()
    profile, created = UserProfile.objects.get_or_create(user=user)
    
    # If this is the first mood entry ever
    if not profile.last_mood_date:
        profile.streak_count = 1
        profile.last_mood_date = today
        profile.save()
        return
    
    # If already logged today, do nothing
    if profile.last_mood_date == today:
        return
    
    # If logged yesterday, increment streak
    if profile.last_mood_date == today - timedelta(days=1):
        profile.streak_count += 1
    else:
        # Otherwise reset streak
        profile.streak_count = 1
    
    profile.last_mood_date = today
    profile.save()