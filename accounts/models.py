from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    streak_count = models.PositiveIntegerField(default=0)
    last_mood_date = models.DateField(null=True, blank=True)
    emergency_contact_email = models.EmailField(blank=True, null=True)
    emergency_contact_number = models.CharField(max_length=15, blank=True, null=True)
    last_suggestion_date = models.DateField(null=True, blank=True)
    last_suggestion = models.ForeignKey('mood.MoodSuggestion', null=True, blank=True, on_delete=models.SET_NULL)
    def __str__(self):
        return f"{self.user.username} Profile"

