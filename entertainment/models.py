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
import requests
from django.core.files.temp import NamedTemporaryFile
from django.core.files.base import ContentFile
from cloudinary import uploader

STATUS_CHOICES = (
    ('pending', 'Pending'),
    ('approved', 'Approved'),
    ('rejected', 'Rejected'),
)
class EntertainmentVideo(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    video_file = CloudinaryField('video', resource_type='video', allowed_formats=['mp4', 'mov', 'avi', 'mkv'])
    thumbnail = models.ImageField(upload_to='video_thumbnails/', blank=True, null=True)
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
        if not self.video_file:
            raise ValidationError("A video file is required.")

        valid_extensions = ['.mp4', '.mov', '.avi', '.mkv']

    # Try to get the file name safely
        file_name = getattr(self.video_file, 'name', None)

        if file_name:
            ext = os.path.splitext(file_name)[1].lower()
            if ext not in valid_extensions:
                raise ValidationError("Unsupported video file extension.")
        else:
        # fallback: Cloudinary? check public_id or URL
            file_url = getattr(self.video_file, 'url', '')
            ext = os.path.splitext(file_url)[1].lower()
            if ext not in valid_extensions:
                raise ValidationError("Unsupported video file format.")


    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)  # Save video first

    # Skip if thumbnail already exists
        if self.thumbnail or not self.video_file:
            return

        try:
        # Only proceed if Cloudinary URL is detected
            if "res.cloudinary.com" in self.video_file.url:
                # Generate Cloudinary thumbnail URL (frame from 2 seconds)
                cloudinary_thumb_url = self.video_file.url.replace('/upload/', '/upload/so_2/')\
                                                      .replace('.mp4', '.jpg')

                # Download the image
                response = requests.get(cloudinary_thumb_url)
                if response.status_code == 200:
                    file_name = f"{uuid.uuid4().hex}.jpg"
                    self.thumbnail.save(file_name, ContentFile(response.content), save=False)
                    super().save(update_fields=["thumbnail"])
                else:
                    print("Cloudinary thumbnail not fetched properly")

        except Exception as e:
            print(f"[Thumbnail Error]: {str(e)}")


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