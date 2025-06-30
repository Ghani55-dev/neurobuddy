from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from accounts.models import UserProfile

class Command(BaseCommand):
    help = 'Checks and resets streaks for users who missed logging their mood'

    def handle(self, *args, **options):
        today = timezone.now().date()
        cutoff_date = today - timedelta(days=1)
        
        # Reset streaks for users who haven't logged in since yesterday
        profiles_to_reset = UserProfile.objects.filter(
            last_mood_date__lt=cutoff_date
        ).exclude(streak_count=0)
        
        count = profiles_to_reset.update(streak_count=0)
        self.stdout.write(f"Reset streaks for {count} users")
        