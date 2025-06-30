from django.db import models
from django.contrib.auth.models import User
from mood.models import MoodSuggestion

class SuggestionFeedback(models.Model):
    FEEDBACK_CHOICES = [
        ("like", "Like"),
        ("dislike", "Dislike"),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    suggestion = models.ForeignKey(MoodSuggestion, on_delete=models.CASCADE)
    liked = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    feedback = models.CharField(max_length=10, choices=FEEDBACK_CHOICES, default="like")
    class Meta:
        unique_together = ('user', 'suggestion')

    def __str__(self):
        return f"{self.user.username} - {self.feedback} - {self.suggestion}"

