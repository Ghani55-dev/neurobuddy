from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save
import subprocess
import uuid
from django.urls import reverse
from django.core.exceptions import ValidationError
import os
from django.conf import settings
from django.core.files import File
from PIL import Image
from cloudinary.models import CloudinaryField
STATUS_CHOICES = (
    ('pending', 'Pending'),
    ('approved', 'Approved'),
    ('rejected', 'Rejected'),
)
class EntertainmentVideo(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    video_file = CloudinaryField('video', resource_type='video')
    thumbnail = CloudinaryField('image', blank=True, null=True)
    upload_date = models.DateTimeField(auto_now_add=True)
    category = models.CharField(max_length=50, default='General')  # e.g., "funny", "inspirational", "relaxing"
    duration = models.IntegerField(default=60)  # in seconds
    likes = models.ManyToManyField(User, related_name='liked_videos', blank=True)
    views = models.IntegerField(default=0)
    share_token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    
    
    def get_absolute_url(self):
        return reverse('video_detail', args=[str(self.id)])
    
    def get_shareable_url(self):
        return reverse('shared_video', args=[str(self.share_token)])
    
    def clean(self):
        """Validate that video_file exists before saving"""
        if not self.video_file:
            raise ValidationError("A video file is required")
        
        # Validate file extension
        ext = self.video_file.name.split('.')[-1].lower()
        if ext not in ['mp4', 'mov', 'avi', 'mkv']:
            raise ValidationError("Unsupported video format.")

    def save(self, *args, **kwargs):
        self.full_clean()  # validate before saving
        super().save(*args, **kwargs)

        # try:
        #     if self.video_file and self.video_file.path and os.path.exists(self.video_file.path):
        #         if not self.thumbnail:
        #             generate_thumbnail(self)
        #         compress_video(self)
        # except Exception as e:
        #     print(f"Error during video processing: {e}")

    def __str__(self):
        return self.title
    def total_likes(self):
        return self.likes.count()


def generate_thumbnail(instance):
    if not instance.video_file:
        return

    input_path = instance.video_file.path
    output_dir = os.path.join(settings.MEDIA_ROOT, 'video_thumbnails')
    os.makedirs(output_dir, exist_ok=True)

    thumb_filename = f"{uuid.uuid4().hex}.jpg"
    output_path = os.path.join(output_dir, thumb_filename)

    # Capture thumbnail using ffmpeg
    command = [
        'ffmpeg',
        '-i', input_path,
        '-ss', '00:00:01.000',
        '-vframes', '1',
        output_path
    ]

    try:
        subprocess.run(command, check=True)
        with open(output_path, 'rb') as f:
            instance.thumbnail.save(thumb_filename, File(f), save=False)
        instance.save()
    except Exception as e:
        print(f"Error generating thumbnail: {e}")
        
def compress_video(instance):
    if not instance.video_file:
        return

    input_path = instance.video_file.path

    if '_compressed' in input_path:
        print("Video already compressed. Skipping.")
        return

    base, ext = os.path.splitext(os.path.basename(input_path))
    compressed_filename = f"{base}_compressed.mp4"
    output_path = os.path.join(os.path.dirname(input_path), compressed_filename)

    command = [
        'ffmpeg',
        '-i', input_path,
        '-vcodec', 'libx264',
        '-crf', '28',
        output_path
    ]

    try:
        subprocess.run(command, check=True)
        with open(output_path, 'rb') as f:
            instance.video_file.save(compressed_filename, File(f), save=False)
        instance.save()
    except Exception as e:
        print(f"Error during compression: {e}")



class VideoComment(models.Model):
    video = models.ForeignKey(EntertainmentVideo, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')
    is_approved = models.BooleanField(default=True)  # AI Moderation Flag

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'{self.user.username} - {self.text[:30]}'


class Playlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    videos = models.ManyToManyField(EntertainmentVideo, through='PlaylistVideo')

    def __str__(self):
        return self.title

class PlaylistVideo(models.Model):
    playlist = models.ForeignKey(Playlist, on_delete=models.CASCADE)
    video = models.ForeignKey(EntertainmentVideo, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)
    position = models.PositiveIntegerField()

    class Meta:
        ordering = ['position']


class WatchHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    video = models.ForeignKey(EntertainmentVideo, on_delete=models.CASCADE)
    watched_at = models.DateTimeField(auto_now_add=True)
    progress = models.IntegerField(default=0)  # in seconds
    
    class Meta:
        ordering = ['-watched_at']
        unique_together = ['user', 'video']
        

class VideoRecommendation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    video = models.ForeignKey(EntertainmentVideo, on_delete=models.CASCADE)
    recommended_on = models.DateTimeField(auto_now_add=True)
    mood_score = models.FloatField()  # The mood score when recommended
    shown = models.BooleanField(default=False)
    clicked = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-recommended_on']