from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from django.db import transaction  # Import added
from accounts.models import UserProfile
from mood.models import MoodEntry

class Command(BaseCommand):
    help = 'Recalculates streaks for all users'

    def handle(self, *args, **options):
        with transaction.atomic():
            for profile in UserProfile.objects.all():
                entries = MoodEntry.objects.filter(user=profile.user).order_by('date')
                
                if not entries.exists():
                    profile.streak_count = 0
                    profile.last_mood_date = None
                    profile.save()
                    continue
                    
                current_streak = 1
                last_date = entries.first().date
                
                for entry in entries[1:]:
                    if entry.date == last_date + timedelta(days=1):
                        current_streak += 1
                    elif entry.date > last_date + timedelta(days=1):
                        current_streak = 1
                    last_date = entry.date
                
                profile.streak_count = current_streak
                profile.last_mood_date = last_date
                profile.save()
                
                self.stdout.write(f"Updated {profile.user.username}: streak={current_streak} last_date={last_date}")