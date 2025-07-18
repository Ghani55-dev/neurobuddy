from django import forms
from .models import EntertainmentVideo, VideoComment
from django.core.exceptions import ValidationError
import os
class VideoUploadForm(forms.ModelForm):
    class Meta:
        model = EntertainmentVideo
        fields = ['title', 'description', 'video_file', 'category', 'duration']

    def clean_video_file(self):
        video_file = self.cleaned_data.get('video_file')

        if not video_file:
            raise ValidationError("Couldn't read uploaded file")

        # ✅ Check file extension
        valid_extensions = ['.mp4', '.mov', '.avi', '.mkv']
        ext = os.path.splitext(video_file.name)[1].lower()
        if ext not in valid_extensions:
            raise ValidationError(f"Invalid video file format. Allowed formats: {', '.join(valid_extensions)}")

        # ✅ Check file size
        if video_file.size > 100 * 1024 * 1024:
            raise ValidationError("File too large. Max allowed size is 100MB.")

        return video_file
        
class CommentForm(forms.ModelForm):
    class Meta:
        model = VideoComment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={
                'rows': 2,
                'placeholder': 'Add a comment...',
                'class': 'form-control'
            })
        }

class ReplyForm(forms.ModelForm):
    class Meta:
        model = VideoComment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 1, 'placeholder': 'Write a reply...'})
        }
        