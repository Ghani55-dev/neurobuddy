from django.db import models

from django.contrib.auth.models import User

class WellnessGoal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    goal_text = models.CharField(max_length=255)
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    target_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.goal_text}"

class Goal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.text

class GoalProgress(models.Model):
    goal = models.ForeignKey(Goal, on_delete=models.CASCADE, related_name='progress')
    date = models.DateField(auto_now_add=True)
    completed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.goal.text[:30]} - {'Done' if self.completed else 'Pending'}"
