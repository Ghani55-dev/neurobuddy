from django.db import models
from django.contrib.auth.models import User
import pandas as pd
from sklearn.linear_model import LinearRegression
import joblib
import re
from django.apps import apps
from django.utils import timezone
from datetime import timedelta
from django.db import transaction
class MoodEntry(models.Model):
    MOOD_CHOICES = [
        (1, '😢 Very Low'),
        (2, '😟 Low'),
        (3, '😐 Neutral'),
        (4, '😊 Good'),
        (5, '😁 Very Good'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    mood_score = models.IntegerField(choices=MOOD_CHOICES)
    note = models.TextField(blank=True, null=True)
    journal = models.TextField(blank=True, null=True)
    ai_insight = models.TextField(blank=True, null=True)
    date = models.DateField(auto_now_add=True)
    sentiment = models.CharField(blank=True, null=True) 
    alert_sent = models.BooleanField(default=False)
    alert_acknowledged = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.date} - {self.get_mood_score_display()} ({self.sentiment})"
    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            self.update_streak()
    
    def update_streak(self):
        UserProfile = self._meta.model._meta.apps.get_model('accounts', 'UserProfile')
        today = timezone.localdate()
        
        # Using transaction.atomic properly
        with transaction.atomic():
            # Changed get_or_create to get since we don't need 'created'
            profile = UserProfile.objects.select_for_update().get(user=self.user)
            
            if not profile.last_mood_date:
                profile.streak_count = 1
            elif profile.last_mood_date == today - timedelta(days=1):
                profile.streak_count += 1
            elif profile.last_mood_date < today - timedelta(days=1):
                profile.streak_count = 1
            
            profile.last_mood_date = today
            profile.save()

class MoodSuggestion(models.Model):
    CATEGORY_CHOICES = [
        ("quote", "Motivational Quote"),
        ("tip", "Wellness Tip"),
        ("video", "Calming Video"),
    ]

    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    content = models.TextField(blank=True, null=True)
    video_url = models.URLField(blank=True, null=True)  # For video suggestions only
    created_at = models.DateTimeField(auto_now_add=True)
    source = models.CharField(max_length=50, default="AI")

    def save(self, *args, **kwargs):
        if self.category == "video" and self.video_url:
            # Check if full <iframe> was pasted instead of a URL
            if "<iframe" in self.video_url:
                # Extract the src URL from iframe using regex
                iframe_match = re.search(r'src="([^"]+)"', self.video_url)
                if iframe_match:
                    self.video_url = iframe_match.group(1)

            # If it's a YouTube watch or short link, convert it to embed format
            url_match = re.search(r"(?:v=|be/)([\w\-]+)", self.video_url)
            if url_match:
                video_id = url_match.group(1)
                self.video_url = f"https://www.youtube.com/embed/{video_id}"

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.category.capitalize()} - {self.content[:50]}"




def train_model():
    df = pd.read_csv('combined_mood_wearable.csv')  # Columns: mood, heart_rate, steps, sleep_hours
    X = df[['heart_rate', 'steps', 'sleep_hours']]
    y = df['mood']
    model = LinearRegression()
    model.fit(X, y)
    joblib.dump(model, 'mood_predictor.pkl')



class MoodPrediction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    predicted_score = models.FloatField()
    heart_rate = models.IntegerField()
    steps = models.IntegerField()
    sleep_hours = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)
