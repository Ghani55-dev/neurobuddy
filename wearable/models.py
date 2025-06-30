from django.db import models

from django.contrib.auth.models import User

class WearableData(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    heart_rate = models.IntegerField(null=True, blank=True)
    steps = models.IntegerField(null=True, blank=True)
    sleep_hours = models.FloatField(null=True, blank=True)
    source = models.CharField(max_length=50, default='fitbit')
    collected_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.collected_at.date()}"

class EmergencyAlert(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    alert_type = models.CharField(max_length=100)  # e.g., High Heart Rate
    message = models.TextField()
    triggered_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.alert_type} at {self.triggered_at.strftime('%Y-%m-%d %H:%M')}"
