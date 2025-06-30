from django.apps import apps
from django.utils import timezone
from datetime import timedelta

def get_streak_info(user):
    """Get streak information without triggering updates"""
    UserProfile = apps.get_model('accounts', 'UserProfile')
    profile = UserProfile.objects.get(user=user)
    return {
        'streak_count': profile.streak_count,
        'last_mood_date': profile.last_mood_date
    }